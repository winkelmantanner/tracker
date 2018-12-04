import random
import time
import copy

import multiprocessing

NUM_ELEMENTS_TO_MAP = 1234
SIZE_OF_EACH_MAP_ELEMENT = 2345
MAX_DATUM_VALUE = 12345
MAX_NUM_THREADS = 10

def func2(arr):
    return [el ** 1.8 for el in arr]

if __name__ == "__main__":
    print("num_threads duration")
    data = [
        [
            random.randint(0, MAX_DATUM_VALUE) for j in range(SIZE_OF_EACH_MAP_ELEMENT)
        ] for k in range(NUM_ELEMENTS_TO_MAP)
    ]
    for num_threads in range(1, MAX_NUM_THREADS + 1):
        bigArr = copy.deepcopy(data)
        with multiprocessing.Pool(num_threads) as p:
            startTime = time.time()
            result = p.map(func2, bigArr)
            duration = time.time() - startTime
            print(str(num_threads) + " " + str(duration))
