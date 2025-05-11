
from cDiscard import Discard
from cMeld import Meld
    
class VisibleState():
    def __init__(self, pid : int, draw: int, hand: list[int], discard: list[Discard], open_melds: list[Meld], visible_dora: list[int], round_wind: int, riichi: list[int]):
        self.pid = pid
        self.draw = draw
        self.hand = hand
        self.discard = discard
        self.open = open_melds
        self.dora = visible_dora
        self.round_wind = round_wind
        self.riichi = riichi

    def flattened(self):
        lst = [self.pid, self.draw] + self.hand
        lst += [x for d in self.discard for x in (d.turn, d.owner_pid, d.tile)]
        lst += [x for m in self.open_melds for x in (m.owner_pid, m.target_pid, m.type, m.tile, m.turn)]
        lst += [round_wind] + riichi
        return lst
