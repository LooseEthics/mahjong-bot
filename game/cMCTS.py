
import copy
import math
from multiprocessing import Pool, cpu_count
import numpy as np
import torch
import torch.nn.functional as F

from common import *
from cQNet import *

class Node:
    def __init__(self, game, args, root_pid, parent = None, action_taken = None, policy_prior = None):
        self.game = game
        self.args = args
        self.root_pid = root_pid
        self.parent = parent
        self.action_taken = action_taken
        self.policy_prior = policy_prior
        
        self.node_pid = self.game.player_to_move()
        
        self.children = []
        self.expandable = game.get_valid_moves(self.node_pid)
        
        self.visit_count = 0
        self.value_sum = 0
    
    def is_fully_expanded(self):
        return len(self.expandable) == 0 and len(self.children) > 0
    
    def select(self):
        best_child = None
        best_ucb = -np.inf
        
        for child in self.children:
            ucb = self.get_ucb(child)
            if ucb > best_ucb:
                best_child = child
                best_ucb = ucb
        return best_child
    
    def get_ucb(self, child):
        if child.visit_count == 0:
            q = 0
        else:
            q = child.value_sum / child.visit_count
        p = child.policy_prior or 1e-8
        return q + self.args['C'] * p * math.sqrt(self.visit_count)/(1 + child.visit_count)
    
    def expand(self, neural_net):
        state_tensor = self.game.get_visible_state(self.node_pid).to_tensor()
        with torch.no_grad():
            policy_logits, value = neural_net(state_tensor)
            policy_probs = F.softmax(policy_logits, dim=1).squeeze(0).cpu().numpy()
        
        for action in self.expandable:
            logit = action2logit(action)
            prob = policy_probs[logit]
            
            # Create child node for each possible action
            child_game = self.game.clone()
            child_game.do_action(action)
            child = Node(child_game, self.args, self.root_pid, self, action, prob)
            self.children.append(child)
        
        self.expandable.clear()
        return self.select()
        
        '''action = np.random.choice(self.expandable)
        self.expandable.remove(action)
        child_game = self.game.clone()
        child_game.do_action(action)
        
        child = Node(child_game, self.args, self.root_pid, self, action)
        self.children.append(child)
        return child'''
    
    def simulate(self):
        value, is_terminal = self.game.get_value_and_ended(self.node_pid)
        
        if is_terminal:
            return value
        
        rollout_game = self.game.clone()
        
        while not is_terminal:
            rollout_pid = rollout_game.player_to_move()
            #print("sim pid", rollout_pid)
            #print("sim hand", rollout_game.hands[rollout_pid])
            #print("sim draw", rollout_game.drawn_tile)
            valid_moves = rollout_game.get_valid_moves(rollout_pid)
            if len(valid_moves) == 0:
                print(rollout_game)
            #print("sim valid moves", valid_moves)
            action = np.random.choice(valid_moves)
            #print("sim choice", action)
            rollout_game.do_action(action)
            value, is_terminal = rollout_game.get_value_and_ended(self.node_pid)
            #print("sim value", value, is_terminal)
        return value
    
    def backpropagate(self, value: int):
        self.value_sum += value
        self.visit_count += 1
        
        if self.parent is not None:
            self.parent.backpropagate(value)

class MCTS:
    def __init__(self, game, args, neural_net):
        self.game = game
        self.args = args
        self.neural_net = neural_net

    def search(self):
        search_game = self.game.clone()
        root = Node(search_game, self.args, search_game.player_to_move())
        action_probs = {a: 0 for a in root.expandable}
        
        num_simulations = self.args['search_num']
        num_workers = min(cpu_count(), self.args.get('num_workers', cpu_count()))
        
        with Pool(num_workers) as pool:
            results = pool.starmap(
                run_simulation,
                [(self.game.clone(), self.args, root.node_pid, self.neural_net) for _ in range(num_simulations)]
            )
        
        # Apply backpropagation serially to avoid race conditions
        for action, value in results:
            # find or create the child node matching the action
            match = next((c for c in root.children if c.action_taken == action), None)
            if match is None:
                new_game = root.game.clone()
                new_game.do_action(action)
                match = Node(new_game, self.args, root.node_pid, root, action)
                root.children.append(match)
            match.backpropagate(value)
        
        for child in root.children:
            action_probs[child.action_taken] = child.visit_count
        action_sum = sum(action_probs.values())
        for key, value in action_probs.items():
            action_probs[key] = value / action_sum
        
        return action_probs

def run_simulation(game, args, root_pid, neural_net):
    node = Node(game.clone(), args, root_pid)
    
    while node.is_fully_expanded():
        node = node.select()

    value, is_terminal = node.game.get_value_and_ended(root_pid)
    
    if not is_terminal:
        node = node.expand(neural_net)
        value = node.simulate()
    
    return node.action_taken, value
