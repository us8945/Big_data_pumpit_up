'''
Created on Apr 8, 2017

@author: uri
'''
#import Preprocessing.print_helper_functions
# Ignore warnings
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import random
import seaborn as sns

# Modelling Algorithms
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier , GradientBoostingClassifier

# Modelling Helpers
from sklearn.feature_selection import RFECV

# Visualisation
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab


# Configure visualisations
#matplotlib inline
#mpl.style.use( 'ggplot' )
pylab.rcParams[ 'figure.figsize' ] = 8 , 6


def load_data():
    train_df = pd.read_csv("../data/Training_data_values.csv")
    train_label_df = pd.read_csv("../data/Training_set_labels.csv")
    test_df    = pd.read_csv("../data/Test_set_values.csv")
    
    #train_df = train_df.drop(["id"],axis=1)
    #test_df = test_df.drop(["Id"],axis=1)
    return train_df, train_label_df, test_df

def describe_more( df ):
    pd.set_option('display.width', 1000)
    pd.set_option('max_colwidth',200)
    var = [] ; l = [] ; t = []; unq =[];
    for x in df:
        var.append( x )
        uniq_counts = len(pd.value_counts(df[x]))
        l.append(uniq_counts)
        t.append( df[ x ].dtypes )
        if uniq_counts < 12:
            unq.append(df[x].value_counts().to_dict())
        else:
            unq.append('Too many')
            
    levels = pd.DataFrame( { 'Variable' : var , 'Levels' : l , 'Datatype' : t , 'Level Values' : unq} )
    #levels.sort_values( by = 'Levels' , inplace = True )
    return levels

def preview_data(train_df, train_lbl_df,test_df):
    pd.set_option('display.max_columns', None)
    print('Display Train data info')
    print(train_df.head(n=5))
    #train_df.info()
    print(describe_more(train_df))
    
    print('Display Train Label data info')
    print("Show first 5 records in Label set")
    print(train_lbl_df.head(n=5))
    print(describe_more(train_lbl_df))
    
    
    print("----------------------------")
    print('Display Test data info')
    print(describe_more(test_df))

def drop_add_features(train_df,test_df,train_lbl_df):
    '''
    Remove columns:
    1. recorded_by - same value for each instance
    2. payment because same as payment_type 
    3. quantity_group same as quantity
    4. waterpoint_type_group same as waterpoint_type
    
    Drop "Id" column from Train data and Train labels
    
    Add columns:
    1. Add year, month and day based on date_recorded
'''
    drop_columns=['recorded_by','payment','quantity_group','waterpoint_type_group']
    date_columns = ['date_recorded']
    
    for df in [train_df, test_df]:
        for col in date_columns:
            df[col] = pd.to_datetime(df[col])
            df[col + "_day"] = df[col].dt.dayofyear
            df[col + "_month"] = df[col].dt.month
            df[col + "_year"] = df[col].dt.year
        df.drop(drop_columns+date_columns,axis=1,inplace=True)

    for df in [train_df, train_lbl_df]:
        df.drop('id',axis=1,inplace=True) 
     
def map_label_to_int(label):
    if label=='functional':
        return 0
    elif label =='non functional':
        return 1
    else: # functional needs repair
        return 2

def map_int_to_label(label):
    if label == 0:
        return 'functional'
    elif label == 1:
        return 'non functional'
    else: # 2
        return 'functional needs repair'
    
def pre_process_data(train_df,test_df,train_lbl_df):
    ''' 
        Encode all categorical columns (defined as 'object' in data-frame
    '''     
    
    missing_columns=['public_meeting','permit','waterpoint_type']
    for f in missing_columns:
        train_df[f].fillna('Missing', inplace=True)
        test_df[f].fillna('Missing', inplace=True)
    
    print("Before Categorical",len(train_df.columns))
    categorical=['permit','public_meeting','source_class','quantity','management_group','quality_group','waterpoint_type','source_type','payment_type','extraction_type_class','water_quality','basin','source']
    train_df = pd.get_dummies(train_df,prefix_sep='_',columns=categorical)
    test_df = pd.get_dummies(test_df,prefix_sep='_',columns=categorical)
    print("After Categorical",len(train_df.columns))
    
    for f in train_df.columns:
        if train_df[f].dtype == 'object':
            #print("processing Column:..",f)
            lbl = preprocessing.LabelEncoder()
            lbl.fit(np.unique(list(train_df[f].values) + list(test_df[f].values)))
            train_df[f] = lbl.transform(list(train_df[f].values))
            test_df[f]       = lbl.transform(list(test_df[f].values))
    
    # fill NaN values
    for f in train_df.columns:
        if train_df[f].dtype in ['float64','int64']:
            train_df[f].fillna(train_df[f].mean(), inplace=True)
            test_df[f].fillna(test_df[f].mean(), inplace=True)
    
    train_lbl_df['status_group'] = train_lbl_df['status_group'].apply(map_label_to_int)
        
    return train_df,test_df, train_lbl_df    


def calculate_rank(prob_array):
    records, columns = prob_array.shape
    rank_list = []
    for c in range(records):
        rank = int(((prob_array[c,0]*1 + prob_array[c,1]*2 +prob_array[c,2]*3 + prob_array[c,3]*4 + prob_array[c,4]*5 + prob_array[c,5]*6 + prob_array[c,6]*7 + prob_array[c,7]*8)/8)*10)
        rank_list.append(rank) 
    return np.asarray(rank_list)

 

if __name__ == '__main__':
    MODELS = {'1':True,'2':False,'2a': False, '3':False, '4':False, '5':False, '6':False, '2_submit':False, 'ALL':False}
    train_df, train_lbl_df, test_df = load_data()
    print('Data is loaded')
    drop_add_features(train_df,test_df,train_lbl_df)
    summary_df = describe_more(train_df)
    print(summary_df)
    summary_df.to_csv("Summary_data1.csv",set='\t')
    summary_df = describe_more(train_lbl_df)
    print(summary_df)
    train_df,test_df, train_lbl_df = pre_process_data(train_df, test_df,train_lbl_df)
    print("Num columns...",len(train_df.columns))
    print(train_lbl_df)
    random.seed(1234)
    
    X_train, X_validate, Y_train, Y_validate = train_test_split(train_df, train_lbl_df, test_size=0.15,random_state = 2015)
    
    
