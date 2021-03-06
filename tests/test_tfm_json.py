from aos.tfm import do_tfm


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

def test_jq ():
    #'[.[] | {message: .commit.message, name: .commit.committer.name, parents: [.parents[].html_url]}]'
    # 'https://api.github.com/repos/stedolan/jq/commits?per_page=5'
    from test_data import get_obj1
    obj = get_obj1()
    #tfm0 = 'commit & c@((message & m) | (committer & (name & n))) #bind intermediate?

    #tfm1 = 'commit & ((message & m) | (committer.name.n)) \
    #            -> ((message & m) | (name & n))'
    tfm1 = 'commit & ((message.m) | (committer.name.n)) \
                -> ((message.m) | (name.n))'

    tfm2 = ' (commit.((message.m) | (committer.name.n))) | \
             (parents & (html_url.hu)*) \
                -> ((message.m) | (name.n) | (parents.(hu)*))'

    #tfm1 = 'commit & (.message.m | .committer.name.n) -> ' 
    #tfm1 = 'commit & (message/m, committer/name/n) -> ' 
    #parse_tfm(tfm1)
    for t in [tfm1, tfm2]:
        y = do_tfm(obj, t)
        print (f'result: {y}')


if __name__ == '__main__':
    test1()
    test2()
    test_jq()


