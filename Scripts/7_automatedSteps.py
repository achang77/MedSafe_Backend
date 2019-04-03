#imports from other research scripts
retrieve = __import__('1_retrieveMerge')
unique = __import__('2_uniqueReasons')
procodes = __import__('4_procodeCompare')
testCompS1 = __import__('5_testCompNotCompRecalls')
testCompS2 = __import__('6_recallClassification_Bayes_New_Data')

#standard module imports
import os

#markers for which sections to execute
pieces = {"Retrieve": True, "Unique": True, "ClassifyS1": True,
        "ClassifyS2": True, "Procodes": False}

'''
    SCRIPT 1 --> Retrieve the data
'''
# if(pieces["Retrieve"]):
#     print "-------------------------------"
#     print "Fetching Data from the Database"
#     print "-------------------------------"
#     #set up the basepath
#     basepath = './../Original_Data';
#     os.chdir(basepath)

#     #get data from 2006-2012
#     for Year in range(2018, 2019):
#         print 'Year '+str(Year);
#         startYear = Year;
#         endYear = Year;

#         #full year at a time
#         startMonth = 1;
#         endMonth = 12;

#         #get the data
#         retrieve.getData(startYear, startMonth, endYear, endMonth)

'''
    SCRIPT 2 --> Make Data Unique
'''
# if(pieces["Unique"]):
#     print "-------------------------------"
#     print "Ensuring Unique Recalls"
#     print "-------------------------------"
#     # files = os.listdir("./../Original_Data")
#     files = []
#     for Year in range(2018, 2019):
#         filename = str(Year)+'.xls'
#         files.append(filename)
#     for fl in files:
#         print fl
#     unique.elimCopyReasons('./../Original_Data', files, './../Unique_Data')

#     #files = ["Unique_Computer_Recalls_2007_2011_copy.xls"]
#     #elimCopyReasons('../../New_Data', files)

# '''
#     SCRIPT 3 --> Computer vs. Not Computer Classification Stage 1
# '''
# if(pieces["ClassifyS1"]):
#     print "-------------------------------"
#     print "Classifying Remaining Recalls"
#     print "-------------------------------"
#     testCompS1.testRecalls()

'''
    SCRIPT 4 --> Computer vs. Not Computer Classification Stage 2
'''
if(pieces["ClassifyS2"]):
    testCompS2.use_sklearn_classify(load_features = False, load_model = False, custom = True)

# '''
#     SCRIPT 5 --> Classify Recalls (Procodes)
# '''
# if(pieces["Procodes"]):
#     print "-------------------------------"
#     print "Determining Procodes for Recalls"
#     print "-------------------------------"
#     #set up the paths for files
#     pathProc = "./../Other_Data/"
#     pathData = "./../Unique_Data/"

#     #find the procode file
#     procodeFile = "All_Recalls_procodes.xls"

#     #datafiles = ["2006.xls","2007.xls","2008.xls","2009.xls","2010.xls","2011.xls","2012.xls","2013.xls"]

#     Procodes_Hash = procodes.developHash(pathProc, procodeFile)
#     #identify procodes for these recalls
#     datafiles = os.listdir("../Original_Data")
#     for i in xrange(len(datafiles)):
#         datafiles[i] = 'unique'+datafiles[i]
#     procodes.compareRecall(pathProc, pathData, procodeFile, Procodes_Hash, datafiles)
