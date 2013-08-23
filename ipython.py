import os
cd = os.getcwd()
assets_dir = os.path.join(cd, 'datacombo', 'assets')
os.chdir(assets_dir)
import pandas as pd
newcsv = pd.read_csv('sample_raw.csv')

from datacombo.models import Survey
mstm = Survey.objects.get(code='tch-ms')