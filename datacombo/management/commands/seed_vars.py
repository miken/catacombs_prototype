from django.core.management.base import BaseCommand, CommandError
import os
import pandas as pd
from datacombo.models import Survey, Variable

class Command(BaseCommand):
    args = '<survey_code survey_code ...>'
    help = 'Seed a set of sample variables for import testing'

    def handle(self, *args, **options):
        for survey_code in args:
            try:
                survey = Survey.objects.get(code=survey_code)
            except Survey.DoesNotExist:
                raise CommandError('Survey "%s" does not exist' % survey_code)

            root_dir = os.getcwd()
            cmd_dir = os.path.join(root_dir, 'datacombo', 'management', 'commands')
            os.chdir(cmd_dir)
            #Import likert.csv
            varlist = pd.read_csv('likert.csv', index_col=['varname'])
            #Remove the factors
            varlist = varlist[varlist['factor'] != '1']                

            for var in varlist.index:
                dj_var = Variable()
                dj_var.survey = survey
                dj_var.name = var
                dj_var.description = varlist.get_value(var, 'factor')
                dj_var.active = True
                dj_var.save()

            print "Sample variables seeded for %s" % survey_code