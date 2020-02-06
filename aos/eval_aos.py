
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



def eval_and(shape, context):
    raise NotImplementedError

def eval_or(shape, context):
    raise NotImplementedError

def eval_seq(shape, context):
    shape_args = shape.args
    assert len(shape_args) == 1, f'eval infeasible, multiple args: ({shape_args})'
    arg = shape_args[0]
    res, err = eval_aos_in_context(arg, context)
    assert isinstance(res, list)
    return res, err

def eval_dim(shape, context):
    dim_name = shape.dim.name.strip()
    res = [v for k, v in context if k == dim_name]
    if len(res) == 1: res = res[0]
    return res, None

def eval_aos_in_context(shape, context):
    res, err = None, None
    op = shape.op
    
    if DEBUG: print(f'eval_aos: {op}, {shape}, {context}')
    if op is None:
        res, err = eval_dim(shape, context)
    elif op == AOop.OR:
        res, err = eval_or(OrEval, shape, context)
    elif op == AOop.AND:
        res, err = eval_and(AndEval, shape, context)
    elif op == AOop.SEQUENCE:
        res, err = eval_seq(shape, context)
    else:
        raise NotImplementedError(f'op: {op}, shape: {shape}')

    #if DEBUG: print (f'< eval_aos: {res}, {err}')
    return res, err












