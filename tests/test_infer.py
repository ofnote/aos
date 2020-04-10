from aos.infer import infer_aos
from aos.common import Config
import json, os

def get_data():
    return {
        'a': [
            { 
            'x': 1, 'y': 2
            },
            {
            'x': 3, 'y': 4

            },
            {
            'x': 5, 'y': 6

            }
        ]
    }

def infer_json(fname):
    if not os.path.exists(fname):
        return
    with open(fname) as f:
        d = json.load(f)
        r = infer_aos(d)
        print(fname)
        print (r)

def test():
    Config.pprint_treelike = False
    x = get_data()
    r = infer_aos(x)
    print(r)

    # data obtained by executing 'run.py' from
    # https://github.com/karpathy/covid-sanity
    infer_json('data/jall.json')
    #infer_json('data/search.json')
    infer_json('data/sim_tfidf_svm.json')
    






if __name__ == '__main__':
    test()
