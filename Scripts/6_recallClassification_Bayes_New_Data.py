import nltk
from nltk.probability import ConditionalFreqDist
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
import string
from nltk.corpus import stopwords
import re
from nltk import bigrams
from nltk import trigrams
#from nltk.tag.stanford import NERTagger
from nltk.tag.stanford import StanfordPOSTagger
import xlrd
import xlwt
import os
import math
from math import log
from operator import itemgetter, attrgetter
import random
from textclean.textclean import textclean
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier, LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, f1_score, classification_report

from numpy import array
import numpy as np
import pickle
data_dir = './../Unique_Data/'
# keyword_dir = './../../Research Data/Keyword_Lists'
# train_filename = 'Merged_Final_Unique_Recalls_2007_2013_gt.xls'


#inputs: training data, test data, sklearn or homemade implementation, output file name, input file name
#train_set, test_files, label_file_suffix, test_file_suffix,
def use_sklearn_classify(load_features = True, load_model = True, custom = True, test_file_suffix = '.xls', label_file_suffix = '', label_filename = 'Merged_Final_Unique_Recalls_2007_2013_gt.xls',train_filename = 'Merged_Final_Unique_Recalls_2007_2011.xls'):
    #utility functions convert text label to numeric label
    def f(s):
        if str(s) == 'Not_Computer':
            return 0
        else:
            return 1
    def f_inv(n):
        if n == 0:
            return 'Not_Computer'
        else:
            return 'Computer'
    
    if load_features:
        features = pickle.load(open('features.txt','r'))
        vect = CountVectorizer(vocabulary=features, binary=True)
        print 'vectorizer loaded'
    else:
        print 'Getting features'
        (train_set, train_text) = get_train_set_text(train_filename)
        features = get_features(train_set, train_text)
        # vect = CountVectorizer(vocabulary=features, binary=True)
        vect = CountVectorizer()
        vect2 = TfidfTransformer()

        print('Vectorizer set')

    
    if load_model:
        nb = pickle.load(open('trained_model.txt','r'))
        print 'Model loaded'
    else:
        print 'Fitting model'
        df = pd.DataFrame(train_set, columns=['id_number','reason','fault_class'])
        xtrain = df.reason
        ytrain = df.fault_class
        ytrain = ytrain.apply(f)
        xtrain = xtrain.str.lower()
        xtrain = vect.fit_transform(xtrain)
        # xtrain = vect2.fit_transform(xtrain)
        # nb = MultinomialNB()
        # nb = SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, random_state=42, max_iter=50, tol=1e-3)
        nb = LogisticRegression(random_state = 0)
        nb.fit(xtrain, ytrain)
        pickle.dump(nb, open('trained_model.txt', 'w'))
        print 'model dumped'

        # get filenames from Unique_Data
    uniqueFiles = os.listdir("./../Unique_Data")
    test_files = get_test(uniqueFiles,start_year = 2012, end_year = 2013)

    for filename in test_files:
        df_test = pd.read_excel(data_dir+str(filename)+test_file_suffix)
        xtest = df_test['Reason for Recall']
        xtest = xtest.str.lower()
        xtest = vect.transform(xtest.values.astype('U'))
        ypred = nb.predict(xtest)

        df_test = pd.concat([df_test, pd.DataFrame(ypred, columns = ['Predicted Fault Class'])], axis=1)

        if custom:
            df_label_file = pd.read_excel(data_dir + label_filename)
            df_label = df_label_file[ df_label_file['Recall Event ID'].isin( df_test['Recall Event ID']) ]
            df_label = df_label.sort_values(by = ['Recall Event ID'])

            df_test = df_test[df_test['Recall Event ID'].isin(df_label['Recall Event ID'])]
            df_test = df_test.sort_values(by = ['Recall Event ID'])

            ypred = df_test['Predicted Fault Class'].values
            
            df_test['Predicted Fault Class'] = df_test['Predicted Fault Class'].apply(f_inv)
            # df_test = pd.concat([df_test, pd.DataFrame(df_label['Fault Class'], columns = ['True Fault Class'])], axis=1)
            df_test['True Fault Class'] = df_label['Fault Class'].values

            ylabel = df_label['Fault Class'].apply(f).values

        else:
            df_label_file = pd.read_excel(data_dir+str(filename)+label_file_suffix)
            df_label = df_label_file['Fault_Class']
            ylabel = df_label.apply(f).values


        print('performance on ' + filename)

        # print('percent computer related predicted')
        # print np.sum(ypred)/ float(np.size(ypred))
        # print('percent computer related true')        
        # print np.sum(ylabel)/ float(np.size(ylabel))

        print("accuracy: {:.2f}%".format(accuracy_score(ylabel, ypred) * 100))
        print("f1 score: {:.2f}%".format(f1_score(ylabel, ypred) * 100))

        print(classification_report(ylabel, ypred))

        df_test = df_test.applymap(lambda x: x.encode('unicode_escape').decode('utf-8') if isinstance(x, str) else x)
        df_test.to_excel(data_dir+str(filename)+'_predicted.xlsx', index = False)

def selectFeatures(train_set, train_text, k):
    dic = open(data_dir+"best_keywords.txt", "wb")
    # Normalize the text
    small_text = train_text.lower()
    # Replace punctuations (except -) with empty spaces
    regex = re.compile('[%s]' % re.escape('!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~'))
    clean_text = regex.sub(' ',small_text)
    # Tokenize the text
    tokens = nltk.word_tokenize(clean_text)
    # Remove English Stop Words and those words with less than 3 characters
    english_stops = set(stopwords.words('english'))
    words = [word for word in tokens if word not in english_stops and len(word) > 3 and not word.isdigit()]
    # Get rid of tenses for verbs
    #wnl = WordNetLemmatizer()
    #words = [wnl.lemmatize(t, 'v') for t in words]
    print str(len(words))+' words found.'

    clean_words = []
    for word in words:
        try:
            v = nltk.pos_tag(word)
            clean_words.append(word)
        except:
            continue

    # Tagging of the parts of speech
    tagged_words = nltk.pos_tag(clean_words)
    words = [word for (word, tag) in tagged_words if tag in ['NN','JJ','NNS','RB','VB','VBD','VBG','VBN','VBP','VBZ']]
    #words = set(words).intersection(set(unigrams+ bigrams+trigrams));
    # Get the frequency of words
    fdist = nltk.FreqDist(words)
    dictionary = fdist.keys()
    print str(len(dictionary))+' words tagged.'

    l= [];
    # Total number of recalls
    N =  len(train_set);
    NC_list = [(w, u, v) for (w, u,v) in train_set if v == 'Not_Computer'];
    C_list = [(w, u, v) for (w, u,v) in train_set if v != 'Not_Computer'];

    # Number of recalls that are computer-related
    N_1 = len(C_list);
    # Number of recalls that are not computer-related
    N_0 = len(NC_list);

    for w in dictionary:
        A_tc = 0;
        # Number of recalls that have term w
        N1_ = 0;
        # Number of recalls that don't have term w
        N0_ = 0;
        # Number of recalls that have term w and are not computer related
        N10 = 0;
        # Number of recalls that have term w and are computer related
        N11 = 0;
        # Number of recalls that don't have term w and are not computer related
        N00 = 0;
        # Number of recalls that don't have term w and are computer related
        N01 = 0;
        for (number, reason, fault_class) in train_set:
            if (reason.lower().find(w) > -1):
                N1_ = N1_ + 1;
                if (fault_class == 'Not_Computer'):
                    N10 = N10 + 1;
                else:
                    N11 = N11 + 1;
            else:
                N0_ = N0_ + 1;
                if (fault_class == 'Not_Computer'):
                    N00 = N00 + 1;
                else:
                    N01 = N01 + 1;
        # Utility function: Mutual Information to find the best words as features
        if (N11 != 0) and (N1_ != 0) and  (N_1 != 0):
            A_tc = A_tc + (float(N11)/float(N)*math.log(float(N*N11)/float(N1_*N_1),2))
        if (N01 != 0) and (N0_ != 0) and (N_1 != 0):
            A_tc = A_tc + (float(N01)/float(N)*math.log(float(N*N01)/float(N0_*N_1),2))
        if (N10 != 0) and (N1_ != 0) and (N_0 != 0):
            A_tc = A_tc + (float(N10)/float(N)*math.log(float(N*N10)/float(N1_*N_0),2))
        if (N00 != 0) and (N0_ != 0) and (N_0 != 0):
            A_tc = A_tc + (float(N00)/float(N)*math.log(float(N*N00)/float(N0_*N_0),2))
        #print w, A_tc
        # Append to the list
        l.append((A_tc, w));
        dic.write(w + ',' + str(A_tc)+'\n')
    # Get the features
    l.sort(key = itemgetter(1),reverse = True)
    l = l[0:k]
    l = array(l)
    l = l[:,0]
    return l

def training(train_set, features):
    # Total number of training recalls
    N =  len(train_set);
    # Total number of terms
    B = len(features)
    Nc = 0;
    Nc_ = 0;

    Ptc = [];
    Ptc_ = [];
    for (s, f) in features:
        N_tc = 1;
        N_tc_ = 1;
        for (number, reason, fault_class) in train_set:
            # Normalize the text
            words = reason.lower()

            if (fault_class == 'Not_Computer'):
                N_tc_ = N_tc_ + words.count(f);
                Nc_ = Nc_ + words.count(f);
            else:
                N_tc = N_tc + words.count(f);
                Nc = Nc + words.count(f);
        Ptc.append((f, N_tc))
        Ptc_.append((f, N_tc_))

    P_tc = {'word':0.0};
    P_tc_ = {'word':0.0};
    for (f,N) in Ptc:
        P_tc[f] = float(N)/(float(Nc)+float(B))

    for (f,N) in Ptc_:
        P_tc_[f] = float(N)/(float(Nc_)+float(B))

    return [P_tc, P_tc_]

def testing(test_set, features, P_tc, P_tc_, Pc, Pc_):
    test_set_labels = []
    for (rownum, number, reason) in test_set:
        testPc = 0;
        testPc_ = 0;
        # Normalize the text
        words = reason.lower()

        for (s,f) in features:
            for i in range(0,words.count(f)):
                testPc = float(testPc) + math.log(float(P_tc[f]),2)
                testPc_ = float(testPc_) + math.log(float(P_tc_[f]),2)

        testPc = float(testPc) + math.log(float(Pc),2);
        testPc_ = float(testPc_) + math.log(float(Pc_),2);

        if (testPc > testPc_):
            fault_class = 'Computer'
        else:
            fault_class = 'Not_Computer'

        test_set_labels.append((rownum, number, reason, fault_class))
    return test_set_labels

def get_train_set_text(train_filename):

    train_workbook = xlrd.open_workbook(data_dir+train_filename)
    try:
        worksheet = train_workbook.sheet_by_name('sheet1')
    except:
        worksheet = train_workbook.sheet_by_name('Sheet1')
    num_rows = worksheet.nrows
    num_cols = worksheet.ncols

    train_text = ''
    NC = 0;
    C = 0;
    text_NC = '';
    text_C = '';
    train_set = [];
    # Find the column numbers for Reason and Action
    for j in range(0, num_cols):
        col = worksheet.cell_value(0, j)
        if(col == 'Reason for Recall'):
            Reason_Index = j
        elif(col == 'Action'):
            Action_Index = j
        elif(col == 'Fault Class'):
            Fault_Index = j
    for i in range(1, num_rows):
        number = (worksheet.cell_value(i, 0).strip()).encode('utf-8')
        reason = (worksheet.cell_value(i, Reason_Index).strip()).encode('utf-8')
        action = (worksheet.cell_value(i, Action_Index).strip()).encode('utf-8')
        fault_class = str(worksheet.cell_value(i, Fault_Index).strip()).encode('utf-8')
        train_set.append((number, reason, fault_class))
        train_text = train_text+' '+reason
    print str(len(train_set))
    return train_set, train_text

def get_features(train_set, train_text, save_features = True):
    # features = selectFeatures(train_set, train_text, 100)

    features = []
    dic = open(data_dir+"best_keywords.txt", "rb")
    for line in dic:
        word = line.split(',')[0].strip()
        score = line.split(',')[1].strip()
        features.append((score, word))
    features = sorted(features, key = itemgetter(0), reverse = True)
    features = array(features)
    features = features[:,1]
    dic.close()

    if save_features:
        pickle.dump(features, open('features.txt', 'w'))
        print features[0:10]
        print 'features were dumped'
    return features

def get_test(uniqueFiles, start_year, end_year = 2100):
    test_files=[]
    #check each filename for format unique####.xls, add to list of filenames if it matches
    for i in range(len(uniqueFiles)):
        fileNm = uniqueFiles[i]
        if re.match("unique[0123456789]{4}.xls",fileNm) != None:
            if (int(fileNm.split('.')[0].split('unique')[1]) >= start_year and int(fileNm.split('.')[0].split('unique')[1]) <= end_year ):
                test_files.append(fileNm.split('.')[0])
    print 'Test files:'
    print test_files
    return test_files

def classify():
    # Get the training set of recalls
    (train_set, train_text) = get_train_set_text()
    test_files = get_test()
    features = get_features(train_set, train_text)
    
    # Total number of recalls in the training set
    N =  len(train_set)
    # Number of recalls that are computer-related
    C_list = [(w, u, v) for (w, u,v) in train_set if v != 'Not_Computer']
    C = len(C_list)
    # Prior Probabilities
    Pc = float(C)/float(N)
    Pc_ = 1-Pc
    (P_tc, P_tc_) = training(train_set, features[1:len(features)/2])

    # Training - Using the highest score features
    for filename in test_files:
        test_set = []
        test_workbook = xlrd.open_workbook(data_dir+filename+'.xls')
        try:
            worksheet = test_workbook.sheet_by_index(0)
        except:
            worksheet = test_workbook.sheet_by_index(0)
        num_rows = worksheet.nrows
        num_cols = worksheet.ncols

        newbook = xlwt.Workbook("iso-8859-2")
        newsheet = newbook.add_sheet('Sheet1', cell_overwrite_ok = True)

        # Find the column numbers for Reason and Action
        for j in range(0, num_cols):
            col = worksheet.cell_value(0, j)
            if(col == 'Reason for Recall'):
                Reason_Index = j
            elif(col == 'Action'):
                Action_Index = j
            elif(col == 'Fault Class'):
                Fault_Index = j
        for i in range(1, num_rows):
            number = (worksheet.cell_value(i, 0).strip()).encode('utf-8')
            reason = (worksheet.cell_value(i, Reason_Index).strip()).encode('utf-8')
            test_set.append((i, number, reason))
        print 'Testing: '+filename
        print str(len(test_set))

        # Testing  - Using the highest score features
        # test_set_labels = testing(test_set, features[1:len(features)/2], P_tc, P_tc_, Pc, Pc_)

        for k in range(0,num_cols):
            newsheet.write(0, k, worksheet.cell_value(0, k));
        newsheet.write(0, k+1, 'Fault_Class');

        test_set_labels = sorted(test_set_labels, key = itemgetter(3), reverse = True)
        
        for (i, number, reason, fault_class) in test_set_labels:
            for k in range(0,num_cols):
                newsheet.write(i, k, worksheet.cell_value(i, k));
            newsheet.write(i, k+1, fault_class);

        newbook.save(data_dir+str(filename)+'_predicted.xls')