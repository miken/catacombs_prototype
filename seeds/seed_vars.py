from datacombo.models import Survey, SummaryMeasure, Variable
import pandas as pd

def execute():
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
        in_loop = varlist.get_value(idx_tuple, 'in_loop')
        if in_loop == 1:
            var.in_loop = True
        else:
            var.in_loop = False
        var.active = True
        var.save()
    print "Sample variables seeded."