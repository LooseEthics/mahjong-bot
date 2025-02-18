
from random import shuffle, randrange

# open meld types
ANKAN = 0
PON = 1
CHII = 2
MINKAN = 3
SHOUMINKAN = 4
OMNames = {
    ANKAN: "Ankan",
    PON: "Pon",
    CHII: "Chii",
    MINKAN: "Minkan",
    SHOUMINKAN: "Shouminkan"
    }
WNames = ("East", "South", "West", "North")
TenhouStr = "mpsz"

def tilelist2tenhou(l):
    l = sorted(l)
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
        

class GameState():
    def __init__(self):
        self.random_start_state()
    
    def random_start_state(self):
        self.tiles = [i for i in range(34) for _ in range(4)]
        shuffle(self.tiles)
        self.hand_e = self.tiles[0:13].sort()
        self.hand_s = self.tiles[13:26].sort()
        self.hand_w = self.tiles[26:39].sort()
        self.hand_n = self.tiles[39:52].sort()
        self.hands = (self.hand_e, self.hand_s, self.hand_w, self.hand_n)
        self.open = [] # tuple (owner pid, target pid, type, tile)
        self.discard = [] # tuple (discarding pid, tile)
        self.riichi = [-1, -1, -1, -1] # -1 not in riichi, >=0 riichi declaration turn
        self.dead_wall = self.tiles[52:66] # dora 1-5, ura 1-5, kan draw 1-4
        self.live_wall = self.tiles[66:]
        self.round_wind = randrange(4)
        self.active_player = 0
        self.turn = 0
        self.kan_cnt = 0
        
    
class VisibleGameState():
    def __init__(self, gs: GameState, pid: int):
        self.pid = pid
        self.hand = gs.hands[pid]
        self.open = gs.open
        self.discard = gs.discard
        self.visible_dora = gs.dead_wall[10: 11 + gs.kan_cnt]
        
            

gs = GameState()
vgs = VisibleGameState(gs, 0)
print(tenhou2tilelist("234m234p"))
