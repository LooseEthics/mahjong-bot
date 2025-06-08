
import numpy as np
from numba import njit

univ_count = 34
mc = 15
deg = 4

from math import comb
comb_table = [[comb(n, k) for k in range(n + 1)] for n in range(35)]

def fast_comb(n, k):
    if k > n:
        return 0
    return comb_table[n][k]

def firstv(mc, deg):
    return np.array([mc] + (deg - 1) * [0], dtype=np.int32)

@njit
def cardinality(vec):
    return np.sum(np.arange(1, len(vec) + 1) * vec)

def nextv(vec):
    n = len(vec)
    weights = np.arange(1, n + 1)
    cum_card = np.cumsum(weights * vec)

    for i in range(n - 1):
        c = cum_card[i]
        if c > i + 1:
            return np.concatenate([
                firstv(c - i - 2, i + 1),
                [vec[i + 1] + 1],
                vec[i + 2:]
            ])

def kappa(a = 1, b = -1, vec = None):
    if vec is None:
        return 0
    ai = a - 1
    bi = b - 1 if b >= a else len(vec)
    return np.sum(vec[ai:bi])

def subset_num(vec, super_vec = (0, 0, 0, 34)):
    tot = 1
    deg = len(vec)
    for i in range(deg):
        tot *= fast_comb(kappa(a = i + 1, vec = super_vec) - kappa(a = i + 2, vec = vec), vec[i])
    return tot

def sub_1(vec, deg, max_deg, subbed_mask = None):
    if subbed_mask is None:
        subbed_mask = np.zeros_like(vec)
    out = []
    for i in range(deg, max_deg + 1):
        if i >= len(vec):
            break
        if vec[i] > 0 and vec[i] > subbed_mask[i]:
            app = vec.copy()
            app[i] -= 1
            if i > deg and (i - deg - 1) >= 0:
                app[i - deg - 1] += 1
            out.append(app)
    return out

@njit
def vec_cnt(vec):
    return np.sum(vec)

@njit
def lowest_pos(vec):
    nonzero = np.nonzero(vec > 0)[0]
    return nonzero[0] if nonzero.size > 0 else -1

def sub_vec(vec, to_sub, max_deg, subbed_mask = None):
    
    #print(f"calling sub_vec with {vec}({type(vec)}), {to_sub}({type(to_sub)}), {max_deg}, {sub_vec.calls}")
    if subbed_mask is None:
        subbed_mask = np.zeros_like(vec)

    subbed = sub_1(vec, lowest_pos(to_sub), max_deg, subbed_mask)
    
    if vec_cnt(to_sub) > 1:
        to_sub_next = to_sub.copy()
        to_sub_next[lowest_pos(to_sub)] -= 1

        out = []
        for sub in subbed:
            mask_diff = vec != sub
            subbed_mask_next = subbed_mask + mask_diff.astype(int)
            out.extend(sub_vec(sub, to_sub_next, max_deg, subbed_mask_next))

        out_unique = np.unique(np.array(out), axis=0)
        return out_unique
    else:
        return np.array(subbed)

def recurse_cnt(super_vec, depth):
    #print((4 - depth) * "  " + f"called recurse_cnt with {super_vec}, {depth}")
    if depth == 0:
        return subset_num(super_vec)
    cnt = 0
    vec = firstv(mc, deg)
    while vec is not None:
        #print(vec)
        subbed = sub_vec(super_vec, vec, 4)
        for s in subbed:
            #print(" ", s, recurse_cnt(s, depth - 1))
            cnt += recurse_cnt(s, depth - 1)
        vec = nextv(vec)
    return cnt

