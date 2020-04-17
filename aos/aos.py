from .dim import Dim, DimSymbol, CategoricalDim, ContinuousDim
from .common import Config
from enum import Enum
from typing import NamedTuple, List
from pprint import pformat

class AOop(Enum):
    AND: int = 0
    OR: int = 1
    COLON: int = 2
    COMMA: int = 3
    SEQUENCE: int = 4

    @staticmethod
    def to_str(op):
        if op == AOop.AND:
            return '&'
        elif op == AOop.OR:
            return '|'
        elif op == AOop.COLON:
            return ':'
        elif op == AOop.SEQUENCE:
            return '*'
        else:
            assert False

def is_dim_instance(shape):
    #check Union
    #if shape.__origin__ is Union:
    return shape in Dim.__args__


class AOConst(NamedTuple):
    UNDERSCORE: str = '_'
    ELLIPSIS: str = '...'

    @staticmethod
    def is_underscore(s: str):
        return s == AOConst().UNDERSCORE

    @staticmethod
    def is_ellipsis(s: str):
        return s == AOConst().ELLIPSIS




'''
Shape = Dim | AndDim of Shape*| OrDim of Shape*
Shape = Dim | Op of op, Shape*
'''

'''
AOShape :=
    ContinuousDim of (name: str, span: Slice)
    | SingletonDim of (name: str, valtype: str, logicaltype: str)
    | CategoricalDim of (name: str, categories: List[SingletonDim])
    | Op of (opt_name, op, List[AOShape])

    # defn without recursion:
    | AOShape of (optname, sexpr) #sexpr is a separate recursive type

'''

class AOShape(NamedTuple):
    op: int = None
    args: 'List[AOShape]' = None
    name: str = None

    dim: Dim = None


    optext2op = {
    '&': AOop.AND,
    '|': AOop.OR,
    ':': AOop.COLON,
    ',': AOop.COMMA,
    '*': AOop.SEQUENCE
    }

    def get_dim_name(self):
        assert self.dim is not None
        return self.dim.name.strip()


    @staticmethod
    def build_from(op, args):
        #print (f'build_from : {op}, {args}')

        if isinstance(op, str):
            op = AOShape.optext2op[op]
        for arg in args:
            assert isinstance(arg, AOShape), f'{arg}'

        if len(args) > 2 and op is AOop.AND: #convert n-ary to a binary tree
            args = args[::-1] #reverse list
            b, a = args[:2] # order of last 2 elements is reversed
            res = AOShape(op=op, args=(a,b))
            for arg in args[2:]:
                res = AOShape(op=op, args=[arg, res])
        else:
            res = AOShape(op=op, args=args)
        #print (f'build_from ret: {AOop.to_str(res.op)}')
        return res

    def make_shape(self, shape):
        assert isinstance(shape, AOShape)

        if is_dim_instance(shape):
            shape = AOShape(dim=shape)
        else:
            assert isinstance(shape, AOShape)
        return shape

    def andop(self, shape, name=None):

        shape = self.make_shape(shape)
        ret = AOShape(op=AOop.AND, args=[self,shape], name=name)
        return ret

    def __and__(self, shape):
        return self.andop(shape)
    def __rand__(self, shape):
        return self.andop(shape)

    def orop(self, shape, name=None):
        shape = self.make_shape(shape)
        ret = AOShape(op=AOop.OR, args=[self,shape], name=name)
        return ret

    def __or__(self, shape):
        return self.orop(shape)
    def __ror__(self, shape):
        return self.orop(shape)

    def __key(self):
        if self.dim is not None:
            return self.dim
        else:
            res = (self.op, self.name) + tuple(self.args)
        return res

    def __hash__(self):
        return hash(self.__key())

    def __repr_obj__(self, depth=0):
        res = {}

        if self.op is None:
            assert self.dim is not None
            res = self.dim.__repr__()
        else:
            op = AOop.to_str(self.op)
            args = [a.__repr_obj__(depth+1) for a in self.args]

            if self.op is AOop.OR:
                res = args
            else:
                res = (op, args)
                if self.op is AOop.AND:
                    arg0 = args[0]
                    rest_args = args[1:] if len(args) > 2 else args[-1] 
                    res = (arg0, rest_args)
                elif self.op is AOop.SEQUENCE:
                    res = {}
                    assert len(args) == 1
                    res[op] = args[0]

        return res

    def __repr__(self):
        if self.op is None:
            assert self.dim is not None
            return self.dim.__repr__()
        else:
            #res = [f'{a} {op}' for i, a in args]
            if not Config.pprint_treelike:
                op = AOop.to_str(self.op)
                #print (f'rep: op = {self.op}, {op}')
                args = [a.__repr__() for a in self.args]

                res = []
                # [x for x in chain.from_iterable(zip_longest(l1, l2)) if x is not None]
                for i, a in enumerate(args):
                    if i != len(args) - 1:
                        res.append(f'{a} {op}')
                    else:
                        res.append(f'{a}')
                #print (f'repr: {res}')
                if op == '*': res.append('*')

                res = '(' + ' '.join(res) + ')'
            
            else:
                res = self.__repr_obj__()
                res = pformat(res, indent=4)

            return res


    def __str__(self):
        return str(self.__repr__())



def decl_dim (name, dimtype, values):
    if dimtype == 'categorical':
        #TODO: convert values to categories
        dim = CategoricalDim(name=name, categories=values)
    elif dimtype == 'continuous':
        #TODO: convert values to span(slice)
        dim = ContinuousDim(name=name, span=values)
    return dim


def get_dims(names):
    '''
    names: 'b c h w', separated by spaces
    '''
    names = names.strip().split(' ')
    res = [AOShape(dim=DimSymbol.lookup(name)) for name in names]
    if len(names) == 1: return res[0]
    else: return res

def get_or_decl_dim(name):
    dim = DimSymbol.lookup(name, hard=False)
    if dim is None:
        dim = decl_dim(name=name, dimtype='categorical', values=[])
    return AOShape(dim=dim)

def get_or_decl_dims(names):
    names = names.strip().split(' ')
    res = [get_or_decl_dim(name) for name in names]
    if len(names) == 1: return res[0]
    else: return res


def show_dims(names):
    names = names.strip().split(' ')
    res = [str(DimSymbol.lookup(name)) for name in names]
    return '\n'.join(res)













