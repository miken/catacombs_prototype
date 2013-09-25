import pandas as pd
import datetime
from time import sleep

# Set up RQ queue
import django_rq
q = django_rq.get_queue('default')

from datacombo.models import School, SchoolParticipation, Student, Response, ImportSession, Teacher, Course, Subject, VarMatchRecord
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
        session.number_of_rows = len(newcsv) - 1
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
            q.enqueue_call(
                func=parse_csv_into_database,
                args=(newcsv, survey_csv_colspec, filetype, survey, session),
            )
    return context


def parse_csv_into_database(newcsv, survey_csv_colspec, filetype, survey, session):
    '''
    Actual function that will work on parsing CSV data
    '''
    # q.enqueue_call(
    #     func=match_survey_vars_with_csv_cols,
    #     args=(newcsv, filetype, survey, session)
    # )
    match_survey_vars_with_csv_cols(newcsv, filetype, survey, session)

    # Get the list of variable names for access
    vmrecords = session.varmatchrecord_set.filter(match_status=True)
    if filetype == 'raw':
        vars_in_csv = vmrecords.values_list('raw_var__raw_name', flat=True)
        vars_in_csv = list(vars_in_csv)
    elif filetype == 'legacy':
        vars_in_csv = vmrecords.values_list('var__name', flat=True)
        vars_in_csv = list(vars_in_csv)
    else:
        vars_in_csv = []

    # First we'll filter to use only those columns available
    # in survey_csv_colspec and vars_in_csv
    filter_cols = survey_csv_colspec + vars_in_csv
    newcsv = newcsv[filter_cols]

    # Match and create schools and participation records first
    # q.enqueue_call(
    #     func=match_and_create_schools,
    #     args=(newcsv, survey, session),
    # )
    match_and_create_schools(newcsv, survey, session)
    # q.enqueue_call(
    #     func=match_and_create_schoolparticipations,
    #     args=(newcsv, survey, session),
    # )
    match_and_create_schoolparticipations(newcsv, survey, session)

    # We'll enqueue the remainder in upload_data in smaller chunks
    # Split newcsv into smaller chunks to work with, 10 rows each or so
    toprownum = 0
    while toprownum < len(newcsv):
        bottomrownum = toprownum + 10
        # If we hit the bottom of newcsv, just re-assign bottomrownum
        if bottomrownum > len(newcsv):
            bottomrownum = len(newcsv)
            # This is when we'll also update the parse status of session
            q.enqueue(update_parse_status, session)
        # Make a copy of it to see if memory size will be smaller
        csv_chunk = newcsv[toprownum:bottomrownum]
        # Enqueue the chunk uploading process
        q.enqueue_call(func=upload_data,
                       args=(csv_chunk, survey, session, filetype, vars_in_csv),
                       )
        toprownum += 10


def match_survey_vars_with_csv_cols(newcsv, filetype, survey, session):
    if filetype == 'raw':
        varname_list = survey.varmap_set.all()
    elif filetype == 'legacy':
        varname_list = survey.var_set.all()
    for v in varname_list:
        c = VarMatchRecord()
        c.session = session
        if filetype == 'raw':
            name = v.raw_name
            c.raw_var = v
        elif filetype == 'legacy':
            name = v.name
            c.var = v
        if name in newcsv.columns:
            c.match_status = True
        else:
            c.match_status = False
        c.save()


def update_parse_status(session):
    session.parse_status = True
    session.save()


def upload_data(newcsv, survey, session, filetype, vars_in_csv):
    # If it's a teacher feedback survey, proceed with teacher & course matching
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
        # TODO
        # We'll rewrite this after optimization
        # match_and_create_teachers(s_t_df, session, fresh_precords_dict)
        # match_and_create_subjects_and_courses(s_t_c_df, session, fresh_precords_dict)
        # pair_new_courses_with_teachers(s_t_c_df, session, fresh_precords_dict)

    # Continue to add students and responses if it's raw data
    if filetype == 'raw':
        match_and_create_students(newcsv, survey, session)
        # Add responses
        if survey.is_teacher_feedback():
            match_and_create_responses(csv_stacked, survey, session, filetype, vars_in_csv)
        else:
            match_and_create_responses(newcsv, survey, session, filetype, vars_in_csv)


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


def generate_vars_in_csv(newcsv, survey, filetype):
    if filetype == 'raw':
        survey_maplist = survey.varmap_set.values_list('raw_name', flat=True)
        vlist = [v for v in survey_maplist if v in newcsv.columns]
    elif filetype == 'legacy':
        survey_varlist = survey.variable_set.values_list('name', flat=True)
        vlist = [v for v in survey_varlist if v in newcsv.columns]
    return vlist


def match_and_create_responses(newcsv, survey, session, filetype, vars_in_csv):
    for i in newcsv.index:
        print 'Importing row {num}'.format(num=str(i+1))
        row = newcsv.ix[i]
        if survey.is_teacher_feedback() and pd.isnull(row['coursename']):
            pass
        # We can insert validation for complete response here later
        else:
            pin = row['V4']
            qid = row['V1']
            # If there's no value for either pin or qid, let's just skip that row
            # since it's probably a fake blank row
            if pd.isnull(pin) or pd.isnull(qid):
                pass
            else:
                resp_defaults_dict = {}
                resp_defaults_dict['student'] = Student.objects.get(response_id=qid)
                resp_defaults_dict['imported_thru'] = session
                if survey.is_teacher_feedback():
                    s_t_c_index = newcsv.get_value(i, 's_t_c')
                    resp_defaults_dict['on_course'] = Course.objects.get(legacy_survey_index=s_t_c_index)
                else:
                    schshort = newcsv.get_value(i, 'School_Short')
                    resp_defaults_dict['on_schoolrecord'] = SchoolParticipation.objects.get(legacy_school_short=schshort)

                for v in vars_in_csv:
                    a = row[v]

                    if pd.isnull(a):
                        # print "Skipping {v} because it's blank".format(v=v)
                        pass
                    else:
                        # Create legacy_survey_index for lookup
                        idx_str_list = []
                        if survey.is_teacher_feedback():
                            idx_str_list.append(row['s_t_c'])
                        else:
                            idx_str_list.append(row['School_Short'])
                        idx_str_list.append(v)
                        # Append PIN here
                        idx_str_list.append(pin)
                        idx = ' - '.join(idx_str_list)
                        # Prepare all lookup fields
                        if filetype == 'legacy':
                            var = survey.variable_set.get(name=v)
                        elif filetype == 'raw':
                            varmap = survey.varmap_set.get(raw_name=v)
                            var = varmap.variable

                        # If it's a qual variable, save under comment
                        if var.qual:
                            resp_defaults_dict['comment'] = a
                        # If it's a blank space / string garbage, skip response creation
                        elif isinstance(a, basestring):
                            # But if a resembles a digit, keep it
                            if a.isdigit():
                                resp_defaults_dict['answer'] = a
                            else:
                                # print "Skipping {v} because it's garbage: {a}".format(v=v, a=a)
                                continue
                        else:
                            resp_defaults_dict['answer'] = a

                        # get or create Response here
                        obj, created = Response.objects.get_or_create(
                            question=var,
                            survey=survey,
                            legacy_survey_index=idx,
                            defaults=resp_defaults_dict,
                        )


def match_and_create_schools(newcsv, survey, session):
    '''
    newcsv: CSV file already converted to dataframe by pandas
    survey: Survey object
    session: ImportSession object
    '''
    # Group and set alpha index for alpha matching
    school_short_name = group_sshort_and_sname(newcsv, survey)
    csv_alpha = school_short_name.set_index('alpha')

    for a in csv_alpha.index:
        sch_defaults_dict = {}
        sch_defaults_dict['abbrev_name'] = csv_alpha.get_value(a, 'abbr')
        sch_defaults_dict['name'] = csv_alpha.get_value(a, 'School_Name')
        sch_defaults_dict['imported_thru'] = session

        obj, created = School.objects.get_or_create(
            alpha=a,
            defaults=sch_defaults_dict
        )


def match_and_create_schoolparticipations(newcsv, survey, session):
    '''
    newcsv: CSV file already converted to dataframe by pandas
    survey: Survey object
    session: ImportSession object
    '''

    # Set School_Short index for legacy_school_short matching
    school_short_name = group_sshort_and_sname(newcsv, survey)
    csv_sshort = school_short_name.set_index('School_Short')

    for s in csv_sshort.index:
        sp_defaults_dict = {}
        alpha = csv_sshort.get_value(s, 'alpha')
        school = School.objects.get(alpha=alpha)
        survey_round = s[-3:]
        sp_defaults_dict['date_participated'] = round_time_conversion[survey_round]
        sp_defaults_dict['note'] = "Imported on {}".format(session.date_created)
        sp_defaults_dict['imported_thru'] = session

        obj, created = SchoolParticipation.objects.get_or_create(
            school=school,
            survey=survey,
            legacy_school_short=s,
            defaults=sp_defaults_dict,
        )


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


def match_and_create_students(csv, survey, session):
    '''
    use get_precords_dict() to retrieve a new paired set of ID and School_Short
    '''
    # Set ['V1'] or Qualtrics ID as index of csv
    csv = csv.set_index('V1')
    for q in csv.index:
        if pd.isnull(q):
            pass
        else:
            std_defaults_dict = {}
            pin = csv.get_value(q, 'V4')
            schshort = csv.get_value(q, 'School_Short')
            precord = SchoolParticipation.objects.get(
                survey=survey,
                legacy_school_short=schshort,
            )
            std_defaults_dict['imported_thru'] = session
            obj, created = Student.objects.get_or_create(
                pin=pin,
                response_id=q,
                surveyed_thru=precord,
                defaults=std_defaults_dict
            )


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
