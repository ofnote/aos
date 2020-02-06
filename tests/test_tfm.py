#from aos.tfm import do_tfm
from aos.parser import parse_aos
from aos.bind_matchers import bind_obj_shape
from aos.eval_aos import eval_aos_in_context
from aos.common import DEBUG

def get_bindings(obj, shape: 'aos'):
    res =  bind_obj_shape(obj, shape)
    if DEBUG: print ('get bindings:', res)
    return res


def do_tfm(obj, tfm: str):
    lhs, rhs = [x.strip() for x in tfm.split('->')]
    lhs = parse_aos(lhs)
    rhs = parse_aos(rhs)

    if DEBUG: print (lhs, rhs)
    context, err = get_bindings(obj, lhs)
    if err is not None:
        raise ValueError(err)
    out, err = eval_aos_in_context(rhs, context)
    return out

def test1():
    d = {'items': [
            {'k': 1}, {'k': 2}, {'k': 3}
        ]}

    tfm = 'items & (k & v)* -> (v)*'

    d_ = do_tfm(d, tfm)
    print('result: ', d_)



if __name__ == '__main__':
    test1()


