
import copy
import math
import numpy as np

from common import *

class Node:
    def __init__(self, game, args, root_pid, parent = None, action_taken = None):
        self.game = game
        self.args = args
        self.root_pid = root_pid
        self.parent = parent
        self.action_taken = action_taken
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
        q_value = child.value_sum / child.visit_count
        return q_value + self.args['C'] * math.sqrt(math.log(self.visit_count)/child.visit_count)
    
    def expand(self):
        action = np.random.choice(self.expandable)
        self.expandable.remove(action)
        child_game = copy.deepcopy(self.game)
        child_game.do_action(action)
        
        child = Node(child_game, self.args, self.root_pid, self, action)
        self.children.append(child)
        return child
    
    def simulate(self):
        value, is_terminal = self.game.get_value_and_ended(self.node_pid)
        
        if is_terminal:
            return value
        
        rollout_game = copy.deepcopy(self.game)
        
        while not is_terminal:
            rollout_pid = rollout_game.player_to_move()
            #print("sim pid", rollout_pid)
            #print("sim hand", rollout_game.hands[rollout_pid])
            #print("sim draw", rollout_game.drawn_tile)
            valid_moves = rollout_game.get_valid_moves(rollout_pid)
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
    def __init__(self, game, args):
        self.game = game
        self.args = args
        
    def search(self):
        
        search_game = copy.deepcopy(self.game)
        root = Node(search_game, self.args, search_game.active_player)
        action_probs = {a: 0 for a in root.expandable}
        
        for _ in range(self.args['search_num']):
            node = root
            while node.is_fully_expanded():
                node = node.select()
                
            value, is_terminal = self.game.get_value_and_ended(node.root_pid)
            
            if not is_terminal:
                node = node.expand()
                value = node.simulate()
            node.backpropagate(value)
        
        for child in root.children:
            action_probs[child.action_taken] = child.visit_count
        action_sum = sum(action_probs.values())
        for key, value in action_probs.items():
            action_probs[key] = value / action_sum
        return action_probs
