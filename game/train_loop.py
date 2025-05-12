
from collections import deque
import numpy as np
import os
import re
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader

from common import *
from cDiscard import Discard
from cGameState import GameState
from cMeld import Meld
from cRoundState import RoundState

from cMCTS import MCTS
from cQNet import *


def train_qnet(qnet, optimizer, dataset, batch_size=32, epochs=1):
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    qnet.train()
    for epoch in range(epochs):
        for state, target_policy, target_value in loader:
            optimizer.zero_grad()
            policy_logits, value_pred = qnet(state)
            policy_loss = F.cross_entropy(policy_logits, target_policy.argmax(dim=1))
            value_loss = F.mse_loss(value_pred, target_value)
            loss = policy_loss + value_loss
            loss.backward()
            optimizer.step()

def latest_model_path(save_dir: str):
    files = os.listdir(save_dir)
    
    max_num = -1
    latest_model = None
    
    pattern = re.compile(r'qnet_ep(\d+)\.pt')
    for filename in files:
        match = pattern.match(filename)
        if match:
            current_num = int(match.group(1))
            if current_num > max_num:
                max_num = current_num
                latest_model = filename
    if latest_model:
        return os.path.join(save_dir, latest_model)
    else:
        return ""
    
    

if __name__ == "__main__":
    
    save_dir = "checkpoints"
    os.makedirs(save_dir, exist_ok = True)
    to_load = latest_model_path(save_dir)
    
    qnet = QNet()
    optimizer = torch.optim.Adam(qnet.parameters(), lr=1e-3)
    if to_load:
        qnet.load_state_dict(torch.load(to_load))
        start_ep = int(to_load[to_load.index('_ep') + 3:to_load.index('.')])
        print(f"Loaded model {to_load}")
    episode_num = 1000
    
    g = GameState()

    mcts_args = {
        'C': 1.41,
        'search_num': 20
    }
    
    for episode in range(start_ep + 1, episode_num + start_ep):
        
        g.init_round()
        trajectory = []
        mcts = MCTS(g.round, mcts_args, qnet)

        while g.round.game_state == GS_ONGOING:
            
            #print(g.round)
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
                #print("mcts_probs", mcts_probs)
                
            g.round.do_action(action)
            
        #print(g.round.game_state_str, g.round.score_change)
        with open("game_results.txt", "a") as f:
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
        
        model_path = os.path.join(save_dir, f"qnet_ep{episode:03d}.pt")
        torch.save(qnet.state_dict(), model_path)
        print(f"Episode {episode} complete — model saved to {model_path}")
