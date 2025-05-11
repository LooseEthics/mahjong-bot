
from common import *
from cDiscard import Discard
from cGameState import GameState
from cMeld import Meld
from cRoundState import RoundState

    
g = GameState()
g.init_round()

def do_predraw():
    if g.round.turn > 1:
        p = g.round.who_can_pon()
        c = g.round.active_can_chii()
        print(f"p {p}, c {c}")
        if (p != INVALID_PLAYER or c == True):
            print(f"p {p}, c {c}")
            calls_made = {i:'?' if (c == True and i == g.round.active_player or p == i) else 'x' for i in range(4)}
            for i, value in calls_made.items():
                if value == 'x':
                    continue
                print(calls_made)
                valid_moves = g.round.get_valid_moves(i)
                call_input = ""
                while call_input not in valid_moves:
                    print("Valid moves:", g.round.get_valid_moves(i))
                    call_input = input(f"player {i}:")
                calls_made[i] = call_input
            
            priority_call = ""
            ron_calls = []
            
            ## ron
            for pid, call in calls_made.items():
                if call[0] == 'R':
                    ron_calls.append(pid)
            if len(ron_calls) > 0:
                priority_call = "R"
                for pid in ron_calls:
                    priority_call += f"{pid}"
            
            ## pon, minkan
            if not priority_call:
                for pid, call in calls_made.items():
                    if call[0] == 'p' or call[0] == 'm':
                        priority_call = call
            
            ## chii
            if not priority_call:
                for pid, call in calls_made.items():
                    if call[0] == 'c':
                        priority_call = call
            
            g.round.do_action(priority_call)
            
        else:
            print("No calls possible")
            g.round.action_draw()
                
    else:
        if g.round.active_can_kyuushuu_kyuuhai():
            valid_moves = ["kk", "x"]
            print("Valid moves:", valid_moves)
            kk_input = ""
            while kk_input not in valid_moves:
                kk_input = input()
            if kk_input == "kk":
                g.round.action_kyuushuu_kyuuhai()
                return
        g.round.action_draw()

def do_postdraw():
    input_str = ""
    valid_moves = g.round.get_valid_moves(g.round.active_player)
    print("Valid moves:", valid_moves)
    while input_str not in valid_moves:
        input_str = input()
    g.round.do_action(input_str)

while g.round.game_state == GS_ONGOING:
    
    print(g.round)
    
    if (g.round.predraw):
        print("predraw")
        do_predraw()
    else:
        print("postdraw")
        do_postdraw()
    g.round.predraw = not g.round.predraw
    
    
