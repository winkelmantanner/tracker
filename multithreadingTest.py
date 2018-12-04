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
    for num_threads in range(1, MAX_NUM_THREADS + 1):
        bigArr = copy.deepcopy(data)
        with multiprocessing.Pool(num_threads) as p:
            startTime = time.time()
            result = p.map(func2, bigArr)
            duration = time.time() - startTime
            print(str(num_threads) + " " + str(duration))
