import pandas as pd
from datacombo.models import Survey, SummaryMeasure

def execute():
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