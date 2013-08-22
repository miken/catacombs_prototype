from django.core.management.base import BaseCommand, CommandError
import os
import pandas as pd
from datacombo.models import Survey, Variable

class Command(BaseCommand):
    help = 'Seed a set of sample variables for import testing'

    def handle(self, *args, **options):
        root_dir = os.getcwd()
        cmd_dir = os.path.join(root_dir, 'datacombo', 'management', 'commands')
        os.chdir(cmd_dir)
        #Import vars.csv
        varlist = pd.read_csv('vars.csv', index_col=['surveycode', 'varname'])                

        surveycode_list = varlist.index.get_level_values(0).unique().tolist()

        for scode in surveycode_list:
            print 'Working on %s' % scode
            var_df = varlist.ix[scode]
            survey = Survey.objects.get(code=scode)
            for var in var_df.index:
                dj_var = Variable()
                dj_var.survey = survey
                dj_var.name = var
                dj_var.description = var_df.get_value(var, 'label')
                dj_var.qraw = var_df.get_value(var, 'qraw')
                inloop = var_df.get_value(var, 'inloop')
                if inloop == 1:
                    dj_var.inloop = True
                else:
                    dj_var.inloop = False
                dj_var.active = True
                dj_var.save()

        print "Sample variables seeded."