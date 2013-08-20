import pandas as pd
import datetime

from datacombo.models import School, SchoolParticipation, Student, Response, ImportSession
from datacombo.helpers import round_time_conversion


def process_uploaded(file, filetype):
    #Create context first to catch all message
    try:
        #Load it as a CSV file
        newcsv = pd.read_csv(uploaded_file)
    except pd._parser.CParserError:
        context = {}
        context['not_csv_file'] = True
    else:
        # Create new import session first
        # First, remember this import session
        session = ImportSession()
        session.title = session_title
        session.date_created = datetime.datetime.now()
        session.save()
        # Next, check what kind of CSV file we're uploading
        # and call in the appropriate upload function

        file_type = request.POST['file_type']
        if filetype == 'legacy':
            context = upload_legacy_data(newcsv, survey, session)
        elif filetype == 'panel':
            pass
        elif filetype == 'raw':
            pass
    return context


def upload_legacy_data(newcsv, survey, session):
    context = {}
    # Tallies of new objects
    number_of_new_schools = 0
    number_of_new_participations = 0
    number_of_new_students = 0
    number_of_rows = len(newcsv)
    number_of_datapoints = 0

    # List of objects for bulk creation later
    new_schools_list = []
    new_records_list = []
    new_students_list = []
    new_responses_list = []


    # Create a few aggregate dataframe for lookup use later:
    tallies = newcsv.groupby(['School_Short', 'School_Name']).size()
    tallies = tallies.reset_index()
    surveycode = survey.alpha_suffix()
    tallies['abbr'] = tallies['School_Short'].str[:-3]
    tallies['alpha'] = tallies['abbr'] + '-' + surveycode
    tallies = tallies.set_index('School_Short')
    # Create a record of unique triples of PIN, ID and School_Short
    csv_pin = newcsv.groupby(['PIN', 'ID', 'School_Short']).size()
    csv_pin = csv_pin.reset_index()
    # Set PIN as index for faster lookup
    csv_pin = csv_pin.set_index('PIN')
    csv_columns = newcsv.columns.tolist()

    # Create/update schools
    # First get a list of currently existing schools to match with the new list of schools
    school_alphalist = School.objects.values_list('alpha', flat=True)
    for a in tallies['alpha']:
        if a in school_alphalist:
            pass
        else:
            series = tallies[tallies['alpha'] == a]
            sch_obj = School()
            sch_obj.abbrev_name = series['abbr'][0]
            sch_obj.name = series['School_Name'][0]
            sch_obj.alpha = a
            sch_obj.imported_thru = session
            # Append to object list for bulk create later
            new_schools_list.append(sch_obj)
            # Add up the tallies
            number_of_new_schools += 1
    # Bulk create new school objects
    School.objects.bulk_create(new_schools_list)


    # Create/update school participation records
    # Retrieve the current set of participation records for this survey
    survey_record_list = survey.schoolparticipation_set.values('legacy_school_short', 'id')
    survey_record_dict = {}
    for valdict in survey_record_list:
        ss = valdict['legacy_school_short']
        i = valdict['id']
        survey_record_dict[ss] = i
    # Get a new set of school records for lookup
    survey_new_sch_list = School.objects.values('abbrev_name', 'id')
    survey_new_sch_dict = {}
    for valdict in survey_new_sch_list:
        abbr = valdict['abbrev_name']
        i = valdict['id']
        survey_new_sch_dict[abbr] = i
    for s in tallies.index:
        if s in survey_record_dict.keys():
            pass
        else:
            pr_obj = SchoolParticipation()
            abbr = tallies.get_value(s, 'abbr')
            pr_obj.school_id = survey_new_sch_dict[abbr]
            pr_obj.survey = survey
            survey_round = s[-3:]
            pr_obj.date_participated = round_time_conversion[survey_round]
            pr_obj.legacy_school_short = s
            pr_obj.note = 'Imported on {}'.format(session.date_created)
            pr_obj.imported_thru = session
            number_of_new_participations += 1
            # Append to object list for bulk create later
            new_records_list.append(pr_obj)
            # Add up the tallies
            number_of_new_participations += 1
    #Bulk create new participation objects
    SchoolParticipation.objects.bulk_create(new_records_list)

    # Create/update teacher records

    # Create/update course records

    # Create/update student records
    # Get the list of student records that are related to the currently existing
    # school participation records, prior to the bulk_add command
    survey_students = Student.objects.filter(surveyed_in_id__in=survey_record_dict.values())
    # Retrieve the list of existing student PINs from that list
    survey_student_pin_list = survey_students.values_list('pin', flat=True)
    # Get a fresh set of participation records after bulk creation
    survey_new_pr_list = SchoolParticipation.objects.values('legacy_school_short', 'id', 'school')
    survey_new_pr_dict = {}
    for valdict in survey_new_pr_list:
        ss = valdict['legacy_school_short']
        i = valdict['id']
        sch_id = valdict['school']
        survey_new_pr_dict[ss] = (i, sch_id)
    for p in csv_pin.index:
        # If the PIN in the CSV file matches the current PIN list, do not create a new student
        if p in survey_student_pin_list:
            pass
        else:
            std_obj = Student()
            std_obj.pin = p
            std_obj.response_id = csv_pin.get_value(p, 'ID')
            #Blank for now
            #std_obj.course
            #std_obj.teacher
            schshort = csv_pin.get_value(p, 'School_Short')
            std_obj.surveyed_in_id = survey_new_pr_dict[schshort][0]
            std_obj.imported_thru = session
            # Append to object list for bulk create later
            new_students_list.append(std_obj)
            # Add up the tallies
            number_of_new_students += 1
    # Bulk create new student objects
    Student.objects.bulk_create(new_students_list)

    # Create/update response records
    survey_varlist = survey.variable_set.values('name', 'id')
    survey_vardict = {}
    for valdict in survey_varlist:
        varname = valdict['name']
        varid = valdict['id']
        survey_vardict[varname] = varid
    # Get the list of PRecord IDs from the fresh set of participation records
    survey_new_pr_id_list = [tpl[0] for tpl in survey_new_pr_dict.values()]
    # Get the fresh set of student records from this "fresh" set of participation records
    # This will include the new student objects that have been added
    survey_new_std = Student.objects.filter(surveyed_in_id__in=survey_new_pr_id_list)
    survey_new_std_list = survey_new_std.values('pin', 'id')
    survey_new_std_dict = {}
    for valdict in survey_new_std_list:
        pin = valdict['pin']
        i = valdict['id']
        survey_new_std_dict[pin] = i

    # Now create a dictionary with key as the variable name from survey_varlist
    # and value as status of whether that variable exists in the CSV file
    var_status = {}
    for var in survey_vardict.keys():
        if var in csv_columns:
            var_status[var] = 1
        else:
            var_status[var] = 0
        for i in newcsv.index:
            row = newcsv.ix[i]
            a = row[var]
            if pd.isnull(a):
                pass
            else:
                resp = Response()
                resp.question_id = survey_vardict[var]
                resp.survey = survey
                resp.answer = a
                pin = row['PIN']
                resp.student_id = survey_new_std_dict[pin]
                # resp.on_course = cse_obj
                # Assign response to school
                schshort = csv_pin.get_value(pin, 'School_Short')
                resp.on_school_id = survey_new_pr_dict[schshort][1]
                resp.imported_thru = session
                # Append to object list for bulk create later
                new_responses_list.append(resp)
                # Add up the tallies
                number_of_datapoints += 1
            # If the list of responses reach 500, we'll do bulk create and reset the list
            if len(new_responses_list) == 500:
                Response.objects.bulk_create(new_responses_list)
                new_responses_list = []
    # Bulk create new response objects
    Response.objects.bulk_create(new_responses_list)
    new_responses_list = []

    # Load all variables into the context for view rendering
    context['survey_name'] = survey.name
    context['number_of_rows'] = number_of_rows
    context['number_of_datapoints'] = number_of_datapoints
    context['var_status_dict'] = var_status
    context['number_of_new_schools'] = number_of_new_schools
    context['number_of_new_participations'] = number_of_new_participations
    context['number_of_new_students'] = number_of_new_students
    context['sch_objects'] = School.objects.filter(imported_thru=session)
    context['participation_objects'] = SchoolParticipation.objects.filter(imported_thru=session)
    context['session_id'] = session.id
    return context
