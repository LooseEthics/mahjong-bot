
import pickle
from random import shuffle, randint

from common import *
from cDiscard import Discard
from cMeld import Meld
from cShanten import Shanten
from cVisibleState import VisibleState

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
        self.open = [Meld(INVALID_PLAYER, INVALID_PLAYER, INVALID_MELD, INVALID_TILE, INVALID_TURN) for _ in range(4*4)] # OpenMeld instances
        self.discard = [Discard(INVALID_TURN, INVALID_PLAYER, INVALID_TILE) for _ in range(88)] # Discard instances
        self.riichi = [INVALID_ROUND, INVALID_ROUND, INVALID_ROUND, INVALID_ROUND] # -1 not in riichi, >=0 riichi declaration turn
        self.dead_wall = self.tiles[52:66] # dora 1-5, ura 1-5, kan draw 1-4
        self.live_wall = self.tiles[66:]
        self.live_wall_index = 0
        self.drawn_tile = INVALID_TILE
        self.winner = []
        self.game_state = GS_ONGOING
        self.game_state_str = "Ongoing"
        self.predraw = True
        self.agari = INVALID_TILE
        self.round_wind = randint(0, 3)
    
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
        s += f"Discards: {[d for d in self.discard if d.turn != INVALID_TURN]}\n"
        s += f"Open melds: {[m for m in self.open if m.type != INVALID_MELD]}\n"
        s += f"Riichi: {self.riichi}\n"
        s += f"Dora: {tilelist2tenhou(self.dead_wall[0:5], False)}\n"
        s += f"Ura:  {tilelist2tenhou(self.dead_wall[5:10], False)}\n"
        s += f"Kan draws:  {tilelist2tenhou(self.dead_wall[10:], False)}\n"
        return s
    
    def kan_cnt(self) -> int:
        return sum(1 for m in self.open if m.type in Kans)
    
    def next_open_index(self) -> int:
        return sum(1 for m in self.open if m.type != INVALID_MELD)
    
    def last_discard(self) -> Discard:
        return self.discard[self.turn - 2]
    
    def ldt(self) -> int:
        return self.last_discard().tile
        
    def player_can_pon(self, pid: int) -> bool:
        return pid != (self.active_player - 1) % 4 and self.hands[pid].count(self.ldt()) >= 2
    
    def who_can_pon(self) -> int:
        for pid in range(4):
            if self.player_can_pon(pid):
                return pid
        return INVALID_PLAYER
    
    def possible_chii_starts(self) -> list[int]:
        ldt = self.ldt()
        ldt_suit = ldt // 9
        ldt_val = ldt % 9
        hand = self.hands[self.active_player]
        out = []
        print("possible chii starts", hand, ldt)
        if ldt_suit < 3:
            if (ldt_val >= 2 and ldt - 1 in hand and ldt - 2 in hand):
                out.append(ldt - 2)
            if (ldt_val >= 1 and ldt_val <= 7 and ldt - 1 in hand and ldt + 1 in hand):
                out.append(ldt - 1)
            if (ldt_val <= 6 and ldt + 1 in hand and ldt + 2 in hand):
                out.append(ldt)
        print(out)
        return out
    
    def active_can_chii(self) -> bool:
        return self.possible_chii_starts() != []
    
    def player_can_minkan(self, pid: int) -> bool:
        ldt = self.ldt()
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
        g.round.round_end([], end_state = GS_RYUUKYOKU, end_state_str = "Kyuushuu Kyuuhai")
    
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
            shanten_tile = self.ldt()
        
        return Shanten(hand = self.open_hand(pid), drawn_tile = shanten_tile)

    def round_end(self, pidl: list[int], end_state: int, end_state_str: str = "Ended") -> None:
        self.winner = pidl
        self.game_state = end_state
        self.game_state_str = state_str
    
    def action_draw(self) -> None:
        if self.live_wall_index < 70:
            self.drawn_tile = self.live_wall[self.live_wall_index]
            self.live_wall_index += 1
        else:
            ## ryuukyoku
            self.round_end([], end_state = GS_RYUUKYOKU, end_state_str = "Ryuukyoku")
    
    def get_kan_owners(self) -> list[int]:
        out = []
        for m in self.open:
            if m.type in (ANKAN, MINKAN, SHOUMINKAN):
                out.append(m.owner_pid)
        return out
    
    def action_draw_kan(self) -> None:
        if len(self.dead_wall) > 10:
            self.drawn_tile = self.dead_wall[10 + self.kan_cnt()]
            kan_owners = self.get_kan_owners
            if len(kan_owners) >= 4:
                if kan_owners[0] != kan_owners[1] or kan_owners[0] != kan_owners[2] or kan_owners[0] != kan_owners[3]:
                    ## suukaikan
                    self.round_end([], end_state = GS_RYUUKYOKU, end_state_str = "Suukaikan")
    
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
        
        self.discard[self.turn - 1].apply(self.turn, self.active_player, tile)
        if self.trigger_suufon_renda():
            self.round_end([], end_state = GS_RYUUKYOKU, end_state_str = "Suufon Renda")
        self.drawn_tile = INVALID_TILE
        self.active_player = (self.active_player + 1) % 4
        self.turn += 1
    
    def trigger_suufon_renda(self):
        return self.turn == 4 and self.discard[0].tile in range(28, 32) and \
            self.discard[0].tile == self.discard[1].tile and \
            self.discard[0].tile == self.discard[2].tile and \
            self.discard[0].tile == self.discard[3].tile
    
    def action_chii(self, start: int) -> None:
        ## sequence starting tile
        tile = self.ldt()
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
        self.open[self.next_open_index()].apply(pid, (pid - 1) % 4, CHII, start, self.turn)
    
    def action_pon(self, pid: int) -> None:
        tile = self.ldt()
        ## twice
        self.hands[pid].remove(tile)
        self.hands[pid].remove(tile)
        self.open[self.next_open_index()].apply(pid, (self.active_player - 1) % 4, PON, tile, self.turn)
        self.active_player = pid
    
    def action_ankan(self) -> None:
        tile = self.drawn_tile
        pid = self.active_player
        ## thrice
        self.hands[pid].remove(tile)
        self.hands[pid].remove(tile)
        self.hands[pid].remove(tile)
        self.open[self.next_open_index()].apply(pid, INVALID_PLAYER, ANKAN, tile, self.turn)
        self.drawn_tile = INVALID_TILE
    
    def action_minkan(self, pid: int) -> None:
        tile = self.ldt()
        ## thrice
        self.hands[pid].remove(tile)
        self.hands[pid].remove(tile)
        self.hands[pid].remove(tile)
        self.open[self.next_open_index()].apply(pid, (self.active_player - 1) % 4, MINKAN, tile, self.turn)
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
        self.round_end([], end_state = GS_RYUUKYOKU, end_state_str = "Suucha Riichi")
    
    def action_ron(self, pidl: list[int]) -> None:
        self.round_end(pidl, end_state = GS_RON, end_state_str = f"Ron {pidl} on {self.last_discard.owner_pid}")
        self.agari = self.ldt()
    
    def action_tsumo(self) -> None:
        self.round_end([self.active_player], end_state = GS_TSUMO, end_state_str = f"Tsumo {self.active_player}")
        self.agari = self.drawn_tile
    
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
        #print("get valid moves called", self.predraw)
        ldt = self.ldt()
        if self.predraw:
            ## predraw
            if self.player_can_pon(pid):
                valid_moves.append(f"p") ## pon
                if self.player_can_minkan(pid):
                    valid_moves.append(f"m") ## minkan
            #print("predraw", pid, self.active_player, self.active_can_chii())
            if pid == self.active_player and self.active_can_chii():
                for t in self.possible_chii_starts():
                    valid_moves.append(f"c{onetile2tenhou(t)}") ## chii
            if shanten.shanten == TENPAI and not self.player_in_furiten(pid, shanten):
                valid_moves.append(f"R") ## ron
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
            last_open = self.open[self.next_open_index() - 1] if self.next_open_index() > 0 else None
            if ldt in self.hands[pid] and last_open is not None:
                ## can't discard called tile
                if last_open.tile_in_meld(ldt):
                    valid_moves.remove(f"d{onetile2tenhou(ldt)}")
            if self.active_can_ankan():
                valid_moves.append(f"a") ## ankan
            if self.active_can_shouminkan():
                valid_moves.append(f"s") ## shouminkan
            if shanten.shanten == 0:
                valid_moves.append(f"T") ## tsumo
        return valid_moves
    
    def do_action(self, action: str = "x"):
        if not action:
            return
        action_type = action[0]
        tail = action[1:]
        tile = tenhou2onetile(tail)
        if action_type == "x":
            return
        elif action_type in ["d", "r"]:
            if action_type == "r":
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
            self.action_draw_kan()
        elif action_type == "s":
            self.action_shouminkan()
            self.action_draw_kan()
        elif action_type == "m":
            self.action_minkan(self.who_can_minkan())
            self.action_draw_kan()
        elif action_type == "T":
            self.action_tsumo()
        elif action_type == "R":
            ron_list = [int(x) for x in action[1:]]
            self.action_ron(ron_list)
        elif action == "kk":
            self.action_kyuushuu_kyuuhai()
    
    def get_value_and_ended(self, pid: int):
        ## TODO - use scoring as return value
        if not self.game_state != GS_ONGOING:
            if pid in self.winner:
                ## player won
                return 1, True
            elif len(self.winner) > 0:
                if self.game_state == GS_RON:
                    if self.last_discard().owner_pid == pid:
                        ## player lost on ron
                        return -1, True
                    else:
                        ## player not involved in ron
                        return 0, True
                else:
                    ## player lost on tsumo
                    return -1, True
            else:
                ## ryuukyoku
                return 0, True
        ## game ongoing
        return 0, False
    
    def player_open_melds(self, pid: int) -> list[Meld]:
        return [m for m in self.open if m.owner_pid == pid]
    
    def player_hand_is_closed(self, pid: int) -> bool:
        return len([m for m in self.player_open_melds(pid) if m.type != ANKAN]) == 0
    
    def get_visible_dora(self):
        out = [INVALID_TILE] * 5
        for i in range(self.kan_cnt() + 1):
            out[i] = self.dead_wall[i]
        return out
    
    def get_visible_state(self, pid: int):
        return VisibleState(pid, self.drawn_tile, self.hands[pid], self.discard, self.open, self.get_visible_dora(), self.round_wind, self.riichi)
            
    def complete_hand_split(self, pid: int) -> list[Meld] | None:
        ## only call this for winning hands
        hand = self.hands[pid] + [agari]
        split = recursive_hand_split(hand)
        split_melds = [Meld(pid, INVALID_PLAYER, PON if m.count(m[0]) == 3 else PAIR if m.count(m[0]) == 2 else CHII, m[0], INVALID_TURN) for m in split]
        hand_melds = self.player_open_melds(pid) + split_melds
        return hand_melds
    
    
    
    ## scoring
    
    def get_fu(self, pid: int) -> int:
        fu = 20
        final_hand = self.hands[pid] + [self.agari]
        final_hand_set = set(final_hand)
        
        ## chiitoi
        if self.player_has_chiitoi(pid):
            return 25
        
        shanten = self.shanten(pid, on_call = (self.drawn_tile == INVALID_TILE))
        ## triple/kan fu
        for m in self.player_open_melds(pid):
            if m.type == PON:
                if m.tile in KokushiTiles:
                    fu += 4
                else:
                    fu += 2
            elif m.type == ANKAN:
                if m.tile in KokushiTiles:
                    fu += 32
                else:
                    fu += 16
            elif m.type in Kans:
                if m.tile in KokushiTiles:
                    fu += 16
                else:
                    fu += 8
        for t in final_hand_set:
            if final_hand.count(t) >= 3:
                if m.tile in KokushiTiles:
                    fu += 8
                else:
                    fu += 4
        
        ## wait fu
        ## only simple waits get fu I think
        if len(shanten.waits) == 1:
            fu += 2
        
        ## yakuhai pair
        for t in final_hand_set:
            if t >= 27 and final_hand.count(t) == 2:
                fu += 2
        
        ## open pinfu
        if not self.player_hand_is_closed(pid) and fu == 20:
            fu += 2
        
        ## rounding up to 10
        fu = fu - (fu % 10) + (fu % 10 > 0)*10
        
        return fu
    
    
    def player_has_chiitoi(self, pid: int) -> bool:
        hand = self.hands[pid] + [self.agari]
        for t in set(hand):
            if hand.count(t) != 2:
                return False
        return True
    
    def player_has_iipeikou(self, hand_melds: list[Meld]) -> bool:
        shuntsu_starts = [m.tile for m in hand_melds if m.type == CHII]
        for tile in set(shuntsu_starts):
            if shuntsu_starts.count(tile) == 2:
                return True
        return False
    
    def player_has_ryanpeikou(self, hand_melds: list[Meld]) -> bool:
        shuntsu_starts = [m.tile for m in hand_melds if m.type == CHII]
        double_shun = 0
        for tile in set(shuntsu_starts):
            if shuntsu_starts.count(tile) == 2:
                double_shun += 1
        return double_shun == 2
    
    def player_has_tanyao(self, pid: int) -> bool:
        for t in self.hands[pid] + [self.agari]:
            if t in KokushiTiles:
                return False
        return True
    
    def player_has_kokushi(self, pid: int) -> bool:
        for t in KokushiTiles:
            if t not in self.hands[pid] + [self.agari]:
                return False
        return True
    
    def hand_is_daisangen(self, hand: list[int]) -> bool:
        open_hand = self.open_hand(pid)
        if open_hand.count(HAKU) == 3 and open_hand.count(HATSU) == 3 and open_hand.count(CHUN) == 3:
            return True
        else:
            return False
    
    def player_has_suuankou(self, pid: int):
        cnts = [self.hands[pid].count(t) for t in set(self.hands[pid])]
        if cnts.count(3) == 4:
            return True
        else:
            return False
    
    def hand_is_suushiihou(self, hand: list[int]) -> bool:
        ## both shousuushii and daisuushii
        return TON in hand and NAN in hand and SHAA in hand and PEI in hand
    
    def hand_is_tsuuiisou(self, hand: list[int]) -> bool:
        for t in hand:
            if t < JIHAI_OFFSET:
                return False
        return True
    
    def hand_is_ryuuiisou(self, hand: list[int]) -> bool:
        for t in hand:
            if t not in RyuuiisouTiles:
                return False
        return True
    
    def hand_is_chinroutou(self, hand: list[int]) -> bool:
        for t in hand:
            if t not in Terminals:
                return False
        return True
    
    def player_has_chuurenpou(self, pid: int) -> bool:
        hand = self.hands[pid] + [agari]
        suit = hand[0] // 9
        if hand[-1] // 9 != suit:
            return False
        if hand.count(hand[0]) == 3 and hand.count(hand[-1]) == 3:
            for t in range(hand[0] + 1, hand[-1]):
                if t not in hand:
                    return False
            return True
        else:
            return False
    
    def player_has_suukantsu(self, open_melds: list[Meld]) -> bool:
        if len(open_melds) == 4:
            for m in open_melds:
                if m.type not in Kans:
                    return False
            return True
        else:
            return False
    
    def player_has_tenhou_chiihou(self) -> bool:
        ## win on first draw, no calls
        return self.turn <= 4 and self.open[0].type == INVALID_MELD and self.drawn_tile != INVALID_TILE
    
    def player_has_rinshan(self, pid: int) -> bool:
        last_open = self.open[-1]
        return last_open.owner_pid == pid and last_open.turn == turn and last_open.type in Kans
    
    def player_yakuhai_cnt(self, hand_melds: list[Meld]) -> int:
        pid = hand_melds[0].owner_pid
        koukan = [m.tile for m in hand_melds if m.type in Kans or m.type == PON]
        cnt = 0
        for t in koukan:
            if t in Sangenpai or (t in Kazehai and (t - JIHAI_OFFSET == pid or t - JIHAI_OFFSET == self.round_wind)):
                cnt += 1
        return cnt
    
    def player_has_chanta(self, hand_melds: list[Meld]) -> bool:
        for m in hand_melds:
            if m.tile in KokushiTiles or (m.type == CHII and m.tile % 9 == 6):
                pass
            else:
                return False
        return True
    
    def get_score(self, pid: int) -> int:
        
        open_hand = self.open_hand(pid) + [self.agari]
        open_melds = self.player_open_melds(pid)
        
        ## yakuman
        if self.player_has_kokushi(pid) or \
            self.hand_is_daisangen(open_hand) or \
            self.player_has_suuankou(pid) or \
            self.hand_is_suushiihou(open_hand) or \
            self.hand_is_tsuuiisou(open_hand) or \
            self.hand_is_ryuuiisou(open_hand) or \
            self.hand_is_chinroutou(open_hand) or \
            self.player_has_chuurenpou(pid) or \
            self.player_has_suukantsu(open_melds) or \
            self.player_has_tenhou_chiihou():
                return 8000 
        
        han = 0
        fu = self.get_fu(pid)
        hand_melds = self.complete_hand_split(pid)
        has_chiitoi = False
        
        if self.riichi[pid] != INVALID_TURN:
            han += 1
            if self.riichi[pid] <= 4 and (open_melds[0].turn == INVALID_TURN or open_melds[0].turn > 4):
                ## double riichi
                han += 1
            if self.riichi[pid] >= self.turn - 4:
                ## ippatsu
                han += 1
        if self.live_wall_index == 70:
            if self.drawn_tile != INVALID_TILE:
                ## haitei
                han += 1
            else:
                ## houtei
                han += 1
        
        if self.player_hand_is_closed(pid):
            if self.drawn_tile != INVALID_TILE:
                ## menzen tsumo
                han += 1
            if fu == 20:
                ## pinfu
                han += 1
            has_chiitoi = self.player_has_chiitoi(pid)
            if has_chiitoi:
                if self.player_has_ryanpeikou(hand_melds):
                    han += 3
                    has_chiitoi = False
                else:
                    han += 2
            elif self.player_has_iipeikou(hand_melds):
                han += 1
        
        if self.player_has_rinshan(pid):
            han += 1
        ## TODO chankan
        if self.player_has_tanyao(pid):
            han += 1
        han += self.player_yakuhai_cnt(hand_melds)
        if self.player_has_chanta(hand_melds):
            han += 2
        ## sanshoku doujun
        ## ittsuu
        ## toitoi
        ## sanankou
        ## sanshoku doukou
        ## sankantsu
        ## honroutou
        ## shousangen
        ## honitsu
        ## junchan
        ## chinitsu
        
        return 0


    
def recursive_hand_split(hand: list[int]) -> list[list[int]] | None:
    first_tile = hand[0]
    sub_split = None
    if hand.count(first_tile) >= 3:
        ## shuntsu
        sub_hand = hand[:]
        meld = [first_tile, first_tile, first_tile]
        sub_hand.remove(first_tile)
        sub_hand.remove(first_tile)
        sub_hand.remove(first_tile)
        if len(sub_hand) > 0:
            sub_split = recursive_hand_split(sub_hand)
            if sub_split is not None:
                return [meld] + sub_split
        else:
            return [meld]
    if hand.count(first_tile) >= 2:
        ## pair
        sub_hand = hand[:]
        meld = [first_tile, first_tile]
        sub_hand.remove(first_tile)
        sub_hand.remove(first_tile)
        if len(sub_hand) > 0:
            sub_split = recursive_hand_split(sub_hand)
            if sub_split is not None:
                return [meld] + sub_split
        else:
            return [meld]
    if first_tile + 1 in hand and first_tile + 2 in hand:
        ## koutsu
        sub_hand = hand[:]
        meld = [first_tile, first_tile + 1, first_tile + 2]
        sub_hand.remove(first_tile)
        sub_hand.remove(first_tile + 1)
        sub_hand.remove(first_tile + 2)
        if len(sub_hand) > 0:
            sub_split = recursive_hand_split(sub_hand)
            if sub_split is not None:
                return [meld] + sub_split
        else:
            return [meld]
    return None
