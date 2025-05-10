import pygame
import sys

# ------------------------------
# 1. Initialize Pygame Settings
# ------------------------------

WIDTH, HEIGHT = 550, 680  # 540x540 grid + 140px space for buttons/info
ROWS, COLS = 9, 9 
CELL_SIZE = WIDTH // COLS

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_BG = (30, 30, 40)
DARKER_BG = (20, 20, 30)
GRAY = (100, 100, 120)
LIGHT_GRAY = (140, 140, 160)
RED = (255, 80, 80)
GREEN = (80, 220, 100)
BLUE = (80, 170, 255)
HIGHLIGHT = (60, 60, 80)

# Game state
selected_cell = None
original_board = [
    [0, 0, 0, 0, 7, 0, 0, 0, 9],
    [4, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 8, 0, 9, 0, 0, 0, 3, 0],
    [0, 0, 3, 0, 0, 4, 0, 7, 0],
    [0, 7, 0, 0, 0, 0, 0, 5, 0],
    [0, 6, 0, 3, 0, 0, 4, 0, 0],
    [0, 1, 0, 0, 0, 5, 0, 9, 0],
    [0, 0, 2, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 1, 0, 0, 0, 0]
]
board = [row[:] for row in original_board]  # Create a deep copy
fixed_cells = [[board[i][j] != 0 for j in range(COLS)] for i in range(ROWS)]
status_message = "Select a cell and use number keys to input values"
active_algorithm = None
button_name_mapping = {}

# ------------------------------
# 2. Drawing Functions
# ------------------------------

def draw_board(screen):
    # Fill background
    screen.fill(DARK_BG, (0, 0, WIDTH, WIDTH))
    
    # Draw grid lines
    for i in range(ROWS + 1):
        thickness = 4 if i % 3 == 0 else 1
        pygame.draw.line(screen, GRAY, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), thickness)
        pygame.draw.line(screen, GRAY, (i * CELL_SIZE, 0), (i * CELL_SIZE, WIDTH), thickness)

    # Highlight selected cell
    if selected_cell:
        row, col = selected_cell
        pygame.draw.rect(screen, HIGHLIGHT, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
        # Highlight same row and column lightly
        for i in range(9):
            if i != col:
                pygame.draw.rect(screen, DARKER_BG, (i * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            if i != row:
                pygame.draw.rect(screen, DARKER_BG, (col * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
        # Highlight 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if i != row or j != col:
                    pygame.draw.rect(screen, DARKER_BG, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Draw numbers
    for i in range(ROWS):
        for j in range(COLS):
            num = board[i][j]
            if num != 0:
                color = WHITE if fixed_cells[i][j] else BLUE
                text = number_font.render(str(num), True, color)
                text_rect = text.get_rect(center=(j * CELL_SIZE + CELL_SIZE // 2, i * CELL_SIZE + CELL_SIZE // 2))
                screen.blit(text, text_rect)

    # Redraw grid lines on top
    for i in range(ROWS + 1):
        thickness = 4 if i % 3 == 0 else 1
        pygame.draw.line(screen, GRAY, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), thickness)
        pygame.draw.line(screen, GRAY, (i * CELL_SIZE, 0), (i * CELL_SIZE, WIDTH), thickness)

def draw_buttons(screen, buttons):
    # Draw status bar background
    pygame.draw.rect(screen, DARKER_BG, (0, WIDTH, WIDTH, HEIGHT - WIDTH))
    
    # Draw status message
    status_text = status_font.render(status_message, True, LIGHT_GRAY)
    screen.blit(status_text, (10, WIDTH + 5))
    
    # Draw buttons
    for name, rect in buttons.items():
        # Change button color if active
        if name == active_algorithm:
            button_color = GREEN
        else:
            button_color = GRAY
            
        pygame.draw.rect(screen, button_color, rect)
        pygame.draw.rect(screen, LIGHT_GRAY, rect, 2)  # Button border
        
        # Use a smaller font for button text
        text = button_font.render(name, True, BLACK if name == active_algorithm else WHITE)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

# ------------------------------
# 3. Interaction Handling
# ------------------------------

def handle_mouse_click(pos, buttons):
    global selected_cell, active_algorithm, status_message
    
    x, y = pos
    
    # Check if click is on the board
    if y < WIDTH:
        col = x // CELL_SIZE
        row = y // CELL_SIZE
        selected_cell = (row, col)
        status_message = f"Selected cell: {row+1},{col+1}"
        return
    
    # Check if click is on a button
    for name, rect in buttons.items():
        if rect.collidepoint(pos):
            if name == "Reset":
                reset_board()
                status_message = "Board reset to initial state"
            else:
                algorithm_name = button_name_mapping[name]
                active_algorithm = name
                status_message = f"Algorithm: {name} selected"
            return

def handle_key_press(key):
    global board, status_message
    
    if selected_cell is None:
        return
        
    row, col = selected_cell
    
    # Don't modify fixed cells
    if fixed_cells[row][col]:
        status_message = "Cannot modify fixed cells"
        return
        
    # Handle number inputs (1-9)
    if pygame.K_1 <= key <= pygame.K_9:
        number = key - pygame.K_0  # Convert key code to number
        board[row][col] = number
        status_message = f"Entered {number} at {row+1},{col+1}"
    
    # Delete/backspace/0 clears the cell
    elif key in (pygame.K_DELETE, pygame.K_BACKSPACE, pygame.K_0):
        board[row][col] = 0
        status_message = f"Cleared cell {row+1},{col+1}"

# ------------------------------
# 4. Animation & Updates
# ------------------------------

def update_cell(row, col, value, delay=20):
    """Update a specific cell with animation"""
    global board
    board[row][col] = value
    
    # Draw the updated state
    screen.fill(DARKER_BG)
    draw_board(screen)
    draw_buttons(screen, get_button_rects())
    
    # Highlight the updated cell
    if not fixed_cells[row][col]:
        pygame.draw.rect(screen, GREEN, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
    
    pygame.display.flip()
    pygame.time.delay(delay)

# ------------------------------
# 5. Utility Functions
# ------------------------------

def get_button_rects():
    """Return dictionary of button positions and sizes."""
    # Map pretty names to actual algorithm names
    global button_name_mapping
    button_name_mapping = {
        "Backtracking": "backtracking",
        "MRV": "backtracking_mrv",
        "Forward Checking": "backtracking_forward_checking",
        "AC-3": "backtracking_ac3",
        "Hybrid": "hybrid_solver",
        "Reset": "Reset"
    }
    
    names = list(button_name_mapping.keys())
    buttons = {}
    
    # Use 2 rows of 3 buttons each
    button_width = 170
    button_height = 35
    margin = 10
    
    # First row (3 buttons)
    y = WIDTH + 25
    for i, name in enumerate(names[:3]):
        x = margin + i * (button_width + margin)
        rect = pygame.Rect(x, y, button_width, button_height)
        buttons[name] = rect
    
    # Second row (3 buttons)
    y = WIDTH + 25 + button_height + margin
    for i, name in enumerate(names[3:]):
        x = margin + i * (button_width + margin)
        rect = pygame.Rect(x, y, button_width, button_height)
        buttons[name] = rect
        
    return buttons

def reset_board():
    """Reset the board to its original state"""
    global board, selected_cell, active_algorithm
    board = [row[:] for row in original_board]
    selected_cell = None
    active_algorithm = None

def gameQuit():
    pygame.quit()
    sys.exit()

def gameInitialize():
    pygame.init()

    global screen, number_font, button_font, status_font
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sudoku Solver - Dark Mode")

    number_font = pygame.font.SysFont("arial", 36, bold=True)
    button_font = pygame.font.SysFont("arial", 14, bold=True)
    status_font = pygame.font.SysFont("arial", 14)
    clock = pygame.time.Clock()
    buttons = get_button_rects()

    running = True
    while running:
        screen.fill(DARKER_BG)
        draw_board(screen)
        draw_buttons(screen, buttons)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_mouse_click(event.pos, buttons)
            elif event.type == pygame.KEYDOWN:
                handle_key_press(event.key)

        pygame.display.flip()
        clock.tick(60)
    
    gameQuit()

# This function would be called by external algorithm implementations
def visualize_solution_step(row, col, value):
    """
    Visualize a single step of the solution process.
    This function would be called by the algorithm implementations.
    """
    update_cell(row, col, value)

# Function to execute the selected algorithm
def execute_algorithm():
    """
    This function would be called to execute the currently selected algorithm.
    It returns the name of the algorithm to be called externally.
    """
    if active_algorithm is None:
        return None
    
    algorithm_name = button_name_mapping[active_algorithm]
    return algorithm_name

# Function to get the current board state
def get_current_board():
    """Returns the current state of the board."""
    return board

gameInitialize()