
import time
import cProfile
from multiset_math_funcs import *
from concurrent.futures import ProcessPoolExecutor
from functools import partial

def process_vec_bound(v, super_vec, depth):
    return sum(recurse_cnt(s, depth - 1) for s in sub_vec(super_vec, v, 4))

def top_level_parallel(super_vec, depth):
    vecs = []
    vec = firstv(mc, deg)
    while vec is not None:
        vecs.append(vec.copy())
        vec = nextv(vec)

    bound_func = partial(process_vec_bound, super_vec=super_vec, depth=depth)
    with ProcessPoolExecutor() as executor:
        results = executor.map(bound_func, vecs)
    return sum(results)

#cProfile.run("recurse_cnt([0, 0, 0, 34], 1)")

#quit()
for i in range(1,5):
    start_time = time.time()
    result = recurse_cnt(np.array([0, 0, 0, 34]), i)
    #result = top_level_parallel(np.array([0, 0, 0, 34]), i)
    elapsed_time = time.time() - start_time
    
    formatted_result = f"{result:.3e}".replace("e", " ×10^")
    print(f"Recursion level {i}: {format(result, ',')}")
    print(f"Done in {elapsed_time:.6f} s")

#a = [tuple(x) for x in sub_vec([2,2,2,2], [2,1,0,0], 4)]
#print(a)
#print(list(set(a)))
