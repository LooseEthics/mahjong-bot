

class Node:
    def __init__(self, game, args, state, parent = None, action_taken = None):
        self.game = game
        self.args = args
        self.state = state
        self.parent = parent
        self.action_taken = action_taken
        
        self.children = []
        self.expandable = game.get_valid_moves(state)

class MCTS:
    def __init__(self, game, args):
        self.game = game
        self.args = args
        
    def search(self, state):
        
        for search in range(self.args['search_num']):
            #selection
            #expansion
            #simulation
            #backpropagation
        
        return visit_counts
