from datacombo.models import Survey, Variable, CustomRecode
import pandas as pd

def execute():
    # Import recodes.csv
    recodes = pd.read_csv('recodes.csv', index_col=['surveycode', 'varname', 'orig_code'])
    for idx_tuple in recodes.index:
        scode = idx_tuple[0]
        survey = Survey.objects.get(code=scode)
        varname = idx_tuple[1]
        print varname
        var = Variable.objects.get(
            survey=survey,
            name=varname
        )
        cr = CustomRecode()
        cr.variable = var
        cr.orig_code = idx_tuple[2]
        cr.recode = recodes.get_value(idx_tuple, 'recode')
        cr.save()
    print "Custom recodes seeded."