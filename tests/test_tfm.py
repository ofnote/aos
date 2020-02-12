#from aos.tfm import do_tfm
from aos.parser import parse_aos
from aos.bind_matchers import bind_obj_shape
from aos.eval_aos import eval_aos_in_context
from aos.common import DEBUG

def parse_tfm(tfm: str):
    lhs, rhs = [x.strip() for x in tfm.split('->')]
    lhs = parse_aos(lhs)
    rhs = parse_aos(rhs)
    if DEBUG: print (lhs, rhs)
    return lhs, rhs

def do_tfm(obj, tfm: str):
    lhs, rhs = parse_tfm(tfm)
    context, err =  bind_obj_shape(obj, lhs)
    if err is not None:
        raise ValueError(err)
    if DEBUG: print ('bindings:', context)

    out, err = eval_aos_in_context(rhs, context)
    return out

def test1():
    d = {'items': [
            {'k': 1}, {'k': 2}, {'k': 3}
        ]}

    tfm = 'items & (k & v)* -> (v)*'

    d_ = do_tfm(d, tfm)
    print('result: ', d_)

def test2():
    '''
           records & ('fin_year' & year | gdb..prices & g | ...)* ->
                .records -> (.fin_year : (GDP..cr & .gdb..prices) )
                = 'year : (GDP..cr & int)'
    '''

    obj = {
        'records': [
                {
                    'fin_year' : 1997,
                    'price': 100
                },
                {
                    'fin_year': 2000,
                    'price': 200
                },
                {
                    'fin_year': 2010,
                    'price': 500
                }
            ]
    }

    tfm1 = '(records & ((fin_year & year) | (price & p))*) -> (year & (price & p))*'
    y = do_tfm(obj, tfm1)
    print (f'result: {y}')

    tfm2 = '(records & ((fin_year & year) | (price & p))*) -> (year : (price & p))'
    y = do_tfm(obj, tfm2)
    print (f'result: {y}')

if __name__ == '__main__':
    #test1()
    test2()


