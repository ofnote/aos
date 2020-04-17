from typing import Callable
from itertools import chain

def unroll_type2actions(t2a):
    res = {}
    for k, a in t2a.items():
        if isinstance(k, tuple):
            for i in k:
                assert i not in res
                res[i] = a
        else:
            res[k] = a
    return res

def apply_match_t2a(t2a, obj, *args, default_func=None, **kwargs):
    '''
        t2a: type2action dictionary for the various 'obj' types
    '''
    t2a = unroll_type2actions(t2a)
    tobj = type(obj)
    #print(f'apply_match: {tobj}, {tobj.__name__}')
    if tobj in t2a:
        tkey = tobj
    elif tobj.__name__ in t2a:
        tkey = tobj.__name__
    elif (f'{tobj.__module__}.{tobj.__name__}') in t2a:
        tkey = f'{tobj.__module__}.{tobj.__name__}'
    else:
        print (f'apply_match: not found {tobj} key')
        assert default_func, 'no default type handler'
        return default_func(obj, *args, **kwargs)     
    
    func = t2a[tkey]
    if isinstance(func, staticmethod):
        func = func.__func__ 
    else:
        assert isinstance(func, Callable), f'apply_match: type = {type(func)}'

    return func(obj, *args, **kwargs)

def apply_match(klass, obj, *args, **kwargs):
    #print(f'from_obj: {obj}, {type(obj)}')
    t2a = klass.type2action
    default_func = getattr(klass, 'default_func', None)
    return apply_match_t2a(t2a, obj, *args, default_func=default_func, **kwargs)


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
