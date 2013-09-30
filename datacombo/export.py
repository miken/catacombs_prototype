import csv
import datetime
from collections import OrderedDict
from time import sleep

from django.core.exceptions import MultipleObjectsReturned
from django.core.files.storage import default_storage

from datacombo.models import Student, Course

# Set up RQ queue
import django_rq
q = django_rq.get_queue('default')


def s3_write_response_data(survey, export, debug=None):
    '''
        export: CSVExport instance
    '''
    # Get all student objects related to this survey
    surveyed_students = Student.objects.filter(school__schoolparticipation__in=survey.schoolparticipation_set.all())
    # For some reason, if we don't do a distinct, we'll have duplicated records
    # of students in queryset, even though the count is the same!
    # So let's apply distinct() here to the Student queryset
    surveyed_students = surveyed_students.distinct()
    student_queryset_count = surveyed_students.count()

    # Let's get the header row out first
    header_dict = OrderedDict()
    # We'll add in meta information first
    # This is either School_Short, School_Name
    # or School_Short, School_Name, teacher & course info
    # depending on type of survey
    for c in survey.panel_columns_for_csv_matching():
        header_dict[c] = None
    # Then we'll append two columns for student information
    # Qualtrics ID and Login PIN
    header_dict['Qualtrics ID'] = None
    header_dict['PIN'] = None
    #header_row.extend(['Qualtrics ID', 'PIN'])
    # Finally we'll append all survey variables here
    # Filter for variables that are not qualitative
    survey_varlist = survey.variable_set.filter(qual=False).values_list('name', flat=True)
    for v in survey_varlist:
        header_dict[v] = None

    # Now pick 10 student objects
    toprownum = 0
    chunk_filename_list = []
    while toprownum < student_queryset_count:
        bottomrownum = toprownum + 10
        if bottomrownum > student_queryset_count:
            bottomrownum = student_queryset_count
        query_chunk = surveyed_students[toprownum:bottomrownum]
        chunk_filename = "temp_chunk_{topnum}_{bottomnum}.csv".format(topnum=toprownum, bottomnum=bottomrownum)
        # If it's the last file, save it too
        if bottomrownum == student_queryset_count:
            last_filename = chunk_filename
        chunk_filename_list.append(chunk_filename)
        # We'll enqueue this task
        # If debug mode is on, we'll use web dyno for processing
        if debug:
            write_student_responses(chunk_filename, survey, query_chunk, header_dict, survey_varlist)
        else:
            q.enqueue_call(
                func=write_student_responses,
                args=(chunk_filename, survey, query_chunk, header_dict, survey_varlist)
            )
        toprownum += 10

    # Now stitch all temp_chunk_*.csv files together
    filename = export.file_name
    # If debug mode is on, we'll use web dyno for processing
    if debug:
        bottomnum = student_queryset_count
        modulus = student_queryset_count % 10   # e.g., 257 % 10 = 7
        topnum = bottomnum - modulus            # e.g., 257 - 7 = 250
        last_filename = "temp_chunk_{topnum}_{bottomnum}.csv".format(topnum=topnum, bottomnum=bottomnum)
        stitch_csv_chunks(last_filename, chunk_filename_list, filename)
    else:
        q.enqueue_call(
            func=stitch_csv_chunks,
            args=(last_filename, chunk_filename_list, filename),
        )

    # Finally when done, set file_status to True and then save it
    if debug:
        update_file_status(export)
    else:
        q.enqueue(update_file_status, export)


def update_file_status(export):
    export.file_status = True
    export.save()


def write_student_responses(chunk_filename, survey, query_chunk, header_dict, survey_varlist):
    '''
    Helper function that will write responses to a temp CSV file
        chunk_filename: string that represents the name of the CSV file
        survey: Survey object
        query_chunk: list of Student objects with response data to be written to this CSV file
        header_dict: dictionary that contains the header row for the csvwriter object
        survey_varlist: list of variables for the given survey
    '''
    with default_storage.open(chunk_filename, 'w') as csvfile:
        # Use DictWriter to match records
        writer = csv.DictWriter(csvfile, fieldnames=header_dict)

        # Now write header row
        writer.writeheader()

        # Next, data rows
        # If it's an overall feedback survey, one row represents one student
        for s in query_chunk:
            print 'Writing response data for student PIN {pin}'.format(pin=s.pin)
            rowdata = {}
            # First element is 'School_Short'
            # Pretty sure each student has only one unique school short
            # So safe to use the first school participation record
            # And extract school short from it
            school_short = s.school.schoolparticipation_set.latest('id').legacy_school_short
            rowdata['School_Short'] = school_short
            # Second element is 'School_Name'
            school_name = s.school.name
            rowdata['School_Name'] = school_name
            # Next is Qualtrics ID
            rowdata['Qualtrics ID'] = s.response_id
            # Next is YouthTruth PIN
            rowdata['PIN'] = s.pin

            # If it's a teacher feedback survey, collect all courses
            # that this student provides feedback for
            if survey.is_teacher_feedback():
                student_courses = s.course_set.all()
                # Iterate over these courses
                for c in student_courses:
                    rowdata['coursename'] = c.name
                    rowdata['subject'] = c.subject.name
                    # First add in teacher full name
                    # If there's only one teacher (which is by default), feel free to add that teacher
                    if c.teacher_set.count() == 1:
                        teacher = c.teacher_set.latest('id')
                        rowdata['teachersalutation'] = teacher.salutation
                        rowdata['teacherfirst'] = teacher.first_name
                        rowdata['teacherlast'] = teacher.last_name
                        # Filter for responses by student s on this course c
                        course_responses = s.response_set.filter(on_course=c)
                        rowdata = insert_responses_into_rowdata(rowdata, course_responses, survey_varlist)
                        writer.writerow(rowdata)
                    else:
                        for t in c.teacher_set.all():
                            rowdata['teachersalutation'] = t.salutation
                            rowdata['teacherfirst'] = t.first_name
                            rowdata['teacherlast'] = t.last_name
                            # Filter for responses by student s on this course c for teacher t
                            teacher_responses = s.response_set.filter(on_course=c, on_teacher=t)
                            rowdata = insert_responses_into_rowdata(rowdata, teacher_responses, survey_varlist)
                            writer.writerow(rowdata)
            else:
                # Get all response data from this student s
                # given this school short
                # and belong to survey_varlist
                student_responses = s.response_set.filter(
                    # on_schoolrecord=s.surveyed_thru, --probably not necessary
                    question__name__in=survey_varlist
                )

                rowdata = insert_responses_into_rowdata(rowdata, student_responses, survey_varlist)
                # Write everything from datarow
                writer.writerow(rowdata)


def insert_responses_into_rowdata(rowdata, student_responses, survey_varlist):
    '''
    Helper function that will use database queries to find a student's response to a question variable
    and then insert into rowdata, which is a dict.
        rowdata: dict object that contains question-answer pairs
        student_responses: all responses object belonging to a student
            in the case of teacher feedback survey, it's all responses on a course belonging to a student
        survey_varlist: list of variables for the given survey
    '''
    # Varnames for matching with CSV row headers
    # We save this in a list first to reduce the number of database hits
    # for faster processing
    varnames = student_responses.values_list('question__name', flat=True)
    for v in survey_varlist:
        if v not in varnames:
            pass
        else:
            # Look for answer from student_responses
            try:
                r = student_responses.get(question__name=v)
            except MultipleObjectsReturned:
                # Usually this should not happen - it only happens when during
                # the upload process, we recorded 2 different responses from
                # a student from the same question!
                # To deal with this situation, we'll just take the first available
                # response in the queryset
                r = student_responses.filter(question__name=v).latest('id')
            rowdata[v] = r.answer
    return rowdata


def stitch_csv_chunks(last_filename, chunk_filename_list, filename):
    # First let's check if the last file exists
    # If it doesn't, wait for another 15 seconds
    # Give up after 10 tries
    trycount = 1
    while trycount < 11:
        try:
            with default_storage.open(last_filename):
                pass
            # Assign trycount to be 11 immediately so we can proceed next to csv stitching
            trycount = 11
        except IOError:
            print 'Could not find file "{last_filename}" in storage'.format(last_filename=last_filename)
            print 'Retrying again in 15 seconds...'
            # Count that as another try
            trycount += 1
            sleep(15)

    # Use 'w' mode for writing to overwrite any previously created file
    with default_storage.open(filename, 'w') as finalcsv:
        # First file
        first_filename = chunk_filename_list[0]
        print 'Reading {filename}'.format(filename=first_filename)
        for line in default_storage.open(first_filename):
            finalcsv.write(line)
        # Now the rest
        for fname in chunk_filename_list[1:]:
            f = default_storage.open(fname)
            print 'Reading {filename}'.format(filename=fname)
            header = True
            for line in f:
                # Skip the header
                if header:
                    header = False
                    pass
                else:
                    finalcsv.write(line)
            f.close()

    # Now delete all temp_chunks file
    for f in chunk_filename_list:
        print 'Now deleting {filename}'.format(filename=f)
        default_storage.delete(f)
