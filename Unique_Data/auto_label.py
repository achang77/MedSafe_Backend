from __future__ import division
import numpy as np
import pandas as pd
startYear = 2014
endYear = 2018
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
total_c = 0
total_not_c = 0 
total_und = 0
total = 0
for dfile in datafiles:
    print ('Year = ' + dfile)
    df = pd.read_excel(data_dir+str(dfile))
    df['Fault_Class'] = ""

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
    
    df = df.sort_values(by = ['Fault_Class'], ascending = False)
    writer = pd.ExcelWriter(dfile.split('.xls')[0] + '_auto.xlsx', engine='xlsxwriter')
    df.to_excel(writer,sheet_name='Sheet1', index=False)
    writer.save()

    c_records = len(df[df['Fault_Class'] == 'Computer'])
    not_c_records = len(df[df['Fault_Class'] == 'Not_Computer'])
    und = len(df[df['Fault_Class'] == 'Undetermined'])

    total_c += c_records
    total_not_c += not_c_records
    total_und += und
    total += c_records + not_c_records + und

    print("computer records: " + str(c_records))

    print("not computer records: " + str(not_c_records))
    
    print("undetermined records: " + str(und))

    print("% undetermined: " + str( und / (und + c_records + not_c_records) ) )

print total_c
print total_not_c
print total_und
print total



