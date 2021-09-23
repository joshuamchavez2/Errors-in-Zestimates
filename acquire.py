import pandas as pd
import numpy as np
import os

from env import host, user, password

def get_db_url(url):
    url = f'mysql+pymysql://{user}:{password}@{host}/{url}'
    return url

def zillow_data():
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

def acquire_zillow():
    '''
    This function reads in titanic data from Codeup database, writes data to
    a csv file if a local file does not exist, and returns a df.
    '''
    if os.path.isfile('zillow_df.csv'):
        
        # If csv file exists, read in data from csv file.
        df = pd.read_csv('zillow_df.csv', index_col=0)
        
    else:
        
        # Read fresh data from db into a DataFrame.
        df = zillow_data()
        
        # Write DataFrame to a csv file.
        df.to_csv('zillow_df.csv')
        
    return df