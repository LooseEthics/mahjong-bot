# recurse_cnt

Calculates the number of possible hand selections from the mahjong tileset.

## Requirements

- **Compilation requires** the GNU Multiple Precision Arithmetic Library (`gmpxx.h`).

## Usage
recurse_cnt.exe [-np]
### Options
- `-np`  
  Sets leaf node weight to 1, calculating the number of ways to select 4 subsets of size 13 from a (0, 0, 0, 34) multiset.  
  *By default, the leaf weight is the number of permutations of the selection complement.*
