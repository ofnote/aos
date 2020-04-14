from aos.infer import infer_aos
from aos.common import Config
import json, os

d1 = {
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

d2 = {
    "checked": False,
    "dimensions": {
        "width": 5,
        "height": 10
    },
    "id": 1,
    "name": "A green door",
    "price": 12.5,
    "tags": [
        "home",
        "green"
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
    Config.pprint_treelike = True
    r = infer_aos(d1)
    print(r)

    print(infer_aos(d2))
    # data obtained by executing 'run.py' from
    # https://github.com/karpathy/covid-sanity
    infer_json('data/jall.json')
    #infer_json('data/search.json')
    infer_json('data/sim_tfidf_svm.json')
    






if __name__ == '__main__':
    test()
