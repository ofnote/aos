
from .parser import parse_aos
from .bind import BindError, TryBind, try_bind
from .binders import PyObjBind

from .common import AndTuple, II, Config

DEBUG = Config.DEBUG

def instanceof(obj, shape):
    if isinstance(shape, str):
        shape = parse_aos(shape)
    
    if DEBUG:
        print (f'\nchecking {obj} against {shape}')

    tb = TryBind(obj, shape)
    res = try_bind(tb, PyObjBind())

    print (res)

    if II(res, BindError): 
        print('=== err ===')
        return False
    else:
        print('=== ok ====')

        return True


def test():
    from .parser import parse_aos

    d = {'city': 'New York', 'country': 'USA'}
    t1 = ('Google', 2001)
    t2 = (t1, d)

    s = parse_aos('(str | int) | ((str & str)*)')

    tb = TryBind(t2, s)
    res = try_bind(tb, PyObjBind())
    print(res)


if __name__ == '__main__':
    test()