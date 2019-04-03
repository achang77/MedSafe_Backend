import numpy as np
import pandas as pd
startYear = 2014
endYear = 2014
#data_dir = './../Unique_Data/'
data_dir = ''
datafiles = []
for Year in range(startYear, endYear):
    datafiles.append('unique'+str(Year)+'.xls');

computer_causes = {
'Device Design',
'Equipment maintenance',
'Software Design Change',
'Software Manufacturing/Software Deployment',
'Software change control',
'Software design',
'Software design (manufacturing process)',
'Software in the Use Environment'
}
not_computer_causes = {
'Error in labeling',
'Incorrect or no expiration date',
'Labeling Change Control',
'Labeling False and Misleading',
'Labeling design',
'Labeling mix-ups',
'No Marketing Application',
'Package design/selection',
'Packaging',
'Packaging change control',
'Packaging process control'
}

for dfile in datafiles:
    print 'Year = ' + dfile
    df = pd.read_excel(data_dir+str(dfile))
    df['Fault_Class'] = np.nan

    for i, row in df.iterrows():
        nc = 'Not_Computer'
        c = 'Computer'
        und = 'Undetermined'
        cause = row['FDA Determined Cause']
        if  cause in computer_causes:
            df.at[i,'Fault_Class'] = c
        elif cause in not_computer_causes:
            df.at[i,'Fault_Class'] = nc
        else:
            df.at[i,'Fault_Class'] = und
    print("computer records: " + len(df[df['Fault_Class'] == 'Computer']))
    print("not computer records: " + len(df[df['Fault_Class'] == 'Not_Computer']))
    print("undetermined records: " + len(df[df['Fault_Class'] == 'Undetermined']))
    




