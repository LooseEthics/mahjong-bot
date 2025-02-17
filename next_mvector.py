
from scipy.special import comb

univ_count = 34
mc = 13
deg = 4

def firstv(mc, deg):
    return [mc] + (deg - 1)*[0]

def cardinality(vec):
    out = 0
    for i in range(len(vec)):
        out += (i + 1)*vec[i]
    return out

def nextv(vec):
    out = None
    for i in range(len(vec) - 1):
        c = cardinality(vec[:i + 1])
        if c > i + 1:
            return firstv(c - i - 2, i + 1) + [vec[i + 1] + 1] + vec[i + 2:]

def kappa(a = 1, b = -1, vec = None):
    if vec is None:
        return 0
    ai = a - 1
    bi = b - 1 if b >= a else len(vec)
    out = 0
    for i in range(ai, bi):
        out += vec[i]
    return out

def hand_num(vec, super_vec = (0, 0, 0, 34)):
    tot = 1
    deg = len(vec)
    for i in range(deg):
        tot *= comb(kappa(a = i + 1, vec = super_vec) - kappa(a = i + 2, vec = vec), vec[i], exact = True)
    return tot

vec = firstv(mc, deg)
cnt = 1
total_subsets = 0
print(cnt, vec)
while (vec := nextv(vec)) is not None:
    cnt += 1
    subsets = hand_num(vec)
    total_subsets += subsets
    print(cnt, vec, format(subsets, ','))
print(f"Total subsets: {format(total_subsets, ',')}")
