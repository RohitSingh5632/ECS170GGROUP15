import pygame
import pygame.font
import time
import random
import snake_Astar


# Initialize pygame
pygame.init()

# Set up display
WIDTH, HEIGHT, SIZE = 640, 480, 10
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")


#board
rows = int(HEIGHT / SIZE)
cols = int(WIDTH / SIZE)

#state space is represented by a 2D list: 0 = empty, 1 = occupied snake body segment, 2 = occupied by food
board = [[0 for i in range(cols)] for j in range(rows)]

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (200, 200, 0)

# Snake and food
snake = [(10, 10)]
board[snake[0][0]][snake[0][1]] = 1
snake_dir = (1, 0)
food_row = random.randint(0, rows - 1)
food_col = random.randint(0, cols - 1)
food = (food_row, food_col)
board[food_row][food_col] = 2

# initialized font and counter
font = pygame.font.Font(None, 36)
counter = 0

#get a list of actions for snake to take to reach food using A* search
actions = actions = snake_Astar.Astar(snake_Astar.Board(board, snake, None, food))

# initialize the clock
start_time = int(time.time())

# Main game loop
clock = pygame.time.Clock()
running = True
score = 0

#renders snake body segments
def draw_snake(snake):
    for segment in snake:
        pygame.draw.rect(screen, GREEN, pygame.Rect(segment[1] * SIZE, segment[0] * SIZE, SIZE, SIZE))

while running: 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # get the current time
    current_time = int(time.time())

    elapsed_time = current_time - start_time

    clock_text = font.render(f'Time: {elapsed_time}', True, GREEN)

    new_head = [0]

    # Update snake position with new_head based on direction given by actions
    if len(actions) > 0:
        #directions in actions are returned in reverse order, so the first direction is last
        new_dir = actions.pop()
        new_head = (snake[0][0] + new_dir[0], snake[0][1] + new_dir[1])
    
    # Check collision with walls or snake's body
    if (
        new_head[0] < 0
        or new_head[0] >= rows
        or new_head[1] < 0
        or new_head[1] >= cols
        or new_head in snake
    ):
        running = False
        continue

    #insert new_head into the front of snake
    board[new_head[0]][new_head[1]] = 1
    snake.insert(0, new_head)

    # Check collision with food
    if snake[0] == food:
        board[food[0]][food[1]] = 1
        food_row = random.randint(0, rows - 1)
        food_col = random.randint(0, cols - 1)
        #check that food isn't spawned on top of the snake
        while True:
            if board[food_row][food_col] == 1:
                food_row = random.randint(0, rows - 1)
                food_col = random.randint(0, cols - 1)
            else:
                break
        food = (food_row, food_col)
        board[food[0]][food[1]] = 2
        score += 1

        actions = snake_Astar.Astar(snake_Astar.Board(board, snake, new_dir, food))

        

        #if there is no path to the food, end the game
        if actions == None:
            print(score)
            start_time = int(time.time())
            break
    else:
        #remove the tail from the snake during game iterations without eating the food
        tail = snake.pop()
        board[tail[0]][tail[1]] = 0

    # Render the counter text
    score_text = font.render(f'Score: {score}', True, YELLOW)

    # Render the clock text
    clock_text = font.render(f'Time: {elapsed_time}', True, YELLOW)
   

    # Draw everything
    screen.fill(BLACK)
    draw_snake(snake)
    pygame.draw.rect(screen, RED, pygame.Rect(food[1] * SIZE, food[0] * SIZE, SIZE, SIZE))\
    
    # Draw the score and clock text
    screen.blit(clock_text, (10, 40))
    screen.blit(score_text, (10, 10))


    #Update Display
    pygame.display.flip()

    #screen.fill(BLACK)

    clock.tick(30)

pygame.quit()
