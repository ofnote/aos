from aos.parser import AOS_Grammar, parse_aos

def test_grammar():
    global AOS_Grammar
    def grma(s):
        tree = AOS_Grammar.parse(s)
        #print(tree)


    grma("((a | b | k) & c & d)")
    grma("(a | b | k) & c & d")
    grma("(a : (b|c) )")
    grma("((a.b.c) | d)")

    grma("a & ((b|c) & d)")
    grma("b:int | c:str")
    grma('(c1 | c2)*')



def test_all():
    examples = [
        'a',
        'c1 | c2',
        'n & (c1 | c2 | c3)',
        'b & c & h & w',
        '((a | b | k) & c & d)',
        "a & ((b|c) & d)",
        "a : (b|c)",
        "(a.c.d) | f",
        "(b:int) | (c:str)",
        '(c1 | c2)*'

    ]
    for e in examples[:]:
        print (f'--->> trying {e}')
        res = parse_aos(e)
        print ('build_aos: ', res)

if __name__ == '__main__':
    DEBUG = False
    test_grammar()
    test_all()

