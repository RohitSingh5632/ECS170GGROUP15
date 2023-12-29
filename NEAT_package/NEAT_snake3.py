import neat
import pygame
import random
import math
import numpy as np

WIDTH, HEIGHT, SIZE = 640, 480, 10
# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

#board
rows = int(HEIGHT / SIZE)
cols = int(WIDTH / SIZE)

body_collision = 0.75
wall_collision = 0.5
eat_food = 1

def updateInputs(snake, board, snake_dir, food_row, food_col, hunger):
    #0: dist above/below food
    #1: dist left/right of food 
    #2-9: nearest obstacles (N, NE, E, SE, S, SW, W, NW) 
    #10: MD to food
    #11: snake growth,
    #12: turn limit
    #13: up/down dir rel to food
    #14: right/left dir rel to food
    inputs = [0] * 15
    head = snake[0]
    #how far above/below the snake's head is the food (if at all)
    inputs[0] = (food_row - head[0])/rows
    #how far to the right/left the snake's head is the food (if at all)
    inputs[1] = (food_col - head[1])/cols
    #update head direction inputs and nearest collisions
    #up
    for i in range(1, head[0]):
        if board[head[0] - i][head[1]] == 1:
            inputs[2] = i/rows
            break
        inputs[2] = head[0]/rows
    #top-right
    for i in range(1, min(cols - head[1], head[0])):
        if board[head[0] - i][head[1] + i] == 1:
            inputs[3] = (2 * i)/(rows + cols)
            break
        inputs[3] = (2 * i)/(rows + cols)
    #right
    for i in range(1, cols - head[1]):
        if board[head[0]][head[1] + i] == 1:
            inputs[4] = i/cols
            break
        inputs[4] = (cols - head[1])/cols
    #bottom-right
    for i in range(1, min(cols - head[1], rows - head[0])):
        if board[head[0] + i][head[1] + i] == 1:
            inputs[5] = (2 * i)/(rows + cols)
            break
        inputs[5] = (2 * i)/(rows + cols)
    #down
    for i in range(1, rows - head[0]):
        if board[head[0] + i][head[1]] == 1:
            inputs[6] = i/rows
            break
        inputs[6] = (rows - head[0])/rows
    #bottom-left
    for i in range(1, min(head[1], rows - head[0])):
        if board[head[0] + i][head[1] - i] == 1:
            inputs[7] = (2 * i)/(rows + cols)
            break
        inputs[7] = (2 * i)/(rows + cols)
    #left
    for i in range(1, head[1]):
        if board[head[0]][head[1] - i] == 1:
            inputs[8] = i/cols
            break
        inputs[8] = head[1]/cols
    #top-left
    for i in range(1, min(head[1], head[0])):
        if board[head[0] - i][head[1] - i] == 1:
            inputs[9] = (2 * i)/(rows + cols)
            break
        inputs[9] = (2 * i)/(rows + cols)
    #calculate MD to food from head
    inputs[10] = abs(snake[0][0] - food_row)/rows + abs(snake[0][1] - food_col)/cols
    #calculate length of snake
    inputs[11] = len(snake) - 5
    
    inputs[12] = hunger/100
    
    #up/down dir rel to food
    if inputs[0] > 0:
        inputs[13] = 1
    elif inputs[0] < 0:
        inputs[13] = -1
    else:
        inputs[13] = 0
    #left/right dir rel to food
    if inputs[1] > 0:
        inputs[14] = 1
    elif inputs[1] < 0:
        inputs[14] = -1
    else:
        inputs[14] = 0


    return inputs



def softmax(outputs):
    activations = []
    for val in outputs:
        activations.append(val)
    activations2 = np.array(activations)
    exp_data = np.exp(activations2 - np.max(activations2, axis=0))  # Subtract max for numerical stability
    score = exp_data / np.sum(exp_data, axis=0, keepdims=True)
    for i in range(len(outputs)):
        activations[i] = score[i]
    return activations
    
def predict(network, inputs, curr_dir):
    outputs = network.activate(inputs)
    #outputs = softmax(outputs)
    
    best_activation = 0
    best_idx = random.randrange(3)

    #determine output node with highest activation
    for i in range(len(outputs)):
        if outputs[i] > best_activation:
            best_activation = outputs[i]
            best_idx = i
    #return direction associated with activated node
    #heading up
    #moving up
    if curr_dir == (-1, 0):
        #move left (left)
        if best_idx == 0:
            return ((0, -1), 1)
        #move forward (up)
        elif best_idx == 1:
            return ((-1, 0), 0)
        #move right (right)
        elif best_idx == 2:
            return ((0, 1), 1)
    #moving right
    elif curr_dir == (0, 1):
        #move left (up)
        if best_idx == 0:
            return ((-1, 0), 1)
        #move forward (right)
        elif best_idx == 1:
            return ((0, 1), 0)
        #move right (down)
        elif best_idx == 2:
            return ((1, 0), 1)
    #moving down
    elif curr_dir == (1, 0):
        #move left (right)
        if best_idx == 0:
            return ((0, 1), 1)
        #move forward (down)
        elif best_idx == 1:
            return ((1, 0), 0)
        #move right (left)
        elif best_idx == 2:
            return ((0, -1), 1)
    #moving left
    elif curr_dir == (0, -1):
        #move left (down)
        if best_idx == 0:
            return ((1, 0), 1)
        #move forward (left)
        elif best_idx == 1:
            return ((0, -1), 0)
        #move right (up)
        elif best_idx == 2:
            return ((-1, 0), 1)


        
def play(network, render):
    #state space is represented by a 2D list: 0 = empty, 1 = occupied snake body segment, 2 = occupied by food
    board = [[0 for i in range(cols)] for j in range(rows)]
    
    # Snake and food
    row = int(math.floor(rows/2))
    col = int(math.floor(cols/2))
    snake = [(row, col), (row, col - 1), (row, col - 2), (row, col - 3), (row, col - 4)]
    for segment in snake:
        board[segment[0]][segment[1]] = 1
    pos = 2
    q_rows = int(math.floor(rows/8))
    q_cols = int(math.floor(cols/8))
    food_quads = [(2, rows/2, 2, cols/2 - 2), (2, rows/2 - 2, rows/2 + 2, cols - 2), (rows/2 + 2, rows - 2, cols/2 + 2, cols - 2), (rows/2 + 2, rows - 2, 2, cols/2 - 2)]
    
    food_pos = [(q_rows, cols - q_cols), (rows - q_rows, cols - q_cols), (rows - q_rows, q_cols), (q_rows, q_cols)]
    snake_dir = (0, 1)#random.choice(dirs)
    #food_row = random.randint(food_quads[pos][0], food_quads[pos][1])
    #food_col = random.randint(food_quads[pos][2], food_quads[pos][3])
    food_row = food_pos[pos][0]
    food_col = food_pos[pos][1]
    pos += 1
    food = (food_row, food_col)
    board[food_row][food_col] = 2
    
    #parameters
    score = 0
    survival = 0
    turnNum = 0
    hunger = 100
    
    #render game using pygame or else just update state representation
    if render == True:
        
        pygame.init()
        # Set up display
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
        # Main game loop
        clock = pygame.time.Clock()
        clock_speed = 30
        pygame.time.delay(1000)
        while True:
            #if AI spends too much time not collecting food, end sim
            if turnNum >= 100:
                break
            
            inputs = updateInputs(snake, board, snake_dir, food[0], food[1], turnNum)
            output = predict(network, inputs, snake_dir)
            new_dir = output[0]
            turn = output[1]
            turnNum += turn
            new_head = (snake[0][0] + new_dir[0], snake[0][1] + new_dir[1])
            snake_dir = new_dir

            # Check collision with walls or snake's body
            if (
                new_head[0] < 0
                or new_head[0] >= rows
                or new_head[1] < 0
                or new_head[1] >= cols
                or new_head in snake
            ):
                if new_head in snake:
                    score -= body_collision
                else:
                    score -= wall_collision     
                if turnNum == 0: 
                    score = 0
                break
            
            #insert new_head into the front of snake
            board[new_head[0]][new_head[1]] = 1
            snake.insert(0, new_head)

            # Check collision with food
            if snake[0] == food:
                turnNum = 0
                hunger = 100
                board[food[0]][food[1]] = 1
                if pos >= 4:
                    pos = 0
                #food_row = random.randint(food_quads[pos][0], food_quads[pos][1])
                #food_col = random.randint(food_quads[pos][2], food_quads[pos][3])
                food_row = food_pos[pos][0]
                food_col = food_pos[pos][1]
                #food_row = random.randint(0, rows - 1)
                #food_col = random.randint(0, cols - 1)
                #check that food isn't spawned on top of the snake
                while True:
                    if board[food_row][food_col] == 1:
                        #food_row = random.randint(food_quads[pos][0], food_quads[pos][1])
                        #food_col = random.randint(food_quads[pos][2], food_quads[pos][3])
                        food_row = food_pos[pos][0]
                        food_col = food_pos[pos][1]
                        #food_row = random.randint(food_quads[pos][0], food_quads[pos][1])
                        #food_col = random.randint(food_quads[pos][2], food_quads[pos][3])
                    else:
                        break
                pos += 1
                food = (food_row, food_col)
                board[food[0]][food[1]] = 2
                score += eat_food         
            else:
                #remove the tail from the snake during game iterations without eating the food
                tail = snake.pop()
                board[tail[0]][tail[1]] = 0

            # Draw everything
            screen.fill(BLACK)
            for segment in snake:
                pygame.draw.rect(screen, GREEN, pygame.Rect(segment[1] * SIZE, segment[0] * SIZE, SIZE, SIZE))
            pygame.draw.rect(screen, RED, pygame.Rect(food[1] * SIZE, food[0] * SIZE, SIZE, SIZE))
            pygame.display.update()
            clock.tick(clock_speed)
            survival += 0.01
            hunger -= 1
        pygame.quit()
    else:
        while True:
            if turnNum > 100:
                break
                        
            inputs = updateInputs(snake, board, snake_dir, food[0], food[1], turnNum)
            output = predict(network, inputs, snake_dir)
            new_dir = output[0]
            turn = output[1]
            turnNum += turn
            new_head = (snake[0][0] + new_dir[0], snake[0][1] + new_dir[1])
            snake_dir = new_dir

            # Check collision with walls or snake's body
            if (
                new_head[0] < 0
                or new_head[0] >= rows
                or new_head[1] < 0
                or new_head[1] >= cols
                or new_head in snake
            ):
                if new_head in snake:
                    score -= body_collision
                else:
                    score -= wall_collision 
                if turnNum == 0: 
                    score = 0
                break
                
            #insert new_head into the front of snake
            board[new_head[0]][new_head[1]] = 1
            snake.insert(0, new_head)

            # Check collision with food
            if snake[0] == food:
                turnNum = 0
                hunger = 100
                board[food[0]][food[1]] = 1
                if pos >= 4:
                    pos = 0
                #food_row = random.randint(food_quads[pos][0], food_quads[pos][1])
                #food_col = random.randint(food_quads[pos][2], food_quads[pos][3])
                food_row = food_pos[pos][0]
                food_col = food_pos[pos][1]
                #food_row = random.randint(0, rows - 1)
                #food_col = random.randint(0, cols - 1)
                #check that food isn't spawned on top of the snake
                while True:
                    if board[food_row][food_col] == 1:
                        #food_row = random.randint(food_quads[pos][0], food_quads[pos][1])
                        #food_col = random.randint(food_quads[pos][2], food_quads[pos][3])
                        food_row = food_pos[pos][0]
                        food_col = food_pos[pos][1]
                        #food_row = random.randint(food_quads[pos][0], food_quads[pos][1])
                        #food_col = random.randint(food_quads[pos][2], food_quads[pos][3])
                    else:
                        break
                pos += 1
                food = (food_row, food_col)
                board[food[0]][food[1]] = 2
                score += eat_food      
            else:
                #remove the tail from the snake during game iterations without eating the food
                tail = snake.pop()
                board[tail[0]][tail[1]] = 0
            survival += 0.01
            hunger -= 1
    return max(0, score - (turnNum * 0.01))
    #return max(0, (score + 1) - (turnNum * 0.01) + hunger/100) 
    #MD = abs(snake[0][0] - food[0])/rows + abs(snake[0][1] - food[1])/cols       
    #return max(0, score - (turnNum * 0.01) + survival + (0.2 * 1/(MD + 1)))            

            