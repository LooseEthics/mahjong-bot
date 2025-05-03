from __future__ import annotations
from common import *

class Shanten:
    def __init__(self, shanten: int = None, waits: list[int] = None, hand: list[int] = None):
        if hand is not None:
            kokushi = self._shanten_kokushi(hand)
            if kokushi.shanten <= 2:
                # 10+ unique terminals, this will be the best
                self.shanten = kokushi.shanten
                self.waits = kokushi.waits
                return
            chiitoi = self._shanten_chiitoi(hand)
            if chiitoi.shanten <= 1:
                # 5+ pairs, standard will be at least 3
                self.shanten = chiitoi.shanten
                self.waits = chiitoi.waits
                return
            standard = self._shanten_standard(hand)
            best = minimal_shanten_tuple(chiitoi, kokushi, standard)
            
            self.shanten = best.shanten
            self.waits = best.waits
        elif shanten is not None and waits is not None:
            self.shanten = shanten
            self.waits = waits
        else:
            print("Shanten class init failed")

    def __repr__(self) -> str:
        return f"{self.shanten} {self.waits}"

    def merge(self, other: Shanten) -> None:
        if self.shanten != other.shanten:
            print(f"Shanten.merge unequal shanten {self.shanten} != {other.shanten}")
            return
        self.waits = list(set(self.waits + other.waits))
    
    def _shanten_chiitoi(self, hand: list[int]) -> tuple[int, list[int]]:
        if len(hand) != 13 and len(hand) != 14:
            return Shanten(np.inf, [])
        
        pairs = 0
        waits = []
        for tile in set(hand):
            count = hand.count(tile)
            if count >= 2:
                pairs += 1
            else:
                waits.append(tile)
        
        return Shanten(6 - pairs, waits)

    def _shanten_kokushi(self, hand: list[int]) -> int:
        if len(hand) != 13 and len(hand) != 14:
            return Shanten(np.inf, [])
        
        unique_terminals = 0
        has_pair = False
        
        for tile in set(hand):
            if tile in KokushiTiles:
                unique_terminals += 1
                if hand.count(tile) >= 2:
                    has_pair = True
        
        return Shanten(13 - unique_terminals - (1 if has_pair else 0), KokushiTiles[:] if not has_pair else [t for t in KokushiTiles if t not in hand])

    def _shanten_standard(self, hand: list[int]) -> int:
        if len(hand) != 13 and len(hand) != 14:
            return Shanten(np.inf, [])
        
        min_shanten = 8  # maximum possible shanten for standard form
        waits = []
        
        # generate all valid groupings
        for grouping in self._generate_groupings(hand):
            complete_melds = 0
            taatsu = 0
            remaining_tiles = []
            
            for group in grouping:
                ## count complete melds
                if len(group) == 3:
                    if (group[0] == group[1] == group[2]) or \
                       (group[0]+1 == group[1] and group[1]+1 == group[2]):
                        complete_melds += 1
                ## count taatsu
                elif len(group) == 2:
                    if group[0] == group[1]:  ## pair
                        taatsu += 1
                    elif group[0] + 1 == group[1] or group[0] + 2 == group[1]:  ## ryanmen or kanchan
                        taatsu += 1
                elif len(group) == 1:
                    remaining_tiles.append(group[0])
            
            ## calculate shanten for this grouping
            current_shanten = 8 - 2*complete_melds - min(4 - complete_melds, taatsu)
            if current_shanten <= min_shanten:
                if current_shanten < min_shanten:
                    waits = []
                    
                min_shanten = current_shanten
                if min_shanten == 0:
                    break
                
                ## find waits
                for group in grouping:
                    if len(group) == 2:
                        if group[0] == group[1]:  ## pair - can become triplet
                            waits.append(group[0])
                        elif (group[0] // 9 == group[1] // 9) and group[0] // 9 < 3:  
                            diff = group[1] - group[0]
                            if diff == 1:  ## ryanmen
                                if group[0] % 9 > 0:
                                    waits.append(group[0] - 1)
                                if group[0] % 9 < 7:
                                    waits.append(group[0] + 2)
                            elif diff == 2:  ## kanchan
                                waits.append(group[0] + 1)

                for t in remaining_tiles:
                    ## can form a pair
                    waits.append(t)
                    ## can form a sequence
                    if t // 9 < 3:
                        v = t % 9
                        if v > 0:
                            waits.append(t - 1)
                            if v > 1:
                                waits.append(t - 2)
                        if v < 8:
                            waits.append(t + 1)
                            if v < 7:
                                waits.append(t + 2)
                
                waits = list(set(waits))
        
        return Shanten(min_shanten, waits)

    def _generate_groupings(self, tiles: list[int]) -> list[list[list[int]]]:
        # generate all possible tile groupings for shanten calc
        if not tiles:
            return [[]]
        
        groupings = []
        
        # Try forming triplets
        for i in range(len(tiles)):
            if i + 2 < len(tiles) and tiles[i] == tiles[i + 1] == tiles[i + 2]:
                remaining = tiles[:i] + tiles[i+3:]
                for group in self._generate_groupings(remaining):
                    groupings.append([[tiles[i]]*3] + group)
        
        # Try forming sequences (only for number tiles)
        unique_tiles = sorted(set(t for t in tiles if t < 27))  # Exclude honors
        for t in unique_tiles:
            if t + 1 in tiles and t + 2 in tiles and t//9 == (t + 1)//9 == (t + 2)//9:
                remaining = tiles.copy()
                remaining.remove(t)
                remaining.remove(t + 1)
                remaining.remove(t + 2)
                for group in self._generate_groupings(remaining):
                    groupings.append([[t, t+1, t+2]] + group)
        
        # Try pairs
        for i in range(len(tiles)):
            if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
                remaining = tiles[:i] + tiles[i + 2:]
                for group in self._generate_groupings(remaining):
                    groupings.append([[tiles[i]]*2] + group)
        
        # Single tiles
        if not groupings:
            groupings = [[[t]] for t in tiles]
        
        return groupings
        
    
def minimal_shanten_tuple(*shantens: Shanten) -> Shanten:
    ret = shantens[0]
    for t in shantens[1:]:
        if ret.shanten > t.shanten:
            ret = t
        elif ret.shanten == t.shanten:
            ret.merge(t)
    return ret
