from typing import List, Tuple, Optional, Dict
import time
import pygame



def is_valid(board: List[List[int]], row: int, col: int, num: int) -> bool:
    # Check for duplicates in the same row of col
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
        
    # Check for duplicates in the same 3x3 grid
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def find_empty(board: List[List[int]]) -> Optional[Tuple[int, int]]:
    # Findes the first empty cell valued 0 
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None


# Core Algorithm: Backtracking


def backtracking(board: List[List[int]], metrics: Dict, update_gui=None) -> bool:
    
    # Finding the next empty cell
    empty = find_empty(board)
    if not empty:
        return True
    
    # testing 1 to 9 in the empty cell
    row, col = empty
    for num in range(1,10):
        # Validating the tested number
        if is_valid(board, row, col, num):
            board[row][col] = num 
            metrics["steps"] += 1 # track the progress
            
            # highlight the currnt cell being process
            if update_gui: 
                update_gui(row, col,num)
                pygame.time.delay(20)
            
            # recursive call to going DFS to find the solution
            if backtracking(board, metrics, update_gui):
                return True
            
            board[row][col] = 0
            metrics["backtracking"] +=1 # track the number of backtrack
    return False
  


# MRV Heuristic Implementation



def find_mrv(board: List[List[int]]) -> Optional[Tuple[int, int]]:
    min_cell = None
    min_options = 10 #starting with number that higher than 9
   
    for i in range(9):
        for j in range(9):
           # checking the empty cells
            if board[i][j] == 0: 
                # counting the valid numbers for the cell
                options = sum(1 for num in range(1, 10) if is_valid(board, i, j, num))
                if options < min_options:
                    min_options = options
                    min_cell = (i,j)
    return min_cell

def backtracking_mrv(board: List[List[int]], metrics: Dict, update_gui=None) -> bool:

    # using find MRV
    empty = find_mrv(board)
    if not empty:
        return True 
    
    row, col = empty
    for num in range(1, 10):
        if is_valid(board, row, col, num):
            board[row][col] = num
            metrics["steps"] += 1
            
            if update_gui:
                update_gui(row, col,num)
                pygame.time.delay(20)

            if backtracking_mrv(board, metrics, update_gui):
                return True

            board[row][col] = 0
            metrics["backtracks"] += 1

    return False


# Forward Checking Implementation


# forward checking prunes invalid values form the empty cells.. returns false if not able to solve the cell
def forward_checking(board: List[List[int]], row: int, col: int, num: int) -> bool:
    # check all cells in the same row
    for i in range(9):
        if board[row][i] == 0:  # checks only the empty cells
            has_valid = False
            for n in range(1, 10): 
                if n != num and is_valid(board, row, i, n):
                    has_valid = True
                    break  # at least there is one valid number
            if not has_valid:
                return False  

    # check all cells in the same column
    for i in range(9):
        if board[i][col] == 0: 
            has_valid = False
            for n in range(1, 10):
                if n != num and is_valid(board, i, col, n):
                    has_valid = True
                    break
            if not has_valid:
                return False

    # Check all cells in the 3x3 subgrid
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == 0: 
                has_valid = False
                for n in range(1, 10):
                    if n != num and is_valid(board, start_row + i, start_col + j, n):
                        has_valid = True
                        break
                if not has_valid:
                    return False

    return True

def backtracking_forward_checking(board: List[List[int]], metrics: Dict, update_gui=None) -> bool:
   
    empty = find_empty(board)
    if not empty:
        return True  
    
    row, col = empty
    for num in range(1, 10):  
        if is_valid(board, row, col, num):  
            if not forward_checking(board, row, col, num):
                continue  # skip this number if it is not solvable

            board[row][col] = num
            metrics["steps"] += 1

            if update_gui:
                update_gui(row, col,num)
                pygame.time.delay(20)

            # recurse call to solve the rest
            if backtracking_forward_checking(board, metrics, update_gui):
                return True

            # backtrack if could not find solution
            board[row][col] = 0
            metrics["backtracking"] += 1

    return False



# AC-3 Algorithm Implementation



def ac3(board: List[List[int]]) -> bool:
   def ac3(board):
       
    # building a queue of arcs (cell pairs (x,y)) wher x and y shars row, col, or subgrid
    queue = []
    for i in range(9):
        for j in range(9):
            for k in range(9):
                for l in range(9):
                    if board[i][j] == 0 and board[k][l] == 0:
                        same_row = (i == k)
                        same_col = (j == l)
                        same_subgrid = (3*(i//3) <= k < 3*(i//3 + 1)) and (3*(j//3) <= l < 3*(j//3 + 1))
                        if same_row or same_col or same_subgrid:
                            queue.append(((i, j), (k, l)))
    
    while queue:
        (x1, y1), (x2, y2) = queue.pop(0)
        if revise(board, x1, y1, x2, y2):
            # check if cell has no valid values left
            if board[x1][y1] == 0:
                has_valid = False
                for n in range(1, 10):
                    if is_valid(board, x1, y1, n):
                        has_valid = True
                        break
                if not has_valid:
                    return False  
            
            # adding the neighbors again to queue
            for neighbor in get_neighbors(x1, y1):
                if board[neighbor[0]][neighbor[1]] == 0:
                    queue.append((neighbor, (x1, y1)))
    
    return True


def revise(board, x1, y1, x2, y2):
    revised = False
    for num in range(1, 10):
        #testing all possible values for X1 then if the num is valid for x1
        if is_valid(board, x1, y1, num):
            valid_for_neighbor = False
            # chicking for a valid value for x2
            for n in range(1, 10):
                if n != num and is_valid(board, x2, y2, n):
                    valid_for_neighbor = True
                    break
            if not valid_for_neighbor:
                board[x1][y1] = 0 # removing the num from x1 domain
                revised = True
    return revised


def get_neighbors(row, col):
    neighbors = []
    # Same column
    for i in range(9):
        if i != row:
            neighbors.append((i, col))
    # Same row
    for i in range(9):
        if i != col:
            neighbors.append((row, i))
    # Same subgrid
    start_row = 3 * (row // 3)
    start_col = 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            r = start_row + i
            c = start_col + j
            if r != row or c != col:
                neighbors.append((r, c))
    return neighbors

def backtracking_ac3(board: List[List[int]], metrics: Dict, update_gui=None) -> bool:
    ac3(board)
    return backtracking(board, metrics, update_gui)


# Hybrid Algorithm Implementation
def hybrid_solver(board: List[List[int]], metrics: Dict, update_gui=None) -> bool:
    ac3(board)
    return backtracking_mrv(board, metrics, update_gui)


# Metrics Collection System

def initialize_metrics() -> Dict:
    return {
        "algorithm": "",
        "time": 0,
        "backtracking": 0,
        "steps": 0,
        "solved": False
    }

                  
