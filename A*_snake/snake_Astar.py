from queue import PriorityQueue
import math
import copy

#I just hardcoded the number of rows and cols b/c I can't be bothered to figure out
#how to import the values from the other file at the moment
rows = 48
cols = 64

#manhattan distance from head to food position
def heuristic(board):
    head = board.snake[0]
    return abs(head[0] - board.foodPos[0]) + abs(head[1] - board.foodPos[1])

#returns a list directions used for determining where the next head will be, or None if no path is found
def Astar(root):
    unexplored = PriorityQueue()
    counter = 0
    unexplored.put((0, counter, root))
    explored = {}
    while not unexplored.empty():
        currNode = unexplored.get()
        board = currNode[2]
        cost = currNode[0]

        if board.is_goal() == True:
            return board.get_path()

        #algorithm explores an abridged state space on considering where the head has been
        #not a perfect solution, but its too computationally intensive to explore states depending on the configuration of the snake's body
        if board.snake[0] in explored and board.cost >= explored[board.snake[0]]:
            continue

        explored[board.snake[0]] = board.cost
   
        children = board.get_children()

        for child in children:
            h = heuristic(child)
            total_cost = board.cost + h
            unexplored.put((total_cost, counter, child))
            counter += 1
            
    return None

        
#stores info about a given board state 
class Board:
    
    def __init__(self, b, s, d, fp, p=None, c=0):
        self.state = b
        self.foodPos = fp
        self.snake = s
        self.snake_dir = d
        self.parent = p
        self.cost = c

    #checks if the head has reached the goal
    def is_goal(self):
        if self.foodPos == self.snake[0]:
            return True
        else:
            return False

    def get_new_board(self, snake_dir):
        #update snake
        new_snake = copy.deepcopy(self.snake)
        head = new_snake[0]
        new_head = (head[0] + snake_dir[0], head[1] + snake_dir[1])
        new_snake.insert(0, new_head)
        tail = new_snake.pop()
        #update board
        new_state = copy.deepcopy(self.state)
        new_state[new_head[0]][new_head[1]] = 1
        new_state[tail[0]][tail[1]] = 0
        #return new_board
        new_board = Board(new_state, new_snake, snake_dir, self.foodPos, self, self.cost + 1)
        return new_board

    #returns a list of new Board states based on the accessiblity of orthogonally adjacent tiles
    def get_children(self):
        children = []
        head = self.snake[0]
        if head[0] + 1 < rows and self.snake_dir != (-1, 0) and self.state[head[0] + 1][head[1]] != 1:
            new_board = self.get_new_board((1, 0))
            children.append(new_board)
        if head[0] - 1 >= 0 and self.snake_dir != (1, 0) and self.state[head[0] - 1][head[1]] != 1:
            new_board = self.get_new_board((-1, 0))
            children.append(new_board)
        if head[1] + 1 < cols and self.snake_dir != (0, -1) and self.state[head[0]][head[1] + 1] != 1:
            new_board = self.get_new_board((0, 1))
            children.append(new_board)
        if head[1] - 1 >= 0 and self.snake_dir != (0, 1) and self.state[head[0]][head[1] - 1] != 1:
            new_board = self.get_new_board((0, -1))
            children.append(new_board)
        return children

    #returns the list of directions the snake needs to follow in reverse order
    def get_path(self):
        path = []
        curr_node = self
        while curr_node:
            path.append(curr_node.snake_dir)
            curr_node = curr_node.parent
        #remove the action associated with reaching the previous food position
        path.pop()
        return path
        
