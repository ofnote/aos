import numpy as np
import sys
import tiledb

# Name of array.
array_name = "/tmp/quickstart_dense"

def create_array():
    # The array will be 4x4 with dimensions "d1" and "d2", with domain [1,4].
    dom = tiledb.Domain(tiledb.Dim(name="d1", domain=(1, 4), tile=4, dtype=np.int32),
                        tiledb.Dim(name="d2", domain=(1, 4), tile=4, dtype=np.int32))

    # The array will be dense with a single attribute "a" so each (i,j) cell can store an integer.
    schema = tiledb.ArraySchema(domain=dom, sparse=False,
                                attrs=[tiledb.Attr(name="a", dtype=np.int32)])

    # Create the (empty) array on disk.
    tiledb.DenseArray.create(array_name, schema)

def write_array():
    # Open the array and write to it.
    with tiledb.DenseArray(array_name, mode='w') as A:
        data = np.array(([1, 2, 3, 4],
                         [5, 6, 7, 8],
                         [9, 10, 11, 12],
                         [13, 14, 15, 16]))
        A[:] = data

def read_array():
    # Open the array and read from it.
    with tiledb.DenseArray(array_name, mode='r') as A:
        # Slice only rows 1, 2 and cols 2, 3, 4.
        data = A[1:3, 2:5]
        print(data["a"])

        sch = A.schema
        #print (sch.domain, sch.ndim, sch.)
        #print (sch.capacity)
        sch.dump()




array_name_sp = "/tmp/quickstart_sparse"

def create_array_sparse():
    # The array will be 4x4 with dimensions "d1" and "d2", with domain [1,4].
    dom = tiledb.Domain(tiledb.Dim(name="d1", domain=(1, 4), tile=4, dtype=np.int32),
                        tiledb.Dim(name="d2", domain=(1, 4), tile=4, dtype=np.int32))

    # The array will be sparse with a single attribute "a" so each (i,j) cell can store an integer.
    schema = tiledb.ArraySchema(domain=dom, sparse=True,
                                attrs=[tiledb.Attr(name="a", dtype=np.int32)])

    # Create the (empty) array on disk.
    tiledb.SparseArray.create(array_name_sp, schema)

def write_array_sparse():
    # Open the array and write to it.
    with tiledb.SparseArray(array_name_sp, mode='w') as A:
        # Write some simple data to cells (1, 1), (2, 4) and (2, 3).
        I, J = [1, 2, 2], [1, 4, 3]
        data = np.array(([1, 2, 3]))
        A[I, J] = data

def read_array_sparse():
    # Open the array and read from it.
    with tiledb.SparseArray(array_name_sp, mode='r') as A:
        # Slice only rows 1, 2 and cols 2, 3, 4.
        data = A[1:3, 2:5]
        a_vals = data["a"]
        for i, coord in enumerate(data["coords"]):
            print("Cell (%d, %d) has data %d" % (coord[0], coord[1], a_vals[i]))



if __name__ == '__main__':
    create_array()
    write_array()
    read_array()

    #create_array_sparse()
    #write_array_sparse()
    #read_array_sparse()







