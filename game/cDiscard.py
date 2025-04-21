
from common import *

class Discard():
    def __init__(self, turn, opid, tile):
        self.turn = turn
        self.owner_pid = opid
        self.tile = tile
    
    def __iter__(self):
        return iter((self.turn, self.owner_pid, self.tile))
    
    def __str__(self):
        #return f"Discard, Turn: {self.turn}, Owner: {WNames[self.owner_pid]}, Tile: {onetile2tenhou(self.tile)}"
        return f"({self.turn}, {self.owner_pid}, {onetile2tenhou(self.tile)})"
    
    def __repr__(self):
        return self.__str__()
