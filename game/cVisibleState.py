
import torch

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

    def print_len(self):
        print("to_tensor hand", len(self.hand))
        print("to_tensor discard", len(self.discard))
        print("to_tensor open", len(self.open))

    def to_tensor(self):
        #self.print_len()
        lst = [self.pid, self.draw] + self.hand ## 2 + 14
        flat_discard = [-1] * 88 * 3
        for i in range(len(self.discard)):
            flat_discard[3*i] = self.discard[i].turn
            flat_discard[3*i + 1] = self.discard[i].owner_pid
            flat_discard[3*i + 2] = self.discard[i].tile
        lst += flat_discard ## 88 * 3
        flat_open = [-1] * 16 * 5
        for i in range(len(self.open)):
            flat_open[5*i] = self.open[i].owner_pid
            flat_open[5*i + 1] = self.open[i].target_pid
            flat_open[5*i + 2] = self.open[i].type
            flat_open[5*i + 3] = self.open[i].tile
            flat_open[5*i + 4] = self.open[i].turn
        lst += flat_open ## 16 * 5
        lst += self.dora ## 5
        lst += [self.round_wind] + self.riichi ## 1 + 4
        ## 370
        #print("to_tensor", len(lst))
        return torch.tensor(lst, dtype=torch.float32).unsqueeze(0)
