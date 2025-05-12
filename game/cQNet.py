
import torch
import torch.nn as nn
import torch.nn.functional as F

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

class QNet(nn.Module):
    def __init__(self):
        super().__init__()
        ## input size - VisibleState - 364
        ## output size - all possible actions - 98
        ##      discard - 34
        ##      riichi discard - 34
        ##      chii calls - 7*3
        ##      pon, kan, tsumo, ron, kk, noop, draw - 9
        self.backbone = nn.Sequential(
            nn.Linear(QN_IN_SIZE, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
        )
        self.policy_head = nn.Linear(256, QN_OUT_SIZE)
        self.value_head = nn.Linear(256, 1)

    def forward(self, x):
        x = self.backbone(x)
        policy_logits = self.policy_head(x)
        value = torch.tanh(self.value_head(x))  # output range [-1, 1]
        return policy_logits, value.squeeze(-1)
