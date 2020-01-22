'''
from sympy import symbols, Integer
from sympy import And, Or
from sympy.core.symbol import Symbol
from sympy import nan, simplify
from sympy.logic.boolalg import BooleanFunction
from sympy.core.function import Function
'''

from math import ceil

#https://stackoverflow.com/questions/57514529/how-to-add-arguments-to-a-class-that-extends-poly-class-in-sympy
#https://stackoverflow.com/questions/57333942/how-to-assign-properties-to-symbols-in-sympy-and-have-them-in-the-same-domain
# dimension class
#class Dim(Symbol):

class DimSymbol():

    decls = {}
    __slots__ = 'name', 'fullname'

    '''
    def __new__(self, name:str, fullname:str =None):
        obj = Symbol.__new__(self, name)
        obj.fullname = fullname
        Dim._declare(obj)
        return obj
    def __new__(self, name:str, *args, **kwargs):
        ret = Symbol.__new__(self, name, commutative=False)
        print(f'new: {ret}')
        return ret
    '''

    def __init__(self, name:str, fullname:str =None):
        # name field accepted by parent class Symbol
        #https://stackoverflow.com/questions/10788976/how-do-i-properly-inherit-from-a-superclass-that-has-a-new-method
        self.name = name
        self.fullname = fullname
        DimSymbol._declare(self)

    @property
    def longname(self):
        res = '' if self.fullname is None else self.fullname
        res += f'({self.name})'
        return res
    

    @staticmethod
    def _declare(d):
        if d.name in DimSymbol.decls:
            raise ValueError(f'Dimension {d.name} already declared')
        DimSymbol.decls[d.name] = d

    @staticmethod
    def lookup(name: str, hard=True):
        if name not in DimSymbol.decls:
            if hard:
                assert False, (f'Dim {name} not declared')
            else: return None
        else:
            return DimSymbol.decls[name]

    def __repr__(self):
        return self.name

    '''
    @staticmethod
    def eval_name(e):
        #evalute a shape expression, in context of declared names
        sub_map = [(e, dv.longname) for e, dv in Dim.decls.items()]
        return str(e.subs(sub_map))
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

class ContinuousDim(DimSymbol):
    __slots__ = 'span', '_size'
    def __init__(self, name: str, span: slice, fullname: str=None):
        super().__init__(name=name, fullname=fullname)
        self.span = span

        size = (span.stop - span.start)
        if span.step is not None:
            size = ceil( (1.* size)/span.step) # (1,8,2) -> 8 - 1 = 7. ceil(7 / 2)
        self._size = size


    def size(self):
        return self._size

    def __repr__(self):
        return super().__repr__()

class SingletonDim(DimSymbol):
    __slots__ = 'valtype'
    def __init__(self, name: str, valtype: str, fullname: str=None):
        super().__init__(name=name, fullname=fullname)
        self.valtype = valtype


class CategoricalDim(DimSymbol):
    __slots__ = 'categories', '_num_categories'

    def __init__(self, name, categories, fullname: str=None):
        super().__init__(name=name, fullname=fullname)
        self.categories = [SingletonDim(name=cat[0], valtype=cat[1]) for cat in categories]
        self._num_categories = len(self.categories)
    def num_categories(self):
        return self._num_categories

from typing import Union, NamedTuple, List

Dim = Union[ContinuousDim, CategoricalDim]

'''
Shape = Dim | AndDim of Shape*| OrDim of Shape*
Shape = Dim | Op of op, Shape*
'''

from enum import Enum
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

class AOShape(NamedTuple):
    op: int = None
    args: 'List[AOShape]' = None
    dim: Dim = None
    name: str = None

    optext2op = {
    '&': AOop.AND,
    '|': AOop.OR,
    ':': AOop.COLON,
    ',': AOop.COMMA,
    '*': AOop.SEQUENCE
    }

    @staticmethod
    def build_from(op, args):
        #print (f'build_from : {op}, {args}')

        if isinstance(op, str):
            op = AOShape.optext2op[op]
        for arg in args:
            assert isinstance(arg, AOShape), f'{arg}'
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

    def __repr__(self):
        if self.op is None:
            assert self.dim is not None
            return self.dim.__repr__()
        else:
            op = AOop.to_str(self.op)
            #print (f'rep: op = {self.op}, {op}')
            args = [a.__repr__() for a in self.args]
            #res = [f'{a} {op}' for i, a in args]
            res = []
            for i, a in enumerate(args):
                if i != len(args) - 1:
                    res.append(f'{a} {op}')
                else:
                    res.append(f'{a}')
            #print (f'repr: {res}')
            if op == '*': res.append('*')

            return '(' + ' '.join(res) + ')'

            # [x for x in chain.from_iterable(zip_longest(l1, l2)) if x is not None]


#from typing import NewType
#AndTuple = NewType('AndTuple', tuple)
class AndTuple(tuple):
    pass

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













