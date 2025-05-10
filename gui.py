import pygame

# ------------------------------
# 1. Initialize Pygame Settings
# ------------------------------

WIDTH, HEIGHT = 540, 600  # 540x540 grid + 60px space for buttons/info
ROWS, COLS = 9, 9 
CELL_SIZE = WIDTH // COLS

# Colors
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
RED = (255, 0, 0)

def gameInitialize():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sudoku_CSP")

    number_font = pygame.font.SysFont("arial", 40)
    button_font = pygame.font.SysFont("arial", 30)
    clock = pygame.time.Clock()

    running = True
    while running:
        screen.fill(BLACK)
        draw_board(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # TODO: Handle input here

        pygame.display.flip()
        clock.tick(60)

# ------------------------------
# 2. Drawing Functions
# ------------------------------

def draw_board(screen):
    for i in range(ROWS + 1):
        thickness = 4 if i % 3 == 0 else 1
        pygame.draw.line(screen, GRAY, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), thickness)
        pygame.draw.line(screen, GRAY, (i * CELL_SIZE, 0), (i * CELL_SIZE, WIDTH), thickness)

    """
    Draw the Sudoku grid and numbers.
    TODO:
    1. Draw 9x9 grid with thick lines for 3x3 subgrids
    2. Render numbers from the board
    3. Highlight selected cell with a colored border
    4. Display performance metrics at the bottom
    """
    pass

def draw_buttons(screen, buttons):
    """
    Draw algorithm selection buttons.
    TODO:
    1. Create buttons for each algorithm:
       - Backtracking
       - MRV
       - Forward Checking
       - AC-3
       - Hybrid
       - Reset
    2. Add hover/click visual feedback
    """
    pass

# ------------------------------
# 3. Interaction Handling
# ------------------------------

def handle_mouse_click(pos, buttons):
    """
    Determine which button or cell was clicked.
    TODO:
    1. Map mouse position to grid cell coordinates
    2. Check if click was inside any button area
    """
    pass

# ------------------------------
# 4. Animation & Updates
# ------------------------------

def update_gui(row, col):
    """
    Animate the solving process.
    TODO:
    1. Highlight current cell being processed
    2. Add small delay for visibility
    3. Refresh display
    """
    pass

# ------------------------------
# 5. Utility Functions
# ------------------------------

def get_button_rects():
    """
    Return dictionary of button positions and sizes.
    TODO: Define precise coordinates for each algorithm button
    """
    pass

def gameQuit():
    pygame.quit()
    sys.exit()

gameInitialize()