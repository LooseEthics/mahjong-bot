from cShanten import Shanten
from cRoundState import recursive_hand_split

hand = [14,15,16, 19,20,21, 27,27,27, 11,11,11, 10]
dt = 1

print(Shanten(hand = hand, drawn_tile = dt))
print(recursive_hand_split(hand + [dt]))
