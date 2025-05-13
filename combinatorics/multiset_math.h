
#include <chrono>
#include <gmpxx.h>
#include <iostream>
#include <vector>

void init_comb_table();
void init_fact_table();
mpz_class recurse_cnt_parallel_memoized(const std::vector<int>& super_vec, int depth, bool use_perm);
std::string to_sci_notation(const mpz_class& num, int sig_digits = 4);
