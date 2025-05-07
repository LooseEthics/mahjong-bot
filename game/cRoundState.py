
import pickle
from random import shuffle, randrange

from common import *
from cDiscard import Discard
from cOpenMeld import OpenMeld
from cShanten import Shanten

class RoundState():
    def __init__(self, init_type: str = "random", **kwargs):
        if init_type == "random":
            self.random_start_state()
        elif init_type == "load":
            self.load(kwargs["fname"])
    
    def random_start_state(self):
        self.turn = 1
        self.active_player = 0
        self.tiles = [i for i in range(34) for _ in range(4)]
        shuffle(self.tiles)
        self.hands = [sorted(self.tiles[i*13: (i+1)*13]) for i in range(4)]
        self.open = [] # OpenMeld instances
        self.discard = [] # Discard instances
        self.riichi = [INVALID_ROUND, INVALID_ROUND, INVALID_ROUND, INVALID_ROUND] # -1 not in riichi, >=0 riichi declaration turn
        self.dead_wall = self.tiles[52:66] # dora 1-5, ura 1-5, kan draw 1-4
        self.live_wall = self.tiles[66:]
        self.drawn_tile = INVALID_TILE
        self.game_running = True
        self.winner = []
        self.game_state_str = "Ongoing"
        self.predraw = True
    
    def load(self, fname: str):
        with open(fname, "rb") as f:
            state = pickle.load(f)
            self.__dict__.update(state)

    def save(self, fname: str):
        with open(fname, "wb") as f:
            pickle.dump(self.__dict__, f)
    
    def __repr__(self):
        s =  f"Turn: {self.turn}\n"
        s += f"Active player: {WNames[self.active_player]}\n"
        s += f"Drawn tile: {onetile2tenhou(self.drawn_tile)}, ({self.drawn_tile})\n"
        s += f"Live wall: {tilelist2tenhou(self.live_wall, False)}\n"
        s += f"Player hands: \n"
        for i in range(4):
            s += f"  {WNames[i].ljust(5)} - {tilelist2tenhou(self.hands[i]).ljust(20)}\n{10*' '}{self.shanten(i)}\n"
        s += f"Discards: {self.discard}\n"
        s += f"Open melds: {self.open}\n"
        s += f"Riichi: {self.riichi}\n"
        s += f"Dora: {tilelist2tenhou(self.dead_wall[0:5], False)}\n"
        s += f"Ura:  {tilelist2tenhou(self.dead_wall[5:10], False)}\n"
        s += f"Kan draws:  {tilelist2tenhou(self.dead_wall[10:], False)}\n"
        return s
    
    def kan_cnt(self) -> int:
        return sum(1 for m in self.open if m.type in Kans)
    
    def last_discard(self) -> int:
        return self.discard[-1].tile
        
    def player_can_pon(self, pid: int) -> bool:
        return pid != (self.active_player - 1) % 4 and self.hands[pid].count(self.last_discard()) >= 2
    
    def who_can_pon(self) -> int:
        for pid in range(4):
            if self.player_can_pon(pid):
                return pid
        return INVALID_PLAYER
    
    def possible_chii_starts(self) -> list[int]:
        ldt = self.last_discard()
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
        return INVALID_PLAYER
    
    def player_can_minkan(self, pid: int) -> bool:
        ldt = self.last_discard()
        return self.kan_cnt() < 4 and pid != self.active_player and self.hands[pid].count(ldt) == 3
    
    def who_can_minkan(self) -> int:
        for pid in range(4):
            if player_can_minkan(pid):
                return pid
        return INVALID_PLAYER
    
    def active_can_ankan(self) -> bool:
        return self.hands[self.active_player].count(self.drawn_tile) == 3 and self.kan_cnt() < 4
    
    def active_can_shouminkan(self) -> bool:
        if self.kan_cnt() < 4:
            for m in self.open:
                if m.owner_pid == self.active_player and m.type == PON and m.tile == self.drawn_tile:
                    return True
        return False
    
    def active_can_kyuushuu_kyuuhai(self) -> bool:
        return self.turn <= 4 and len(self.open) == 0 and len([t for t in KokushiTiles if t in self.hands[self.active_player]]) >= 9
    
    def action_kyuushuu_kyuuhai(self):
        g.round.round_end([], "Kyuushuu Kyuuhai")
    
    def open_hand(self, pid: int) -> list[int]:
        out = self.hands[pid].copy()
        for m in self.open:
            if m.owner_pid == pid:
                if m.type == CHII:
                    out += [m.tile, m.tile + 1, m.tile + 2]
                else:
                    # consider kans equivalent to pons for this
                    out += 3*[m.tile]
        return sorted(out)
                
    
    def shanten(self, pid: int, on_call: bool = False) -> Shanten:
        # find minimal shanten
        shanten_tile = INVALID_TILE
        if self.active_player == pid and self.drawn_tile != INVALID_TILE:
            shanten_tile = self.drawn_tile
        elif on_call:
            shanten_tile = self.last_discard()
        
        return Shanten(hand = self.open_hand(pid), drawn_tile = shanten_tile)

    def round_end(self, pidl: list[int], state_str: str = "Ended") -> None:
        self.game_running = False
        self.winner = pidl
        self.game_state_str = state_str
    
    def action_draw(self) -> None:
        if self.live_wall:
            self.drawn_tile = self.live_wall.pop(0)
        else:
            ## ryuukyoku
            self.round_end([], "Ryuukyoku")
    
    def get_kan_owners(self) -> list[int]:
        out = []
        for m in self.open:
            if m.type in (ANKAN, MINKAN, SHOUMINKAN):
                out.append(m.owner_pid)
        return out
    
    def action_draw_kan(self) -> None:
        if len(self.dead_wall) > 10:
            self.drawn_tile = self.dead_wall.pop(10)
            kan_owners = self.get_kan_owners
            if len(kan_owners) >= 4:
                if kan_owners[0] != kan_owners[1] or kan_owners[0] != kan_owners[2] or kan_owners[0] != kan_owners[3]:
                    ## suukaikan
                    self.round_end([], "Suukaikan")
    
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
        if self.trigger_suufon_renda():
            self.round_end([], "Suufon Renda")
        self.drawn_tile = INVALID_TILE
        self.active_player = (self.active_player + 1) % 4
        self.turn += 1
    
    def trigger_suufon_renda(self):
        return self.turn == 4 and self.discard[0].tile in range(28, 32) and
            self.discard[0].tile == self.discard[1].tile and
            self.discard[0].tile == self.discard[2].tile and
            self.discard[0].tile == self.discard[3].tile
    
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
            hand.remove(start + 2)
        else:
            hand.remove(start)
            hand.remove(start + 1)
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
        self.open.append(OpenMeld(pid, INVALID_PLAYER, ANKAN, tile))
        self.drawn_tile = INVALID_TILE
    
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
                self.drawn_tile = INVALID_TILE
                return
    
    def action_riichi(self) -> None:
        self.riichi[self.active_player] = self.turn
        for r in self.riichi:
            if r == INVALID_TURN:
                return
        self.round_end([], "Suucha Riichi")
    
    def action_ron(self, pidl: list[int]) -> None:
        self.round_end(pidl, f"Ron {pidl} on {self.discard[-1].owner_pid}")
    
    def action_tsumo(self) -> None:
        self.round_end([self.active_player], f"Tsumo {self.active_player}")
    
    def player_in_furiten(self, pid: int, shanten: Shanten = None) -> bool:
        if shanten is None:
            shanten = self.shanten(pid, on_call = (self.drawn_tile == INVALID_TILE))
        for t in shanten.waits:
            if t in self.player_discard_list(pid):
                return True
        return False
        
    def player_discard_list(self, pid: int) -> list[int]:
        lst = []
        for d in self.discard:
            if d.owner_pid == pid and d.tile not in lst:
                lst.append(d.tile)
        return lst
    
    def get_valid_moves(self, pid: int) -> list[str]:
        valid_moves = []
        shanten = self.shanten(pid, on_call = (self.drawn_tile == INVALID_TILE))
        if self.predraw:
            ## predraw
            ldt = self.last_discard()
            if self.player_can_pon(pid):
                valid_moves.append(f"p{onetile2tenhou(ldt)}") ## pon
                if self.player_can_minkan(pid):
                    valid_moves.append(f"m{onetile2tenhou(ldt)}") ## minkan
            if pid == self.active_player and self.active_can_chii():
                for t in self.possible_chii_starts():
                    valid_moves.append(f"c{onetile2tenhou(t)}") ## chii
            if shanten.shanten == TENPAI and not self.player_in_furiten(pid, shanten):
                valid_moves.append(f"R{onetile2tenhou(ldt)}") ## ron
            if valid_moves != []:
                valid_moves.append("x") ## no call
        else:
            ## postdraw
            dt = self.drawn_tile
            if self.riichi[pid] == INVALID_TURN:
                if self.shanten(pid).shanten == IISHANTEN:
                    for t in shanten.riichi_discards():
                        valid_moves.append(f"r{onetile2tenhou(t)}") ## riichi discard
                for t in set(self.hands[pid]):
                    valid_moves.append(f"d{onetile2tenhou(t)}") ## normal discards
            if self.drawn_tile not in self.hands[pid] or self.riichi[pid] != INVALID_TURN:
                valid_moves.append(f"d{onetile2tenhou(dt)}") ## drawn tile discard
            if self.active_can_ankan():
                valid_moves.append(f"a{onetile2tenhou(dt)}") ## ankan
            if self.active_can_shouminkan():
                valid_moves.append(f"s{onetile2tenhou(dt)}") ## shouminkan
            if shanten.shanten == 0:
                valid_moves.append(f"T{onetile2tenhou(dt)}") ## tsumo
        return valid_moves
    
    def do_action(self, action: str = "x"):
        if not action:
            return
        action_type = action[0]
        tile = tenhou2onetile(action[1:])
        if action_type == "x":
            return
        elif action_type == "d":
            if tile == INVALID_TILE:
                self.action_discard(self.drawn_tile)
            else:
                self.action_discard(tile)
        elif action_type == "r":
            self.action_riichi()
            if tile == INVALID_TILE:
                self.action_discard(self.drawn_tile)
            else:
                self.action_discard(tile)
        elif action_type == "c":
            self.action_chii(tile)
        elif action_type == "p":
            self.action_pon(self.who_can_pon())
        elif action_type == "a":
            self.action_ankan()
        elif action_type == "s":
            self.action_shouminkan()
        elif action_type == "m":
            self.action_minkan(self.who_can_minkan())
        elif action_type == "T":
            self.action_tsumo()
        elif action_type == "R":
            ron_list = [int(x) for x in action[1:]]
            self.action_ron(ron_list)
        elif action == "kk":
            self.action_kyuushuu_kyuuhai()
