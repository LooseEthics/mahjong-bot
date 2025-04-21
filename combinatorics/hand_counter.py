
from multiset_math_funcs import *

vec = firstv(mc, deg)
cnt = 0
total_subsets = 0

while vec is not None:
    cnt += 1
    subsets = subset_num(vec)
    total_subsets += subsets
    print(cnt, vec, format(subsets, ','))
    subbed_1 = sub_1(vec, 1, 4)
    print(subbed_1)
    subbed = sub_vec(vec, np.array([0, 2, 0, 0]), 4)
    print(subbed)
    print("===")
    vec = nextv(vec)
print(f"Total subsets: {format(total_subsets, ',')}")
