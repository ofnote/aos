![experimental](https://img.shields.io/badge/stability-experimental-orange.svg)

# And-Or Shape (aos) Language


Writing data pipelines involves complex data transformations over nested data, e.g., list of dictionaries or dictionary of tensors. 

- The *shape* of nested data is not explicit in code and hence not accessible readily to the developer.
- Leads to cognitive burden (guessing shapes), technical debt and inadvertent programming errors.
- Data pipelines are very opaque to examination and comprehension.

---

`aos` is a compact, regex-like language for describing the shapes (schemas) of both homogeneous (tensors) and heterogeneous (dictionaries, tables) data, and combinations, independent of the specific data library. 

* Based on an intuitive **regex-like** algebra of data shapes.
* **Infer** `aos` shape from a data instance: `aos.infer.infer_aos`.
* **Validate** data against `aos` shapes anywhere: `aos.checker.instanceof`.
* **Transform** data using `aos` shapes, declaratively: `aos.tfm.do_tfm`.
* Allows writing explicit data shapes, **inline** in code. In Python, use type annotations.
* Write shapes for a variety of data conveniently -- Python native objects (`dict`, `list`, scalars), tensors (`numpy`,` pytorch`, `tf`), `pandas`,`hdf5`,`tiledb`,`xarray`,`struct-tensor`, etc.

### Installation

```pip install aos```

## Shape of Data ?

Consider a few quick examples.

- the shape of scalar data is simply its type, e.g., `int`, ` float`, `str`, ...
- for nested data, eg.  list of `int`s:  `(int)*`
- for a dictionary of form `{'a': 3, b: 'hi'}` : shape is  `(a & int) | (b & str)`.

Now, we can describe the shape of *arbitrary, nested* data with these `&`(and)- `|`(or) expressions. Intuitively, a list is an `or`-structure, a dictionary is an `or` of `and`s, a tensor is an `and`-structure, and so on.

* Why is a `list` an or-structure? Ask: how do we *access* any value `v` in the `list`? Choose **some** index of the list, corresponding to the value `v`. 
* Similarly, a `dictionary` is an or-and structure: we pick **one** of the *key*s, together (**and**) with its *value*.
* In contrast, an n-dimensional `tensor` has an `and`-shape: we must choose indices from *all* the dimensions of the tensor to access a scalar value. 
* In general, for a data structure, we *ask*: what choices must we make to access a scalar value?

Thinking in terms of `and`-`or` shapes takes a bit of practice initially. Read more about the and-or expressions [here](docs/and-or-thinking.md).

#### More complex `aos` examples

* Lists over shape `s` are denoted as `(s)*`.  Shorthand for `(s|..|s)`.
* Dictionary: `(k1 & v1) | (k2 & v2) | ... | (kn & vn)` where `ki` and `vi` is the `i`th key and value.
* Pandas tables: `(n & ( (c1&int)| (c2&str) | ... | (cn&str) )` where `n` is the row dimension (the number of rows) and `c1,...,cn` are column names.

The `aos` expressions are very *compact*. For example, consider a highly nested Python object `X` of type

 `Sequence[Tuple[Tuple[str, int], Dict[str, str]]]`  

This is both verbose and hard to interpret. Instead, `X`'s `aos` is written compactly as
 `((str|int) | (str : str))* `.

> The full data shape may be irrelevant in many cases. To keep it brief, the language supports wildcards: `_` and `...` to allow writing partial shapes. 
>
> So, we could write a dictionary's shape as `(k1 & ...)| ... | (kn & ...)`.



## Shape Inference

Unearthing the shape of opaque data instances, e.g., returned from a web request, or passed into a function call, is a major pain. 

* Use `aos.infer.infer_aos` to obtain compact shapes of arbitrary data instances.
* From command line, run `aos-infer <filename.json>`

```python
from aos.infer import infer_aos

def test_infer():

  d = {
      "checked": False,
      "dimensions": { "width": 5, "height": 10},
      "id": 1,
      "name": "A green door",
      "price": 12.5,
      "tags": ["home","green"]
  }

  infer_aos(d) 

  # ((checked & bool) 
  # | (dimensions & ((width & int) | (height & int)))
  # | (id & int) | (name & str) | (price & float) | (tags & (str *)))
  
  dlist = []
  for i in range(100):
      d['id'] = i
      dlist.append(d.copy())
      
  infer_aos(dlist) 

  # ((checked & bool) 
  # | (dimensions & ((width & int) | (height & int)))
  # | (id & int) | (name & str) | (price & float) | (tags & (str *)))*


```



## Shape/Schema Validation

Using `aos.checker.instanceof`, we can 

* write `aos` assertions to validate data shapes (schemas). 
* validate data structure partially using placeholders:  `_` matches a scalar, `...` matches an arbitrary object (sub-tree).
* works with python objects, pandas, numpy, ..., extensible to other data types (libraries).

```python
from aos.checker import instanceof

def test_pyobj():
    d = {'city': 'New York', 'country': 'USA'}
    t1 = ('Google', 2001)
    t2 = (t1, d)

    instanceof(t2, '(str | int) | (str & str)') #valid
    instanceof(t2, '... | (str & _)') #valid
    instanceof(t2, '(_ | _) | (str & int)') #error
    
    tlist = [('a', 1), ('b', 2)]
    instanceof(tlist, '(str | int)*') #valid

def test_pandas():
    d =  {'id': 'CS2_056', 'cost': 2, 'name': 'Tap'}
    df = pd.DataFrame([d.items()], columns=list(d.keys()) )

    instanceof(df, '1 & (id | cost | name)')

def test_numpy():
    #arr = np.array()
    arr = np.array([[1,2,3],[4,5,6]]) 
    instanceof(arr, '2 & 3')

def test_pytorch():
    #arr = np.array()
    arr = torch.tensor([[1,2,3],[4,5,6]])
    instanceof(arr, '2 & 3')
```



## Transformations with AOS

Because `aos` expressions can both *match* and *specify* heterogeneous data shapes, we can write `aos` **rules** to **transform** data. 

The rules are written as `lhs -> rhs`, where both `lhs` and `rhs` are `aos` expressions:

* `lhs` *matches* a part (sub-tree) of the input data instance *I*. 
* `query` variables in the `lhs` *capture* (bind with) parts of *I*.
* `rhs` specifies the expected shape (aos) of the output data instance *O*.

To write rules, ask: which *parts* of *I*, do we need to construct *O* ?

```python
from aos.tfm import do_tfm
def tfm_example():
    # input data
    I = {'items': [{'k': 1}, {'k': 2}, {'k': 3}],
        'names': ['A', 'B', 'C']}

    # specify transformation (left aos -> right aos)
    # using `query` variables `k` and `v`
    
    # here `k` binds with each of the keys in the list and 
    # `v` binds with the corresponding value
    # the `lhs` automatically ignores parts of I, which are irrelevant to O
    
    tfm = 'items & (k & v)* -> values & (v)*'

    O = do_tfm(I, tfm)
    print(O) # {'values': [1, 2, 3]}
```



The above example illustrates a simple JSON transformation using `aos` rules. Rules can be more complex, e.g., include *conditions*, *function* application on query variables. They work not only with JSON data, but also apply to heterogeneous nested objects.

See more examples [here](tests/test_tfm_json.py) and [here](tests/test_tfm_spark_json.py). 



## And-Or Shape Dimensions

The above examples of use strings or type names (`str`) or integer values (`2`,`3`) in shape expressions. A more principled approach is to first declare **dimension names** and define shape over these names. 

Data is defined over two kinds of dimensions:

* **Continuous**. A range of values, e.g., a numpy array of shape (5, 200) is defined over two continuous dimensions, say `n` and `d`, where `n` ranges over values `0-4` and `d` ranges over `0-199`.
* **Categorical**. A set of names, e.g., a dictionary `{'a': 4, 'b': 5}` is defined over *keys*  (dim names) `['a', 'b']`. One can also view each key, e.g., `a` or `b` , as a **Singleton** dimension.



**Programmatic API**. The library provides an API to declare both type of dimensions and `aos` expressions over these dimensions, e.g., declare `n` and `d` as two continuous dimensions and then define shape `n & d`.



## Status

*The library is under active development. More documentation coming soon..*



