
import numpy as np
import math

class Node:
    def __init__(self, game, args, state, parent = None, action_taken = None):
        self.game = game
        self.args = args
        self.state = state
        self.parent = parent
        self.action_taken = action_taken
        
        self.children = []
        self.expandable = game.get_valid_moves(state)
        
        self.visit_count = 0
        self.value_sum = 0
    
    def is_fully_expanded(self):
        return len(self.expandable) == 0 and len(seld.children) > 0
    
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
        self.expandable[action] = 0
        child_state = self.state.copy()
        child_state = self.game.get_next_state(child_state, action)
        
        child = Node(self.game, self.args, child_state, self, action)
        self.children.append(child)
        return child
    
    def simulate(self):
        value, is_terminal = self.game.get_value_and_ended()
        value = self.game.get_opponent_value(value)
        
        if is_terminal:
            return value
        
        rollout_state = self.state.copy()
        while True:
            valid_moves = self.game.get_valid_moves()
            action = np.random.choice(valid_moves)
            rollout_state = self.game.get_next_state(rollout_state, action)
            value, is_terminal = self.game.get_value_and_ended()
            if is_terminal:
                

class MCTS:
    def __init__(self, game, args):
        self.game = game
        self.args = args
        
    def search(self, state):
        
        root = Node(self.game, self.args, state)
        
        for search in range(self.args['search_num']):
            node = root
            while node.is_fully_expanded():
                node = node.select()
                
            value, is_terminal = game.get_value_and_ended()
            value = self.game.get_opponent_value(value)
            
            if not is_terminal:
                node = node.expand()
                value = node.simulate()
                #simulation
                
            #backpropagation
        
        return visit_counts
