import os
import pandas as pd

#Set up Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'catacombs.settings'
#curr_dir = '/Users/club292/Dropbox/Python/catacombs/datacombo/imports'
curr_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.join(curr_dir, '..', '..')
os.chdir(root_dir)
print os.getcwd()
from datacombo.models import Survey, Variable


#Import likert.csv
os.chdir(curr_dir)
varlist = pd.read_csv('likert.csv', index_col=['varname'])
#Remove the factors
varlist = varlist[varlist['factor'] != '1']
#os.chdir(root_dir)

#Find that HS TM survey
hstm = Survey.objects.get(code='hstm')

for var in varlist.index:
    dj_var = Variable()
    dj_var.survey = hstm
    dj_var.name = var
    dj_var.description = varlist.get_value(var, 'factor')
    dj_var.active = True
    dj_var.save()