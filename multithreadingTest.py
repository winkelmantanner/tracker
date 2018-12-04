"""
This file contains a test of the multiprocessing module, which uses subprocesses as a workaround to the GIL.
"""


import random
import time
import copy

import multiprocessing

DATA_SIZE = 12345678
MAX_DATUM_VALUE = 12345
MAX_NUM_THREADS = 10

def func2(el):
    return el ** 1.8

if __name__ == "__main__":
    print("num_threads duration")
    data = [random.randint(0, MAX_DATUM_VALUE) for k in range(DATA_SIZE)]
    for num_threads in range(MAX_NUM_THREADS + 1):
        bigArr = copy.deepcopy(data)
        if num_threads == 0:
            startTime = time.time()
            result = [func2(el) for el in bigArr]
            duration = time.time() - startTime
            print("not_threaded" + " " + str(duration))
        else:
            with multiprocessing.Pool(num_threads) as p:
                startTime = time.time()
                result = p.map(func2, bigArr)
                duration = time.time() - startTime
                print(str(num_threads) + " " + str(duration))
