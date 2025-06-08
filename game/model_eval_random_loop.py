
import sys
import torch
import torch.nn.functional as F

from cGameState import GameState
from cQNet import *
from model_common import *

def main_eval_random_loop(argv):
    arg_dict = parse_args(argv)
    if "model_path" not in arg_dict:
        print("Missing model")
        quit()
    
    model_path = arg_dict["model_path"]
    print("model_path", model_path)
    qnet = QNet(config['hidden_num'], config['hidden_dim'])
    qnet.load_state_dict(torch.load(model_path))
    qnet.eval()
    
    g = GameState()
    episode_num = arg_dict["episode_num"] if "episode_num" in arg_dict else 1
    
    for episode in range(episode_num):
        
        print(f"episode {episode}")
        g.init_round()
        
        while g.round.game_state == GS_ONGOING:
            
            pid = g.round.player_to_move()
            valid_moves = g.round.get_valid_moves(pid)
            if arg_dict["verbose"]:
                print(g.round)
                print("Valid moves:", valid_moves)
            if len(valid_moves) == 1:
                g.round.do_action(valid_moves[0])
            else:
                input_tensor = g.round.get_visible_state(pid).to_tensor()
                
                with torch.no_grad():
                    policy_logits, value = qnet(input_tensor)
                    
                action_probs = F.softmax(policy_logits, dim=1).squeeze(0).cpu().numpy()
                best_action = max(valid_moves, key=lambda a: action_probs[action2logit(a)])

                if arg_dict["verbose"]:
                    print("Value estimate:", value.item())
                    print("Best action:", best_action)
                g.round.do_action(best_action)
                if arg_dict["wait_flag"]:
                    input("Press Enter to proceed")
        
        print(g.round.game_state_str, g.round.score_change)
        with open(os.path.join(arg_dict["repo_path"], "game_results_eval.txt"), "a") as f:
            f.write(f"model {model_dir}\\{arg_dict['model_name']} {g.round.game_state_str} {g.round.score_change}\n")

if __name__ == "__main__":
    main_eval_random_loop(sys.argv)
