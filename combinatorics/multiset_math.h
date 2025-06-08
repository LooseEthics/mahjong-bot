
#include <chrono>
#include <gmpxx.h>
#include <iostream>
#include <unordered_map>
#include <vector>

using Key = std::pair<std::vector<int>, int>;
struct KeyHash {
    size_t operator()(const Key& k) const {
        size_t seed = 0;
        for (int i : k.first) seed ^= std::hash<int>()(i) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
        seed ^= std::hash<int>()(k.second);
        return seed;
    }
};

void init_comb_table();
void init_fact_table();
mpz_class recurse_cnt_parallel_memoized(const std::vector<int>& super_vec, int depth, bool use_perm);
std::string to_sci_notation(const mpz_class& num, int sig_digits = 4);
