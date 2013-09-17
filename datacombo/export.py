import csv
from collections import OrderedDict

from django.core.exceptions import MultipleObjectsReturned

from datacombo.models import Student, Response


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
