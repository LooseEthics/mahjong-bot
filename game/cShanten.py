from __future__ import annotations
from functools import lru_cache
from numpy import inf

from common import *

class Shanten:
    def __init__(self, shanten: int = None, waits: list[int] = None, riichi_discards: list[int] = None, hand: list[int] = None, drawn_tile: int = None):
        self.shanten = inf
        self.waits = []
        self.riichi_discards = []
        if hand is not None and drawn_tile is not None:
            kokushi = self._shanten_kokushi(hand)
            if kokushi.shanten <= 2:
                # 10+ unique terminals, this will be the best
                self.copy(kokushi)
                return
            chiitoi = self._shanten_chiitoi(hand)
            if chiitoi.shanten <= 1:
                # 5+ pairs, standard will be at least 3
                self.copy(chiitoi)
                return
            standard = _shanten_standard(tuple(hand))
            best = minimal_shanten_tuple(chiitoi, kokushi, standard)
            
            self.copy(best)
        elif shanten is not None and waits is not None and riichi_discards is not None:
            self.shanten = shanten
            self.waits = waits
            self.riichi_discards = riichi_discards
        else:
            print("Shanten class init failed")
            print(shanten is None, waits is None, riichi_discards is None, hand is None, drawn_tile is None)

    def __repr__(self) -> str:
        return f"s: {self.shanten}, w: {tilelist2tenhou(self.waits)}, rd: {tilelist2tenhou(self.riichi_discards)}"

    def merge(self, other: Shanten) -> None:
        if self.shanten != other.shanten:
            print(f"Shanten.merge unequal shanten {self.shanten} != {other.shanten}")
            return
        self.waits = list(set(self.waits + other.waits))
        self.riichi_discards = list(set(self.riichi_discards + other.riichi_discards))
    
    def copy(self, other: Shanten) -> None:
        self.shanten = other.shanten
        self.waits = other.waits
        self.other = other.riichi_discards
    
    def _shanten_chiitoi(self, hand: list[int]) -> tuple[int, list[int]]:
        if len(hand) != 13 and len(hand) != 14:
            return Shanten(shanten = inf, waits = [], riichi_discards = [])
        
        pairs = 0
        waits = []
        for tile in set(hand):
            count = hand.count(tile)
            if count >= 2:
                pairs += 1
            else:
                waits.append(tile)
        
        sh = 6 - pairs
        rd = []
        if sh == 1:
            for tile in set(hand):
                cnt = hand.count(tile)
                if cnt > 2:
                    rd = [tile]
                    break
                if cnt == 1:
                    rd.append(tile)
        
        return Shanten(6 - pairs, waits, rd)

    def _shanten_kokushi(self, hand: list[int]) -> int:
        if len(hand) != 13 and len(hand) != 14:
            return Shanten(shanten = inf, waits = [], riichi_discards = [])
        
        unique_terminals = 0
        has_pair = False
        
        rd = []
        for tile in set(hand):
            if tile in KokushiTiles:
                unique_terminals += 1
                if hand.count(tile) >= 2:
                    has_pair = True
            else:
                rd.append(tile)
                    
        sh = 13 - unique_terminals - (1 if has_pair else 0)
        if sh == 1:
            if len(rd) == 0:
                ## double pair or triple
                rd = [tile for tile in set(hand) if hand.count(tile) >= 2]
        else:
            rd = []
                
        return Shanten(shanten = sh, waits = list(KokushiTiles) if not has_pair else [t for t in KokushiTiles if t not in hand], riichi_discards = rd)

@lru_cache(maxsize=100000)
def _shanten_standard(hand: tuple[int]) -> int:
    if len(hand) != 13 and len(hand) != 14:
        return Shanten(shanten = inf, waits = [], riichi_discards = [])
    
    min_shanten = 8  # maximum possible shanten for standard form
    waits = []
    rd = []
    
    # generate all valid groupings
    for grouping in _generate_groupings_cached(tuple(hand)):
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
                rd = []
                
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
            
            ## riichi discards
            if min_shanten == 1:
                group_lengths = [len(group) for group in grouping]
                if 1 in group_lengths:
                    ## yojouhai or kuttsuki
                    for group in grouping:
                        if len(group) == 1:
                            rd += group
                else:
                    ## kanzenkei or atamanashi
                    1
    
    return Shanten(shanten = min_shanten, waits = waits, riichi_discards = rd)

@lru_cache(maxsize=100000)
def _generate_groupings_cached(tiles: tuple[int]) -> list[list[list[int]]]:
    # generate all possible tile groupings for shanten calc
    if not tiles:
        return [[]]
    
    groupings = []
    tiles = list(tiles)
    
    # Try forming triplets
    for i in range(len(tiles)):
        if i + 2 < len(tiles) and tiles[i] == tiles[i + 1] == tiles[i + 2]:
            remaining = tiles[:i] + tiles[i+3:]
            for group in _generate_groupings_cached(tuple(remaining)):
                groupings.append([[tiles[i]]*3] + group)
    
    # Try forming sequences (only for number tiles)
    unique_tiles = sorted(set(t for t in tiles if t < 27))  # Exclude honors
    for t in unique_tiles:
        if t + 1 in tiles and t + 2 in tiles and t//9 == (t + 1)//9 == (t + 2)//9:
            remaining = tiles.copy()
            remaining.remove(t)
            remaining.remove(t + 1)
            remaining.remove(t + 2)
            for group in _generate_groupings_cached(tuple(remaining)):
                groupings.append([[t, t+1, t+2]] + group)
    
    # Try pairs
    for i in range(len(tiles)):
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            remaining = tiles[:i] + tiles[i + 2:]
            for group in _generate_groupings_cached(tuple(remaining)):
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
