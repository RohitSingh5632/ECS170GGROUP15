import pygame
import random
import NEAT_network
import math

WIDTH, HEIGHT, SIZE = 320, 240, 10
# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

#board
rows = int(HEIGHT / SIZE)
cols = int(WIDTH / SIZE)
"""
def updateInputs(snake, board, snake_dir, food_row, food_col, hunger):
    # 0-3: dist above,below,left, and right of food, 
    #4-7: snake_dir NESW
    #8-11: nearest obstacles NESW 
    #12: MD to food, 
    #13: snake length, 
    #14: hunger,
    inputs = [0] * 15
    head = snake[0]
    #how far above the snake's head is the food (if at all)
    inputs[0] = max(0, (head[0] - food_row)/rows)
    #how far to the right of the snake's head is the food (if at all)
    inputs[1] - max(0, (food_col - head[1])/cols)
    #how far below the snake's head is the food (if at all)
    inputs[2] = max(0, (food_row - head[0])/rows)
    #how far to the left of the snake's head is the food (if at all)
    inputs[3] = max(0, (head[1] - food_col)/cols)
    
    #directions
    #up
    if snake_dir == (-1, 0):
        inputs[4] = 1
    #right
    elif snake_dir == (0, 1):
        inputs[5] = 1
    #down
    elif snake_dir == (1, 0):
        inputs[6] = 1
    #left
    elif snake_dir == (0, -1):
        inputs[7] = 1 
        
    #check collisions dist
    #up
    for i in range(head[0] - 1, -1, -1):
        if board[i][head[1]] == 1:
            inputs[8] = i/rows
            break
        inputs[8] = head[0]/rows
    #right
    for i in range(head[1] + 1, cols):
        if board[head[0]][i] == 1:
            inputs[9] = i/cols
            break
        inputs[9] = (cols - head[1])/cols
    #down
    for i in range(head[0] + 1, rows):
        if board[i][head[1]] == 1:
            inputs[10] = i/rows
            break
        inputs[10] = (rows - head[0])/rows
    #left
    for i in range(head[1] - 1, -1, -1):
        if board[head[0]][i] == 1:
            inputs[11] = i/cols
            break
        inputs[11] = head[1]/cols
        
    #calculate MD to food from head
    inputs[12] = abs(snake[0][0] - food_row)/rows + abs(snake[0][1] - food_col)/cols
    #calculate length of snake
    inputs[13] = len(snake)/100
    #add hunger
    inputs[14] = hunger/100

    return inputs
"""
def updateInputs(snake, board, snake_dir, food_row, food_col, turns):
    #0: dist above/below food
    #1: dist left/right of food 
    #2-9: nearest obstacles (N, NE, E, SE, S, SW, W, NW) 
    #10: MD to food
    #11: snake growth,
    #12: turn limit
    #13: up/down dir
    #14: right/left dir
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
    
    inputs[12] = turns/75
    
    #up/down dir
    inputs[13] = snake_dir[0]
    #left/right dir
    inputs[14] = snake_dir[1]


    return inputs
# Initialize pygame

#renders snake body segments



def play(genome, render, pos):
    #state space is represented by a 2D list: 0 = empty, 1 = occupied snake body segment, 2 = occupied by food
    board = [[0 for i in range(cols)] for j in range(rows)]
    
    # Snake and food
    row = int(math.floor(rows/2))
    col = int(math.floor(cols/2))
    snake = [(row, col), (row, col - 1), (row, col - 2), (row, col - 3), (row, col - 4)]
    for segment in snake:
        board[segment[0]][segment[1]] = 1
    snake_dir = (0, 1)#random.choice(dirs)    
    food_row = pos[0]
    food_col = pos[1]
    food = (food_row, food_col)
    board[food_row][food_col] = 2
    
    #parameters
    score = 0
    survival = 0
    turnNum = 0
    
    #render game using pygame or else just update state representation
    if render == True:
        pygame.init()
        # Set up display
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
        # Main game loop
        clock = pygame.time.Clock()
        clock_speed = 50
        while True:
            #if AI spends too much time not collecting food, end sim
            if turnNum >= 500:
                score = 1
                MD = abs(snake[0][0] - food[0])/rows + abs(snake[0][1] - food[1])/cols       
                return max(0, score - (turnNum * 0.01) + survival + (0.2 * 1/(MD + 1)))  
            
            inputs = updateInputs(snake, board, snake_dir, food[0], food[1], turnNum)
            new_dir, turn = genome.predict(inputs, snake_dir)
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
                    score = 0.25
                else:
                    score = 1
                if turnNum == 0:
                    return 0
                MD = abs(snake[0][0] - food[0])/rows + abs(snake[0][1] - food[1])/cols
               # print(score, turnNum * 0.01, survival, (0.2 * 1/(MD + 1)))
            #    print(score - (turnNum * 0.01) + survival + (0.2 * 1/(MD + 1)))
                return max(0, score - (turnNum * 0.01) + survival + (0.2 * 1/(MD + 1)))  
            
            #insert new_head into the front of snake
            board[new_head[0]][new_head[1]] = 1
            snake.insert(0, new_head)

            # Check collision with food
            if snake[0] == food:
                #print(True)
                score = 15
                MD = abs(snake[0][0] - food[0])/rows + abs(snake[0][1] - food[1])/cols       
                return max(0, (score) - (turnNum * 0.01) + survival + (0.2 * 1/(MD + 1)))           
            else:
                #remove the tail from the snake during game iterations without eating the food
                tail = snake.pop()
                board[tail[0]][tail[1]] = 0

            # Draw everything
            screen.fill(BLACK)
            for segment in snake:
                pygame.draw.rect(screen, GREEN, pygame.Rect(segment[1] * SIZE, segment[0] * SIZE, SIZE, SIZE))
            pygame.draw.rect(screen, RED, pygame.Rect(food[1] * SIZE, food[0] * SIZE, SIZE, SIZE))
            pygame.display.flip()
            clock.tick(clock_speed)
            survival += 0.02

        pygame.quit()
    else:
        while True:
            if turnNum > 500:
                score = 1
                MD = abs(snake[0][0] - food[0])/rows + abs(snake[0][1] - food[1])/cols       
                return max(0, score - (turnNum * 0.01) + survival + (0.2 * 1/(MD + 1)))  
                        
            inputs = updateInputs(snake, board, snake_dir, food[0], food[1], turnNum)
            new_dir, turn = genome.predict(inputs, snake_dir)
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
                    score = 0.25
                else:
                    score = 1     
                if turnNum == 0:
                    return 0
                MD = abs(snake[0][0] - food[0])/rows + abs(snake[0][1] - food[1])/cols       
                return max(0, score - (turnNum * 0.01) + survival + (0.2 * 1/(MD + 1)))  
            
            #insert new_head into the front of snake
            board[new_head[0]][new_head[1]] = 1
            snake.insert(0, new_head)

            # Check collision with food
            if snake[0] == food:
                score = 15
                MD = abs(snake[0][0] - food[0])/rows + abs(snake[0][1] - food[1])/cols       
                return max(0, score - (turnNum * 0.01) + survival + (0.2 * 1/(MD + 1)))            
            else:
                #remove the tail from the snake during game iterations without eating the food
                tail = snake.pop()
                board[tail[0]][tail[1]] = 0
            survival += 0.02


def train_food_direction(genome, render):
    score = 0    #NE       #SE       #SW      #NW
    quarter_row = int(math.floor(rows/4))
    quarter_col = int(math.floor(cols/4))
    food_pos = [(6, 24), (18, 24), (18, 6), (6, 6)]
    for i in range(4):
        score += play(genome, render, food_pos[i])
        if score <= 1:
            break
    return score

