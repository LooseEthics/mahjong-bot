
from common import *
from cDiscard import Discard
from cGameState import GameState
from cOpenMeld import OpenMeld
from cPlayerState import PlayerState
from cRoundState import RoundState

    
g = GameState()
g.init_round()

game_end = False

def do_predraw():
    if g.round.discard:
        p = g.round.who_can_pon()
        c = g.round.active_can_chii()
        m = g.round.who_can_minkan()
        if (p != -1 or c != -1 or m != -1):
            print(f"p {p}, c {c}, m {m}")
            calls_made = {i:'x' if (c != i and p != i and m != i) else '?' for i in range(4)}
            while '?' in calls_made.values():
                print(calls_made)
                call_input = input("<player: 0-3><action: p/c<tile>/m/x>\n").split()
                for s in call_input:
                    calls_made[int(s[0])] = s[1:]
            pid = -1
            for pid, call in calls_made.items():
                if call == 'p':
                    g.round.action_pon(pid)
                    return
                elif call == 'm':
                    g.round.action_minkan(pid)
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
    
    
