
from .utils import apply_match, pair_items
from .aos import AOop
from collections import defaultdict
from .common import Config, OrVals, AndTuple
DEBUG = Config.DEBUG

class AndSplitter():
    def for_dict(obj, shape, **kwargs):
        res, err = None, None
        shape_args = shape.args

        if len(shape_args) == 2:
            k, v = shape_args
            k = k.get_dim_name()
            if k not in obj:
                keys = obj.keys()
                if len(keys) != 1:
                    err = f'bind infeasible to multiple keys {keys}'
                else:
                    res = []
                    for obj_k, obj_v in obj.items():
                        res.extend([(obj_k, k), (obj_v, v)])
            else:
                obj_v = obj[k]
                res = [(obj_v, v)]

        else:
            err = f'bind infeasible: more than 2 args for AND \n{obj}\n{shape_args}'
        return res, err
    
    def for_AndTuple(obj, shape, **kwargs):
        res, err = pair_items([obj], shape.args, sample=False) 
        return res, err


    type2action = {
        dict: for_dict,
        AndTuple: for_AndTuple
    }


class OrSplitter():
    '''
    convert an or-like object into a list of objects
    '''
    def from_list(obj, shape, **kwargs):
        raise NotImplementedError
    def from_tuple(obj, shape, **kwargs):
        raise NotImplementedError

    def from_AndTuple(obj, shape, **kwargs):
        err = f'mismatch: cannot convert AndTuple to Or-shape {obj}, {shape}'
        return None, err


    def from_dict(obj, shape, **kwargs):
        #convert into a list of AND types (ANDtuple)
        pairs = [(obj, x) for x in shape.args] #try to bind each OR arg with dict
        #pairs = [(AndTuple(x), shape) for x in obj.items()] #try to bind 
        #res = [get_bind_candidates(items, shape) for arg in shape.args]
        return pairs, None
    def default_func(arr):
        err = f'mismatch: expected list or dict: unknown arr type {type(obj)}'
        return None, err

    type2action = {
        list: from_list,
        AndTuple: from_AndTuple,
        tuple: from_tuple,
        dict: from_dict
    }

class SeqSplitter():
    def from_list(obj, shape, **kwargs):
        res, err = None, None
        shape_args = shape.args
        if len(shape_args) != 1:
            err = f'bind infeasible, multiple args: ({shape_args})'
        else:
            res = [(x, shape_args[0]) for x in obj]
        return res, err

    def from_dict(obj, shape, **kwargs):
        res, err = None, None
        shape_args = shape.args
        if len(shape_args) != 1:
            err = f'bind infeasible, multiple args: ({shape_args})'
        else:
            arg = shape_args[0]
            #convert dict to list of AndTuples
            res = [(AndTuple((k,v)), arg) for k, v in obj.items()]

        return res, err

    type2action = {
        list: from_list,
        dict: from_dict
    }

def bind_dim(obj, shape):
    #print (f'matching {obj}, {dim_name}')
    dim_name = shape.get_dim_name()

    err = None
    if DEBUG: print (f'bind_dim: dname = {dim_name}, {type(dim_name)}, {obj}')
    return [{dim_name: obj}], err


def get_bind_candidates(obj, shape):
    '''
    return a list of (obj, shape) pairs, *all* of which must bind
    '''
    res, err = None, None
    op = shape.op
    if DEBUG: print(f'\nget_bind_candidates: {op}, {obj}, {shape}')
    if op == AOop.OR:
        res, err = apply_match(OrSplitter, obj, shape)
    elif op == AOop.AND:
        res, err = apply_match(AndSplitter, obj, shape)
    elif op == AOop.SEQUENCE:
        res, err = apply_match(SeqSplitter, obj, shape)
    else:
        raise NotImplementedError(f'op: {op}, shape: {shape}')

    if DEBUG: print (f'< get_bind_candidates: {res}, {err}')
    return res, err


def combiner(ctx: 'list', shape):
    assert shape.op is not None
    res = None
    if shape.op == AOop.OR:
        or_dict = {}
        for c in ctx: 
            assert isinstance(c, dict), c
            or_dict.update(c)
        res = [or_dict]
    elif shape.op == AOop.AND:
        res = ctx
        #raise NotImplementedError(f'{ctx}, {shape}')
    elif shape.op == AOop.SEQUENCE:
        #res = ctx
        temp_dict = defaultdict(list)

        # make one dict
        for c in ctx:
            assert isinstance(c, dict)
            for k, v in c.items():
                temp_dict[k].append(v)

        #print(temp_dict)
        #assert False, temp_dict

        res = [{k: OrVals(v) for k, v in temp_dict.items()}] # list of dicts
        #assert False, (ctx, res)

    else:
        raise NotImplementedError(f'op: {op}, shape: {shape}') 
    if DEBUG:  print (f'---> combiner({shape.op})', ctx)

    return res

def bind_obj_shape(obj, shape) -> 'list | err':
    ctx, err = [], None
    if DEBUG: print (f'bind_obj_shape: {obj}, {shape}')

    if shape.op is None:
        ctx, err = bind_dim(obj, shape)
    else:
        to_bind_pairs, err = get_bind_candidates(obj, shape)
        if err is None: 
            ctx = []
            for pair in to_bind_pairs:
                res, err = bind_obj_shape(pair[0], pair[1])
                #if DEBUG: print('ret bind_obj_shape', res)
                if err is not None: break
                ctx.extend(res)
            ctx = combiner(ctx, shape)

    return ctx, err


