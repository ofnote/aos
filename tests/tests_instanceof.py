from aos.checker import instanceof as aosii
from aos.checker_old import instanceof as aosii2


def test_pyds():
    #Sequence[Tuple[Tuple[str, int], Dict[str, str]]]: '((str|int)|(str & str))* '
    #print (AOConst)
    #assert ('_' == getattr(AOConst, 'UNDERSCORE'))
    d = {'city': 'New York', 'country': 'USA'}
    t1 = ('Google', 2001)
    t2 = (t1, d)

    aosii(t2, '(str | int) | (str & str)')

    tlist = [('a', 1), ('b', 2)]
    aosii(tlist, '(str | int)*')
    aosii(tlist, '(_ | _)*')

    aosii(t2, '(_ | _) | (str & _)*')
    aosii(t2, '... | (str & _)')

    aosii(t2, '(_ | _) | (str & int)')

def test_pandas():
    d =  {'id': 'CS2_056', 'cost': 2, 'name': 'Tap'}
    df = pd.DataFrame([d])

    aosii2(df, '1 & (id | cost | name)')

def test_numpy():
    #arr = np.array()
    arr = np.array([[1,2,3],[4,5,6]]) 
    aosii2(arr, '2 & 3')

def test_pytorch():
    #arr = np.array()
    arr = torch.tensor([[1,2,3],[4,5,6]])
    aosii2(arr, '2 & 3')

if __name__ == '__main__':
    import pandas as pd
    import numpy as np
    import torch
    
    test_pyds()
    '''
    test_pandas()
    test_numpy()
    test_pytorch()
    '''


