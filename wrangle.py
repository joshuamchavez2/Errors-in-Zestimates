from acquire import acquire
from prepare import prepare_mode, prepare

def wrangle_mode(mode, k):
    
    train, validate, test = prepare_mode(acquire(), mode, k)
    
    return train, validate, test

def wrangle():
    
    train, validate, test = prepare(acquire())
    
    return train, validate, test