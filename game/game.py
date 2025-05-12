
import numpy as np

from common import *
from cDiscard import Discard
from cGameState import GameState
from cMeld import Meld
from cRoundState import RoundState

from cMCTS import MCTS

    
g = GameState()
g.init_round()

args = {
    'C': 1.41,
    'search_num': 10
}
mcts = MCTS(g.round, args)
player = 0

while g.round.game_state == GS_ONGOING:
    
    print(g.round)
    ptm = g.round.player_to_move()
    if ptm == player:
        valid_moves = g.round.get_valid_moves(ptm)
        action = ""
        print("Valid moves:", valid_moves)
        while action not in valid_moves:
            action = input()
    else:
        mcts_probs = mcts.search()
        print("mcts_probs", mcts_probs)
        action, prob = "", -np.inf
        for key,value in mcts_probs.items():
            if value > prob:
                action = key
                prob = value
    g.round.do_action(action)
    
    
