import sys
from collections import defaultdict

from .aos import AOShape, AOop, AOConst
from .dim import DimSymbol, ContinuousDim, CategoricalDim, Dim
from .dim import is_dim_or_scalar
from .common import AndTuple, II, Config

DEBUG = Config.DEBUG

class BindError(str):
    def __str__(self):
        return f'<Error>: {repr(self)}'

class Bind:
    def __init__(self, name: 'variable' = None, v: 'value' = None, subst=None ):
        # value from object
        # name from shape
        if subst is not None:
            self.subst = subst
        elif (name is not None and v is not None):
            self.subst = {name: [v]}
        else:
            self.subst = defaultdict(list)

    def keys(self):
        return self.subst.keys()

    @staticmethod
    def disj_union(binds):
        subst = defaultdict(list)
        for b in binds:
            keys = list(b.keys())
            if DEBUG: print(keys, subst.keys())
            assert not any([k in subst for k in keys])
            subst.update(b.subst)
        return Bind(subst=subst)


    @staticmethod
    def multi_union(binds):
        b = binds[0]
        subst = defaultdict(list)

        for b in binds[1:]:
            keys = list(b.keys())
            if len(subst) > 0:
                assert len(keys) == sum([k in subst for k in keys])
            for k in keys:
                subst[k].extend(b.subst[k])
        return Bind(subst=subst)

    def __str__(self):
        res = str(self.subst)
        return res



class TryBind:
    #TODO: slot for the fields
    def __init__(self, o: 'obj', s: 'aos'):
        self.o = o #obj
        self.s = s #shape ! (shape)*
        #self.op = s.op

    #def len_match(self):
    #    return (len(self.o) == len(self.s.args))

    def build_matching_pairs(self):
        #only ordered (non-commutative) trials
        o = self.o
        # assert o is an iterator

        args: '(shape)*'

        if II(self.s, list):
            args = self.s
        else: args = self.s.args

        args_len = len(args)

        if len(o) < args_len:
            return BindError(f'build_matching_pairs: {self.o}, {args}')
        else:
            rest_o_len = len(o) - args_len


        tbs = [TryBind(o_, arg) for o_, arg in zip(o[:args_len-1], args[:-1])]
        #last arg binds to rest o sub-objects 
        rest_o = o[args_len-1:] if rest_o_len > 1 else o[-1]
        tb_last = TryBind(rest_o, args[-1])
        tbs.append(tb_last)
        return tbs

    def __repr__(self):
        return  f'{self.o} :-? {self.s}'
    def __str__(self):
        return  f'{self.o} :-? {self.s}'




def combine_binds (op, binds: '(Bind | BindError)*' ):
    err = list(filter(lambda x: II(x, BindError), binds))
    if len(err) > 0:
        return BindError(', '.join(err))

    if op == AOop.OR:
        res = Bind.disj_union(binds)
    elif op == AOop.AND:
        res = Bind.disj_union(binds)
    elif op == AOop.SEQUENCE:
        res = Bind.multi_union(binds)
    else:
        assert False, f'combine_binds: op = {op}'

    return res 

def split_try_bind(op, tb, obinder):
    if op == AOop.OR:
        res = obinder.bind_or(tb)
    elif op == AOop.AND:
        res = obinder.bind_and(tb)
    elif op == AOop.SEQUENCE:
        res = obinder.bind_star(tb)
    else:
        assert False, 'cant split op = {op}'

    res: 'list(TryBind) | BindErr'
    if DEBUG:
        print(f'> split_try_bind: {op}, {tb} \n\t  {res}')
    return res     

def try_bind (tb, obinder):
    op = tb.s.op
    if op is None: #terminal
        res: 'Bind ! BindErr' = obinder.bind_terminal(tb)
    else:
        #split tb
        tbs = split_try_bind(op, tb, obinder)
        if II(tbs, BindError): 
            return tbs
        # apply
        res = [try_bind(tb, obinder) for tb in tbs]
        res: '(Bind | BindError)*' 

        # combine
        res = combine_binds(op, res)
    if DEBUG: print(f'> try_bind: {tb}, {res}')    
    return res


'''

x :(ISIN | name | r1),  y : (name | r2)
y[ISIN] = y [(name & n* ) | ...], x[(name & n2*) | (ISIN & i*) | ...], n == n2 -> (n, i)*

'''










        
