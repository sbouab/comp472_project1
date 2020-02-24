# Project3 code for the first project of COMP472 - AI class at Concordia University.
# Written by: Soufiane Bouabdallah - ID: 40029995
# Description: Program which reads the Indonesian puzzle inputs (initial board configurations) from a text file and uses various algorithms to try and find a solution to them.
#              While doing so, it keeps track of the search path for each algorithm and shows the solution path found (if it is the case).

# importing the necessary libraries for the program to run
import sys, copy, heapq, itertools, os
from ordered_set import OrderedSet

# Node object which stores a board configuation, the parent from which it was generated, its depth, the move from which it was born and the clicked tile tracker (only used for the custom A* algorithm, i.e. heuristic #2)
class Node:
    def __init__(self, board, parent, depth, born_from, clicked):
        self.board = board
        self.parent = parent
        self.depth = depth
        self.born_from = born_from
        self.clicked = clicked

    # override '==' so that two objects are considered the same if they have the same board configuration
    def __eq__(self, other):
        return self.board == other.board

    # - simply return False if two h(n) are the same for BFS
    # - check for smallest depth for A* & custom A* and if it's the same, simply return False
    def __lt__(self, other):
        if bfs_running == 1:
            return False
        if astar_running == 1 or custom_astar_running == 1:
            if (self.depth < other.depth):
                return True
            else:
                return False

# function which returns a string representation of the binary number which represents the configuration of the board
def binary_to_string(board):
    board = bin(board)
    board = board[2:]
    # prepend any '0' if they have been cut after using the bin() function
    while len(board) != last_tile_index+1:
        board = '0' + board
    return board

# function which flips the targeted tile by modifying (from 0 to 1 or from 1 to 0) the character of the string to which the tile corresponds
def flip(board, tile_index):
    if board[tile_index] == '1':
        board = board[:tile_index] + '0' + board[tile_index + 1:]
    else:
        board = board[:tile_index] + '1' + board[tile_index + 1:]
    return board

# function which keeps track of clicked tiles so that the same tile isn't flipped more than once
def clicked(clicked, tile_index):
    # if tile wasn't already clicked, click and mark it as clicked
    if clicked[tile_index] == 'n':
        clicked = clicked[:tile_index] + 'y' + clicked[tile_index + 1:]
        return clicked
    # else, return None
    else:
        return None

# function which flips the tile and the tiles around it following the rules of the game
def move(parent_node, index_to_move):
    child_node = Node(copy.deepcopy(parent_node.board), parent_node, parent_node.depth+1, "-", "-")
    child_node.board = binary_to_string(child_node.board)
    child_node.board = flip(child_node.board, index_to_move)

    # logical conditions which flip the correct tiles around flipped tile

    # if the tile to flip is in the first row, flip it, the tile under it and:
    # - tile to its right if it's the leftmost
    # - tile to its left if it's the rightmost
    # - both its left and right tiles if not the leftmost or rightmost tile
    if index_to_move < n:
        child_node.board = flip(child_node.board, index_to_move+n)
        if index_to_move == 0:
            child_node.board = flip(child_node.board, index_to_move+1)
        elif index_to_move == n-1:
            child_node.board = flip(child_node.board, index_to_move-1)
        else:
            child_node.board = flip(child_node.board, index_to_move+1)
            child_node.board = flip(child_node.board, index_to_move-1)
    # if the tile to flip is in the last row, flip it, the tile above it and:
    # - tile to its right if it's the leftmost
    # - tile to its left if it's the rightmost
    # - both its left and right tiles if not the leftmost or rightmost tile
    elif index_to_move > (last_tile_index - n):
        child_node.board = flip(child_node.board, index_to_move-n)
        if index_to_move == (last_tile_index - (n-1)):
            child_node.board = flip(child_node.board, index_to_move+1)
        elif index_to_move == last_tile_index:
            child_node.board = flip(child_node.board, index_to_move-1)
        else:
            child_node.board = flip(child_node.board, index_to_move+1)
            child_node.board = flip(child_node.board, index_to_move-1)
    # if not first or last row - flip the tile, the ones above and below it and:
    # - tile to its right if it's the leftmost
    # - tile to its left if it's the rightmost
    # - both its left and right tiles if not the leftmost or rightmost tile
    else:
        child_node.board = flip(child_node.board, index_to_move+n)
        child_node.board = flip(child_node.board, index_to_move-n)
        if (index_to_move % n) == 0:
            child_node.board = flip(child_node.board, index_to_move+1)
        elif (index_to_move % n == n-1):
            child_node.board = flip(child_node.board, index_to_move-1)
        else:
            child_node.board = flip(child_node.board, index_to_move+1)
            child_node.board = flip(child_node.board, index_to_move-1)
    
    # transform string back to binary and add born_from value to child_config (e.g. 'C3' - the current config was born by flipping 'C3' on the parent config)
    child_node.board = int(child_node.board, 2)
    child_node.born_from = chr(ord('@')+((index_to_move//n)+1)) + str((index_to_move%n)+1)
    return child_node

# function which flips the tile and the tiles around it following the rules of the game
# - related to custom A* heuristic, i.e. heuristic #2 which will check if a tile has already been flipped in the current sequence of flips (branch of the tree)
def custom_astar_move(parent_node, index_to_move):
    child_node = Node(copy.deepcopy(parent_node.board), parent_node, parent_node.depth+1, "-", copy.deepcopy(parent_node.clicked))
    child_node.board = binary_to_string(child_node.board)
    child_node.clicked = clicked(child_node.clicked, index_to_move)
    # if already clicked, ignore this child_node
    if child_node.clicked is None:
        return None
    
    child_node.board = flip(child_node.board, index_to_move)

    # logical conditions which flip the correct tiles around flipped tile

    # if the tile to flip is in the first row, flip it, the tile under it and:
    # - tile to its right if it's the leftmost
    # - tile to its left if it's the rightmost
    # - both its left and right tiles if not the leftmost or rightmost tile
    if index_to_move < n:
        child_node.board = flip(child_node.board, index_to_move+n)
        if index_to_move == 0:
            child_node.board = flip(child_node.board, index_to_move+1)
        elif index_to_move == n-1:
            child_node.board = flip(child_node.board, index_to_move-1)
        else:
            child_node.board = flip(child_node.board, index_to_move+1)
            child_node.board = flip(child_node.board, index_to_move-1)
    # if the tile to flip is in the last row, flip it, the tile above it and:
    # - tile to its right if it's the leftmost
    # - tile to its left if it's the rightmost
    # - both its left and right tiles if not the leftmost or rightmost tile
    elif index_to_move > (last_tile_index - n):
        child_node.board = flip(child_node.board, index_to_move-n)
        if index_to_move == (last_tile_index - (n-1)):
            child_node.board = flip(child_node.board, index_to_move+1)
        elif index_to_move == last_tile_index:
            child_node.board = flip(child_node.board, index_to_move-1)
        else:
            child_node.board = flip(child_node.board, index_to_move+1)
            child_node.board = flip(child_node.board, index_to_move-1)
    # if not first or last row - flip the tile, the ones above and below it and:
    # - tile to its right if it's the leftmost
    # - tile to its left if it's the rightmost
    # - both its left and right tiles if not the leftmost or rightmost tile
    else:
        child_node.board = flip(child_node.board, index_to_move+n)
        child_node.board = flip(child_node.board, index_to_move-n)
        if (index_to_move % n) == 0:
            child_node.board = flip(child_node.board, index_to_move+1)
        elif (index_to_move % n == n-1):
            child_node.board = flip(child_node.board, index_to_move-1)
        else:
            child_node.board = flip(child_node.board, index_to_move+1)
            child_node.board = flip(child_node.board, index_to_move-1)
    # transform string back to binary and adds born_from value to child_config (e.g. 'C3' - meaning that the current config was born from pressing 'C3' on the parent)
    child_node.board = int(child_node.board, 2)
    child_node.born_from = chr(ord('@')+((index_to_move//n)+1)) + str((index_to_move%n)+1)
    return child_node

# function which is related to the custom brute force algorithm
# - flips the tile and the tiles around it following the rules of the game
# - "clears the board"
def custom_brute_force_move(board):
    for row in range(1, n):
        for col in range(0, n):
            if board[row-1][col] == 1:
                if board[row][col] == 1:
                    board[row][col] = 0
                else:
                    board[row][col] = 1
                if row == n-1:
                    if board[row-1][col] == 1:
                        board[row-1][col] = 0
                    else:
                        board[row-1][col] = 1
                    if col == 0:
                        if board[row][col+1] == 1:
                            board[row][col+1] = 0
                        else:
                            board[row][col+1] = 1
                    if col == n-1:
                        if board[row][col-1] == 1:
                            board[row][col-1] = 0
                        else:
                            board[row][col-1] = 1
                    if col != 0 and col != n-1:
                        if board[row][col-1] == 1:
                            board[row][col-1] = 0
                        else:
                            board[row][col-1] = 1
                        if board[row][col+1] == 1:
                            board[row][col+1] = 0
                        else:
                            board[row][col+1] = 1
                else:
                    if board[row-1][col] == 1:
                        board[row-1][col] = 0
                    else:
                        board[row-1][col] = 1
                    if board[row+1][col] == 1:
                        board[row+1][col] = 0
                    else:
                        board[row+1][col] = 1
                    if col == 0:
                        if board[row][col+1] == 1:
                            board[row][col+1] = 0
                        else:
                            board[row][col+1] = 1
                    if col == n-1:
                        if board[row][col-1] == 1:
                            board[row][col-1] = 0
                        else:
                            board[row][col-1] = 1
                    if col != 0 and col != n-1:
                        if board[row][col-1] == 1:
                            board[row][col-1] = 0
                        else:
                            board[row][col-1] = 1
                        if board[row][col+1] == 1:
                            board[row][col+1] = 0
                        else:
                            board[row][col+1] = 1
    return board

# depth first search brute-force algorithm
def dfs(n, max_d, initial_board, puzzle_index):
    # initialize open list as a stack & append the initial state of the board to it
    open_list = []
    open_list.append(Node(initial_board, None, 1, "0", "-"))
    # closed list initialized as OrderedSet to speed-up lookup and avoid duplicate board configurations
    closed_list = OrderedSet()

    # create string representing the winning board configuration
    winning_string = ""
    temp_counter = 0
    while temp_counter != last_tile_index+1:
        winning_string += '0'
        temp_counter += 1
    winning_board = int(winning_string, 2)

    solution_found = 0

    # while we still have nodes to analyze
    while len(open_list) != 0:
        current_config = open_list.pop()

        # check if we have the solved board
        if current_config.board == winning_board:
            closed_list.add(current_config.board)
            solution_found = 1
            output_solution_list = []
            # use node.parent and node.born_from parameters to trace the solution path and write it to the file
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
            closed_list.add(current_config.board)
            # initialize a temporary open list which will store the children of the current node
            temp_openlist = []
            # generate each possible move from the current configuration and if it hasn't already been visited, append to the temporary open list
            for tile_index in range(0, last_tile_index+1):
                child_config = move(current_config, tile_index)
                add_to_open_list = 1
                for element in closed_list:
                    if element == child_config.board:
                        add_to_open_list = 0
                        break
                if add_to_open_list == 1:
                    temp_openlist.append(child_config)
            # sort children to prioritize them following a top-down, left-right approach (as per requirement)
            temp_openlist.sort(key=lambda x: x.board, reverse=True)
            # append the sorted elements to the stack
            open_list = open_list + temp_openlist

    # if we have exhausted our search and no solution has been found, write "no solution" to the solution file
    if solution_found == 0:
        output_solution_file = open(str(puzzle_index)+"_dfs_solution.txt", "w")
        output_solution_file.write("no solution")

    # regardless of solution, write the search path to the search file using the closed list    
    output_search_file = open(str(puzzle_index)+"_dfs_search.txt", "w")
    for element in closed_list:
        output_search_file.write("0\t0\t0\t" + binary_to_string(element) + "\n")

# best-first search algorithm using the heuristic:
# - each move can flip at most 5 tiles and hence, NumberOfBlackTokens/5 would be the estimate for the number of moves needed to reach the goal (the lower it is, the better)
def bfs(n, max_l, initial_board, puzzle_index, initial_black_tokens_number):
    # initialize open list, convert it into a priority heap queue and append the initial configuration to it
    open_list = []
    heapq.heapify(open_list)
    heapq.heappush(open_list, (initial_black_tokens_number/5, Node(initial_board, None, 1, "0", "-")))
    # closed list initialized as OrderedSet to speed-up lookup and avoid duplicate board configurations
    closed_list = OrderedSet()

    # create string representing the winning board configuration
    winning_string = ""
    temp_counter = 0
    while temp_counter != last_tile_index+1:
        winning_string += '0'
        temp_counter += 1
    winning_board = int(winning_string, 2)

    solution_found = 0

    # while we still have nodes to analyze and while we haven't reached max_l;
    while len(open_list) != 0 and len(closed_list) <= max_l:
        # pop next element from the list (smallest number of black tiles according to the heuristic)
        current_config = heapq.heappop(open_list)        

        # check if we have the solved board
        if current_config[1].board == winning_board:
            closed_list.add(current_config[1].board)
            solution_found = 1
            # use node.parent and node.born_from parameters to trace the solution path and write it to the file
            output_solution_list = []
            cur_config = current_config[1]
            while(cur_config.depth != 1):
                output_solution_list.append(cur_config.born_from + "\t" + binary_to_string(cur_config.board) + "\n")
                cur_config = cur_config.parent
            output_solution_list.append(cur_config.born_from + "\t" + binary_to_string(cur_config.board) + "\n")
            output_solution_file = open(str(puzzle_index) + "_bfs_solution.txt", "w")
            for element in reversed(output_solution_list):
                output_solution_file.write(element)
            break

        else:
            closed_list.add(current_config[1].board)
            # generate each possible move from the current configuration and if it hasn't already been visited, add to the priority queue
            for tile_index in range(0, last_tile_index+1):
                child_config = move(current_config[1], tile_index)
                add_to_open_list = 1
                for element in closed_list:
                    if element == child_config.board:
                        add_to_open_list = 0
                        break
                if add_to_open_list == 1:
                    heapq.heappush(open_list, (binary_to_string(child_config.board).count('1')/5, child_config))

    # if we have exhausted our search and no solution has been found, write "no solution" to the solution file
    if solution_found == 0:
        output_solution_file = open(str(puzzle_index)+"_bfs_solution.txt", "w")
        output_solution_file.write("no solution")

    # regardless of solution, write the search path to the search file using the closed list    
    output_search_file = open(str(puzzle_index)+"_bfs_search.txt", "w")
    for element in closed_list:
        element = binary_to_string(element)
        fn_hn = str(element.count('1')/5)
        output_search_file.write(fn_hn + "\t" + fn_hn + "\t0\t" + element + "\n")

# astar search algorithm using heuristic:
# - lower h(n) is better as it represents the estimated number of moves to reach winning configuration (numberOfBlackTokens/5)
# - lower g(n) is better as it represents a lower depth, meaning that the solution would be more optimal
# - lowest f(n) is the next node to go to, if more than one lowest f(n): choose the one with lowest g(n) and if still more than one lowest f(n), don't prioritize
def astar(n, max_l, initial_board, puzzle_index, initial_black_tokens_number):
    # initialize open list, convert it into a heap and append initial configuration to it
    open_list = []
    heapq.heapify(open_list)
    heapq.heappush(open_list, (initial_black_tokens_number/5, Node(initial_board, None, 1, "0", "-")))
    closed_list = []

    # create string with correct length representing the winning board configuration
    winning_string = ""
    temp_counter = 0
    while temp_counter != last_tile_index+1:
        winning_string += '0'
        temp_counter += 1
    winning_board = int(winning_string, 2)

    solution_found = 0

    # while we still have nodes to analyze and while we haven't reached max_l;
    while len(open_list) != 0 and len(closed_list) <= max_l:
        # pop next element from the list (smallest fn)
        current_config = heapq.heappop(open_list)        

        # check if we have the solved board
        if current_config[1].board == winning_board:
            closed_list.append(current_config[1])
            solution_found = 1
            # use node.parent and node.born_from parameters to trace the solution path and write it to the file
            output_solution_list = []
            cur_config = current_config[1]
            while(cur_config.depth != 1):
                output_solution_list.append(cur_config.born_from + "\t" + binary_to_string(cur_config.board) + "\n")
                cur_config = cur_config.parent
            output_solution_list.append(cur_config.born_from + "\t" + binary_to_string(cur_config.board) + "\n")
            output_solution_file = open(str(puzzle_index) + "_astar_solution.txt", "w")
            for element in reversed(output_solution_list):
                output_solution_file.write(element)
            break

        else:
            closed_list.append(current_config[1])
            # generate each possible move from the current configuration and if it hasn't already been visited, add to the priority queue
            for tile_index in range(0, last_tile_index+1):
                child_config = move(current_config[1], tile_index)
                add_to_open_list = 1
                for element in closed_list:
                    if element.board == child_config.board:
                        add_to_open_list = 0
                        break
                if add_to_open_list == 1:
                    heapq.heappush(open_list, ((binary_to_string(child_config.board).count('1'))/5 + child_config.depth, child_config))

    # if we have exhausted our search and no solution has been found, write "no solution" to the solution file
    if solution_found == 0:
        output_solution_file = open(str(puzzle_index)+"_astar_solution.txt", "w")
        output_solution_file.write("no solution")

    # regardless of solution, write the search path to the search file using the closed list    
    output_search_file = open(str(puzzle_index)+"_astar_search.txt", "w")
    for element in closed_list:
        gn = element.depth
        element = binary_to_string(element.board)
        hn = element.count('1')/5
        fn = gn + hn
        output_search_file.write(str(fn) + "\t" + str(gn) + "\t" + str(hn) + "\t" + element + "\n")

# custom astar search algorithm similar to the one above, except for:
# - if a tile in a sequence of flips has already been clicked, don't click it again (in the decision tree, this would mean that we ignore some children for each node)
def custom_astar(n, max_l, initial_board, puzzle_index, initial_black_tokens_number):
    # initialize open list & clicked list, heapify open list & append initial configuration to it and initialize closed list
    open_list = []
    heapq.heapify(open_list)
    initial_clicked = ""
    i = 0
    while i != last_tile_index+1:
        initial_clicked = initial_clicked + 'n'
        i += 1
    heapq.heappush(open_list, (initial_black_tokens_number/5, Node(initial_board, None, 1, "0", initial_clicked)))
    closed_list = []

    # create string representing the winning board configuration
    winning_string = ""
    temp_counter = 0
    while temp_counter != last_tile_index+1:
        winning_string += '0'
        temp_counter += 1
    winning_board = int(winning_string, 2)

    solution_found = 0

    # while we still have nodes to analyze and while we haven't reached max_l;
    while len(open_list) != 0 and len(closed_list) <= max_l:
        # pop next element from the list (smallest fn)
        current_config = heapq.heappop(open_list)

        # check if we have the solved board
        if current_config[1].board == winning_board:
            closed_list.append(current_config[1])
            solution_found = 1
            # use node.parent and node.born_from parameters to trace the solution path and write it to the file
            output_solution_list = []
            cur_config = current_config[1]
            while(cur_config.depth != 1):
                output_solution_list.append(cur_config.born_from + "\t" + binary_to_string(cur_config.board) + "\n")
                cur_config = cur_config.parent
            output_solution_list.append(cur_config.born_from + "\t" + binary_to_string(cur_config.board) + "\n")
            output_solution_file = open(str(puzzle_index) + "_custom_astar_solution.txt", "w")
            for element in reversed(output_solution_list):
                output_solution_file.write(element)
            break

        else:
            closed_list.append(current_config[1])
            # generate each possible move and only consider the ones in which we don't click a tile that we have already clicked in the current sequence of moves (current branch path)
            for tile_index in range(0, last_tile_index+1):
                child_config = custom_astar_move(current_config[1], tile_index)
                add_to_open_list = 1
                if child_config is None:
                    add_to_open_list = 0
                if add_to_open_list == 1:
                    for element in closed_list:
                        if element == child_config:
                            add_to_open_list = 0
                            break
                if add_to_open_list == 1:
                    heapq.heappush(open_list, (binary_to_string(child_config.board).count('1')/5 + child_config.depth, child_config))

    # if we have exhausted our search and no solution has been found, write "no solution" to the solution file
    if solution_found == 0:
        output_solution_file = open(str(puzzle_index)+"_custom_astar_solution.txt", "w")
        output_solution_file.write("no solution")

    # regardless of solution, write the search path to the search file using the closed list    
    output_search_file = open(str(puzzle_index)+"_custom_astar_search.txt", "w")
    for element in closed_list:
        gn = element.depth
        config = binary_to_string(element.board)
        hn = config.count('1')/5
        fn = gn + hn
        output_search_file.write(str(fn) + "\t" + str(gn) + "\t" + str(hn) + "\t" + config + "\n")

# custom brute force algorithm following a "clear the board" principle
# - for each row starting from the second, click the tile if the tile above it is black
# - this will give the "baseline" configuration of the board which will have all its tiles white except for some (or all) of them in the last row
# - then, because the lower rows are dependent on the ones above them, try various clicking combinations on the first row and repeat the clearing the board process until we win (if it's possible)
def custom_brute_force(n, initial_board, puzzle_index):
    board = []
    char_position = 0
    # create a 2D array which represents the initial board configuration
    for row in range(0, n):
        new_row = []
        for col in range(0, n):
            new_row.append(int(initial_board[char_position]))
            char_position += 1
        board.append(new_row)
    
    output_search_file = open(str(puzzle_index) + "_clearTheBoard_search.txt", "w")
    output_solution_file = open(str(puzzle_index) + "_clearTheBoard_solution.txt", "w")
    output_solution_file.write("Initial board configuration: ")
    temp_board = copy.deepcopy(board)
    # flatten the configuration and write to the solution and search output files
    for row in range(0, n):
        temp_board[row] = ''.join(map(str, temp_board[row]))
    output_solution_file.write(''.join(map(str, temp_board)))
    output_solution_file.write("\n")
    output_search_file.write("Initial board configuration: ")
    temp_board = copy.deepcopy(board)
    for row in range(0, n):
        temp_board[row] = ''.join(map(str, temp_board[row]))
    output_search_file.write(''.join(map(str, temp_board)))
    output_search_file.write("\n")

    # represent the winning board configuration as a 2D array
    winning_board = []
    for row in range(0, n):
        new_row = []
        for col in range(0, n):
            new_row.append(0)
        winning_board.append(new_row)
    
    # clear the board for the first time and save the baseline configuration
    board = custom_brute_force_move(board)
    output_solution_file.write("Board after first clearTheBoard run (i.e. Baseline Board): ")

    # flatten the configuration and write to the solution and search output files
    temp_board = copy.deepcopy(board)
    for row in range(0, n):
        temp_board[row] = ''.join(map(str, temp_board[row]))
    output_solution_file.write(''.join(map(str, temp_board)))
    output_solution_file.write("\n")
    output_search_file.write("Board after first clearTheBoard run (i.e. Baseline Board): ")
    temp_board = copy.deepcopy(board)
    for row in range(0, n):
        temp_board[row] = ''.join(map(str, temp_board[row]))
    output_search_file.write(''.join(map(str, temp_board)))
    output_search_file.write("\n")

    # if board is all white, we've found a solution
    if board == winning_board:
        return print("Win!")
    
    else:
        baseline_board = copy.deepcopy(board)
        # generate all possible clicking combinations for the first row (depending on size of the puzzle) and clear the baseline board again
        # - repeat until we find a winning combination or until we have tried all combinations and haven't found the solution
        first_row_possibilities = [list(i) for i in itertools.product([0, 1], repeat=n)]
        for i in range(1, len(first_row_possibilities)):
            first_row_to_touch = first_row_possibilities[i]
            for j in range(0, len(first_row_to_touch)):
                if first_row_to_touch[j] == 1:
                    if board[0][j] == 1:
                        board[0][j] = 0
                    else:
                        board[0][j] = 1
                    if board[1][j] == 1:
                        board[1][j] = 0
                    else:
                        board[1][j] = 1
                    if j == 0:
                        if board[0][j+1] == 1:
                            board[0][j+1] = 0
                        else:
                            board[0][j+1] = 1
                    if j == len(first_row_to_touch) - 1:
                        if board[0][j-1] == 1:
                            board[0][j-1] = 0
                        else:
                            board[0][j-1] = 1
                    if j != 0 and j != len(first_row_to_touch) - 1:
                        if board[0][j-1] == 1:
                            board[0][j-1] = 0
                        else:
                            board[0][j-1] = 1
                        if board[0][j+1] == 1:
                            board[0][j+1] = 0
                        else:
                            board[0][j+1] = 1
            # flatten and write to the search file the board before and after the move 
            output_search_file.write("Board after touching ")
            output_search_file.write(''.join(map(str, first_row_to_touch)))
            output_search_file.write(" in the first row: ")
            temp_board = copy.deepcopy(board)
            for row in range(0, n):
                temp_board[row] = ''.join(map(str, temp_board[row]))
            output_search_file.write(''.join(map(str, temp_board)))
            output_search_file.write("\n")
            pre_solution_board = copy.deepcopy(board)
            board = custom_brute_force_move(board)
            output_search_file.write("Board after clearTheBoard run: ")
            temp_board = copy.deepcopy(board)
            for row in range(0, n):
                temp_board[row] = ''.join(map(str, temp_board[row]))
            output_search_file.write(''.join(map(str, temp_board)))
            output_search_file.write("\n")
            # if we have found the solution, write to the solution file the board before and after the move 
            if board == winning_board:
                output_solution_file.write("Board after touching ")
                output_solution_file.write(''.join(map(str, first_row_to_touch)))
                output_solution_file.write(" in the first row: ")
                temp_board = copy.deepcopy(pre_solution_board)
                for row in range(0, n):
                    temp_board[row] = ''.join(map(str, temp_board[row]))
                output_solution_file.write(''.join(map(str, temp_board)))
                output_solution_file.write("\n")
                output_solution_file.write("Board after clearTheBoard run: ")
                temp_board = copy.deepcopy(board)
                for row in range(0, n):
                    temp_board[row] = ''.join(map(str, temp_board[row]))
                output_solution_file.write(''.join(map(str, temp_board)))
                output_solution_file.write("\n")
                output_solution_file.write("Win!")
                output_search_file.write("Win!")
                return print("Win!")
            # if we haven't found the solution, try another first row clicking combination
            else:
                board = copy.deepcopy(baseline_board)
                output_search_file.write("Retrying Baseline Board with a different first row flipping.\n")
    
    # if all combinations for the first row have been exhausted and we haven't found an answer, overwrite the solution file with "no solution"
    output_solution_file.close()
    os.remove(str(puzzle_index) + "_clearTheBoard_solution.txt")
    output_solution_file = open(str(puzzle_index) + "_clearTheBoard_solution.txt", "w")
    output_solution_file.write("no solution")
    print("Done.")

# read input_file path
input_file = open(sys.argv[1], 'r')
# used when naming the output files
puzzle_index = 0
# for each puzzle in the input_file, apply algorithms to try to solve it
for puzzle in input_file:
    # parse the line to get the puzzle parameters
    puzzle = puzzle.split()
    n = int(puzzle[0])
    max_d = int(puzzle[1])
    max_l = int(puzzle[2])
    initial_board_string = puzzle[3]
    # useful
    last_tile_index = (n*n)-1
    # used for the various heuristics
    initial_black_tokens_number = initial_board_string.count('1')
    # convert to binary for faster processing
    initial_board = int(initial_board_string, 2)
    dfs(n, max_d, initial_board, puzzle_index)
    # flags to use correct overriding of '<'
    bfs_running = 0
    astar_running = 0
    custom_astar_running = 0
    bfs_running = 1
    bfs(n, max_l, initial_board, puzzle_index, initial_black_tokens_number)
    bfs_running = 0
    astar_running = 1
    astar(n, max_l, initial_board, puzzle_index, initial_black_tokens_number)
    astar_running = 0
    #custom_astar_running = 1
    #custom_astar(n, max_l, initial_board, puzzle_index, initial_black_tokens_number)
    #custom_astar_running = 0
    custom_brute_force(n, binary_to_string(initial_board), puzzle_index)
    puzzle_index += 1