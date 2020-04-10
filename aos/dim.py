from math import ceil

class DimSymbol():

    decls = {}
    __slots__ = 'name', 'fullname'

    def __init__(self, name:str, fullname:str =None):
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

from typing import Union

Dim = Union[ContinuousDim, CategoricalDim]
