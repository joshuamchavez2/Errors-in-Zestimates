import pandas as pd
import numpy as np
import os

from env import host, user, password

def get_db_url(url):
    url = f'mysql+pymysql://{user}:{password}@{host}/{url}'
    return url

def data():
    '''
    This function reads the titanic data from the Codeup db into a df,
    write it to a csv file, and returns the df.
    '''
    sql_query = """
            
    select *
    from properties_2017 as prop
    join(
        select parcelid, max(transactiondate) as transactiondate
        from predictions_2017
        group by parcelid
         ) as txn using(parcelid)
    join predictions_2017 as pred using(parcelid, transactiondate)
    left join airconditioningtype as act using (airconditioningtypeid)
    left join architecturalstyletype as ast using(architecturalstyletypeid)
    left join buildingclasstype as bct using(buildingclasstypeid)
    left join heatingorsystemtype as hst using(heatingorsystemtypeid)
    left join propertylandusetype as plt using(propertylandusetypeid)
    left join storytype as st using(storytypeid)
    left join typeconstructiontype as tct using(typeconstructiontypeid)
    where latitude IS NOT NULL and longitude IS NOT NULL; """

    df = pd.read_sql(sql_query, get_db_url('zillow'))

    return df

def acquire():
    '''
    This function reads in titanic data from Codeup database, writes data to
    a csv file if a local file does not exist, and returns a df.
    '''
    if os.path.isfile('zillow_df.csv'):
        
        # If csv file exists, read in data from csv file.
        df = pd.read_csv('zillow_df.csv', index_col=0)
        
    else:
        
        # Read fresh data from db into a DataFrame.
        df = data()
        
        # Write DataFrame to a csv file.
        df.to_csv('zillow_df.csv')
        
    return df

def get_data_dictionary(df):
    
    d_list = [
    'Number of bathrooms',
    'Number of bedrooms',
    'Size of the home in sq ft',
    'latitude coordinate',
    'longitude coordinate',
    'Size of the entire property',
    'year built',
    'Home Value',
    'Home taxable amount',
    'log error of actual vs predicted home price',
    'Central, Floor/Wall, Yes, Forced air',
    'Created this feature from fips.  LA, Orange, Ventura',
    'Created this feature lot_size/tax_value',
    'Number of bathrooms scaled',
    'Number of bedrooms scaled',
    'Area of Home scaled',
    'Are of property scaled',
    'year built scaled',
    'Home taxable amount scaled',
    'Home value scaled',
    'Latitude coordinates scaled',
    'Longitude coordinates scaled',
    'lot_size/tax_value scaled',
    '0, 1, 2, 3, 4',
    '0, 1',
    '0, 1',
    '0, 1',
    '0, 1',
    '0, 1',]


    data_dictionary = pd.DataFrame([{'Feature': col,
         'Datatype': f'{df[col].count()} non-null: {df[col].dtype}'} for col in df.columns])
    
    describe = pd.Series(d_list)
    df = pd.concat([data_dictionary, describe.rename("Description")], axis = 1)
    return df.set_index("Feature")

def get_target(df):    
    df = get_data_dictionary(df)
    df= df.reset_index()
    df = df.rename(index = {61: 'Target'})
    return df.iloc[61]