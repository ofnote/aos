
from .utils import apply_match
from .aos import AndTuple, AOop
from .common import DEBUG


class AndBinder():
    def for_dict(obj, shape, **kwargs):
        res, err = None, None
        shape_args = shape.args

        if len(shape_args) == 2:
            k, v = shape_args
            k = k.get_dim_name()
            if k in obj:
                res = [(obj[k], v)]
            else:
                err = f'bind infeasible (no field [{k}], {type(k)}): {obj}, {shape_args}'
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


class OrBinder():
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
        items = [AndTuple(x) for x in obj.items()]
        return items, None
    def default_func(arr):
        err = f'mismatch: expected list or dict: unknown arr type {type(obj)}'
        return None, err

    type2action = {
        list: from_list,
        AndTuple: from_AndTuple,
        tuple: from_tuple,
        dict: from_dict
    }

class SeqBinder():
    def from_list(obj, shape, **kwargs):
        res, err = None, None
        shape_args = shape.args
        if len(shape_args) != 1:
            err = f'bind infeasible, multiple args: ({shape_args})'
        else:
            res = [(x, shape_args[0]) for x in obj]
        return res, err

    type2action = {
        list: from_list
    }

def bind_dim(obj, shape):
    #print (f'matching {obj}, {dim_name}')
    dim_name = shape.get_dim_name()

    err = None
    if DEBUG: print (f'bind_dim: dname = {dim_name}, {type(dim_name)}, {obj}')
    return [(dim_name, obj)], err


def get_bind_candidates(obj, shape):
    '''
    return a list of (obj, shape) pairs, *all* of which must bind
    '''
    res, err = None, None
    op = shape.op
    if DEBUG: print(f'get_bind_candidates: {op}, {obj}, {shape}')
    if op == AOop.OR:
        res, err = apply_match(OrBinder, obj, shape)
    elif op == AOop.AND:
        res, err = apply_match(AndBinder, obj, shape)
    elif op == AOop.SEQUENCE:
        res, err = apply_match(SeqBinder, obj, shape)
    else:
        raise NotImplementedError(f'op: {op}, shape: {shape}')

    if DEBUG: print (f'< get_bind_candidates: {res}, {err}')
    return res, err

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
                print('ret bind_obj_shape', res)
                if err is not None: break
                ctx.extend(res)

    return ctx, err


