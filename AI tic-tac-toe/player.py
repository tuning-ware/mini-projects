import math
import random

class Player:
    def __init__(self, letter):
        # letter is x or o
        self.letter = letter

    # get the next move
    def get_move(self, game):
        pass

class RandomComputerPlayer(Player):
    def __init__(self, letter):
        # the super() function is used to access methods and attributes from the superclass (parent class) within the subclass (child class).
        super().__init__(letter)

    def get_move(self, game):
        # get a random valid spot for our next move, random.choice() chooses 1 thing in a list at random
        square = random.choice(game.available_moves())
        return square

class HumanPlayer(Player):
    def __init__(self, letter):
        super().__init__(letter)

    def get_move(self, game):
        valid_square = False
        val = None
        while not valid_square:
            square = input(self.letter + '\'s turn. Input move (0-8):')
            # verify input is integer and spot is available on board, else return error
            try:
                val = int(square)
                if val not in game.available_moves():
                    raise ValueError
                valid_square = True
            except ValueError:
                print('Invalid square. Try again.')

        return val
    
class GeniusComputerPlayer(Player):
    def __init__(self, letter):
        super().__init__(letter)

    def get_move(self, game):
        if len(game.available_moves()) == 9:
            square = random.choice(game.available_moves()) # randomly chooses one
        else:
            # get the square based off the minimax algorithm
            square = self.minimax(game, self.letter)['position']
            print(self.minimax(game, self.letter))
        return square
    
    def minimax(self, state, player):
        max_player = self.letter # yourself!! 
        other_player = 'O' if player == 'X' else 'X' # the other player.. so whatever letter is NOT

        # first, we want to check if the previous move is a winner (for the other player, that is)
        # this is our base case
        if state.current_winner == other_player:
            # we should return position AND score because we need to keep track of the score
            # for minimax to work
            # check if the player in the previous turn is the max player and returns the score accordingly
            return {'position': None, 
                    'score': 1 * (state.num_empty_squares() + 1) if other_player == max_player else -1 * (state.num_empty_squares() + 1)
                    }
        
        elif not state.empty_squares(): # no empty squares
            return {'position': None, 'score': 0}
        
        if player == max_player:
            best = {'position': None, 'score': -math.inf} # each score should maximize (be larger)
        # min player
        else:
            best = {'position': None, 'score': math.inf} # each score should minimize (start from largest)

        for possible_move in state.available_moves():
            # step 1, make a move, try that spot
            state.make_move(possible_move, player)
            # step 2: recurse using minimax to simulate a game after making that move
            sim_score = self.minimax(state, other_player) # now, we alternate players

            # step 3: undo the move
            state.board[possible_move] = ' '
            state.current_winner = None
            sim_score['position'] = possible_move # otherwise this will get messed up from the recursion

            # step 4: update the dictionaries if necessary
            if player == max_player: # we are trying to minimize the max_player
                if sim_score['score'] > best['score']:
                    best = sim_score # replace best
            else: # but minimize the other player
                if sim_score['score'] < best['score']:
                    best = sim_score # replace best

        return best
    
class BeatableComputerPlayer(Player):
    def __init__(self, letter):
        super().__init__(letter)

    def get_move(self, game):
        opponent = 'O' if self.letter == 'X' else 'X'

        # defend the diagonals
        # check diagonals
        # list comprehension creates a list of the elements in the diagonals
        diagonal1 = [game.board[i] for i in [0, 4, 8]]
        # print(f"diagonal1: {diagonal1}")
        diagonal2 = [game.board[i] for i in [2, 4, 6]]
        # print(f"diagonal2: {diagonal2}")
        if diagonal1.count(opponent) == 2 and diagonal1.count(self.letter) == 0:
            move = [i for i, position in enumerate(diagonal1) if opponent != position]
            move = [0, 4, 8][move[0]]
            return move
        
        elif diagonal2.count(opponent) == 2 and diagonal2.count(self.letter) == 0:
            move = [i for i, position in enumerate(diagonal2) if opponent != position]
            move = [2, 4, 6][move[0]]
            return move
        

        rows = [game.board[i*3 : (i + 1)*3] for i in range(3)]
        # i*3 creates the column, adding j shifts the column leftwards
        columns = [[game.board[i*3 +j] for i in range(3)] for j in range(3)]

        # go for victory!
        for col_num, col in enumerate(columns):
            if col.count(self.letter) == 2 and col.count(opponent) == 0:
                move = [i for i, position in enumerate(col) if self.letter != position]
                move = col_num + move[0]*3
                return move
            
        for row_num, row in enumerate(rows):
            if row.count(self.letter) == 2 and row.count(opponent) == 0:
                move = [i for i, position in enumerate(row) if self.letter != position]
                move = move[0] + row_num*3
                return move
            

        # defend the rows
        # print(f"rows: {rows}") 
        for row_num, row in enumerate(rows):
            if row.count(opponent) == 2 and row.count(self.letter) == 0:
                move = [i for i, position in enumerate(row) if opponent != position]
                move = move[0] + row_num*3
                return move
            
        # defend the columns 
        # print(f"columns: {columns}")
        for col_num, col in enumerate(columns):
            if col.count(opponent) == 2 and col.count(self.letter) == 0:
                move = [i for i, position in enumerate(col) if opponent != position]
                move = col_num + move[0]*3
                return move

        # take the centre spot
        if 4 in game.available_moves():
            return 4
        
        # take the corner spot
        elif any(move in game.available_moves() for move in [0, 2, 6, 8]):
            return random.choice([move for move in [0, 2, 6, 8] if move in game.available_moves()])
        
        
        return random.choice(game.available_moves())