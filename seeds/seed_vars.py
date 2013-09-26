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
        qual = varlist.get_value(idx_tuple, 'qual')
        if qual == 1:
            var.qual = True
        else:
            var.qual = False
        demographic = varlist.get_value(idx_tuple, 'demographic')
        if demographic == 1:
            var.demographic = True
        else:
            var.demographic = False
        var.active = True
        var.save()
    print "Sample variables seeded."