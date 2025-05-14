
import os

from common import *
from model_common import state_dir
from cRoundState import RoundState

r = RoundState()

r.turn = 1
r.active_player = 0
r.call_player = INVALID_PLAYER
r.calls_made = {pid: 'x' for pid in range(4)}
r.tiles = [i for i in range(34) for _ in range(4)]
r.hands = [sorted(r.tiles[i*13: (i+1)*13]) for i in range(4)]
r.open = []
r.discard = []
r.riichi = [INVALID_ROUND, INVALID_ROUND, INVALID_ROUND, INVALID_ROUND]
r.dead_wall = r.tiles[52:66]
r.live_wall = r.tiles[66:]
r.live_wall_index = 0
r.drawn_tile = INVALID_TILE
r.winner = []
r.game_state = GS_ONGOING
r.game_state_str = "Ongoing"
r.predraw = True
r.agari = INVALID_TILE
r.round_wind = 0
r.score_change = [0, 0, 0, 0]

print(r)
r.save(os.path.join(state_dir, "test.mgs"))

l = RoundState("load", fname = os.path.join(state_dir, "test.mgs"))
print(l)
