
from .utils import apply_match
from .aos import AndTuple, AOop
from .common import DEBUG


class OrVals(list):
    pass

def get_res_err_from_tuples(res_err_n):
    res = [x[0] for x in res_err_n]
    err = [x[1] for x in res_err_n if x[1] is not None]
    return res, err

def pair_lists(A, B):
    #assert len(o1) == len(o2), f'o1={o1}\no2={o2}'
    from itertools import cycle
    zip_list = zip(A, cycle(B)) if len(A) > len(B) else zip(cycle(A), B)
    #if DEBUG: print ('pairLIsts', A, B, list(zip_list))
    return list(zip_list)

def eval_and(shape, contexts, colon=False):
    shape_args = shape.args
    assert len(shape_args) == 2, f'eval_and: only handling 2 args'
    res_err_n = [eval_aos_in_context(arg, contexts) for arg in shape_args]
    res, err = get_res_err_from_tuples(res_err_n)

    if not err:
        key, vals = res
        #assert isinstance(vals, OrVals), f'vals = {vals}'
        if colon:
            assert isinstance(key, OrVals), f'{key}'

        if isinstance(key, OrVals) and not isinstance(vals, OrVals):
            res = OrVals([{k: vals} for k in key])
        elif not isinstance(key, OrVals) and isinstance(vals, OrVals):
            res = OrVals([{key: v} for v in vals])
        elif isinstance(key, OrVals) and isinstance(key, OrVals):
            assert len(key) == len(vals)
            res = zip(key, vals)
            res = dict(res)
        else: #none is orvals
            res = {key: vals}

        err = None
    else:
        res = None
        assert False, err

    #if DEBUG:
        #print(f'{shape}, {contexts} ->\n {key}\n {vals} \n {res}')
    return res, err

def eval_colon(shape, contexts):
    return eval_and(shape, contexts, colon=True)

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
    res = None
    if isinstance(contexts, list):
        res = OrVals()
        for c in contexts:
            assert isinstance(c, dict)
            if dim_name in c:
                res.append(c[dim_name])
    elif isinstance(contexts, dict):
        if dim_name in contexts:
            res = contexts[dim_name] 

    if not res: #no match in contexts: res = None or []
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
    elif op == AOop.COLON:
        res, err = eval_colon(shape, contexts)
    else:
        raise NotImplementedError(f'op: {op}, shape: {shape}')

    #if DEBUG: print (f'< eval_aos: {res}, {err}')
    return res, err












