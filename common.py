
from random import shuffle, randrange

# open meld types
ANKAN = 0
PON = 1
CHII = 2
MINKAN = 3
SHOUMINKAN = 4
Kans = (ANKAN, MINKAN, SHOUMINKAN)
OMNames = {
    ANKAN: "Ankan",
    PON: "Pon",
    CHII: "Chii",
    MINKAN: "Minkan",
    SHOUMINKAN: "Shouminkan"
    }
WNames = ("East", "South", "West", "North")
TenhouStr = "mpsz"
KokushiTiles = (0, 8, 9, 17, 18, 26, 27, 28, 29, 30, 31, 32, 33)

def tilelist2tenhou(l, sort = True):
    l = sorted(l) if sort else l
    s = ""
    csuit = -1
    nsuit = -1
    for t in l:
        nsuit = t // 9
        if csuit != nsuit:
            if csuit > -1:
                s += TenhouStr[csuit]
            csuit = nsuit
        s += str((t % 9) + 1)
    s += TenhouStr[csuit]
    return s

def tenhou2tilelist(s):
    l = []
    back = 0
    for x in s:
        if x >= "1" and x <= "9":
            l.append(int(x) - 1)
            back += 1
        else:
            suit_num = TenhouStr.index(x)
            for i in range(len(l) - back, len(l)):
                l[i] += suit_num * 9
            back = 0
    return l

def lstsub(lst1, lst2):
    out = lst1[:]
    for x in lst2:
        out.remove(x)
    return out

class OpenMeld():
    def __init__(self, opid, tpid, meld_type, tile):
        self.owner_pid = opid
        self.target_pid = tpid
        self.type = meld_type
        self.tile = tile
    
    def __iter__(self):
        return iter((self.owner_pid, self.target_pid, self.type, self.tile))
    
    def __str__(self):
        s = f"{OMNames[self.type]}, O: {WNames[self.owner_pid]}, T: {WNames[self.target_pid]}, Tiles: "
        if self.type == CHII:
            s += tilelist2tenhou([self.tile, self.tile + 1, self.tile + 2])
        elif self.type == PON:
            s += tilelist2tenhou(3*[self.tile])
        else:
            s += tilelist2tenhou(4*[self.tile])
        return s

class Discard():
    def __init__(self, turn, opid, tile):
        self.turn = turn
        self.owner_pid = opid
        self.tile = tile
    
    def __iter__(self):
        return iter((self.turn, self.owner_pid, self.tile))
    
    def __str__(self):
        return f"Discard, Turn: {self.turn}, Owner: {WNames[self.owner_pid]}, Tile: {tilelist2tenhou([self.tile])}"
   

class GameState():
    def __init__(self):
        self.round_wind = 0
        self.round_num = 0
        self.honba = 0
        self.scores = (25000, 25000, 25000, 25000)
        self.init_round()
    
    def init_round(self):
        self.round = RoundState()
        self.players = [PlayerState(self.round, i) for i in range(4)]
    
    def __repr__(self):
        s =  f"Game state: {WNames[self.round_wind]} {self.round_num}, Honba {self.honba}\n"
        s += f"  Scores: {self.scores}"
        return s
    

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
    
    def __repr__(self):
        s =  f"Turn: {self.turn}\n"
        s += f"Live wall: {tilelist2tenhou(self.live_wall, False)}\n"
        s += f"Player hands: \n"
        for i in range(4):
            s += f"  {WNames[i].ljust(5)} - {tilelist2tenhou(self.hands[i])}\n"
        s += f"Discards: {self.discard}\n"
        s += f"Open melds: {self.open}\n"
        s += f"Riichi: {self.riichi}\n"
        s += f"Dora: {tilelist2tenhou(self.dead_wall[0:5], False)}\n"
        s += f"Ura:  {tilelist2tenhou(self.dead_wall[5:10], False)}\n"
        return s
    
    def kan_cnt(self):
        return sum(1 for m in self.open if m.type in Kans)
    
    def last_discard(self):
        return self.discard[-1].tile
    
    def who_can_pon(self):
        ldt = self.discard[-1].tile
        for pid in range(4):
            if pid != self.active_player and self.hands[pid].count(ldt) >= 2:
                return pid
        return -1
    
    def who_can_chii(self):
        ldt = self.discard[-1].tile
        ldt_suit = ldt // 9
        ldt_val = ldt % 9
        hand = self.hands[self.active_player]
        if ldt_suit < 3 and (
            (ldt_val >= 2 and ldt - 1 in hand and ldt - 2 in hand) or
            (ldt_val >= 1 and ldt_val <= 7 and ldt - 1 in hand and ldt + 1 in hand) or
            (ldt_val <= 6 and ldt + 1 in hand and ldt + 2 in hand)
        ):
            return self.active_player
        return -1
    
    def who_can_minkan(self):
        ldt = self.discard[-1].tile
        if self.kan_cnt < 4:
            for pid in range(4):
                if pid != self.active_player and self.hands[pid].count(ldt) == 3 :
                    return pid
        return -1
    
    def who_can_ankan(self):
        if self.hands[self.active_player].count(self.drawn_tile) == 3 and self.kan_cnt < 4:
            return self.active_player
        return -1
    
    def who_can_shouminkan(self):
        if self.kan_cnt < 4:
            for m in self.open:
                if m.owner_pid == self.active_player and m.type == PON and m.tile == self.drawn_tile:
                    return self.active_player
        return -1
    
    def who_has_tenpai(self):
        # get chiitoi and kokushi shanten, explore breadth first with remaining tiles up to shanten depth
        pass
    
    def shanten(self, pid):
        shanten_depth = min(self.shanten_chiitoi(pid), self.shanten_kokushi(pid))
        hand = self.hands[pid]
        
        # remove full melds
        trips = [tile for tile in set(hand) if hand.count(x) >= 3]
        for tile in trips:
            hand = lstsub(hand, [tile]*3)
        while True:
            seq = -1
            for tile in hand:
                if (tile % 9) < 7 and tile + 1 in hand and tile + 2 in hand:
                    seq = x
                    break
            if seq >= 0:
                hand.remove(seq)
                hand.remove(seq + 1)
                hand.remove(seq + 2)
            else:
                break
        
        # remove taatsu
        # TODO
    
    def shanten_chiitoi(self, pid):
        hand = self.hands[pid]
        if len(hand) < 13:
            return np.inf
        pairs = 0
        for tile in set(hand):
            if hand.count(tile) >= 2:
                pairs += 1
        return 6 - pairs
    
    def shanten_kokushi(self, pid):
        hand = self.hands[pid]
        if len(hand) < 13:
            return np.inf
        has_pair = False
        terminals = 0
        for tile in KokushiTiles:
            if tile in hand:
                terminals += 1
                if hand.count(tile) > 1:
                    has_pair = True
        return 13 - terminals - (1 if has_pair else 0)
    
    def action_draw(self):
        self.drawn_tile = self.live_wall.pop(0)
    
    def action_draw_kan(self):
        self.drawn_tile = self.dead_wall.pop(10)
    
    def action_discard(self, tile):
        # tile id, not position in hand
        self.hands[self.active_player].remove(tile)
        self.hands[self.active_player].append(self.drawn_tile)
        self.discard.append(Discard(self.turn, self.active_player, tile))
        self.drawn_tile = -1
        self.active_player = (self.active_player + 1) % 4
        self.turn += 1
    
    def action_chii(self, start):
        # starting tile
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
    
    def action_pon(self, pid):
        tile = self.last_discard()
        # twice
        self.hands[pid].remove(tile)
        self.hands[pid].remove(tile)
        self.open.append(OpenMeld(pid, (self.active_player - 1) % 4, PON, tile))
        self.active_player = pid
    
    def action_ankan(self):
        tile = self.drawn_tile
        pid = self.active_player
        # thrice
        self.hands[pid].remove(tile)
        self.hands[pid].remove(tile)
        self.hands[pid].remove(tile)
        self.open.append(OpenMeld(pid, -1, ANKAN, tile))
        self.drawn_tile = -1
    
    def action_minkan(self, pid):
        tile = self.last_discard()
        # thrice
        self.hands[pid].remove(tile)
        self.hands[pid].remove(tile)
        self.hands[pid].remove(tile)
        self.open.append(OpenMeld(pid, (self.active_player - 1) % 4, MINKAN, tile))
        self.active_player = pid
    
    def action_shouminkan(self):
        pass
    
    def action_riichi(self):
        pass
    
    def action_ron(self):
        pass
    
    def action_tsumo(self):
        pass
    
    
class PlayerState():
    def __init__(self, rs: RoundState, pid: int):
        self.pid = pid
        self.rs = rs
        self.hand = rs.hands[pid]
        self.open = rs.open
        self.discard = rs.discard
        self.riichi = rs.riichi


g = GameState()
g.init_round()
print(g.round)
