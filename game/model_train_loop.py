
from collections import deque
import numpy as np
import os
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import TensorDataset

from common import *
from cDiscard import Discard
from cGameState import GameState
from cMeld import Meld
from cRoundState import RoundState

from cMCTS import MCTS
from cQNet import *
from model_common import *
    
    

if __name__ == "__main__":
    parse_conf()
    if not repo_name:
        print("No repo name")
        quit()
    os.makedirs(model_dir, exist_ok = True)
    arg_dict = parse_args(sys.argv)
    model_path = arg_dict["model_path"]
    
    qnet = QNet()
    optimizer = torch.optim.Adam(qnet.parameters(), lr=1e-3)
    if model_path:
        qnet.load_state_dict(torch.load(model_path))
        start_ep = int(model_path[model_path.index('_ep') + 3:model_path.index('.')])
        print(f"Loaded model {model_path}")
    else:
        start_ep = 0
    
    g = GameState()
    episode_num = arg_dict["episode_num"] if "episode_num" in arg_dict else 1000
    print(f"Training for {episode_num} episodes")
    
    for episode in range(start_ep + 1, episode_num + start_ep):
        
        g.init_round()
        trajectory = []
        mcts = MCTS(g.round, mcts_args, qnet)

        while g.round.game_state == GS_ONGOING:
            
            if arg_dict["verbose"]:
                print(g.round)
            ptm = g.round.player_to_move()
            valid_moves = g.round.get_valid_moves(ptm)
            if len(valid_moves) == 1:
                action = valid_moves[0]
            else:
                mcts_probs = mcts.search()
                policy = torch.zeros(QN_OUT_SIZE)
                
                for action, p in mcts_probs.items():
                    policy[action2logit(action)] = p
                    
                state_tensor = g.round.get_visible_state(ptm).to_tensor().squeeze(0)
                trajectory.append((state_tensor, policy, ptm))

                action = max(mcts_probs.items(), key=lambda x: x[1])[0]
                if arg_dict["verbose"]:
                    print("mcts_probs", mcts_probs)
                
            g.round.do_action(action)
            
        if arg_dict["verbose"]:
            print(g.round.game_state_str, g.round.score_change)
        with open("game_results_training.txt", "a") as f:
            f.write(f"ep {episode} {g.round.game_state_str} {g.round.score_change}\n")
        
        results = g.round.get_normalized_score_change()
        data = []
        
        for state, policy, pid in trajectory:
            value = torch.tensor(results[pid], dtype=torch.float32)
            data.append((state, policy, value))
        if data:
            states, policies, values = zip(*data)
            dataset = TensorDataset(torch.stack(states), torch.stack(policies), torch.stack(values))
            train_qnet(qnet, optimizer, dataset)
        
        model_path = os.path.join(model_dir, f"qnet_ep{episode:03d}.pt")
        torch.save(qnet.state_dict(), model_path)
        print(f"Episode {episode} complete — model saved to {model_path}")
