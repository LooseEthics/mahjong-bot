#include <algorithm>
#include <array>
#include <iomanip>
#include <mutex>
#include <numeric>
#include <ostream>
#include <sstream>
#include <thread>
#include <unordered_map>

#include "multiset_math.h"

constexpr int univ_count = 34;
constexpr int mc = 13;
constexpr int deg = 4;
constexpr int comb_table_size = 4*34 + 1;

// Precomputed combination table
std::array<std::array<mpz_class, comb_table_size>, comb_table_size> comb_table;
std::array<mpz_class, comb_table_size> fact_table;

void init_comb_table() {
    for (int n = 0; n < comb_table_size; ++n) {
        comb_table[n][0] = 1;
        for (int k = 1; k <= n; ++k) {
            comb_table[n][k] = comb_table[n - 1][k - 1] + comb_table[n - 1][k];
        }
    }
}

void init_fact_table() {
  mpz_class f = 1;
  for (int i = 0; i < comb_table_size; i++){
    fact_table[i] = f;
    f *= i + 1;
    //std::cout << "f" << i << "=" << fact_table[i] << std::endl;
  }
}

std::ostream& operator<<(std::ostream& os, const std::vector<int>& vec) {
    os << "[";
    for (std::size_t i = 0; i < vec.size(); ++i) {
        os << vec[i];
        if (i + 1 < vec.size()) os << ", ";
    }
    os << "]";
    return os;
}

mpz_class fast_comb(int n, int k) {
    mpz_class ret;
    if (k > n) ret = 0;
    ret = comb_table[n][k];
    //std::cout << n << " c " << k << " = " << ret << std::endl;
    return ret;
}

std::vector<int> firstv(int mc, int deg) {
    std::vector<int> vec(deg, 0);
    vec[0] = mc;
    return vec;
}

int cardinality(const std::vector<int>& vec) {
    int sum = 0;
    for (size_t i = 0; i < vec.size(); ++i)
        sum += (i + 1) * vec[i];
    return sum;
}

std::vector<int> nextv(const std::vector<int>& vec) {
    int n = vec.size();
    std::vector<int> weights(n), cum_card(n);
    std::iota(weights.begin(), weights.end(), 1);
    for (int i = 0; i < n; ++i)
        cum_card[i] = weights[i] * vec[i] + (i > 0 ? cum_card[i - 1] : 0);

    for (int i = 0; i < n - 1; ++i) {
        if (cum_card[i] > i + 1) {
            std::vector<int> new_vec = firstv(cum_card[i] - i - 2, i + 1);
            new_vec.push_back(vec[i + 1] + 1);
            new_vec.insert(new_vec.end(), vec.begin() + i + 2, vec.end());
            return new_vec;
        }
    }
    return {};
}

int kappa(int a, int b, const std::vector<int>& vec) {
    if (vec.empty()) return 0;
    int ai = a - 1;
    int bi = (b >= a) ? b - 1 : vec.size();
    return std::accumulate(vec.begin() + ai, vec.begin() + bi, 0);
}

inline mpz_class mpz_pow(const mpz_class& base, unsigned long exp) {
    mpz_class result;
    mpz_pow_ui(result.get_mpz_t(), base.get_mpz_t(), exp);
    return result;
}

mpz_class mul_perm(const std::vector<int>& vec){
    mpz_class div = 1;
    for (unsigned int i = 0; i < vec.size(); i++){
        div *= mpz_pow(fact_table[i + 1], vec[i]);
    }
    mpz_class result = fact_table[cardinality(vec)]/div;
    //std::cout << fact_table[cardinality(vec)] << " / " << div << " = " << result << std::endl;
    //std::cout << cardinality(vec) << "! / " << div << " = " << result << std::endl;
    return result;
}


mpz_class subset_num(const std::vector<int>& vec, const std::vector<int>& super_vec = {0, 0, 0, 34}, bool use_perm = false) {
    mpz_class tot = 1;
    int deg = vec.size();
    for (int i = 0; i < deg; ++i) {
        int n = kappa(i + 1, -1, super_vec) - kappa(i + 2, -1, vec);
        tot *= fast_comb(n, vec[i]);
        //std::cout << "tot is " << tot << std::endl;
    }
    if (use_perm){
        tot *= mul_perm(vec);
        //std::cout << "tot is " << tot << std::endl;
    }
    return tot;
}

std::vector<std::vector<int>> sub_1(const std::vector<int>& vec, unsigned int deg, unsigned int max_deg, const std::vector<int>& subbed_mask) {
    std::vector<std::vector<int>> out;
    for (unsigned int i = deg; i <= max_deg && i < vec.size(); ++i) {
        if (vec[i] > 0 && vec[i] > subbed_mask[i]) {
            std::vector<int> app = vec;
            app[i] -= 1;
            if (i > deg && (i - deg - 1) >= 0)
                app[i - deg - 1] += 1;
            out.push_back(app);
        }
    }
    return out;
}

int vec_cnt(const std::vector<int>& vec) {
    return std::accumulate(vec.begin(), vec.end(), 0);
}

int lowest_pos(const std::vector<int>& vec) {
    for (unsigned int i = 0; i < vec.size(); ++i) {
        if (vec[i] > 0)
            return i;
    }
    return -1;
}

std::vector<std::vector<int>> sub_vec(
    const std::vector<int>& vec,
    const std::vector<int>& to_sub,
    int max_deg,
    std::vector<int> subbed_mask = {}) {

    if (subbed_mask.empty()) subbed_mask.resize(vec.size(), 0);

    int low = lowest_pos(to_sub);
    auto subbed = sub_1(vec, low, max_deg, subbed_mask);

    if (vec_cnt(to_sub) > 1) {
        std::vector<int> to_sub_next = to_sub;
        to_sub_next[low] -= 1;

        std::vector<std::vector<int>> out;
        for (const auto& sub : subbed) {
            std::vector<int> mask_diff(vec.size(), 0);
            for (unsigned int i = 0; i < vec.size(); ++i) {
                if (vec[i] != sub[i]) mask_diff[i] = 1;
            }
            std::vector<int> subbed_mask_next = subbed_mask;
            for (unsigned int i = 0; i < vec.size(); ++i)
                subbed_mask_next[i] += mask_diff[i];

            auto recursed = sub_vec(sub, to_sub_next, max_deg, subbed_mask_next);
            out.insert(out.end(), recursed.begin(), recursed.end());
        }

        // Remove duplicates
        std::sort(out.begin(), out.end());
        out.erase(std::unique(out.begin(), out.end()), out.end());
        return out;
    }
    return subbed;
}

using Key = std::pair<std::vector<int>, int>;
struct KeyHash {
    size_t operator()(const Key& k) const {
        size_t seed = 0;
        for (int i : k.first) seed ^= std::hash<int>()(i) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
        seed ^= std::hash<int>()(k.second);
        return seed;
    }
};

std::unordered_map<Key, mpz_class, KeyHash> memo;
std::mutex memo_mutex;

mpz_class recurse_cnt_memo(const std::vector<int>& super_vec, int depth, bool use_perm) {
    Key key{super_vec, depth};

    {
        std::lock_guard<std::mutex> lock(memo_mutex);
        auto it = memo.find(key);
        if (it != memo.end()) return it->second;
    }

    if (depth == 0) {
        mpz_class val = subset_num(super_vec, {0, 0, 0, 34}, use_perm);
        std::lock_guard<std::mutex> lock(memo_mutex);
        return memo[key] = val;
    }

    mpz_class cnt = 0;
    std::vector<int> vec = firstv(mc, deg);
    while (!vec.empty()) {
        auto subbed = sub_vec(super_vec, vec, 4);
        for (const auto& s : subbed) {
            cnt += recurse_cnt_memo(s, depth - 1, use_perm);
        }
        vec = nextv(vec);
    }

    cnt /= depth;
    std::lock_guard<std::mutex> lock(memo_mutex);
    return memo[key] = cnt;
}

mpz_class recurse_cnt_parallel_memoized(const std::vector<int>& super_vec, int depth, bool use_perm) {
    std::vector<std::thread> threads;
    std::mutex mtx;
    mpz_class total = 0;

    std::vector<int> vec = firstv(mc, deg);
    std::vector<std::vector<int>> to_process;

    while (!vec.empty()) {
        to_process.push_back(vec);
        vec = nextv(vec);
    }

    int n_threads = std::thread::hardware_concurrency();
    size_t chunk_size = (to_process.size() + n_threads - 1) / n_threads;

    for (int i = 0; i < n_threads; ++i) {
        threads.emplace_back([&, i]() {
            mpz_class local = 0;
            for (size_t j = i * chunk_size; j < std::min(to_process.size(), (i + 1) * chunk_size); ++j) {
                const auto& vec = to_process[j];
                auto subbed = sub_vec(super_vec, vec, 4);
                for (const auto& s : subbed) {
                    local += recurse_cnt_memo(s, depth - 1, use_perm);
                }
            }
            std::lock_guard<std::mutex> lock(mtx);
            total += local;
        });
    }

    for (auto& t : threads) t.join();
    return total/depth;
}

std::string to_sci_notation(const mpz_class& num, int sig_digits) {
    std::string str = num.get_str();
    int len = str.length();

    if (len <= sig_digits) {
        return str;
    }

    std::ostringstream oss;
    oss << str[0];
    if (sig_digits > 1) {
        oss << "." << str.substr(1, sig_digits - 1);
    }
    oss << "*10^" << (len - 1);
    return oss.str();
}
