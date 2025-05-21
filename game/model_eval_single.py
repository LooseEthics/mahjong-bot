
import os
import sys
import torch

from cRoundState import RoundState

from cMCTS import MCTS
from cQNet import *
from model_common import *

if __name__ == "__main__":
    parse_conf()
    if not repo_path:
        print("No repo name")
        quit()
    arg_dict = parse_args(sys.argv)
    if "state_path" not in arg_dict or "model_path" not in arg_dict:
        print("Missing model or state")
        quit()
    
    model_path = os.path.join(arg_dict["repo_path"], arg_dict["model_path"])
    
    qnet = QNet()
    qnet.load_state_dict(torch.load(model_path))
    qnet.eval()

    r = RoundState("load", fname = arg_dict["state_path"])
    mcts = MCTS(r, mcts_args, qnet)
    
    while r.game_state == GS_ONGOING:
    
        pid = r.player_to_move()
        valid_moves = r.get_valid_moves(pid)
        
        print(r)
        print("Valid moves:", valid_moves)
            
        if len(valid_moves) == 1:
            r.do_action(valid_moves[0])
        else:
            input_tensor = r.get_visible_state(pid).to_tensor()
            
            with torch.no_grad():
                policy_logits, value = qnet(input_tensor)
                
            action_probs = F.softmax(policy_logits, dim=1).squeeze(0).cpu().numpy()
            best_action = max(valid_moves, key=lambda a: action_probs[action2logit(a)])

            print("Value estimate:", value.item())
            print("Best action:", best_action)
            
            r.do_action(best_action)
            if arg_dict["wait_flag"]:
                input("Press Enter to proceed")
