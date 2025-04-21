
from cRoundState import RoundState
    
class PlayerState():
    def __init__(self, rs: RoundState, pid: int):
        self.pid = pid
        self.rs = rs
        self.hand = rs.hands[pid]
        self.open = rs.open
        self.discard = rs.discard
        self.riichi = rs.riichi
