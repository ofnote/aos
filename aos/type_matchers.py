from aos import AndTuple
from itertools import chain

class OrList():
    '''
    convert an or-like object into a list of objects
    '''
    def from_AndTuple(arr):
        err = f'mismatch: cannot convert AndTuple to Or-shape {arr}'
        return None, err
    #def from_list(arr):
    #    return arr, None
    #def from_tuple(arr):
    #    return list(arr), None
    def from_dict(arr):
        #convert into a list of AND types (ANDtuple)
        items = [AndTuple(x) for x in arr.items()]
        return items, None
    def default_func(arr):
        err = f'mismatch: expected list or dict: unknown arr type {type(arr)}'
        return None, err

    type2action = {
        list: lambda arr: (arr, None),
        AndTuple: from_AndTuple,
        tuple: lambda arr: (list(arr), None),
        dict: from_dict
    }

    @classmethod
    def add_action(cls, klass, func):
        assert klass not in cls.type2action
        cls.type2action[klass] = func




def pair_items(items: 'iterator', shape_args: 'list', sample=False):
    '''
    pair some or all items from <items> with <shape_args>
    '''
    res, err = None, None

    if sample:
        item = next(iter(items))
        if len(item) != len(shape_args):
            return None, f'shape mismatch: {item}, {shape_args}'
        res = zip(item, shape_args)
    else:
        pairs = []
        for item in items:
            if len(item) != len(shape_args):
                return None, f'shape mismatch: {item}, {shape_args}'
            else:
                pairs.append(zip(item, shape_args))
        res = chain.from_iterable(pairs)

    return res, err

class AndMatcher():
    def for_dict(obj, shape_args, **kwargs):
        res, err = None, None
        if not kwargs['exact']: 
            res, err = pair_items(obj.items(), shape_args, sample=kwargs['sample'])
        else:
            err = f'shape mismatch: dict cannot match with AND: \n{dict}\n{shape_args}'
        return res, err

    def for_dataframe(obj, shape_args, **kwargs):
        res, err = None, None
        n = len(obj)
        if len(shape_args) != 2:
            err = f'mismatch: shape {shape_args} with pandas DataFrame'
        else:
            res = zip([n]+ [list(obj)], shape_args) 
        return res, err

    def for_AndTuple(obj, shape_args, **kwargs):
        res, err = pair_items([obj], shape_args, sample=False) 
        return res, err

    def for_ndarray(arr, shape_args, **kwargs):
        res, err = None, None
        shape = arr.size()
        #print(f'{arr.shape}, {shape_args}')
        if len(shape) != len(shape_args):
            err = f'mismatch: shape {shape} against args {shape_args}'
        else:
            res = zip(shape, shape_args)
        return res, err
    
    def for_torch_tensor(arr, shape_args, **kwargs):
        res, err = None, None
        shape = arr.size()
        #print(f'{arr.shape}, {shape_args}')
        if len(shape) != len(shape_args):
            err = f'mismatch: shape {shape} against args {shape_args}'
        else:
            res = zip(shape, shape_args)
        return res, err


    def default_func(obj, shape_args, **kwargs):
        raise NotImplementedError(f'AndMatcher : type = {type(obj), type(obj).__name__}')

    type2action = {
        dict: for_dict,
        AndTuple: for_AndTuple,
        'DataFrame': for_dataframe,
        'ndarray': for_ndarray,
        'torch.Tensor': for_torch_tensor
    }


