from typing import List, Tuple, Optional, Dict, Set
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


# forward checking prunes invalid values from empty cells.. returns false if not able to solve the grid
def forward_checking(board, row, col, num):
    # Temporarily place the number to check its impact
    board[row][col] = num
    
    # check all unassigned cells in the same row
    for k in range(9):
        if k != col and board[row][k] == 0:
            has_valid = False
            for n in range(1, 10):
                if is_valid(board, row, k, n): 
                    has_valid = True
                    break
            if not has_valid:
                board[row][col] = 0  # restore the board state
                return False  # no valid number left for this cell
    
    # check all unassigned cells in the same column
    for i in range(9):
        if i != row and board[i][col] == 0:
            has_valid = False
            for n in range(1, 10):
                if is_valid(board, i, col, n):
                    has_valid = True
                    break
            if not has_valid:
                board[row][col] = 0  # restore the board
                return False  # no valid number left for this cell
    
    # check all unassigned cells in the same subgrid
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            r, c = start_row + i, start_col + j
            if (r != row or c != col) and board[r][c] == 0:
                has_valid = False
                for n in range(1, 10):
                    if is_valid(board, r, c, n):
                        has_valid = True
                        break
                if not has_valid:
                    board[row][col] = 0  # restore the board
                    return False  # no valid number left for this cell
    
    # Restore the board
    board[row][col] = 0
    return True

def backtracking_forward_checking(board, metrics, update_gui=None):
    empty = find_empty(board)
    if not empty:
        return True  
    
    row, col = empty
    for num in range(1, 10):
        if is_valid(board, row, col, num):
            # check if this choice leads to a solvable state
            if not forward_checking(board, row, col, num):
                metrics["pruned"] = metrics.get("pruned", 0) + 1
                continue  # Skip this number if it is unsolvable state
            
            board[row][col] = num
            metrics["steps"] = metrics.get("steps", 0) + 1
            
            if update_gui:
                update_gui(row, col, num)
                pygame.time.delay(20)
            
            if backtracking_forward_checking(board, metrics, update_gui):
                return True
            
            board[row][col] = 0
            metrics["backtracking"] = metrics.get("backtracking", 0) + 1
    
    return False


# AC-3 Algorithm Implementation


def get_peers(row: int, col: int) -> Set[Tuple[int, int]]:
    """Get all cells that share a row, column, or subgrid with (row, col)."""
    peers = set()
    
    # Same row
    for i in range(9):
        if i != col:
            peers.add((row, i))
    
    # Same column
    for i in range(9):
        if i != row:
            peers.add((i, col))
    
    # Same subgrid
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            r, c = start_row + i, start_col + j
            if r != row or c != col:
                peers.add((r, c))
    
    return peers

def revise(board: List[List[int]], xi: int, xj: int, yi: int, yj: int) -> bool:
    """Revise the domain of cell (xi, xj) based on constraints with (yi, yj)."""
    revised = False
    
    # Check all possible values for (xi, xj)
    for num in range(1, 10):
        if is_valid(board, xi, xj, num):
            valid_found = False
            
            # Check if there's at least one valid value for (yi, yj) ≠ num
            for n in range(1, 10):
                if n != num and is_valid(board, yi, yj, n):
                    valid_found = True
                    break
            
            # If no valid value found for (yi, yj), remove num from (xi, xj)'s domain
            if not valid_found:
                board[xi][xj] = 0
                revised = True
    
    return revised

def ac3(board: List[List[int]]) -> bool:
    """Apply Arc Consistency Algorithm (AC-3) to reduce the board's domains."""
    queue = []
    
    # Initialize queue with all arcs (X, Y) where X and Y are peers
    for row in range(9):
        for col in range(9):
            peers = get_peers(row, col)
            for (p_row, p_col) in peers:
                queue.append(((row, col), (p_row, p_col)))
    
    # Process each arc in the queue
    while queue:
        (xi, xj), (yi, yj) = queue.pop(0)
        
        if revise(board, xi, xj, yi, yj):
            # If domain of (xi, xj) becomes empty, return failure
            if board[xi][xj] == 0:
                has_valid = False
                for num in range(1, 10):
                    if is_valid(board, xi, xj, num):
                        has_valid = True
                        break
                if not has_valid:
                    return False
            
            # Add all peers of (xi, xj) to queue for re-checking
            for (neighbor_row, neighbor_col) in get_peers(xi, xj):
                if (neighbor_row, neighbor_col) != (yi, yj):
                    queue.append(((neighbor_row, neighbor_col), (xi, xj)))
    
    return True

def backtracking_ac3(board: List[List[int]], metrics: Dict, update_gui=None) -> bool:
    """Solve Sudoku using backtracking after applying AC-3."""
    # First apply AC-3 to reduce the search space
    if not ac3(board):
        return False
    
    # Proceed with regular backtracking
    return backtracking(board, metrics, update_gui)


# Hybrid Algorithm Implementation
def hybrid_solver(board: List[List[int]], metrics: Dict, update_gui=None) -> bool:
    ac3(board)
    return backtracking_mrv(board, metrics, update_gui)



                  
