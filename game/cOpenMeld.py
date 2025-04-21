

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
