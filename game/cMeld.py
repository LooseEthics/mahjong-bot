
from common import *

class Meld():
    def __init__(self, opid, tpid, meld_type, tile, turn):
        self.apply(opid, tpid, meld_type, tile, turn)
    
    def __iter__(self):
        return iter((self.owner_pid, self.target_pid, self.type, self.tile))
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        s = f"{OMNames[self.type]} - {self.turn}, O: {WNames[self.owner_pid]}, T: {WNames[self.target_pid]}, Tiles: "
        if self.type == CHII:
            s += tilelist2tenhou([self.tile, self.tile + 1, self.tile + 2])
        elif self.type == PON:
            s += tilelist2tenhou(3*[self.tile])
        else:
            s += tilelist2tenhou(4*[self.tile])
        return s

    def apply(self, opid, tpid, meld_type, tile, turn):
        self.owner_pid = opid
        self.target_pid = tpid
        self.type = meld_type
        self.tile = tile
        self.turn = turn

    def tile_in_meld(self, tile: int) -> bool:
        if self.type == CHII and tile in range(self.tile, self.tile + 3):
            return True
        if (self.type == PON or self.type) in Kans and tile == self.tile:
            return True
        return False
