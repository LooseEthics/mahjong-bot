
#include <iostream>
#include <vector>

std::vector<int> legal_chii{1, 1, 1, 1, 1, 1, 0, 0,  1, 1, 1, 1, 1, 1, 0, 0,  1, 1, 1, 1, 1, 1, 0, 0,  0, 0, 0, 0,  0, 0, 0};
std::vector<int> meld_vec{0, 0, 0, 0, 0};
std::vector<int> result(34, 0);

std::ostream& operator<<(std::ostream& os, const std::vector<int>& vec) {
    os << "[";
    for (std::size_t i = 0; i < vec.size(); ++i) {
        os << vec[i];
        if (i + 1 < vec.size()) os << ", ";
    }
    os << "]";
    return os;
}

void next_meld_vec(std::vector<int> &meld_vec){
  bool carry = 1;
  for (int i = 0; i < 5; i++){
    if (carry){
      meld_vec[i] = (meld_vec[i] + 1) % 34;
      carry = meld_vec[i] == 0 ? 1 : 0;
    }
  }
}

void hand_vec(std::vector<int> &meld_vec, int pon_mask, std::vector<int> &result){
  result = std::vector<int>(34, 0);
  for (int i = 0; i < 4; i++){

  }
}

int main(){
  return 0;
  while (true){
    std::cout << meld_vec << std::endl;
    next_meld_vec(meld_vec);

  }
}
