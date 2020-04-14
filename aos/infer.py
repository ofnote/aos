from .aos import get_or_decl_dim, AOShape, AOop
from .utils import apply_match_t2a

class InferAOS():
    def __init__(self, max_list_items=10, simplify=True):
        self.max_list_items = max_list_items
        self.simplify = simplify

        self.type2action = {
            dict: self.for_dict,
            (list, tuple): self.for_list_tuple,
            (str, int, float, bool): self.for_scalar,
        }

    def for_dict(self, obj, **kwargs):
        res = []
        for k, v in obj.items():
            k_ = get_or_decl_dim(k)
            v_ = self.infer(v)
            kv = AOShape.build_from(AOop.AND, [k_, v_])
            res.append(kv)

        res = AOShape.build_from(AOop.OR, res)
        return res

    def for_list_tuple(self, obj, **kwargs):
        max_list_items = self.max_list_items

        if len(obj) > max_list_items:
            print (f'Warning: only observing {max_list_items}/{len(obj)} items in list!')
        args = [self.infer(v) for v in obj[:max_list_items]]
        res = AOShape.build_from(AOop.OR, args)

        if self.simplify:
            args_ = list(set(res.args))
            if len(args_) == 1:
                res = AOShape.build_from(AOop.SEQUENCE, args_)
            if len(args_) < len(res.args):
                print ('Suggestion: list aos can be potentially compressed')

        return res

    def for_scalar(self, obj, **kwargs):
        return get_or_decl_dim(type(obj).__name__)

    def default_func(self, obj, **kwargs):
        raise NotImplementedError(f'InferAOS : type = {type(obj), type(obj).__name__}')

    def infer(self, obj):
        return apply_match_t2a(self.type2action, obj, default=self.default_func)

def infer_aos (x, max_list_items=10, simplify=True):
    res = InferAOS(max_list_items, simplify).infer(x)

    return res




















