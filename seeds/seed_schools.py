from datacombo.models import Survey, School, SchoolParticipation
import pandas as pd
from datacombo.helpers import round_time_conversion

def execute():
    # Import schools.csv
    schools = pd.read_csv('schools.csv', index_col=['School_Alpha', 'School_Short'])
    for idx in schools.index:
        # Retrieve or create a new school object
        sch_alpha = idx[0]
        name = schools.get_value(idx, 'School_Name')
        abbrev_name = schools.get_value(idx, 'Short')
        sch_defaults_dict = {}
        sch_defaults_dict['name'] = name
        sch_defaults_dict['abbrev_name'] = abbrev_name
        sch_obj, created = School.objects.get_or_create(
            alpha=sch_alpha,
            defaults=sch_defaults_dict
        )


        # Now retrieve or create a new school participation record
        # First, add a participation record for Overall Survey
        # Get last two characters from school alpha, e.g. 'hs' or 'ms'
        last_two = sch_alpha[-2:]
        survey_code = 'sch-{lev}'.format(lev=last_two)
        survey = Survey.objects.get(code=survey_code)
        sch_short = idx[1]
        round_rec = schools.get_value(idx, 'Round')
        time_rec = round_time_conversion[round_rec]

        pr_defaults_dict = {}
        pr_defaults_dict['date_participated'] = time_rec

        pr_obj, created = SchoolParticipation.objects.get_or_create(
            legacy_school_short=sch_short,
            survey=survey,
            school=sch_obj,
            defaults=pr_defaults_dict
        )

        # Check if this school participated in Teacher Module previously
        tm = schools.get_value(idx, 'tm')
        if tm == 1:
            survey_code = 'tch-{lev}'.format(lev=last_two)
            survey = Survey.objects.get(code=survey_code)
            pr_tch_obj, created = SchoolParticipation.objects.get_or_create(
                legacy_school_short=sch_short,
                survey=survey,
                school=sch_obj,
                defaults=pr_defaults_dict
            )

    print "Schools and their participation records seeded."