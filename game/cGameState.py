
from cRoundState import RoundState

class GameState():
    def __init__(self):
        self.round_wind = 0
        self.round_num = 0
        self.honba = 0
        self.scores = (25000, 25000, 25000, 25000)
        self.init_round()
    
    def init_round(self):
        self.round = RoundState()
    
    def __repr__(self):
        s =  f"Game state: {WNames[self.round_wind]} {self.round_num}, Honba {self.honba}\n"
        s += f"  Scores: {self.scores}"
        return s
