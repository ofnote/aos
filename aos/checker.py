import sys
from itertools import chain

from parser import parse_aos
from aos import AOShape, AOop, AOConst
from aos import DimSymbol, ContinuousDim, CategoricalDim, Dim
from aos import AndTuple
from type_matchers import OrList, AndMatcher
from utils import apply_match

DEBUG = False

def as_or_list(obj):
    return apply_match(OrList, obj)

def get_or_match_args (obj, shape):
    res, err = None, None
    shape_args = shape.args

    obj_args, err = as_or_list(obj)
    if err is not None: return res, err

    if len(obj_args) != len(shape_args):
        err = f'shape mismatch: {obj_args}, {shape_args}'
        return res, err
    res = zip(obj_args, shape_args)
    return res, err


def get_and_match_args(obj, shape, exact=False, sample=False):
    shape_args = shape.args
    return apply_match(AndMatcher, obj, shape_args, exact=exact, sample=sample)

def get_sequence_match_args(obj, shape, exact=True, sample=False):

    #obj : list(x1, x2, ..), shape = (c|d)*
    # match(x1, 'c|d')
    res, err = None, None
    assert len(shape.args) == 1
    shape_arg = shape.args[0]

    if isinstance(obj, list):
        res = [(o, shape_arg) for o in obj]
    elif isinstance(obj, dict):
        res = [(AndTuple(item), shape_arg) for item in obj.items()]
    else:
        err = f'shape mismatch with sequence: {type(obj)}'

    return res, err

def get_match_args (op, obj, shape):
    '''
    return a list of (obj, shape) pairs to match
    '''
    if DEBUG: print(f'get_match_args: {op}, {obj}, {shape}')
    if op == AOop.OR:
        res = get_or_match_args(obj, shape)
    elif op == AOop.AND:
        res = get_and_match_args(obj, shape)
    elif op == AOop.SEQUENCE:
        res = get_sequence_match_args(obj, shape)
    else:
        raise NotImplementedError(f'op: {op}, shape: {shape}')

    if DEBUG: print (f'< get_match_args: {res}')
    return res

def is_scalar(obj):
    return isinstance(obj, (str, int, float, bool))

def is_dim(obj):
    if isinstance(obj, (ContinuousDim, CategoricalDim)): return True
    if isinstance(obj, str):
        return (DimSymbol.lookup(obj, hard=False) is not None)
    return False

def is_dim_or_scalar(obj):
    return is_scalar(obj) or is_dim(obj)

def match_obj_const(obj, const):

    if isinstance(obj, int) or (isinstance(obj, str) and obj.isdigit()):
        return int(obj) == const

    dim = DimSymbol.lookup(obj, hard=False)
    if dim is None: return False

    if isinstance(dim, ContinuousDim):
        return dim.size() == const
    return False


def match_dim(obj, dim_name):
    #print (f'matching {obj}, {dim_name}')
    err = None
    if DEBUG: print (f'match_dim: dname = {dim_name}, {type(dim_name)}')
    if AOConst.is_ellipsis(dim_name):  #match anything
        pass
    else:
        test = False
        if dim_name.isdigit():
            test = match_obj_const(obj, int(dim_name))
        else:
            test = (obj is sys.intern(dim_name)) \
                or sys.intern(type(obj).__name__) is sys.intern(dim_name)\
                or (is_dim_or_scalar(obj) and (AOConst.is_underscore(dim_name))\
                )

        err = None if test\
            else f'** Leaf mismatch: obj=({obj}), dim=({dim_name}) **'

    return err

def match_obj_shape(obj, shape) -> 'err':
    err = None
    if DEBUG: print (f'match_obj_shape: {obj}, {shape}')

    if shape.op is None:
        dname = shape.dim.name.strip()
        err = match_dim(obj, dname)

    else:

        match_pairs, err = get_match_args(shape.op, obj, shape)
        if err is not None: return err

        for pair in match_pairs:
            err = match_obj_shape(pair[0], pair[1])
            if err is not None:
                return err

    return err

def is_aos_shape(arr, shape):
    if isinstance(shape, str):
        shape = parse_aos(shape)
    
    print (f'\nchecking {arr} against {shape}')

    err = match_obj_shape(arr, shape)
    if err: 
        print (err)
        return False, err
    else:
        return True, None
