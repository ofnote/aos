
from .utils import apply_match
from .aos import AOop
from .common import Config, OrVals, AndTuple
import itertools
from collections import ChainMap

DEBUG = Config.DEBUG
II = isinstance

def get_res_err_from_tuples(res_err_n):
    #print ('**get: ', res_err_n, len(res_err_n))
    res = [x[0] for x in res_err_n]
    err = [x[1] for x in res_err_n if x[1] is not None]
    err = list(itertools.chain(*err)) #TODO: fix
    if not err:
        err = None
    return res, err

def pair_lists(A, B):
    #assert len(o1) == len(o2), f'o1={o1}\no2={o2}'
    from itertools import cycle
    zip_list = zip(A, cycle(B)) if len(A) > len(B) else zip(cycle(A), B)
    #if DEBUG: print ('pairLIsts', A, B, list(zip_list))
    return list(zip_list)

def to_AndTuple(k, v):
    return AndTuple((k,v))

def and_simplify(key, vals):
    # moving OrVals up the result expression
    if II(key, OrVals) and not II(vals, OrVals):
        #print (key)
        res = OrVals([to_AndTuple(k, vals) for k in key])
    elif not II(key, OrVals) and II(vals, OrVals):
        res = OrVals([to_AndTuple(key, v) for v in vals])
    elif II(key, OrVals) and II(vals, OrVals):
        assert len(key) == len(vals)
        res = zip(key, vals)
        res = OrVals([to_AndTuple(k,v) for (k,v) in res])
    else: #none is orvals
        res = to_AndTuple(key, vals)
    return res

def eval_and(shape, contexts, colon=False):
    shape_args = shape.args
    assert len(shape_args) == 2, f'eval_and: only handling 2 args'
    res_err_n = [eval_aos_in_context(arg, contexts) for arg in shape_args]
    res, err = get_res_err_from_tuples(res_err_n)

    if not err:
        key, vals = res
        #assert II(vals, OrVals), f'vals = {vals}'
        if colon:
            assert II(key, OrVals), f'{key}'
            res = and_simplify(key, vals)
            #print(res)
            res = dict(res)
        else:
            res = and_simplify(key, vals)

        err = None
    else:
        res = None
        assert False, err

    if DEBUG:
        #print(f'eval_and: {shape}, {contexts} ->\n {key}\n {vals} \n {res}')
        print (f'eval_and: {key}, {vals}')
        print(f'eval_and:  {res}')
    return res, err

def eval_colon(shape, contexts):
    return eval_and(shape, contexts, colon=True)


def eval_or(shape, contexts, simplify_or=False):
    shape_args = shape.args
    #assert len(shape_args) == 2, f'eval_or: only handling 2 args: {shape_args}'
    res_err_n = [eval_aos_in_context(arg, contexts) for arg in shape_args]
    res, err = get_res_err_from_tuples(res_err_n)
    if DEBUG: print (f'eval_or: from children: res:{res}, \n err:{err}')

    if not err:
        #assert each element of res is a list
        #res = list(itertools.chain(*res))
        #assert each element of list is a dict
        if isinstance(res[0], OrVals):
            res = OrVals.merge(res)
        if DEBUG:
            print(f'eval_or: {shape}, {contexts}')
            print (f'eval_or - res: {res}')
        
        
        if simplify_or:
            res = res.simplify()

    else:
        res = None
        assert False, err
    return res, err

def eval_seq(shape, contexts):
    shape_args = shape.args
    assert len(shape_args) == 1, f'eval infeasible, multiple args: ({shape_args})'
    arg = shape_args[0]

    assert len(contexts) == 1
    ctx = contexts[0]
    '''
    res_n = []
    for ctx in contexts:
        res, err = eval_aos_in_context(arg, ctx)
        assert err is None
        res_n.append(res)
    '''
    res, err = eval_aos_in_context(arg, ctx)
    assert err is None, err
    assert II(res, OrVals)
    #when OrVals hits a Seq, it becomes an ordinary list
    res_n = [x for x in res]
    #res_n = list(itertools.chain(*res_n))
    if DEBUG: print(f'eval_seq: {res_n}')
    assert II(res_n, list)
    return res_n, err

def eval_dim(shape, contexts):
    dim_name = shape.dim.name.strip()
    res = None
    if II(contexts, list):
        res = OrVals()
        for c in contexts:
            assert II(c, dict)
            if dim_name in c:
                res.append(c[dim_name])
            else:
                pass
                #TODO: append None or not?
                #res.append(None)
        #single element contexts also passed in as list above
        if len(res) == 1: res = res[0]

    elif II(contexts, dict):
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












