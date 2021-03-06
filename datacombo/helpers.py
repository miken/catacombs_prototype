import datetime

round_time_conversion = {}
round_time_conversion['13Y'] = datetime.datetime(2013, 5, 1, 0, 0, 0)
round_time_conversion['13X'] = datetime.datetime(2013, 3, 1, 0, 0, 0)
round_time_conversion['13S'] = datetime.datetime(2013, 1, 1, 0, 0, 0)
round_time_conversion['12F'] = datetime.datetime(2012, 11, 1, 0, 0, 0)
round_time_conversion['12Y'] = datetime.datetime(2012, 5, 1, 0, 0, 0)
round_time_conversion['12X'] = datetime.datetime(2012, 4, 1, 0, 0, 0)
round_time_conversion['12S'] = datetime.datetime(2012, 1, 1, 0, 0, 0)
round_time_conversion['11F'] = datetime.datetime(2011, 11, 1, 0, 0, 0)
round_time_conversion['11S'] = datetime.datetime(2011, 1, 1, 0, 0, 0)
round_time_conversion['10F'] = datetime.datetime(2010, 11, 1, 0, 0, 0)
round_time_conversion['10S'] = datetime.datetime(2010, 1, 1, 0, 0, 0)
round_time_conversion['09F'] = datetime.datetime(2009, 11, 1, 0, 0, 0)
round_time_conversion['09S'] = datetime.datetime(2009, 1, 1, 0, 0, 0)
round_time_conversion['08F'] = datetime.datetime(2008, 11, 1, 0, 0, 0)
round_time_conversion['08S'] = datetime.datetime(2008, 1, 1, 0, 0, 0)


#Export CSV from model
import os
import pandas as pd
target_dir = os.getcwd()


def write_csv(model, fields):
    '''
    model: Django model
    fields: list of 
    '''
    df = pd.DataFrame()
    for instance in model.objects.all():
        df['id'] = instance.id
        for f in fields:
            df['f'] = eval('instance.'+f)
    filename = 'export.csv'
    filepath = os.path.join(target_dir, filename)
    df.to_csv(filepath)
