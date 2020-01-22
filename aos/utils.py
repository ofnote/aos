from typing import Callable

def apply_match(klass, obj, *args, **kwargs):
    #print(f'from_obj: {obj}, {type(obj)}')
    t2a = klass.type2action
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
        return klass.default_func(obj, *args, **kwargs)     
    
    func = t2a[tkey]
    if isinstance(func, staticmethod):
        func = func.__func__ 
    else:
        assert isinstance(func, Callable), f'apply_match: type = {type(func)}'

    return func(obj, *args, **kwargs)
