import pandas as pd
import numpy as np
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import SimpleImputer

from functions import nulls_by_col, nulls_by_row, handle_missing_values, remove_columns, add_scaled_columns, remove_outliers

######################## Clean ############################

def clean(df):
    
    # Create county from fips
    df["county"] = df["fips"].map({6037: "Los Angeles", 6059: "Orange", 6111: "Ventura"})

    # Filter through only Single Family Residentails
    df = df[df.propertylandusedesc == 'Single Family Residential']
    
    # Removing columns that are missing greater than 60% of its values
    # Removing rows that are missing 75% of its values
    df = handle_missing_values(df)

    # Removing columns that I found not useful
    cols_to_remove = ['propertylandusetypeid', 'heatingorsystemtypeid', 'parcelid', 'buildingqualitytypeid',\
                  'finishedsquarefeet12', 'fullbathcnt', 'propertylandusedesc', 'id.1', 'assessmentyear',\
                  'structuretaxvaluedollarcnt', 'roomcnt', 'regionidcity', 'regionidcounty', 'regionidzip',\
                  'propertycountylandusecode', 'censustractandblock', 'landtaxvaluedollarcnt',\
                  'rawcensustractandblock', 'propertyzoningdesc', 'transactiondate', 'calculatedbathnbr', 'id','fips']

    df = remove_columns(df, cols_to_remove)

    # Removing any rows who unitcnt is greater than 1, then removing the column entirely
    selRows = df[df.unitcnt == 2.0].index
    df = df.drop(selRows, axis=0)
    df = remove_columns(df, ['unitcnt'])

    # Removing some outliers in heaters 
    selRows = df[(df.heatingorsystemdesc == 'Yes') | (df.heatingorsystemdesc == 'Gravity') |\
    (df.heatingorsystemdesc == 'Radiant') | (df.heatingorsystemdesc == 'Baseboard')|\
    (df.heatingorsystemdesc == 'None')| (df.heatingorsystemdesc == 'Solar')].index
    df = df.drop(selRows, axis=0)

    # Rename
    df = df.rename(columns = {
        'bedroomcnt':'bed', 
        'bathroomcnt':'bath', 
        'calculatedfinishedsquarefeet':'area',
        'taxvaluedollarcnt':'tax_value',
        'latitude':'lat',
        'longitude':'long',
        'lotsizesquarefeet':'lot_size',
        'yearbuilt':'year',
        'taxamount':'tax_amount',
        'heatingorsystemdesc':'heating_type',})

    # Imputing by most_frequent
    nulls = list(df.columns[df.isnull().sum() > 0])
    imputer = SimpleImputer(missing_values = np.nan, strategy='most_frequent')
    imputer =imputer.fit(df[nulls])
    df[nulls] = imputer.transform(df[nulls])

    return df

def split(df):
    
    train_validate, test = train_test_split(df, test_size=.2, random_state=123)
    train, validate = train_test_split(train_validate, test_size=.3, random_state=123)

    return train, validate, test

def outlier(df, k):
    col_list = ['bath','bed','area','lot_size','year','tax_amount','tax_value']
    df = remove_outliers(df, k, col_list)
    return df

def scaled(train, validate, test):
    scaler = MinMaxScaler()
    columns_to_scale = ['bath','bed','area','lot_size','year','tax_amount','tax_value']
    train, validate, test = add_scaled_columns(train, validate, test, scaler, columns_to_scale)
    return train, validate, test

def prepare_mode(df, mode, k):

    # For intial_explore clean and split only
    if mode=='intial_explore':
        df = clean(df)
        train, validate, test = split(df)
        return train, validate, test

    # For explore clean, remove outliers, and split
    if mode=='explore':
        df = clean(df)
        df = outlier(df, k)
        train, validate, test = split(df)
        return train, validate, test

    # For clustering clean, remove outliers, split, and scaled. 
    if mode=='cluster':
        df = clean(df)
        df = outlier(df, k)
        train, validate, test = split(df)
        train, validate, test = scaled(train, validate, test)
        return train, validate, test
    
    # For model clean, remove outliers, split, and scaled.
    if mode=='model':
        df = clean(df)
        df = remove_outliers(df, k)
        train, validate, test = split(df)
        train, validate, test = scaled(train, validate, test)
        return train, validate, test

def prepare(df):
    df = clean(df)
    train, validate, test = split(df)
    return train, validate, test