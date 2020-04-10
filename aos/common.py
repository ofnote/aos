from types import SimpleNamespace

class OrVals(list):
    def __repr__(self):
        s = super().__repr__()
        return f'`{s}`'
    

config = dict(
    pprint_treelike=False, 
    DEBUG=True
)
Config = SimpleNamespace(**config)