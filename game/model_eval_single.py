
import os
import sys
import torch

from cQNet import *

if __name__ == "__main__":
    arg_dict = parse_args(sys.argv)
    if "state_path" not in arg_dict or "model_path" not in arg_dict:
        print("Missing model or state")
        quit()
    
    
    qnet = QNet()
    qnet.load_state_dict(torch.load(arg_dict["model_path"]))
    qnet.eval()

    # Get the player-to-move
    pid = g.round.player_to_move()

    # Get the visible state
    visible_state = g.round.get_visible_state(pid)

    # Convert to tensor
    input_tensor = visible_state.to_tensor()  # shape: [1, 369]

    # Get output
    with torch.no_grad():
        policy_logits, value = qnet(input_tensor)

    # Convert policy logits to action probabilities
    import torch.nn.functional as F
    action_probs = F.softmax(policy_logits, dim=1).squeeze(0).cpu().numpy()  # shape: (98,)

    # Example: pick the most probable legal action
    valid_moves = g.round.get_valid_moves(pid)
    best_action = max(valid_moves, key=lambda a: action_probs[action2logit(a)])

    print("Value estimate:", value.item())
    print("Best action:", best_action)
