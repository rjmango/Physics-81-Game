import random

# Define constants
CELL = 'c'
WALL = 'w'
UNVISITED = 'u'
HEIGHT = 10
WIDTH = 15

# Initialize maze
maze = [[UNVISITED for _ in range(WIDTH)] for _ in range(HEIGHT)]

# Function to print maze
def print_maze(maze):
    for row in maze:
        print(' '.join(row))

# Function to initialize maze
def init_maze(width, height):
    maze = [[UNVISITED for _ in range(width)] for _ in range(height)]
    return maze

# Function to create entrance and exit
def create_entrance_exit(width, height):
    for i in range(0, width):
        if maze[1][i] == CELL:
            maze[0][i] = CELL
            break
    for i in range(width-1, 0, -1):
        if maze[height-2][i] == CELL:
            maze[height-1][i] = CELL
            break

# Function to check surrounding cells
def surroundingCells(rand_wall):
    s_cells = 0
    if maze[rand_wall[0]-1][rand_wall[1]] == CELL:
        s_cells += 1
    if maze[rand_wall[0]+1][rand_wall[1]] == CELL:
        s_cells += 1
    if maze[rand_wall[0]][rand_wall[1]-1] == CELL:
        s_cells += 1
    if maze[rand_wall[0]][rand_wall[1]+1] == CELL:
        s_cells += 1
    return s_cells

# Function to delete wall
def delete_wall(rand_wall):
    for wall in walls:
        if wall[0] == rand_wall[0] and wall[1] == rand_wall[1]:
            walls.remove(wall)

# Create maze
maze = init_maze(WIDTH, HEIGHT)

# Choose a random starting point
starting_height = random.randint(1, HEIGHT-2)
starting_width = random.randint(1, WIDTH-2)

# Mark starting point as cell and add surrounding walls to list
maze[starting_height][starting_width] = CELL
walls = [
    [starting_height-1, starting_width],
    [starting_height, starting_width-1],
    [starting_height, starting_width+1],
    [starting_height+1, starting_width]
]

# Create maze using Prim's algorithm
while walls:
    rand_wall = walls.pop(random.randint(0, len(walls)-1))
    
    # Ensure wall is within bounds
    if rand_wall[0] > 0 and rand_wall[0] < HEIGHT-1 and rand_wall[1] > 0 and rand_wall[1] < WIDTH-1:
        if maze[rand_wall[0]][rand_wall[1]] == UNVISITED:
            s_cells = surroundingCells(rand_wall)
            if s_cells == 1:  # Ensure only one adjacent cell is a path
                maze[rand_wall[0]][rand_wall[1]] = CELL
                walls.extend([
                    [rand_wall[0]-1, rand_wall[1]],
                    [rand_wall[0], rand_wall[1]-1],
                    [rand_wall[0], rand_wall[1]+1],
                    [rand_wall[0]+1, rand_wall[1]]
                ])

# Create entrance and exit
create_entrance_exit(WIDTH, HEIGHT)

# Print maze
# print_maze(maze)

# Convert maze to 2D array format
def convert_maze_to_array(maze):
    maze_array = []
    for row in maze:
        row_array = []
        for cell in row:
            if cell == CELL:
                row_array.append(0)
            else:
                row_array.append(1)
        maze_array.append(row_array)
    return maze_array

# Convert maze to 2D array
maze_array = convert_maze_to_array(maze)