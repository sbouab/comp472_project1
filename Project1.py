# Project1 code for the first project of COMP472 - AI class at Concordia University.
# Written by: Soufiane Bouabdallah - ID: 40029995
# Description: Implementation of a DFS approach to find a solution to the Indonesian puzzle.
#   Takes an input file with multiple lines (puzzles), each one containing the size of the puzzle, 
#   the max depth parameter and the initial configuration of the board.

# importing necessary libraries to read input from the command line and the puzzle file and to store board configurations
import sys
import copy
from ordered_set import OrderedSet

# Node object which stores a board configuation, the parent from which it was generated, the depth and the move from which it was born
class Node:
    def __init__(self, board, parent, depth, born_from):
        self.board = board
        self.parent = parent
        self.depth = depth
        self.born_from = born_from

# overwrites the '==' so that two objects are considered the same if they have the same board configuration
    def __eq__(self, other):
        return self.board == other.board

# function which flips the targeted tile by modifying (from 0 to 1 or from 1 to 0) the character of the string to which the tile corresponds
def flip(board, tile_index):
    if board[tile_index] == '1':
        board = board[:tile_index] + '0' + board[tile_index + 1:]
    else:
        board = board[:tile_index] + '1' + board[tile_index + 1:]
    return board

# function which returns a string representation of the binary number which represents the configuration of the board
def binary_to_string(board):
    board = bin(board)
    board = board[2:]
    # prepend any '0' if they have been cut after using the bin() function
    while len(board) != last_tile_index+1:
        board = '0' + board
    return board

# function which flips the tile and the tiles around it following the rules of the game
def move(parent_node, index_to_move):
    # creates a new Node object with according parameters
    child_node = Node(copy.deepcopy(parent_node.board), parent_node, parent_node.depth+1, "-")
    # gets a string representation of the board
    child_node.board = binary_to_string(child_node.board)
    # logical conditions which flip the correct tiles around flipped tile
    # if the tile to flip is in the first row
    if index_to_move < n:
        # flip the tile itself and the tile below it
        child_node.board = flip(child_node.board, index_to_move)
        child_node.board = flip(child_node.board, index_to_move+n)
        # if the tile to flip is the left corner, flip the tile right to it
        if index_to_move == 0:
            child_node.board = flip(child_node.board, index_to_move+1)
        # if the tile to flip is the right corner, flip the tile left to it
        elif index_to_move == n-1:
            child_node.board = flip(child_node.board, index_to_move-1)
        # else, flip the right and left tiles
        else:
            child_node.board = flip(child_node.board, index_to_move+1)
            child_node.board = flip(child_node.board, index_to_move-1)
    # if the tile to flip is in the last row
    elif index_to_move > (last_tile_index - n):
        # flip the tile itself and the tile above it
        child_node.board = flip(child_node.board, index_to_move)
        child_node.board = flip(child_node.board, index_to_move-n)
        # if the tile is the left corner, flip the tile right to it
        if index_to_move == (last_tile_index - (n-1)):
            child_node.board = flip(child_node.board, index_to_move+1)
        # if the tile is the right corner, flip the tile left to it
        elif index_to_move == last_tile_index:
            child_node.board = flip(child_node.board, index_to_move-1)
        # else, flip the right and left tiles
        else:
            child_node.board = flip(child_node.board, index_to_move+1)
            child_node.board = flip(child_node.board, index_to_move-1)
    # else, the tile is between the first and last row
    else:
        # flip the tile itself and the tiles above and below it
        child_node.board = flip(child_node.board, index_to_move)
        child_node.board = flip(child_node.board, index_to_move+n)
        child_node.board = flip(child_node.board, index_to_move-n)
        # if the tile is in the leftmost column, flip the tile right to it
        if (index_to_move % n) == 0:
            child_node.board = flip(child_node.board, index_to_move+1)
        # if the tile is in the rightmost column, flip the tile left to it
        elif (index_to_move % n == n-1):
            child_node.board = flip(child_node.board, index_to_move-1)
        # else, flip the right and left tiles
        else:
            child_node.board = flip(child_node.board, index_to_move+1)
            child_node.board = flip(child_node.board, index_to_move-1)
    # transform string back to binary
    child_node.board = int(child_node.board, 2)
    # add born_from parameter to the node with rows being letters and numbers being columns (e.g. 'C3')
    child_node.born_from = chr(ord('@')+((index_to_move//n)+1)) + str((index_to_move%n)+1)
    return child_node

# depth first search brute-force algorithm
def dfs(n, max_d, initial_board, puzzle_index):
    # initialize open list as a stack and append the initial state of the board to it
    open_list = []
    # closed list initialized as an ordered set to speed-up lookup and avoid duplicate board configurations
    closed_list = OrderedSet()
    open_list.append(Node(initial_board, None, 1, "0"))

    # create string with correct length representing the winning board configuration
    winning_string = ""
    temp_counter = 0
    while temp_counter != last_tile_index+1:
        winning_string += '0'
        temp_counter += 1
    winning_board = int(winning_string, 2)

    # flag which shows if a solution has been found
    solution_found = 0

    # while we still have nodes to analyze
    while len(open_list) != 0:
        # pop element from the list
        current_config = open_list.pop()

        # check if we have the solved board
        if current_config.board == winning_board:
            # add the winning configuration to the closed list
            closed_list.add(current_config.board)
            # show that a solution has been found
            solution_found = 1
            # use node.parent and node.born_from parameters to trace the solution path and write it to the file
            output_solution_list = []
            while(current_config.depth != 1):
                output_solution_list.append(current_config.born_from + "\t" + binary_to_string(current_config.board) + "\n")
                current_config = current_config.parent
            output_solution_list.append(current_config.born_from + "\t" + binary_to_string(current_config.board) + "\n")
            output_solution_file = open(str(puzzle_index) + "_dfs_solution.txt", "w")
            for element in reversed(output_solution_list):
                output_solution_file.write(element)
            break
        
        # if we have reached the maximum depth, don't analyze any deeper
        elif current_config.depth == max_d:
            closed_list.add(current_config.board)

        else:
            # add current board configuration to closed list
            closed_list.add(current_config.board)
            # initialize a temporary open list which will store the children of the current node
            temp_openlist = []
            # generate each possible move from the current configuration and if it hasn't already been visited, append to the temporary open list
            for tile_index in range(0, last_tile_index+1):
                child_config = move(current_config, tile_index)
                if child_config.board not in closed_list:
                    temp_openlist.append(child_config)
            # sort children to prioritize them following a top-down, left-right approach (as per requirement)
            temp_openlist.sort(key=lambda x: x.board, reverse=True)
            # append the sorted elements to the stack and delete the temporary open list
            open_list = open_list + temp_openlist
            del temp_openlist

    # if we have exhausted our search and no solution has been found, write "no solution" to the solution file
    if solution_found == 0:
        output_solution_file = open(str(puzzle_index)+"_dfs_solution.txt", "w")
        output_solution_file.write("no solution")

    # regardless of solution, write the search path to the search file using the closed list    
    output_search_file = open(str(puzzle_index)+"_dfs_search.txt", "w")
    for element in closed_list:
        output_search_file.write("0\t0\t0\t" + binary_to_string(element) + "\n")

# read input_file path
input_file = open(sys.argv[1], 'r')
# puzzle_index used for naming the solution and search files
puzzle_index = 0
# for each puzzle in the input_file, call the DFS algorithm to try to solve it
for puzzle in input_file:
    # parse the line to get the puzzle parameters
    puzzle = puzzle.split()
    # row (and column) length of the puzzle
    n = int(puzzle[0])
    # maximum depth
    max_d = int(puzzle[1])
    # maximum length
    max_l = int(puzzle[2])
    # last_tile_index calculated right away to facilitate work later on
    last_tile_index = (n*n)-1
    # initial board configuration
    initial_board = int(puzzle[3], 2)
    # calling the algorithm
    dfs(n, max_d, initial_board, puzzle_index)
    # increment puzzle_index for the next puzzle to solve
    puzzle_index += 1