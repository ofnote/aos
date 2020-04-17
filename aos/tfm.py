from aos.parser import parse_aos
from aos.bind_matchers import bind_obj_shape
from aos.eval_aos import eval_aos_in_context
from aos.common import Config, simplify_and2dict
DEBUG = Config.DEBUG

def parse_tfm(tfm: str):
    lhs, rhs = [x.strip() for x in tfm.split('->')]
    lhs = parse_aos(lhs)
    rhs = parse_aos(rhs)
    if DEBUG: print (lhs, rhs)
    return lhs, rhs

def do_tfm(obj, tfm: str):
    if DEBUG: print (f'\ntfm -> {tfm}, {obj}')
    lhs, rhs = parse_tfm(tfm)
    context, err =  bind_obj_shape(obj, lhs)
    if err is not None:
        raise ValueError(err)
    if DEBUG: print ('bindings:', context)
    #assert False

    out, err = eval_aos_in_context(rhs, context)
    #print('simplify_and2dict')
    out = simplify_and2dict(out)
    return out