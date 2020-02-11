
from .utils import apply_match
from .aos import AndTuple, AOop
from .common import DEBUG


class AndEval():


    def default_func(obj, *args, **kwargs):
        err = f'not implemented type {type(obj)}'
        return None, err


    type2action = {
        #dict: for_dict,
        #AndTuple: for_AndTuple
    }



def eval_and(shape, contexts):
    shape_args = shape.args
    assert len(shape_args) == 2, f'eval_and: only handling 2 args'
    res_err_n = [eval_aos_in_context(arg, contexts) for arg in shape_args]
    res = [x[0] for x in res_err_n]
    err = [x[1] for x in res_err_n if x[1] is not None]
    if len(err) is 0 :
        res = {res[0]: res[1]}
        err = None
    else:
        res = None
        assert False, err
    return res, err

def eval_or(shape, contexts):
    raise NotImplementedError

def eval_seq(shape, contexts):
    shape_args = shape.args
    assert len(shape_args) == 1, f'eval infeasible, multiple args: ({shape_args})'
    arg = shape_args[0]

    res_n = []
    for ctx in contexts:
        res, err = eval_aos_in_context(arg, ctx)
        assert err is None
        res_n.append(res)
    if DEBUG: print(f'eval_seq: {res_n}')
    assert isinstance(res_n, list)
    return res_n, err

def eval_dim(shape, contexts):
    dim_name = shape.dim.name.strip()
    res = [v for k, v in contexts.items() if k == dim_name]
    if len(res) == 1: res = res[0] #only one match in contexts
    elif len(res) == 0: #no match in contexts
        res = dim_name
    #if DEBUG: print(f'> eval_dim: {res}')
    return res, None

def eval_aos_in_context(shape, contexts):
    res, err = None, None
    op = shape.op
    
    if DEBUG: print(f'eval_aos: op-{op}, {shape}, {contexts}')
    if op is None:
        res, err = eval_dim(shape, contexts)
    elif op == AOop.OR:
        res, err = eval_or(shape, contexts)
    elif op == AOop.AND:
        res, err = eval_and(shape, contexts)
    elif op == AOop.SEQUENCE:
        res, err = eval_seq(shape, contexts)
    else:
        raise NotImplementedError(f'op: {op}, shape: {shape}')

    #if DEBUG: print (f'< eval_aos: {res}, {err}')
    return res, err












