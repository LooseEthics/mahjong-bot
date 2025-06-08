
#include <gmpxx.h>

#include "multiset_math.h"

extern std::unordered_map<Key, mpz_class, KeyHash> memo;

int main(int argc, char* argv[]) {
    init_comb_table();
    init_fact_table();
    std::vector<int> super_vec = {0, 0, 0, 34};
    bool use_perm = true;

    for (int i = 1; i < argc; ++i) {
        if (std::string(argv[i]) == "-np") {
            use_perm = false;
            break;
        }
    }

/*
    std::vector<int> vec = firstv(4*13, 4);
    mpz_class total_subsets = 0;
    int cnt = 0;
    while (!vec.empty()) {
            if (vec_cnt(vec) <= univ_count){
            cnt++;
            mpz_class subsets = subset_num(vec, super_vec, true);
            total_subsets += subsets;
            std::cout << cnt << " " << to_sci_notation(subsets) << " " << vec << std::endl;
        }
        vec = nextv(vec);
    }
    std::cout << "Total subsets: " << to_sci_notation(total_subsets) << std::endl;
    return 0;
*/

    for (int depth = 1; depth <= 4; depth++){
      auto start = std::chrono::high_resolution_clock::now();
      mpz_class result = recurse_cnt_parallel_memoized(super_vec, depth, use_perm);
      auto end = std::chrono::high_resolution_clock::now();
      std::chrono::duration<double> elapsed = end - start;

      std::cout << depth << "-hand states: " << to_sci_notation(result) << " = " << result << std::endl;
      std::cout << "Elapsed time: " << elapsed.count() << " seconds" << std::endl;
      std::cout << "Memo size: " << memo.size() << std::endl;
    }
    return 0;
}
