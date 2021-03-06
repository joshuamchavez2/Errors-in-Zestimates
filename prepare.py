import pandas as pd
import numpy as np
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import SimpleImputer
from sklearn.cluster import KMeans
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
    
    # Create new features
    df['price_per_sqft']= df.lot_size/df.tax_value

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

def outlier(df):
    # LA
    # Dropped any homes higher than $2.50 price_per_sqft in LA.
    # House was either really big or really inexpensive.
    selRows = df[(df['price_per_sqft'] >2.5) & (df['county']=='Los Angeles')].index
    df = df.drop(selRows, axis=0)

    #Ventura
    selRows = df[(df['lot_size'] > 250_000) & (df['county']=='Ventura')].index
    df = df.drop(selRows, axis=0)

    selRows = df[(df['tax_value'] < 55_000) & (df['county']=='Ventura')].index
    df = df.drop(selRows, axis=0)

    selRows = df[(df['price_per_sqft'] > .16) & (df['county']=='Ventura')].index
    df = df.drop(selRows, axis=0)

    #Orange County
    selRows = df[(df['tax_value'] > 2_000_000) & (df['county']=='Orange')].index           
    df = df.drop(selRows, axis=0)

    selRows = df[(df['tax_value'] < 55_000) & (df['county']=='Orange')].index           
    df = df.drop(selRows, axis=0)

    selRows = df[(df['price_per_sqft'] > .08) & (df['county']=='Orange')].index           
    df = df.drop(selRows, axis=0)
    
    return df

def scaled(train, validate, test):
    scaler = MinMaxScaler()
    columns_to_scale = ['bath','bed','area','lot_size','year','tax_amount','tax_value', 'lat', 'long', 'price_per_sqft']
    train, validate, test = add_scaled_columns(train, validate, test, scaler, columns_to_scale)
    return train, validate, test

def cluster(train, validate, test):
    X_train = train[["lat_scaled","long_scaled", 'area_scaled', "price_per_sqft_scaled"]]

    X_validate = validate[["lat_scaled","long_scaled", 'area_scaled', "price_per_sqft_scaled"]]

    X_test = test[["lat_scaled","long_scaled", 'area_scaled', "price_per_sqft_scaled"]]
    
    kmeans = KMeans(n_clusters=5, random_state=1349)

    # fit the thing
    kmeans.fit(X_train)

    # Use (predict using) the thing 
    kmeans.predict(X_train)
    train['cluster'] = kmeans.predict(X_train)
    validate['cluster'] = kmeans.predict(X_validate)
    test['cluster'] = kmeans.predict(X_test)

    # Create dummies for train
    boolean_dummy = pd.get_dummies(train['cluster'], drop_first=False)
    train = pd.concat([train, boolean_dummy], axis = 1)
    train = train.rename(columns = {
            0:'cluster_0', 
            1:'cluster_1', 
            2:'cluster_2',
            3:'cluster_3',
            4:'cluster_4',})

     # Create dummies for validate
    boolean_dummy = pd.get_dummies(validate['cluster'], drop_first=False)
    validate = pd.concat([validate, boolean_dummy], axis = 1)
    validate = validate.rename(columns = {
            0:'cluster_0', 
            1:'cluster_1', 
            2:'cluster_2',
            3:'cluster_3',
            4:'cluster_4',})

     # Create dummies for test
    boolean_dummy = pd.get_dummies(test['cluster'], drop_first=False)
    test = pd.concat([test, boolean_dummy], axis = 1)
    test = test.rename(columns = {
            0:'cluster_0', 
            1:'cluster_1', 
            2:'cluster_2',
            3:'cluster_3',
            4:'cluster_4',})

    return train, validate, test


def prepare_mode(df, mode):

    # For intial_explore clean and split only
    if mode=='intial_explore':
        df = clean(df)
        train, validate, test = split(df)
        return train, validate, test

    # For explore clean, remove outliers, and split
    if mode=='explore':
        df = clean(df)
        df = outlier(df)
        train, validate, test = split(df)
        return train, validate, test

    # For clustering clean, remove outliers, split, and scaled. 
    if mode=='cluster':
        df = clean(df)
        df = outlier(df)
        train, validate, test = split(df)
        train, validate, test = scaled(train, validate, test)
        return train, validate, test
    
    # For model clean, remove outliers, split, and scaled.
    if mode=='model':
        df = clean(df)
        df = remove_outliers(df)
        train, validate, test = split(df)
        train, validate, test = scaled(train, validate, test)
        return train, validate, test

def prepare(df):
    df = clean(df)
    df = outlier(df)
    train, validate, test = split(df)
    train, validate, test = scaled(train, validate, test)
    train, validate, test = cluster(train, validate, test)
    return train, validate, test