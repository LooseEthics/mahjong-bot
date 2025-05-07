
from common import *
from cDiscard import Discard
from cGameState import GameState
from cOpenMeld import OpenMeld
from cPlayerState import PlayerState
from cRoundState import RoundState

    
g = GameState()
g.init_round()

def do_predraw():
    if g.round.discard:
        p = g.round.who_can_pon()
        c = g.round.active_can_chii()
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
                    print(g.round.get_valid_moves(i))
                    call_input = input(f"player {i}: <action: p/c<tile>/m/x>\n")
                calls_made[i] = call_input
            for pid, call in calls_made.items():
                if call[0] == 'p':
                    g.round.action_pon(pid)
                    return
                elif call[0] == 'm':
                    g.round.action_minkan(pid)
                    g.round.action_draw_kan()
                    return
            for pid, call in calls_made.items():
                if call[0] == 'c':
                    g.round.action_chii(tenhou2onetile(call[1:]))
                    return
            g.round.action_draw()
        else:
            print("No calls possible")
            g.round.action_draw()
                
    else:
        g.round.action_draw()

def do_postdraw():
    input_str = ""
    valid_moves = g.round.get_valid_moves(g.round.active_player)
    ## TODO print possible discards/calls
    print(valid_moves)
    while input_str not in valid_moves:
        input_str = input()
    if input_str == 'q':
        game_end = True
        return
    
    action_key = input_str[0]
    tile = input_str[1:]
    print(action_key, tile)
    if input_str[0] == 'd':
        if len(input_str) == 1:
            g.round.action_discard(g.round.drawn_tile)
        else:
            g.round.action_discard(tenhou2onetile(tile))

while g.round.game_running:
    
    print(g.round)
    
    if (g.round.drawn_tile == -1):
        do_predraw()
    else:
        do_postdraw()
    
    
