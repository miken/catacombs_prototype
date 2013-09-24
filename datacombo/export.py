import csv
import datetime
from collections import OrderedDict

from django.core.exceptions import MultipleObjectsReturned
from django.core.files.storage import default_storage

from datacombo.models import Student, Response, CSVExport

# Set up RQ queue
import django_rq
q = django_rq.get_queue('default')


def write_response_data(response, survey):
    # Start with header row
    header_dict = OrderedDict()
    # We'll add in meta information first
    # This is either School_Short, School_Name
    # or School_Short, School_Name, teacher & course info
    # depending on type of survey
    for c in survey.panel_columns_for_csv_matching():
        header_dict[c] = None
    #header_row.extend(survey.panel_columns_for_csv_matching())
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
    #header_row.extend(survey_varlist)

    # Use DictWriter to match records
    writer = csv.DictWriter(response, fieldnames=header_dict)

    # Now write header row
    writer.writeheader()

    # Next, data rows
    # If it's an overall feedback survey, one row represents one student
    if not survey.is_teacher_feedback():
        # Get all student objects related to this survey
        surveyed_students = Student.objects.filter(surveyed_thru__in=survey.schoolparticipation_set.all())
        rowcount = 1
        for s in surveyed_students:
            print 'Appending row {rowcount} for student with PIN {pin}'.format(rowcount=rowcount, pin=s.pin)
            rowdata = {}
            # First element is 'School_Short'
            school_short = s.surveyed_thru.legacy_school_short
            rowdata['School_Short'] = school_short
            # Second element is 'School_Name'
            school_name = s.surveyed_thru.school.name
            rowdata['School_Name'] = school_name
            # Next is Qualtrics ID
            rowdata['Qualtrics ID'] = s.response_id
            # Next is YouthTruth PIN
            rowdata['PIN'] = s.pin
            # Now get all response data on this school short
            # and belong to survey_varlist
            student_responses = s.response_set.filter(
                on_schoolrecord=s.surveyed_thru,
                question__name__in=survey_varlist
            )
            # Varnames for matching with CSV row headers
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
                        r = student_responses.filter(question__name=v)[0]
                    rowdata[v] = r.answer
            # Write everything from datarow
            writer.writerow(rowdata)
            rowcount += 1
    # If it's a teacher feedback survey, one row represents a student's feedback on a course
    else:
        pass
    return response


def s3_write_response_data(survey):
    # New CSVExport object
    export = CSVExport()
    export.title = 'Student Responses'
    export.export_type = 'response'
    now = datetime.datetime.now()
    export.date_requested = now
    export.survey = survey

    # Prepare CSV file
    today = now.strftime('%Y%m%d')
    time = now.strftime('%H%M')
    filename = "export_{surveycode}_responses_{today}_{time}.csv".format(
        surveycode=survey.code,
        today=today,
        time=time,
    )

    with default_storage.open(filename, 'w') as csvfile:
        # CSV Write Code here -- copied from above
        # Start with header row
        header_dict = OrderedDict()
        # We'll add in meta information first
        # This is either School_Short, School_Name
        # or School_Short, School_Name, teacher & course info
        # depending on type of survey
        for c in survey.panel_columns_for_csv_matching():
            header_dict[c] = None
        #header_row.extend(survey.panel_columns_for_csv_matching())
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
        #header_row.extend(survey_varlist)

        # Use DictWriter to match records
        writer = csv.DictWriter(csvfile, fieldnames=header_dict)

        # Now write header row
        writer.writeheader()

        # Next, data rows
        # If it's an overall feedback survey, one row represents one student
        if not survey.is_teacher_feedback():
            # Get all student objects related to this survey
            surveyed_students = Student.objects.filter(surveyed_thru__in=survey.schoolparticipation_set.all())
            student_queryset_count = surveyed_students.count()
            # We're gonna split surveyed_students into smaller query chunks
            # for faster background worker processing
            toprownum = 0
            while toprownum < student_queryset_count:
                bottomrownum = toprownum + 10
                if bottomrownum > student_queryset_count:
                    bottomrownum = student_queryset_count
                query_chunk = surveyed_students[toprownum:bottomrownum]
                write_student_responses(query_chunk, survey_varlist, writer)
                print 'Rows {top}-{bottom} written'.format(top=toprownum+1, bottom=bottomrownum+1)
                toprownum += 10

    export.file_name = filename
    # Finally when done, set file_status to True and then save it
    export.file_status = True
    export.save()


def write_student_responses(query_chunk, survey_varlist, writer):
    '''
    Helper function that will write responses from query_chunk to a writer (an opened CSV file)
    '''
    for s in query_chunk:
        print 'Writing response data from student with PIN {pin}'.format(pin=s.pin)
        rowdata = {}
        # First element is 'School_Short'
        school_short = s.surveyed_thru.legacy_school_short
        rowdata['School_Short'] = school_short
        # Second element is 'School_Name'
        school_name = s.surveyed_thru.school.name
        rowdata['School_Name'] = school_name
        # Next is Qualtrics ID
        rowdata['Qualtrics ID'] = s.response_id
        # Next is YouthTruth PIN
        rowdata['PIN'] = s.pin
        # Now get all response data on this school short
        # and belong to survey_varlist
        student_responses = s.response_set.filter(
            on_schoolrecord=s.surveyed_thru,
            question__name__in=survey_varlist
        )
        # Varnames for matching with CSV row headers
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
                    r = student_responses.filter(question__name=v)[0]
                rowdata[v] = r.answer
        # Write everything from datarow
        writer.writerow(rowdata)
