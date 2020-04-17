from aos.checker import instanceof as aosii
from aos.tfm import do_tfm

from aos.common import Config
Config.DEBUG = False

# Spark
# https://docs.databricks.com/delta/data-transformation/complex-types.html
# https://databricks.com/blog/2017/02/23/working-complex-data-formats-structured-streaming-apache-spark-2-1.html
d1 = {
  "a": {
     "b": 1
  }
}

d2 = {
  "a": {
     "b": 1,
     "c": 2
  }
}

d3 = {
    "a": 1, "b": 2, "c": 3
}

d4 = {
    "a": [1, 2]
}

d5 = [{ "x": 1 }, { "x": 2 }]

d6 = [{ "x": 1, "y": "a" }, { "x": 2, "y": "b" }]

d7 = {
  "a": [
    {"b": 1},
    {"b": 2}
  ]
}

d8 = [{ "a": "x: 1" }, { "a": "y: 2" }]

def checks():
    aosii(d1, 'a.b.int')

def tfms():


    #select
    z = do_tfm(d1, 'a.b.v -> b.v') # {b: 1}
    print(z)

    z = do_tfm(d2, 'a & v -> v') #{b: 1, c: 2}
    print(z)

    z = do_tfm(d3, 'a & v -> x.y.v') #{x : {y: 1}}
    print(z)

    #do_tfm(d4, 'a & (v)* -> x & f(v)', f=lambda v: v[0]) #{ "x": 1 }
    #todo: basic expressions: x & v[0]

    z = do_tfm(d4, 'a & (v)* -> (x & v)* ') # [{ "x": 1 }, { "x": 2 }]
    print(z)

    z = do_tfm(d2, 'a & (k & v)* -> ((x.k) | (y.v))*') # [{ "x": "b", "y": 1 }, { "x": "c", "y": 2 }]
    print(z)


    z = do_tfm(d5, '(x & v)* -> x & (v)*') #{ "x": [1, 2] }
    print(z)


    #do_tfm(d6, '(x & v | z)* -> (z | (x & list(v))*)') #[{ "y": "a", "x": [1]}, { "y": "b", "x": [2]}]
    #simpler: x & (v)* ? overload (v)* accumulator as list constructor

    z = do_tfm(d7, 'a & (b & v)* -> (b & (v)*)') #{"b": [1, 2]}
    print(z)

    import re
    #do_tfm(d8, '(a & s)* -> (c & f(s))*', f=lambda s: re.search('([a-z]):', s).group(1)) 
    #[{ "c": "x" }, { "c": "y" }]





#TODO: COVID AWS Lake 
# https://aws.amazon.com/blogs/big-data/a-public-data-lake-for-analysis-of-covid-19-data/
# infer schema and perform transforms

if __name__ == '__main__':
    tfms()


