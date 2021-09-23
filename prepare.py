import pandas as pd
import numpy as np
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import SimpleImputer

from functions import nulls_by_col, nulls_by_row, handle_missing_values, remove_columns, add_scaled_columns, remove_outliers

######################## Clean ############################

def clean_zillow(df):
    
    df = df[df.propertylandusedesc == 'Single Family Residential']
    
    df = handle_missing_values(df)

    nulls = list(df.columns[df.isnull().sum() > 0])

    imputer = SimpleImputer(missing_values = np.nan, strategy='most_frequent')

    imputer =imputer.fit(df[nulls])

    df[nulls] = imputer.transform(df[nulls])

    return df

def split_zillow(df):
    
    train_validate, test = train_test_split(df, test_size=.2, random_state=123)
    train, validate = train_test_split(train_validate, test_size=.3, random_state=123)

    return train, validate, test

def prepare_zillow(df):

    df = clean_zillow(df)

    train, validate, test = split_zillow(df)

    return train, validate, test