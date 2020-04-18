from types import SimpleNamespace
II = isinstance


#from typing import NewType
#AndTuple = NewType('AndTuple', tuple)
class AndTuple(tuple):
    def __repr__(self):
        s = super().__repr__()
        return f'`{s}`'

def simplify_and2dict(obj):
    if isinstance(obj, AndTuple):
        k, v = obj
        #assert isinstance(k, str)
        res = {k: simplify_and2dict(v)}
    elif isinstance(obj, dict):
        res = {k: simplify_and2dict(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        ty = type(obj)
        res = ty([simplify_and2dict(x) for x in obj])
    elif isinstance(obj, (int, float, str, bool)):
        res = obj

    else:
        raise ValueError(f'not handled type {type(obj)}')

    return res


class OrVals(list):
    # for storing a list of disjoint contexts
    def __repr__(self):
        s = super().__repr__()
        return f'|{s}|'

    @staticmethod
    def merge (ovlist: 'List[OrVals]'):
        lens = [len(ov) for ov in ovlist]
        assert lens.count(lens[0]) == len(lens), 'all OrVals not of same length'

        pairs = list(zip(*ovlist))
        #print (f'merge: {ovlist}, \n{list(pairs)}')
        res = ([OrVals(p).simplify() for p in pairs])

        res = OrVals(res) #BUG? do we need additional OrVals here ot List
        return res

    def simplify(self):
        # list of AndTuple -> dict
        for x in self:
            if not II(x, AndTuple): return self
            #z = dict(x)
        res = dict(self)
        return res
    

config = dict(
    pprint_treelike=False, 
    DEBUG=False
)
Config = SimpleNamespace(**config)