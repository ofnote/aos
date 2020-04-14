from typing import Callable

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

def apply_match_t2a(t2a, obj, default=None, *args, **kwargs):
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
        return default(obj, *args, **kwargs)     
    
    func = t2a[tkey]
    if isinstance(func, staticmethod):
        func = func.__func__ 
    else:
        assert isinstance(func, Callable), f'apply_match: type = {type(func)}'

    return func(obj, *args, **kwargs)

def apply_match(klass, obj, *args, **kwargs):
    #print(f'from_obj: {obj}, {type(obj)}')
    t2a = klass.type2action
    return apply_match_t2a(t2a, obj, default=klass.default_func, *args, **kwargs)

