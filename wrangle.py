from acquire import acquire_zillow
from prepare import prepare_zillow

def wrangle_zillow():
    
    train, validate, test = prepare_zillow(acquire_zillow())
    
    return train, validate, test