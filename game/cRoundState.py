
from random import shuffle, randrange
from common import *
from cDiscard import Discard
from cOpenMeld import OpenMeld

class RoundState():
    def __init__(self):
        self.random_start_state()
    
    def random_start_state(self):
        self.turn = 0
        self.active_player = 0
        self.tiles = [i for i in range(34) for _ in range(4)]
        shuffle(self.tiles)
        self.hands = [sorted(self.tiles[i*13: (i+1)*13]) for i in range(4)]
        self.open = [] # OpenMeld instances
        self.discard = [] # Discard instances
        self.riichi = [-1, -1, -1, -1] # -1 not in riichi, >=0 riichi declaration turn
        self.dead_wall = self.tiles[52:66] # dora 1-5, ura 1-5, kan draw 1-4
        self.live_wall = self.tiles[66:]
        self.drawn_tile = -1
        self.game_running = True
        self.winner = []
    
    def __repr__(self):
        s =  f"Turn: {self.turn}\n"
        s += f"Active player: {WNames[self.active_player]}\n"
        s += f"Drawn tile: {onetile2tenhou(self.drawn_tile)}, ({self.drawn_tile})\n"
        s += f"Live wall: {tilelist2tenhou(self.live_wall, False)}\n"
        s += f"Player hands: \n"
        for i in range(4):
            s += f"  {WNames[i].ljust(5)} - {tilelist2tenhou(self.hands[i]).ljust(20)} {self.shanten(i)}\n"
        s += f"Discards: {self.discard}\n"
        s += f"Open melds: {self.open}\n"
        s += f"Riichi: {self.riichi}\n"
        s += f"Dora: {tilelist2tenhou(self.dead_wall[0:5], False)}\n"
        s += f"Ura:  {tilelist2tenhou(self.dead_wall[5:10], False)}\n"
        return s
    
    def kan_cnt(self) -> int:
        return sum(1 for m in self.open if m.type in Kans)
    
    def last_discard(self) -> int:
        return self.discard[-1].tile
        
    def player_can_pon(self, pid: int) -> bool:
        return pid != self.active_player and self.hands[pid].count(ldt) >= 2
    
    def who_can_pon(self) -> int:
        ldt = self.discard[-1].tile
        for pid in range(4):
            if player_can_pon(pid):
                return pid
        return -1
    
    def possible_chii_starts(self) -> list[int]:
        ldt = self.discard[-1].tile
        ldt_suit = ldt // 9
        ldt_val = ldt % 9
        hand = self.hands[self.active_player]
        out = []
        if ldt_suit < 3:
            if (ldt_val >= 2 and ldt - 1 in hand and ldt - 2 in hand):
                out.append(ldt - 2)
            if (ldt_val >= 1 and ldt_val <= 7 and ldt - 1 in hand and ldt + 1 in hand):
                out.append(ldt - 1)
            if (ldt_val <= 6 and ldt + 1 in hand and ldt + 2 in hand):
                out.append(ldt)
        return out
    
    def active_can_chii(self) -> int:
        if self.possible_chii_starts() != []:
            return self.active_player
        return -1
    
    def who_can_minkan(self) -> int:
        ldt = self.discard[-1].tile
        if self.kan_cnt() < 4:
            for pid in range(4):
                if pid != self.active_player and self.hands[pid].count(ldt) == 3 :
                    return pid
        return -1
    
    def active_can_ankan(self) -> bool:
        return self.hands[self.active_player].count(self.drawn_tile) == 3 and self.kan_cnt() < 4
    
    def active_can_shouminkan(self) -> bool:
        if self.kan_cnt() < 4:
            for m in self.open:
                if m.owner_pid == self.active_player and m.type == PON and m.tile == self.drawn_tile:
                    return True
        return False
    
    def open_hand(self, pid: int) -> list[int]:
        out = self.hands[pid].copy()
        for m in self.open:
            if m.owner_pid == pid:
                if m.type == CHII:
                    out += [m.tile, m.tile + 1, m.tile + 2]
                else:
                    # consider kans equivalent to pons for this
                    out += 3*[m.tile]
        if self.active_player == pid and self.drawn_tile != -1:
            out.append(self.drawn_tile)
        return sorted(out)
    
    def shanten(self, pid: int) -> int:
        # find minimal shanten
        hand = self.hands[pid].copy()
        if self.active_player == pid and self.drawn_tile != -1:
            hand.append(self.drawn_tile)
        
        # Check all possible shanten types
        kokushi = self._shanten_kokushi(hand)
        if kokushi <= 2:
            # 10+ unique terminals, this will be the best
            return kokushi
        chiitoi = self._shanten_chiitoi(hand)
        if chiitoi <= 1:
            # 5+ pairs, standard will be at least 3
            return chiitoi
        standard = self._shanten_standard(self.open_hand(pid))
        
        return min(chiitoi, kokushi, standard)
        
    def _shanten_chiitoi(self, hand: list[int]) -> int:
        if len(hand) != 13 and len(hand) != 14:
            return np.inf
        
        pairs = 0
        for tile in set(hand):
            count = hand.count(tile)
            if count >= 2:
                pairs += 1
        
        return 6 - pairs

    def _shanten_kokushi(self, hand: list[int]) -> int:
        if len(hand) != 13 and len(hand) != 14:
            return np.inf
        
        unique_terminals = 0
        has_pair = False
        
        for tile in set(hand):
            if tile in KokushiTiles:
                unique_terminals += 1
                if hand.count(tile) >= 2:
                    has_pair = True
        
        return 13 - unique_terminals - (1 if has_pair else 0)

    def _shanten_standard(self, hand: list[int]) -> int:
        if len(hand) != 13 and len(hand) != 14:
            return np.inf
        
        min_shanten = 8  # maximum possible shanten for standard form
        
        # generate all valid groupings
        for grouping in self._generate_groupings(hand):
            complete_melds = 0
            taatsu = 0
            remaining_tiles = []
            
            for group in grouping:
                # count complete melds
                if len(group) == 3:
                    if (group[0] == group[1] == group[2]) or \
                       (group[0]+1 == group[1] and group[1]+1 == group[2]):
                        complete_melds += 1
                # count taatsu
                elif len(group) == 2:
                    if group[0] == group[1]:  # pair
                        taatsu += 1
                    elif group[0] + 1 == group[1] or group[0] + 2 == group[1]:  # ryanmen or kanchan
                        taatsu += 1
                elif len(group) == 1:
                    remaining_tiles.append(group[0])
            
            # calculate shanten for this grouping
            current_shanten = 8 - 2*complete_melds - min(4 - complete_melds, taatsu)
            min_shanten = min(min_shanten, current_shanten)
            if min_shanten == 0:
                break
        
        return min_shanten

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
    
    def round_end(self, pidl: list[int]) -> None:
        self.game_running = False
        self.winner = pidl
    
    def action_draw(self) -> None:
        if self.live_wall:
            self.drawn_tile = self.live_wall.pop(0)
        else:
            ## ryuukyoku
            self.round_end([])
    
    def action_draw_kan(self) -> None:
        if len(self.dead_wall) > 10:
            self.drawn_tile = self.dead_wall.pop(10)
            ## TODO check suukaikan
        else:
            ## 5th kan draw illegal
            self.round_end([])
    
    def action_discard(self, tile: int) -> None:
        ## tile id, not position in hand
        if tile in self.hands[self.active_player]:
            self.hands[self.active_player].remove(tile)
            self.hands[self.active_player].append(self.drawn_tile)
        elif tile == self.drawn_tile:
            ## nothing here
            1
        else:
            print(f"{self.action_discard.__name__}: invalid discard")
            print(self.hands[self.active_player], tile)
            return
        
        self.discard.append(Discard(self.turn, self.active_player, tile))
        self.drawn_tile = -1
        self.active_player = (self.active_player + 1) % 4
        self.turn += 1
    
    def action_chii(self, start: int) -> None:
        ## sequence starting tile
        tile = self.last_discard()
        pid = self.active_player
        hand = self.hands[pid]
        if start == tile:
            hand.remove(start + 1)
            hand.remove(start + 2)
        elif start + 1 == tile:
            hand.remove(start)
            hand.remove(start + 1)
        else:
            hand.remove(start)
            hand.remove(start + 2)
        self.open.append(OpenMeld(pid, (pid - 1) % 4, CHII, start))
    
    def action_pon(self, pid: int) -> None:
        tile = self.last_discard()
        ## twice
        self.hands[pid].remove(tile)
        self.hands[pid].remove(tile)
        self.open.append(OpenMeld(pid, (self.active_player - 1) % 4, PON, tile))
        self.active_player = pid
    
    def action_ankan(self) -> None:
        tile = self.drawn_tile
        pid = self.active_player
        ## thrice
        self.hands[pid].remove(tile)
        self.hands[pid].remove(tile)
        self.hands[pid].remove(tile)
        self.open.append(OpenMeld(pid, -1, ANKAN, tile))
        self.drawn_tile = -1
    
    def action_minkan(self, pid: int) -> None:
        tile = self.last_discard()
        ## thrice
        self.hands[pid].remove(tile)
        self.hands[pid].remove(tile)
        self.hands[pid].remove(tile)
        self.open.append(OpenMeld(pid, (self.active_player - 1) % 4, MINKAN, tile))
        self.active_player = pid
    
    def action_shouminkan(self) -> None:
        for m in self.open:
            if m.owner_pid == self.active_player and m.tile == self.drawn_tile and m.type == PON:
                m.type = SHOUMINKAN
                self.drawn_tile = -1
                return
    
    def action_riichi(self) -> None:
        self.riichi[self.active_player] = self.turn
    
    def action_ron(self, pidl: list[int]) -> None:
        self.round_end(pidl)
    
    def action_tsumo(self) -> None:
        self.round_end([self.active_player])
    
