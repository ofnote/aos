#!/usr/bin/env python3

# https://github.com/erikrose/parsimonious
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
import sys

DEBUG = False
AOS_Grammar = Grammar(
        """
        main = aos / (lpar ws? aos ws? rpar)
        aos =  (term opterms)
        opterms = opterm*
        opterm = operator term
        term = (lpar aos rpar star?) / word
        operator = ws? (or / and / colon) ws?

        and    = '&'
        or     = '|'
        colon  = ':'
        star   = '*'

        word        = ~"\w+" / "..."
        number      = ~"\d+"
        lpar        = "("
        rpar        = ")"
        ws          = ~"\s*"

        """
)



from aos import get_or_decl_dim, AOShape

class AosVisitor(NodeVisitor):

    def __init__(self):
        self.depth = 0
        self.par_expr = []

    def visit_main(self, node, visited_children):
        cnt = len(visited_children)
        assert cnt == 1
        assert isinstance(visited_children, list), f'{visited_children}'
        res = visited_children[0]
        if isinstance(res, list):
                res = res[2]
        return res

    def visit_aos(self, node, visited_children):
        if DEBUG: print ('visit_aos\n:', visited_children)
        term, (op, terms) = visited_children
        #print ('aos: op\n',op)
        #print (term)
        #print (terms)
        if op is None:
            assert len(terms) == 0
            return term
        else:
            return (op, [term] + terms)


    def visit_term(self, node, visited_children):
        #res = build_aos_term (op, args)
        cnt = len(visited_children)
        if cnt == 1: 
            assert isinstance(visited_children, list), f'{visited_children}'
            child = visited_children[0]
            if isinstance(child, list):
                if DEBUG: print (f'--- term: {child}, {len(child)}')
                _, aos, _, star = child

                #TODO: is there a better way to handle optional args
                if isinstance(star, list):
                    star = star[0]
                else: star = None
                
                if star is None:
                    res = aos
                else:
                    res = (star, aos)
            else:
                res = child

            #if DEBUG: print (f'>>term is {res}, len {len(res)}')

        else:
            assert False, f'cnt = {cnt}'

        return res

    def visit_opterms(self, node, visited_children):
        #print (len(visited_children))
        #print(visited_children[0])
        res = []
        op = None

        for c in visited_children: #opterm
            op1, term = c
            if DEBUG:
                print ('opterms: op\n',op)
                print ('term\n',term)
            #print (term.text)
            if op is None: op = op1
            else: 
                assert op == op1, f'op={op}, op1={op1}'

            res.append( term )
        #if op is not None: op = str(op)
        return (op, res)

    def visit_opterm(self, node, visited_children):
        op, term = visited_children
        return visited_children

    def visit_operator(self, node, visited_children):
        assert len(visited_children) == 3
        _, op, _ = visited_children
        #print (f'operator: \n{op}')
        #print (visited_children)
        #res =  AosVisitor.optext2op[op.text]
        return op[0]

    def visit_word(self, node, visited_children):
        return sys.intern(node.text)

    def visit_and(self, node, visited_children):
        return node.text
    def visit_or(self, node, visited_children):
        return node.text
    def visit_colon(self, node, visited_children):
        return '&'
    def visit_star(self, node, visited_children):
        return node.text

    def visit_lpar(self, node, visited_children):
        self.depth += 1

    def visit_rpar(self, node, visited_children):
        self.depth -= 1

    def generic_visit(self, node, visited_children):
        if DEBUG: print (f'gen visit: {node.expr_name}')
        #assert False
        if visited_children:
            if DEBUG: print (f'gen visit cnt: {len(visited_children)}')
            return visited_children
        else: return node




def build_aos (prefix_rep):
    if isinstance(prefix_rep, str):
        if DEBUG: print (f'build_aos: str -- {prefix_rep}')

        res: 'aoshape' = get_or_decl_dim(prefix_rep)
    elif isinstance(prefix_rep, tuple):
        op, arg = prefix_rep
        if DEBUG: print (f'build_aos: {op} -- {arg}')
        aos: 'X' = build_aos(arg)
        if isinstance(aos, AOShape): aos = [aos]
        else: assert isinstance(aos, list), aos

        aos: 'List[aoshape]'

        if op is None:
            assert len(aos) == 1
            res: 'aoshape' = aos[0]
        else:
            res: 'aoshape' = AOShape.build_from(op, aos)

    elif isinstance(prefix_rep, list):
        if DEBUG: print (f'build_aos: list -- {prefix_rep}')

        res: 'List[aoshape]' = [build_aos(arg) for arg in prefix_rep]


    return res



def test_grammar():
    global AOS_Grammar
    def grma(s):
        tree = AOS_Grammar.parse(s)


    grma("((a | b | k) & c & d)")
    grma("(a | b | k) & c & d")
    grma("(a : (b|c) )")

    grma("a & ((b|c) & d)")
    grma("b:int | c:str")
    grma('(c1 | c2)*')


def parse_aos(aos_str):
    global AOS_Grammar
    tree = AOS_Grammar.parse(aos_str)
    if DEBUG: print (tree)
    res = (AosVisitor().visit(tree))
    if DEBUG: print ('visited:', res)
    res = build_aos(res)
    return res


def test_all():
    examples = [
        'a',
        'c1 | c2',
        'n & (c1 | c2 | c3)',
        'b & c & h & w',
        '((a | b | k) & c & d)',
        "a & ((b|c) & d)",
        "a : (b|c)",
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

































