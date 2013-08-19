import os
from catacombs import settings
import pandas as pd

cd = os.getcwd()
cd = os.path.join (cd, 'datacombo', 'imports')
os.chdir(cd)

from datacombo.models import Survey, Variable


#Import likert.csv
varlist = pd.read_csv('likert.csv', index_col=['varname'])
#Remove the factors
varlist = varlist[varlist['factor'] != '1']

#Find that HS TM survey
hstm = Survey.objects.get(code='tch-hs')

for var in varlist.index:
    dj_var = Variable()
    dj_var.survey = hstm
    dj_var.name = var
    dj_var.description = varlist.get_value(var, 'factor')
    dj_var.active = True
    dj_var.save()

schhs = Survey.objects.get(code='sch-hs')

for var in varlist.index:
    dj_var = Variable()
    dj_var.survey = schhs
    dj_var.name = var
    dj_var.description = varlist.get_value(var, 'factor')
    dj_var.active = True
    dj_var.save()