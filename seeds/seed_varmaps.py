from datacombo.models import Survey, Variable, VarMap
import pandas as pd

def execute():
    # Import maps.csv
    maps = pd.read_csv('maps.csv', index_col=['qraw'])
    for vm_raw in maps.index:
        vm = VarMap()
        vm.raw_name = vm_raw
        scode = maps.get_value(vm_raw, 'surveycode')
        survey = Survey.objects.get(code=scode)
        vm.survey = survey
        varname = maps.get_value(vm_raw, 'varname')
        var = Variable.objects.get(survey=survey, name=varname)
        vm.variable = var
        vm.save()
    print "Sample varmaps seeded."