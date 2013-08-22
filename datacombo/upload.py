import pandas as pd
import datetime

from datacombo.models import School, SchoolParticipation, Student, Response, ImportSession, Teacher, Course, Subject
from datacombo.helpers import round_time_conversion


def process_uploaded(file, filetype, survey, session_title):
    #Create context first to catch all message
    try:
        #Load it as a CSV file
        newcsv = pd.read_csv(file)
    except pd._parser.CParserError:
        context = {}
        context['not_csv_file'] = True
    else:
        # Create new import session first
        # First, remember this import session
        session = ImportSession()
        session.title = session_title
        session.import_type = filetype
        session.date_created = datetime.datetime.now()
        session.survey = survey
        session.save()
        # Next, check what kind of CSV file we're uploading
        # and call in the appropriate upload function
        if filetype == 'legacy':
            context = upload_legacy_data(newcsv, survey, session)
        elif filetype == 'panel':
            context = upload_panel_data(newcsv, survey, session)
        elif filetype == 'raw':
            context = upload_raw_data(newcsv, survey, session)
        # If there's no context returned, then it's a file mismatch
        # Let the user know in the view
        context['filetype'] = filetype
    return context


def upload_panel_data(newcsv, survey, session):
    context = {}
    context['survey_name'] = survey.name
    # Check that the user is uploading the correct CSV file
    survey_csv_colspec = survey.panel_columns_for_csv_matching()
    newcsv_col_set = set(newcsv.columns)
    # If the CSV files don't have all the required column names, return None
    if not set(survey_csv_colspec).issubset(newcsv_col_set):
        context['not_csv_match'] = True
    else:
        new_schools_dict = match_and_create_schools(newcsv, survey, session)
        new_schoolparticipations_dict = match_and_create_schoolparticipations(newcsv, survey, session)

        # If it's a teacher feedback survey, proceed with teacher & coursename creation
        if survey.is_teacher_feedback():
            newcsv['teacherfull'] = newcsv['teacherfirst'] + ' ' + newcsv['teacherlast']
            # Match & create new teachers
            number_of_new_teachers = 0
            new_teachers_list = []
            # Obtain unique list of tuples of (School_Short, teacherfull) from the CSV file
            s_t_df = newcsv.groupby(['School_Short', 'teacherfull', 'teachersalutation', 'teacherfirst', 'teacherlast']).size()
            # Release the current index and construct a custom index instead
            s_t_df = s_t_df.reset_index()
            s_t_df['index'] = s_t_df['School_Short'] + ' - ' + s_t_df['teacherfull']
            # De-dupe this index column
            # One example for this de-duping feature is let's say, there's an error in data
            # where a teacher could be "Mr. Jenny Leighton"
            # and "Ms. Jenny Leighton" in other rows
            # This de-duping method will only take the name "Jenny Leighton" into consideration
            # The teacher will be recorded as "Mr. Jenny Leighton,"
            # and we could rename salutation from Mr. to Ms. later manually
            s_t_df = s_t_df.drop_duplicates(cols='index')
            s_t_df = s_t_df.set_index('index')
            # Get the existing list of teachers 
            # prior to the bulk_create command
            existing_teachers = Teacher.objects.filter(feedback_given_in_id__in=existing_record_ids)
            # Retrieve these teachers' schoolshort + full names and id
            existing_teachers_dict = {}
            for t in existing_teachers:
                schshort = t.feedback_given_in.legacy_school_short
                idx = schshort + ' - ' + t.full_name()
                existing_teachers_dict[idx] = t.id
            # Get a fresh set of participation records to pair with new teachers
            # after bulk_create command
            fresh_records = SchoolParticipation.objects.filter(survey=survey)
            fresh_record_dict = {}
            for pr in fresh_records:
                fresh_record_dict[pr.legacy_school_short] = pr.id
            fresh_record_ids = fresh_record_dict.values()
            for idx in s_t_df.index:
                if idx in existing_teachers_dict.keys():
                    pass
                else:
                    t = Teacher()
                    t.first_name = s_t_df.get_value(idx, 'teacherfirst')
                    t.last_name = s_t_df.get_value(idx, 'teacherlast')
                    t.salutation = s_t_df.get_value(idx, 'teachersalutation')
                    schshort = s_t_df.get_value(idx, 'School_Short')
                    t.feedback_given_in_id = fresh_record_dict[schshort]
                    #t.courses = ?
                    t.imported_thru = session
                    # Append to object list for bulk create later
                    new_teachers_list.append(t)
                    # Add up the tallies
                    number_of_new_teachers += 1
            #Bulk create new participation objects
            Teacher.objects.bulk_create(new_teachers_list)

            # Match & create new courses and subjects
            number_of_new_subjects = 0
            new_subjects_list = []
            number_of_new_courses = 0
            new_courses_list = []
            # Obtain unique list of tuples of (School_Short, teacherfull) from the CSV file
            s_t_c_df = newcsv.groupby(['School_Short', 'teacherfull', 'subject', 'coursename']).size()
            s_t_c_df.name = 'size'
            # Release the current index and construct a custom index instead
            s_t_c_df = s_t_c_df.reset_index()
            s_t_c_df['index'] = s_t_c_df['School_Short'] + ' - ' + s_t_c_df['teacherfull'] + ' - ' + s_t_c_df['coursename']
            # Recreate s_t_index to pair the 2 tables
            s_t_c_df['s_t_index'] = s_t_c_df['School_Short'] + ' - ' + s_t_c_df['teacherfull']
            # De-dupe this index column
            # One example for this de-duping feature is let's say, there's an error in data
            # where a teacher could be "Mr. Jenny Leighton"
            # and "Ms. Jenny Leighton" in other rows
            # This de-duping method will only take the name "Jenny Leighton" into consideration
            # The teacher will be recorded as "Mr. Jenny Leighton,"
            # and we could rename salutation from Mr. to Ms. later manually
            s_t_c_df = s_t_c_df.drop_duplicates(cols='index')
            s_t_c_df = s_t_c_df.set_index('index')
            # Get the existing list of courses 
            # prior to the bulk_create command
            existing_courses_dict = {}
            for t in existing_teachers:
                schshort = t.feedback_given_in.legacy_school_short
                for c in t.courses.all():
                    idx = schshort + ' - ' + t.full_name() + ' - ' + c.name
                    if idx in existing_courses_dict.keys():
                        pass
                    else:
                        existing_courses_dict[idx] = c.id
            for idx in s_t_c_df.index:
                if idx in existing_courses_dict.keys():
                    pass
                else:
                    c = Course()
                    coursename = s_t_c_df.get_value(idx, 'coursename')
                    c.name = coursename
                    # Was there a subject that already exists? If not, add it
                    subject_name = s_t_c_df.get_value(idx, 'subject')
                    try:
                        s = Subject.objects.get(name=subject_name)
                    except Subject.DoesNotExist:
                        s = Subject()
                        s.name = subject_name
                        s.save()
                        number_of_new_subjects += 1
                        new_subjects_list.append(s)
                    c.subject = s
                    c.classroom_size = s_t_c_df.get_value(idx, 'size')
                    c.legacy_survey_key = idx
                    c.imported_thru = session
                    # Must save first before adding course
                    # We'll take care of this record matching later
                    # Append to object list for bulk create later
                    new_courses_list.append(c)
                    # Add up the tallies
                    number_of_new_courses += 1
            #Bulk create new participation objects
            Course.objects.bulk_create(new_courses_list)

            # Match up teachers with their corresponding courses
            # Do this for just the new courses, we don't connect old courses
            # with newly imported teachers, i.e., teachers don't teach courses
            # that existed in the past
            # Get a fresh set of teachers to pair with new courses
            # after bulk_create command
            fresh_teachers = Teacher.objects.filter(feedback_given_in_id__in=fresh_record_ids)
            fresh_teacher_dict = {}
            for t in fresh_teachers:
                schshort = t.feedback_given_in.legacy_school_short
                idx = schshort + ' - ' + t.full_name()
                fresh_teacher_dict[idx] = t.id
            added_courses = Course.objects.filter(imported_thru=session)
            for c in added_courses:
                idx = c.legacy_survey_key
                # Find the teacher_id with this key
                s_t_index = s_t_c_df.get_value(idx, 's_t_index')
                teacher_id = fresh_teacher_dict[s_t_index]
                teacher = Teacher.objects.get(id=teacher_id)
                c.teacher_set.add(teacher)

        number_of_rows = len(newcsv)

        #Assign everything to context
        context['number_of_rows'] = number_of_rows
        context['number_of_new_schools'] = new_schools_dict['newcount']
        context['number_of_new_participations'] = new_schoolparticipations_dict['newcount']
        if survey.is_teacher_feedback():
            context['number_of_new_teachers'] = number_of_new_teachers
            context['number_of_new_courses'] = number_of_new_courses
            context['number_of_new_subjects'] = number_of_new_subjects
            added_teachers = Teacher.objects.filter(imported_thru=session).order_by('feedback_given_in__school__name', 'first_name', 'last_name')
            context['added_teachers'] = added_teachers
            context['added_subjects'] = new_subjects_list
        context['added_schools'] = School.objects.filter(imported_thru=session)
        context['added_records'] = SchoolParticipation.objects.filter(imported_thru=session)
        context['session_id'] = session.id
    return context


def upload_raw_data(newcsv, survey, session):
    context = {}
    context['survey_name'] = survey.name
    # Check that the user is uploading the correct CSV file
    survey_csv_colspec = survey.raw_columns_for_csv_matching()
    newcsv_col_set = set(newcsv.columns)
    # If the CSV files don't have all the required column names, return None
    if not set(survey_csv_colspec).issubset(newcsv_col_set):
        context['not_csv_match'] = True
    else:
        new_schools_dict = match_and_create_schools(newcsv, survey, session)
        new_schoolparticipations_dict = match_and_create_schoolparticipations(newcsv, survey, session)

        # If it's a teacher feedback survey, convert_to_stack format for data import

        # Get list of response_ids
        csv_qid_list = newcsv['ResponseID'].tolist()
        # Set ResponseID as index
        newcsv = newcsv.set_index('ResponseID')
        # Filter only for those Response IDs that don't exist in database
        students_qid_matched = Student.objects.filter(response_id__in=csv_qid_list).values_list('response_id', flat=True)
        # We'll create new student objects with these IDs
        qid_to_create = [q for q in csv_qid_list if q not in students_qid_matched]
        # Create student objects
        number_of_new_students = 0
        new_students_list = []
        # For loop to create students here

        number_of_rows = len(newcsv)

        #Assign everything to context
        context['number_of_rows'] = number_of_rows
        context['number_of_new_schools'] = new_schools_dict['newcount']
        context['number_of_new_participations'] = new_schoolparticipations_dict['newcount']
        context['added_schools'] = School.objects.filter(imported_thru=session)
        context['added_records'] = SchoolParticipation.objects.filter(imported_thru=session)
        context['session_id'] = session.id
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


def match_and_create_schools(newcsv, survey, session):
    '''
    newcsv: CSV file already converted to dataframe by pandas
    survey: Survey object
    session: ImportSession object
    '''
    d = {}
    # Match & create new schools
    number_of_new_schools = 0
    new_schools_list = []
    # First get a list of currently existing schools to match with the new list of schools
    school_alphalist = School.objects.values_list('alpha', flat=True)

    # Group and set alpha index for alpha matching
    school_short_name = group_sshort_and_sname(newcsv, survey)
    csv_alpha = school_short_name.set_index('alpha')

    for a in csv_alpha.index:
        if a in school_alphalist:
            pass
        else:
            sch_obj = School()
            sch_obj.abbrev_name = csv_alpha.get_value(a, 'abbr')
            sch_obj.name = csv_alpha.get_value(a, 'School_Name')
            sch_obj.alpha = a
            sch_obj.imported_thru = session
            # Append to object list for bulk create later
            new_schools_list.append(sch_obj)
            # Add up the tallies
            number_of_new_schools += 1
    # Bulk create new school objects
    School.objects.bulk_create(new_schools_list)
    d['newcount'] = number_of_new_schools
    d['obj_list'] = new_schools_list
    return d

def match_and_create_schoolparticipations(newcsv, survey, session):
    '''
    newcsv: CSV file already converted to dataframe by pandas
    survey: Survey object
    session: ImportSession object
    '''
    d = {}
    # Match & create new school participation records
    number_of_new_participations = 0
    new_records_list = []

    # Retrieve the current set of participation records for this survey
    survey_record_list = survey.schoolparticipation_set.values('legacy_school_short', 'id')
    survey_record_dict = {}
    for valdict in survey_record_list:
        ss = valdict['legacy_school_short']
        i = valdict['id']
        survey_record_dict[ss] = i
    existing_record_ids = survey_record_dict.values()
    
    # Get a new set of school records for lookup
    survey_new_sch_list = School.objects.values('alpha', 'id')
    survey_new_sch_dict = {}
    for valdict in survey_new_sch_list:
        abbr = valdict['alpha']
        i = valdict['id']
        survey_new_sch_dict[abbr] = i
    
    # Set School_Short index for legacy_school_short matching
    school_short_name = group_sshort_and_sname(newcsv, survey)
    csv_sshort = school_short_name.set_index('School_Short')
    for s in csv_sshort.index:
        if s in survey_record_dict.keys():
            pass
        else:
            pr_obj = SchoolParticipation()
            alpha = csv_sshort.get_value(s, 'alpha')
            pr_obj.school_id = survey_new_sch_dict[alpha]
            pr_obj.survey = survey
            survey_round = s[-3:]
            pr_obj.date_participated = round_time_conversion[survey_round]
            pr_obj.legacy_school_short = s
            pr_obj.note = "Imported on {}".format(session.date_created)
            pr_obj.imported_thru = session
            number_of_new_participations += 1
            # Append to object list for bulk create later
            new_records_list.append(pr_obj)
            # Add up the tallies
            number_of_new_participations += 1
    #Bulk create new participation objects
    SchoolParticipation.objects.bulk_create(new_records_list)
    d['newcount'] = number_of_new_participations
    d['obj_list'] = new_records_list
    return d

def group_sshort_and_sname(newcsv, survey):
    school_short_name = newcsv.groupby(['School_Short', 'School_Name']).size()
    school_short_name = school_short_name.reset_index()
    surveycode = survey.alpha_suffix()
    school_short_name['abbr'] = school_short_name['School_Short'].str[:-3]
    school_short_name['alpha'] = school_short_name['abbr'] + '-' + surveycode
    return school_short_name


def convert_raw_to_stack(newcsv, survey):
    cols_to_retain = []
    left_cols = survey.raw_columns_for_csv_matching
    # Retrieve all variables for 
    right_cols = survey.variable_set.values_list('name', flat=True)
    stackcols = left_cols + right_cols + ['ID_insert']
    left = newcsv[left_cols]
    raw_stack = pd.DataFrame(columns=stackcols)
    # Loop from course 1 to course 5
    iterlist = [str(i) for i in range(1, 6)]
    for i in iterlist:
        varcols = ['{var}({i})'.format(var=varname, i=i) for c in right_cols]
        likert_data = newcsv[varcols]
        # Rename the columns so that they conform to right_cols

    raw = pd.read_csv(os.path.join(sql_dir, 'raw.csv'))
    retain_list = raw.columns[:22].tolist()                                 # in console, check that the columns run from 'ID' to 'm_gender'
    stack_list = survey_meta + varlist
    stackcols = retain_list + stack_list + ['ID_insert']
    student_meta = raw[retain_list]
    raw_stack = pd.DataFrame(columns=stackcols)
    iterlist = [str(i) for i in range(1, 5)]                                # Loop from course 1 to course 4
    for i in iterlist:
        varcols = [varname+i for varname in stack_list]
        likert_data = raw[varcols]                                          # Extract survey data for this course first
        likert_data.columns = stack_list                                    # Rename the columns so that they conform to stack_list
        data_tostack = student_meta.join(likert_data)
        data_tostack['ID_insert'] = data_tostack['ID'] + ' - ' + i
        raw_stack = raw_stack.append(data_tostack)
    raw_stack.to_csv(os.path.join(combo_dir, 'raw_stack.csv'), index=False)
    print 'Raw data saved as stacked format in raw_stack.csv'