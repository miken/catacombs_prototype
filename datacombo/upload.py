import pandas as pd
import datetime

# Set up RQ queue
import django_rq
q = django_rq.get_queue('high')

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
        context = {}
        context['filetype'] = filetype
        context['survey_name'] = survey.name
        # Check that the user is uploading the correct CSV file
        if filetype == 'panel':
            survey_csv_colspec = survey.panel_columns_for_csv_matching()
        elif filetype == 'raw':
            survey_csv_colspec = survey.raw_columns_for_csv_matching()
        newcsv_col_set = set(newcsv.columns)
        # If the CSV files don't have all the required column names, return None
        if not set(survey_csv_colspec).issubset(newcsv_col_set):
            context['not_csv_match'] = True
        else:
            # Function to parse upload data here:
            # Send uploading process to Redis queue
            # And take parse_status from this
            parse_status = q.enqueue(upload_data,
                                     args=(newcsv, survey, session, filetype,),
                                     timeout=36000)
            if parse_status:
                session.parse_status = True
                session.save()
    return context


def upload_data(newcsv, survey, session, filetype):
    match_and_create_schools(newcsv, survey, session)
    match_and_create_schoolparticipations(newcsv, survey, session)

    # If it's a teacher feedback survey, proceed with teacher & course matching
    fresh_precords_dict = get_precords_dict(survey)
    if survey.is_teacher_feedback():
        if filetype == 'raw':
            # If we're importing raw data, we need to
            # convert newcsv to stackformat first
            csv_stacked = convert_raw_to_stack(newcsv, survey)
            # Add a new column for this table
            csv_stacked['s_t_c'] = (csv_stacked['School_Short'] +
                                    ' - ' +
                                    csv_stacked['teacherfirst'] +
                                    ' ' +
                                    csv_stacked['teacherlast'] +
                                    ' - ' +
                                    csv_stacked['coursename']
                                    )
            # Set 'ID_insert', created with convert_raw_to_stack(), as index
            csv_stacked = csv_stacked.set_index('ID_insert')
            # With a fresh list of PartipationRecords, mix & match teachers, subjects, and courses
            s_t_df = group_teacher_level(csv_stacked)
            s_t_c_df = group_course_level(csv_stacked)
        else:
            s_t_df = group_teacher_level(newcsv)
            s_t_c_df = group_course_level(newcsv)
        # Now proceed with mixing and matching
        match_and_create_teachers(s_t_df, session, fresh_precords_dict)
        match_and_create_subjects_and_courses(s_t_c_df, session, fresh_precords_dict)
        # Pair the new courses with teachers
        pair_new_courses_with_teachers(s_t_c_df, session, fresh_precords_dict)
    # Continue to add students and responses if it's raw data
    if filetype == 'raw':
        match_and_create_students(newcsv, session, fresh_precords_dict)
        # Add responses
        if survey.is_teacher_feedback():
            match_and_create_responses(csv_stacked, survey, session, fresh_precords_dict, filetype)
        else:
            match_and_create_responses(newcsv, survey, session, fresh_precords_dict, filetype)
    # If everything's good, return True to parse_status in process_uploaded
    return True


# FIX THIS
def upload_legacy_data(newcsv, survey, session):
    # Check that the user is uploading the correct CSV file
    survey_csv_colspec = survey.raw_columns_for_csv_matching()
    newcsv_col_set = set(newcsv.columns)
    # If the CSV files don't have all the required column names, return None
    if not set(survey_csv_colspec).issubset(newcsv_col_set):
        context['not_csv_match'] = True
    else:
        new_schools_dict = match_and_create_schools(newcsv, survey, session)
        new_schoolparticipations_dict = match_and_create_schoolparticipations(newcsv, survey, session)
        context['number_of_rows'] = len(newcsv)
        context['number_of_new_schools'] = new_schools_dict['newcount']
        context['number_of_new_participations'] = new_schoolparticipations_dict['newcount']
        context['added_schools'] = School.objects.filter(imported_thru=session)
        context['added_records'] = SchoolParticipation.objects.filter(imported_thru=session)
        context['session_id'] = session.id
        # If it's a teacher feedback survey, proceed with teacher & course matching
        if survey.is_teacher_feedback():
            # If we're importing raw data, we need to
            # convert newcsv to stackformat first
            csv_stacked = convert_raw_to_stack(newcsv, survey)

            fresh_precords_dict = get_precords_dict(survey)
            # With a fresh list of PartipationRecords, mix & match teachers, subjects, and courses
            s_t_df = group_teacher_level(csv_stacked)
            s_t_c_df = group_course_level(csv_stacked)
            new_teachers_dict = match_and_create_teachers(s_t_df, survey, session, fresh_precords_dict)
            new_subjects_and_courses_dict = match_and_create_subjects_and_courses(s_t_c_df, survey, session, fresh_precords_dict)
            # Pair the new courses with teachers
            pair_new_courses_with_teachers(s_t_c_df, survey, session, fresh_precords_dict)

            # Import responses from csv_stacked
        else:
            pass
            # Import responses from newcsv
        new_students_dict = match_and_create_students(newcsv, survey, session, fresh_precords_dict)


def match_and_create_responses(newcsv, survey, session, fresh_precords_dict, filetype):
    # Match & create new teachers
    number_of_new_datapoints = 0
    new_responses_list = []
    fresh_courses_dict = get_courses_dict(fresh_precords_dict)
    fresh_students_dict = get_students_dict(fresh_precords_dict)
    existing_responses_dict = get_responses_dict(survey)

    if filetype == 'raw':
        # Get the list of raw variable names for this survey
        survey_maplist = survey.varmap_set.values('raw_name', 'id')
        survey_mapdict = {}
        for valdict in survey_maplist:
            rawname = valdict['raw_name']
            mapid = valdict['id']
            survey_mapdict[rawname] = mapid
        vdict_touse = survey_mapdict
    elif filetype == 'legacy':
        # Create/update response records
        survey_varlist = survey.variable_set.values('name', 'id')
        survey_vardict = {}
        for valdict in survey_varlist:
            varname = valdict['name']
            varid = valdict['id']
            survey_vardict[varname] = varid
        vdict_touse = survey_vardict

    # Now create a dictionary with key as the variable name from either survey_mapdict
    # or survey_vardict and value as status of whether that variable exists in the CSV file
    var_status = {}
    vars_in_csv = []
    for var in vdict_touse.keys():
        if var in newcsv.columns:
            var_status[var] = 1
            vars_in_csv.append(var)
        else:
            var_status[var] = 0
    for i in newcsv.index:
        print 'Importing row {num}'.format(num=str(i+1))
        row = newcsv.ix[i]
        if survey.is_teacher_feedback() and pd.isnull(row['coursename']):
            pass
        # We can insert validation for complete response here later
        else:
            for v in vars_in_csv:        
                a = row[v]
                if pd.isnull(a):
                    pass
                else:
                    idx_str_list = []
                    if survey.is_teacher_feedback():
                        idx_str_list.append(row['s_t_c'])
                    else:
                        idx_str_list.append(row['School_Short'])
                    idx_str_list.append(v)
                    idx = ' - '.join(idx_str_list)
                    # If there's a match of student ID & variable name (idx) in the database,
                    # we'll skip adding a new variable
                    if idx in existing_responses_dict.keys():
                        pass
                    else:
                        resp = Response()
                        # If we're importing a legacy file, map directly to survey_vardict
                        if filetype == 'legacy':
                            var_id = vdict_touse[v]
                            var = survey.variable_set.get(id=var_id)
                            resp.question = var
                        # If we're importing a raw file, find the database variable
                        # that this raw variable maps to
                        elif filetype == 'raw':
                            varmap_id = vdict_touse[v]
                            varmap = survey.varmap_set.get(id=varmap_id)
                            resp.question = varmap.variable
                        resp.survey = survey
                        # If it's a qual variable, save under comment
                        if resp.question.qual:
                            resp.comment = a
                        # If it's a blank space / string garbage, skip response creation
                        elif isinstance(a, basestring):
                            continue
                        else:
                            resp.answer = a
                        pin = row['V4']
                        resp.student_id = fresh_students_dict[pin]
                        # Assign response to either course or school
                        if survey.is_teacher_feedback():
                            s_t_c_index = newcsv.get_value(i, 's_t_c')
                            resp.on_course_id = fresh_courses_dict[s_t_c_index]
                        else:
                            schshort = newcsv.get_value(i, 'School_Short')
                            resp.on_schoolrecord_id = fresh_precords_dict[schshort]
                        resp.legacy_survey_index = idx
                        resp.imported_thru = session
                        # Append to object list for bulk create later
                        new_responses_list.append(resp)
                        # Add up the tallies
                        number_of_new_datapoints += 1
        # If the list of responses reach 500, we'll do bulk create and reset the list
        if len(new_responses_list) > 500:
            Response.objects.bulk_create(new_responses_list)
            new_responses_list = []
    # Bulk create new response objects and flush out the list
    Response.objects.bulk_create(new_responses_list)
    new_responses_list = []


def match_and_create_schools(newcsv, survey, session):
    '''
    newcsv: CSV file already converted to dataframe by pandas
    survey: Survey object
    session: ImportSession object
    '''
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


def match_and_create_schoolparticipations(newcsv, survey, session):
    '''
    newcsv: CSV file already converted to dataframe by pandas
    survey: Survey object
    session: ImportSession object
    '''
    # Match & create new school participation records
    number_of_new_participations = 0
    new_records_list = []

    # Retrieve the current set of participation records for this survey
    existing_precords_dict = get_precords_dict(survey)

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
        if s in existing_precords_dict.keys():
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


def match_and_create_teachers(s_t_df, session, fresh_precords_dict):
    '''
    s_t_df: CSV file grouped by School_Short and Teacher_Full_Name
    session: ImportSession object
    fresh_precords_dict: List of IDs of ParticipationRecords, including the new ones
                         Create this by using get_precords_dict() after bulk_create
                         the new school participation records
    '''
    # Match & create new teachers
    number_of_new_teachers = 0
    new_teachers_list = []
    existing_teachers_dict = get_teachers_dict(fresh_precords_dict)

    for idx in s_t_df.index:
        if idx in existing_teachers_dict.keys():
            pass
        else:
            t = Teacher()
            t.first_name = s_t_df.get_value(idx, 'teacherfirst')
            t.last_name = s_t_df.get_value(idx, 'teacherlast')
            t.salutation = s_t_df.get_value(idx, 'teachersalutation')
            schshort = s_t_df.get_value(idx, 'School_Short')
            t.feedback_given_in_id = fresh_precords_dict[schshort]
            t.legacy_survey_index = idx
            t.imported_thru = session
            # Append to object list for bulk create later
            new_teachers_list.append(t)
            # Add up the tallies
            number_of_new_teachers += 1
    #Bulk create new participation objects
    Teacher.objects.bulk_create(new_teachers_list)


def match_and_create_subjects_and_courses(s_t_c_df, session, fresh_precords_dict):
    '''
    s_t_df: CSV file grouped by School_Short and Teacher_Full_Name
    session: ImportSession object
    '''
    # Match & create new courses and subjects
    number_of_new_subjects = 0
    new_subjects_list = []
    number_of_new_courses = 0
    new_courses_list = []
    existing_courses_dict = get_courses_dict(fresh_precords_dict)
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
            c.legacy_survey_index = idx
            schshort = s_t_c_df.get_value(idx, 'School_Short')
            c.feedback_given_in_id = fresh_precords_dict[schshort]
            c.imported_thru = session
            # Must save first before adding course
            # We'll take care of this record matching later
            # Append to object list for bulk create later
            new_courses_list.append(c)
            # Add up the tallies
            number_of_new_courses += 1
    #Bulk create new participation objects
    Course.objects.bulk_create(new_courses_list)


def pair_new_courses_with_teachers(s_t_c_df, session, fresh_precords_dict):
    '''
    Match up teachers with their corresponding courses
    Do this for just the new courses, we don't connect old courses
    with newly imported teachers, i.e., teachers don't teach courses
    that existed in the past
    '''
    # Get a fresh set of teachers to pair with new courses
    # after bulk_create command
    fresh_teachers_dict = get_teachers_dict(fresh_precords_dict)
    added_courses = Course.objects.filter(imported_thru=session)
    for c in added_courses:
        idx = c.legacy_survey_index
        # Find the teacher_id with this key
        s_t_index = s_t_c_df.get_value(idx, 's_t_index')
        teacher_id = fresh_teachers_dict[s_t_index]
        teacher = Teacher.objects.get(id=teacher_id)
        c.teacher_set.add(teacher)


def match_and_create_students(csv, session, fresh_precords_dict):
    '''
    use get_precords_dict() to retrieve a new paired set of ID and School_Short
    '''
    number_of_new_students = 0
    new_students_list = []
    # Get the list of student records that are related to the school participation records
    fresh_precords_ids = fresh_precords_dict.values()
    survey_students = Student.objects.filter(surveyed_thru_id__in=fresh_precords_ids)
    # Retrieve the list of existing student PINs from that list
    survey_student_pin_list = survey_students.values_list('pin', flat=True)
    # Set ['V4'] as index of csv
    csv = csv.set_index('V4')
    for p in csv.index:
        if pd.isnull(p):
            pass
        # If the PIN in the CSV file matches the current PIN list, do not create a new student
        elif p in survey_student_pin_list:
            pass
        else:
            std_obj = Student()
            std_obj.pin = p
            std_obj.response_id = csv.get_value(p, 'V1')
            schshort = csv.get_value(p, 'School_Short')
            std_obj.surveyed_thru_id = fresh_precords_dict[schshort]
            std_obj.imported_thru = session
            # Append to object list for bulk create later
            new_students_list.append(std_obj)
            # Add up the tallies
            number_of_new_students += 1
    # Bulk create new student objects
    Student.objects.bulk_create(new_students_list)


def get_precords_dict(survey):
    # Retrieve the current set of participation records for this survey
    survey_record_list = survey.schoolparticipation_set.values('legacy_school_short', 'id')
    survey_record_dict = {}
    for valdict in survey_record_list:
        ss = valdict['legacy_school_short']
        i = valdict['id']
        survey_record_dict[ss] = i
    return survey_record_dict


def get_teachers_dict(precords_dict):
    '''
    precords_dict can be obtained by running get_precords_dict
    Create a dict of teacher metainfo
    '''
    precords_ids = precords_dict.values()
    teachers = Teacher.objects.filter(feedback_given_in_id__in=precords_ids)
    teachers_dict = {}
    for t in teachers:
        idx = t.legacy_survey_index
        teachers_dict[idx] = t.id
    return teachers_dict


def get_courses_dict(precords_dict):
    '''
    precords_dict can be obtained by running get_precords_dict
    Create a dict of courses metainfo
    key is <School_Short> - <Teacher_Full_Name> - <Course_Name>
    value is id of course in database
    '''
    precords_ids = precords_dict.values()
    fresh_teachers = Teacher.objects.filter(feedback_given_in_id__in=precords_ids)
    courses_dict = {}
    for t in fresh_teachers:
        schshort = t.feedback_given_in.legacy_school_short
        for c in t.courses.all():
            idx = schshort + ' - ' + t.full_name() + ' - ' + c.name
            if idx in courses_dict.keys():
                pass
            else:
                courses_dict[idx] = c.id
    return courses_dict


def get_students_dict(precords_dict):
    '''
    precords_dict can be obtained by running get_precords_dict
    Create a dict of students metainfo
    key is YouthTruth Login PIN
    value is student_id in database
    '''
    precords_ids = precords_dict.values()
    fresh_students = Student.objects.filter(surveyed_thru_id__in=precords_ids)
    students_list = fresh_students.values('pin', 'id')
    students_dict = {}
    for valdict in students_list:
        pin = valdict['pin']
        i = valdict['id']
        students_dict[pin] = i
    return students_dict


def get_responses_dict(survey):
    survey_responses_list = survey.response_set.values('legacy_survey_index', 'id')
    responses_dict = {}
    for resp in survey_responses_list:
        idx = resp['legacy_survey_index']
        i = resp['id']
        responses_dict[idx] = i
    return responses_dict


def group_sshort_and_sname(newcsv, survey):
    school_short_name = newcsv.groupby(['School_Short', 'School_Name']).size()
    school_short_name = school_short_name.reset_index()
    surveycode = survey.alpha_suffix()
    school_short_name['abbr'] = school_short_name['School_Short'].str[:-3]
    school_short_name['alpha'] = school_short_name['abbr'] + '-' + surveycode
    return school_short_name


def group_teacher_level(newcsv):
    newcsv['teacherfull'] = newcsv['teacherfirst'] + ' ' + newcsv['teacherlast']
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
    return s_t_df


def group_course_level(newcsv):
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
    return s_t_c_df


def convert_raw_to_stack(newcsv, survey):
    # left_cols are columns like 'V4', 'V1', etc.
    # specified by the method raw_columns_for_csv_matching()
    # in survey
    left_cols = survey.raw_columns_for_csv_matching()
    # middle_cols are variables that are in the variable_set
    # of the survey, but are not part of the survey loop
    # e.g., race variables
    middle_cols = list(survey.variable_set.values_list('name', flat=True))
    # meta_cols are the following columns:
    # 'teachersalutation', 'teacherfirst', 'teacherlast', 'subject', 'coursename'
    # These columns values will change depending on which survey loop we're in
    meta_cols = [m for m in survey.panel_columns_for_csv_matching() if m not in left_cols]
    # right_cols are variables that are in the variable_set
    # of the survey and part of the survey loop
    # e.g., ts_enjoy --> ts_enjoy(1), ts_enjoy(2), ts_enjoy(3)
    right_cols = list(survey.variable_set.filter(in_loop=True).values_list('name', flat=True))
    stackcols = left_cols + middle_cols + meta_cols + right_cols + ['ID_insert']
    left_middle = newcsv[left_cols + middle_cols]
    # Loop from course 1 to course 5
    iterlist = [str(i) for i in range(1, 6)]
    raw_stack = pd.DataFrame(columns=stackcols)
    newcsv_cols_set = set(newcsv.columns)
    for i in iterlist:
        course_metacols = ['{metainfo}{i}'.format(metainfo=m, i=i) for m in meta_cols]
        likert_varcols = ['{var}({i})'.format(var=c, i=i) for c in right_cols]
        if set(likert_varcols).issubset(newcsv_cols_set):
            # e.g., ts_enjoy(1)
            meta = newcsv[course_metacols]
            right = newcsv[likert_varcols]
            # Rename the columns so that they conform to meta_cols and right_cols
            meta.columns = meta_cols
            right.columns = right_cols
            data_tostack = left_middle.join([meta, right])
            data_tostack['ID_insert'] = data_tostack['V1'] + ' - ' + i
            raw_stack = raw_stack.append(data_tostack)
    # raw_stack.to_csv('test.csv')
    return raw_stack
