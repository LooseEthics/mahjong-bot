
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader

from common import *

QN_IN_SIZE = 370
QN_OUT_SIZE = 98

def action2logit(action: str):
    action_type = action[0]
    tile = tenhou2onetile(action[1:]) if len(action) > 1 else None
    call_str = "pamsTRkxD"
    if action_type == "d" and tile != INVALID_TILE:
        return tile
    elif action_type == "r" and tile != INVALID_TILE:
        return 34 + tile
    elif action_type == "c" and tile != INVALID_TILE:
        return 68 + tile - 2*(tile // 9)
    elif action_type in call_str:
        return 89 + call_str.index(action_type)

def logit2action(logit: int):
    if logit < 34:
        return "d" + onetile2tenhou(logit)
    elif logit < 68:
        tile = logit - 34
        return "r" + onetile2tenhou(tile)
    elif logit < 89:
        tile = logit - 68 + 2*(logit // 7)
        return "d" + onetile2tenhou(tile)
    else:
        return "pamsTRkxD"[logit - 89]

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

class QNet(nn.Module):
    def __init__(self, num_hidden = 1, hidden_dim = 256):
        super().__init__()
        ## input size - VisibleState - 364
        ## output size - all possible actions - 98
        ##      discard - 34
        ##      riichi discard - 34
        ##      chii calls - 7*3
        ##      pon, kan, tsumo, ron, kk, noop, draw - 9
        layers = [nn.Linear(QN_IN_SIZE, hidden_dim), nn.ReLU()]
        for _ in range(num_hidden):
            layers.append(nn.Linear(hidden_dim, hidden_dim))
            layers.append(nn.ReLU())
        self.backbone = nn.Sequential(*layers)
        self.policy_head = nn.Linear(hidden_dim, QN_OUT_SIZE)
        self.value_head = nn.Linear(hidden_dim, 1)

    def forward(self, x):
        x = self.backbone(x)
        policy_logits = self.policy_head(x)
        value = torch.tanh(self.value_head(x))  # output range [-1, 1]
        return policy_logits, value.squeeze(-1)
