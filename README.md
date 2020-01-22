![experimental](https://img.shields.io/badge/stability-experimental-orange.svg)

# And-Or Shape (aos) Language


Writing data pipelines involves doing complex data transformations over nested data, e.g., list of dictionaries or dictionary of tensors. 

- The **shape** of nested data is not explicit in code and hence not accessible readily to the developer.
- Leads to cognitive burden (guessing shapes), technical debt and inadvertent programming errors.
- Data pipelines are very opaque to examination and comprehension.

---

`aos` is a unified, compact language for describing the shapes of both homogeneous (tensors) and heterogeneous (dictionaries) data, and combinations, independent of the specific data library. 

* Based on a well-defined (Boolean-like) **algebra** of data shapes.

* Allows writing explicit data shapes, **inline** in code. In Python, use type annotations.

* Validate concrete data against `aos` shapes anywhere via **assertions**.

* Write shapes for a variety of data conveniently -- Python native objects, tensors (`numpy`,` pytorch`, `tf`), `pandas`,`hdf5`,`tiledb`,`xarray`,`struct-tensor`, etc.

  

### Shape of Data ?

- for scalar data, its shape is simply its type, e.g., `int`, ` float`, `str`, ...
- for nested data, eg.  list of `int`s:  `(int)*`
- for a dictionary of form `{'a': 3, b: 'hi'}` : shape is  `(a & int) | (b & str)`.

We can describe shape of arbitrary, nested data with these `&`(and)- `|`(or) expressions. A list is an `or`-structure, a dictionary is an `or` of `and`s, a tensor is an `and`-structure, and so on.

* Why is a `list` an or-structure? Think of how do we *access* a scalar value in the `list`. We need to pick **some** value from its indices to get to a value. 
* Similarly, a `dictionary` is an or-structure: pick **one** of its keys to access the *sub-tree* values.
* In contrast, an n-dimensional `tensor` has an `and`-shape: we must choose indices from *all* the dimensions of the tensor to *access* a scalar value. 
* In general, for a data structure, we *ask*: what are the access paths to get to a scalar value?

Thinking in terms of `and`-`or` shapes takes a bit of practice but proves to be very useful in making hidden shapes explicit. Read more about how to think in the and-or style [here](and-or-thinking.md).

#### `aos` Expressions

Lists over shape `s` are denoted as `(s)*`. 
Dictionary: `(k1 & v1) | (k2 & v2) | ... | (kn & vn)` where `ki` and `vi` is the `i`th key and value.

Pandas tables: `(n & (c1|c2|...|cn))` where `n` is the row dimension (the number of rows) and `c1,...,cn` are column names.

The `aos` expressions let you write object shapes very *compactly* . For example, consider a highly nested Python object `O` of type

 `Sequence[Tuple[Tuple[str, int], Dict[str, str]]]`  

 `O`'s `aos` is simply`((str|int)|(str : str))* `.

 Writing full shapes of data variables may get cumbersome. The language supports wildcards: `_` and `...` which represent a single dimension name or an arbitrary shape, respectively.

So, we could write a dictionary's shape as `(k1 & ...)| ... | (kn & ...)`.

### Shape Validation Examples

Using `aos.is_aos_shape`, we can write `aos` assertions to validate data shapes. 

* The language allows *lazy* shape specifications using placeholders:  `_` matches a scalar, `...` matches an arbitrary object.

```python
from aos import is_aos_shape

def test_pyobj():
    d = {'city': 'New York', 'country': 'USA'}
    t1 = ('Google', 2001)
    t2 = (t1, d)

    is_aos_shape(t2, '(str | int) | (str & str)')

    tlist = [('a', 1), ('b', 2)]
    is_aos_shape(tlist, '(str | int)*')
    is_aos_shape(tlist, '(_ | _)*')

    is_aos_shape(t2, '(_ | _) | (str & _)*')
    is_aos_shape(t2, '... | (str & _)')

    is_aos_shape(t2, '(_ | _) | (str & int)') #error

def test_pandas():
    d =  {'id': 'CS2_056', 'cost': 2, 'name': 'Tap'}
    df = pd.DataFrame([d.items()], columns=list(d.keys()) )

    is_aos_shape(df, '1 & (id | cost | name)')

def test_numpy():
    #arr = np.array()
    arr = np.array([[1,2,3],[4,5,6]]) 
    is_aos_shape(arr, '2 & 3')

def test_pytorch():
    #arr = np.array()
    arr = torch.tensor([[1,2,3],[4,5,6]])
    is_aos_shape(arr, '2 & 3')
```



### And-Or Shape Dimensions

The above examples of use type names (`str`) or integer values in shapes. A more principled approach is to first declare `dimension` names and define shape over these names. 

Data is defined over two broad types of dimensions

* Continuous Dimensions. Think of a range of values, e.g., a numpy array of shape (5, 200) is defined over two continuous dimensions, say `n` and `d`, where `n` ranges over values `0-4` and `d` ranges over `0-199`.
* Categorical Dimensions. A set of names, e.g., a dictionary `{'a': 4, 'b': 5}` is defined over names `['a', 'b']`. One can view each key, e.g., `a` or `b` as a Singleton dimension.



The library provides an API to declare both type of dimensions and `aos` expressions over these dimensions, e.g., `n & d`.



*Examples coming soon...*



