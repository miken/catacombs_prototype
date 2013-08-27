from django.core.management.base import BaseCommand, CommandError
import os

root_dir = os.getcwd()
cmd_dir = os.path.join(root_dir, 'datacombo', 'management', 'commands')
os.chdir(cmd_dir)

def seed_surveys():
    from datacombo.models import Survey
    tchhs = Survey(name='HS Teacher Feedback Survey',
                   code='tch-hs')
    tchhs.save()
    tchms = Survey(name='MS Teacher Feedback Survey',
                   code='tch-ms')
    tchms.save()
    tches = Survey(name='ES Teacher Feedback Survey',
                   code='tch-es')
    tches.save()
    schhs = Survey(name='HS Overall Experience Survey',
                   code='sch-hs')
    schhs.save()
    schms = Survey(name='MS Overall Experience Survey',
                   code='sch-ms')
    schms.save()

    print "Seeded 5 surveys."


def seed_factors():
    import pandas as pd
    from datacombo.models import Survey, SummaryMeasure
    # Import factors.csv
    factors = pd.read_csv('factors.csv', index_col=['surveycode', 'varname'])
    for idx_tuple in factors.index:
        scode = idx_tuple[0]
        new_factor = SummaryMeasure()
        survey = Survey.objects.get(code=scode)
        new_factor.survey = survey
        varname = idx_tuple[1]
        new_factor.name = varname
        new_factor.label = factors.get_value(idx_tuple, 'label')
        new_factor.save()
    print "Summary Measures seeded."
        


def seed_vars():
    from datacombo.models import Survey, SummaryMeasure, Variable
    import pandas as pd
    #Import vars.csv
    varlist = pd.read_csv('vars.csv', index_col=['surveycode', 'factor', 'varname'])
    for idx_tuple in varlist.index:
        scode = idx_tuple[0]
        var = Variable()
        survey = Survey.objects.get(code=scode)
        var.survey = survey
        fname = idx_tuple[1]
        if pd.isnull(fname):
            pass
        else:
            factor = SummaryMeasure.objects.get(name=fname)
            var.summary_measure = factor
        var.name = idx_tuple[2]
        var.description = varlist.get_value(idx_tuple, 'label')
        var.qraw = varlist.get_value(idx_tuple, 'qraw')
        demographic = varlist.get_value(idx_tuple, 'demographic')
        if demographic == 1:
            var.demographic = True
        else:
            var.demographic = False
        in_loop = varlist.get_value(idx_tuple, 'in_loop')
        if in_loop == 1:
            var.in_loop = True
        else:
            var.in_loop = False
        in_report = varlist.get_value(idx_tuple, 'in_report')
        if in_report == 1:
            var.in_report = True
        else:
            var.in_report = False
        var.active = True
        var.save()
    print "Sample variables seeded."


class Command(BaseCommand):
    help = 'Set up surveys and variables for testing'

    def handle(self, *args, **options):
        seed_surveys()
        seed_factors()
        seed_vars()