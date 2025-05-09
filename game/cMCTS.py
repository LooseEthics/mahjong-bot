
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
            #selection
            #expansion
            #simulation
            #backpropagation
        
        return visit_counts
