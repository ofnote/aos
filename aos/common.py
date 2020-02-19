

class OrVals(list):
    def __repr__(self):
        s = super().__repr__()
        return f'`{s}`'
    
DEBUG = True

