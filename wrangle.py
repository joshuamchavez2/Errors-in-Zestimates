from acquire import acquire
from prepare import prepare

def wrangle(mode, k):
    
    train, validate, test = prepare(acquire(), mode, k)
    
    return train, validate, test