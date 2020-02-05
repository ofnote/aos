from aos.checker import is_aos_shape



def test_pyds():
    #Sequence[Tuple[Tuple[str, int], Dict[str, str]]]: '((str|int)|(str & str))* '
    #print (AOConst)
    #assert ('_' == getattr(AOConst, 'UNDERSCORE'))
    d = {'city': 'New York', 'country': 'USA'}
    t1 = ('Google', 2001)
    t2 = (t1, d)

    is_aos_shape(t2, '(str | int) | (str & str)')

    tlist = [('a', 1), ('b', 2)]
    is_aos_shape(tlist, '(str | int)*')
    is_aos_shape(tlist, '(_ | _)*')

    is_aos_shape(t2, '(_ | _) | (str & _)*')
    is_aos_shape(t2, '... | (str & _)')




    is_aos_shape(t2, '(_ | _) | (str & int)')

def test_pandas():
    d =  {'id': 'CS2_056', 'cost': 2, 'name': 'Tap'}
    df = pd.DataFrame([d])

    is_aos_shape(df, '1 & (id | cost | name)')

def test_numpy():
    #arr = np.array()
    arr = np.array([[1,2,3],[4,5,6]]) 
    is_aos_shape(arr, '2 & 3')

def test_pytorch():
    #arr = np.array()
    arr = torch.tensor([[1,2,3],[4,5,6]])
    is_aos_shape(arr, '2 & 3')

if __name__ == '__main__':
    import pandas as pd
    import numpy as np
    import torch
    
    test_pyds()
    test_pandas()
    test_numpy()
    test_pytorch()



