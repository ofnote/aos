import sys
from collections import defaultdict

from .aos import AOShape, AOop, AOConst
from .dim import DimSymbol, ContinuousDim, CategoricalDim, Dim
from .dim import is_dim_or_scalar
from .common import AndTuple, II, Config
from .bind import TryBind, BindError, Bind


class PyObjBind:
    def __init__(self, bind_types=False):
        self.bind_types = bind_types

    def bind_and (self, tb: 'TryBind'):
        if II(tb.o, AndTuple):
            tbs = tb.build_matching_pairs()
            return tbs
        else:
            return BindError(f'cannot bind_and: {tb.o}, {tb.s}')

    def bind_or(self, tb: 'TryBind'):
        if II(tb.o, dict):
            items = [AndTuple(x) for x in tb.o.items()]
            tbs = TryBind(items, tb.s.args).build_matching_pairs()
        elif II(tb.o, (tuple, list)):
            tbs = TryBind(tb.o, tb.s.args).build_matching_pairs()
        else:
            return BindError(f'cannot bind_or: {tb.o}, {tb.s}')
        return tbs


    def bind_star(self, tb: 'TryBind'):
        arg = tb.s.args[0]
        if II(tb.o, (list, tuple)):
            tbs = [TryBind(x, arg) for x in tb.o]
        elif II(tb.o, dict):
            tbs = [TryBind(AndTuple(item), arg) for item in tb.o.items()]
        else:
            return BindError(f'cannot bind_star: {tb.o}, {tb.s}')

        return tbs

    def bind_terminal(self, tb: 'TryBind'):
        err = BindError(f'bind_terminal: {tb}') #not a terminal dim name
        if not tb.s.is_dim():
            return err

        obj, name = tb.o, tb.s.get_dim_name()

        is_type_name = (sys.intern(type(obj).__name__) is sys.intern(name))
        same_name = (obj is sys.intern(name))
        name_is_underscore = (AOConst.is_underscore(name))


        #print(f'name: {name}, {type(name)}')
        '''
        test = (obj is sys.intern(name)) \
                or is_type_name\
                or (is_dim_or_scalar(obj) and (AOConst.is_underscore(name))\
                or self.bind_variables
                )
        if not test:
            return BindError(f'bind_terminal: {obj}, {name}')
        '''

        res = Bind()
        if is_type_name or name_is_underscore: # don't bind type names, only variables
            return res
        res = Bind(name=name, v=obj)
        return res