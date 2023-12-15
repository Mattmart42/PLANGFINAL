import os
import re
import sys
import time
import copy
from constants import Constants
from typing import *

class Environment:
    '''
    Environment class responsible for configuring and running
    the MazePitfall problem with BlindBot agent
    '''
    
    def __init__ (self, maze: list[str], tick_length: int = 1, verbose: bool = True) -> None:
        """
        Initializes the environment from a given maze, specified as an
        array of strings with maze elements
        
        Parameters:
            maze (list): 
                The array of strings specifying the maze entities
                in this Environment's challenge
            tick_length (int):
                The duration between agent decisions, in seconds; set to
                0 for instant games, or slower to inspect behavior
            verbose (bool):
                Whether or not the maze updates will be printed; set to
                False for silent games, or True to see each step
        """
        self._maze: list = maze
        self._rows: int = len(maze)
        self._cols: int = len(maze[0])
        self._tick_length: int = tick_length
        self._verbose: bool = verbose
        self._pits: set[tuple[int, int]] = set()
        self._goals: set[tuple[int, int]] = set()
        self._walls: set[tuple[int, int]] = set()
        self._playable: set[tuple[int, int]] = set()
        self._explored: set[tuple[int, int]] = set()
        self._frontier: set[tuple[int, int]] = set()
        self._wrn_tiles: dict = dict()
        
        # Scan for pits and goals in the input maze
        for (row_num, row) in enumerate(maze):
            for (col_num, cell) in enumerate(row):
                loc = (col_num, row_num)
                if cell == Constants.WALL_BLOCK:
                    self._walls.add(loc)
                    continue
                if cell == Constants.GOAL_BLOCK:
                    self._goals.add(loc)
                if cell == Constants.PIT_BLOCK:
                    self._pits.add(loc)
                if cell == Constants.PLR_BLOCK:
                    self._player_loc = self._initial_loc = (loc)
                    self._explored.add(loc)
                self._playable.add(loc)
        
        # Create "warning tiles" that depict the number of adjacent tiles containing pits
        self._spcl: set[tuple[int, int]] = self._pits | self._goals | self._walls
        for pit in self._pits:
            for wrn_possible in self.get_cardinal_locs(pit, 1) - self._spcl:
                self._wrn_tiles[wrn_possible] = self._get_wrn_num(wrn_possible)
        
        # Initialize the MazeAgent and ready simulation!
        self._goal_reached: bool = False
        self._ag_maze: list = self._make_agent_maze()
        self._maze = [list(row) for row in maze] # Easier to change elements in this format
        self._og_maze: list = copy.deepcopy(self._maze)
        self._og_maze[self._player_loc[1]][self._player_loc[0]] = Constants.SAFE_BLOCK
        for (c, r), pit_count in self._wrn_tiles.items():
            self._og_maze[r][c] = str(pit_count)
        self._ag_tile: str = self._og_maze[self._player_loc[1]][self._player_loc[0]]
        self._update_frontier(self._player_loc)
        self._agent: "MazeAgent" = MazeAgent(self, self._get_current_perception())
    
    
    ##################################################################
    # Methods
    ##################################################################
    
    def get_player_loc (self) -> tuple[int, int]:
        """
        Returns the player's current location as a maze tuple
        
        Returns:
            tuple[int, int]:
                The player's current location, a (c, r) tuple
        """
        return self._player_loc
    
    def get_goal_loc (self) -> tuple[int, int]:
        """
        Returns the goal tile's location as a maze tuple
        
        Returns:
            tuple[int, int]:
                The goal's location, a (c, r) tuple
        """
        return next(iter(self._goals))
    
    def get_agent_maze (self) -> list[list[str]]:
        """
        Returns the agent's mental model of the maze, without key
        components revealed that have yet to be explored. Unknown
        spaces are filled with "?"
        
        [!] Useful for your agent to maintain its own copy of the maze
        for record-keeping. The agent's self.maze attribute will be
        displayed at every tick of environments wherein VERBOSE = True
        
        [!] As the agent moves around the maze, the agent's representation
        will also be updated by the environment for any encountered cells;
        any INFERRED cells will need to be changed by you. To make this easier,
        the maze is converted to a list of list of strings, so each cell is
        its own maze entity that can be assigned to.
        
        Example:
            # True    # Agent's (returned by this method)
            XXXXXX    XXXXXX
            X...GX    X???GX
            X..PPX    X????X
            X....X    X????X
            X..P.X    X????X
            X@...X    X@???X
            XXXXXX    XXXXXX
        
        Returns:
            list[list[str]]:
                The agent's view of the maze
        """
        return self._ag_maze
    
    def get_playable_locs (self) -> set[tuple[int, int]]:
        """
        Returns the set of ALL positions within the playable maze
        
        Example:
            012345        env.get_playable_locs()
            XXXXXX 0      => {(1,1), (1,2), (1,3), ... , (4,5)}
            X...GX 1    
            X..PPX 2
            X....X 3
            X..P.X 4
            X@...X 5
            XXXXXX 6
        
        Returns:
            set[tuple[int, int]]:
                The set of all locations into which the player may move
        """
        return copy.deepcopy(self._playable)
    
    def get_explored_locs (self) -> set[tuple[int, int]]:
        """
        Returns the set of ALL locations that have previously been explored /
        moved upon.
        
        Example:
              012345      Starting Location: (1,5)
              XXXXXX 0    Previous Moves: (2,5), (3,5), (4,5), (1,4)
              X???GX 1    env.get_explored_locs()
              X????X 2    => {(1,5), (2,5), (3,5), (4,5), (1,4)}
              X????X 3   
              X@?P?X 4   
              X..1.X 5   
              XXXXXX 6
        
        Returns:
            set[tuple[int, int]]:
                The set of all locations into which a player has already moved
                (you should never need to repeat movement onto a tile)
        """
        return copy.deepcopy(self._explored)
    
    def get_frontier_locs (self) -> set[tuple[int, int]]:
        """
        Returns the set of ALL unexplored and playable locs that have at least
        one explored neighboring tile.
        
        Example:
              012345      Starting Location: (1,5)
              XXXXXX 0    Previous Moves: (2,5), (3,5), (4,5), (1,4)
              X???GX 1    env.get_frontier_locs()
              X????X 2    => {(1,3), (2,4), (3,4), (4,4)}
              XF???X 3   
              X@FPFX 4    [!] Example to the left artificially adds "F" tiles to
              X..1.X 5    denote the frontier, which will not be displayed in-game
              XXXXXX 6
        
        Returns:
            set[tuple[int, int]]:
                The set of all locations into which a player may legally move next
                (some of which will be more dangerous than others -- tread lightly!)
        """
        return copy.deepcopy(self._frontier)
    
    def get_cardinal_locs (self, loc: tuple[int, int], offset: int) -> set[tuple[int, int]]:
        """
        Returns a set of the 4 adjacent tiles at the given offset/distance to the given loc
        that are also in the set of playable locations (i.e., ignoring locations like walls)
        
        Example:
            012345        env.get_cardinal_locs((1,5), 1)
            XXXXXX 0      => {(1,4), (2,5)}
            X...GX 1      
            X..PPX 2      env.get_cardinal_locs((3,3), 2)
            X....X 3      => {(1,3), (3,1), (3,5)}
            X..P.X 4      (5,3) missing above because it's a wall
            X@...X 5
            XXXXXX 6
        
        Parameters:
            loc (tuple[int, int]):
                2-tuple indicating a maze location, (x,y) or (c,r)
            offset (int):
                The distance of requested tiles from the given loc
        
        Returns:
            set[tuple[int, int]]:
                The set of all *playable* maze locations within that distance of offset from
                the given loc
        """
        (x, y) = loc
        pos_locs = [(x+offset, y), (x-offset, y), (x, y+offset), (x, y-offset)]
        return set(filter(lambda loc: loc[0] >= 0 and loc[1] >= 0 and loc[0] < self._cols and loc[1] < self._rows and loc in self._playable, pos_locs))
    
    def start_mission (self) -> int:
        """
        Manages the agent's action loop and the environment's record-keeping
        mechanics; the general order of operations at each action loop are:
        1. The agent's think method is fed the current perception: its location
           and the type of tile it is currently standing on
        2. The agent returns the next tile it wishes to move to along the
           frontier (moves that are not on the frontier will be considered invalid
           and will end the game immediately with a max penalty score)
        3. The move is enacted, and penalty of that move added to the score
        4. The game ends if either the minimum score threshold is reached, or the
           agent has reached the goal
        
        Returns:
            int:
                The overall score (sum of penalties) encountered by the agent during
                the game, with a minimum score threshold that cannot be exceeded as
                defined in Constants.py.
        """
        score = 0
        if self._verbose:
            self._update_display()
            print("\nCurrent Loc: " + str(self._player_loc) + " [" + self._ag_tile + "]\nInitial State\nScore: " + str(score) + "\n")
        while (score > Constants.get_min_score()):
            time.sleep(self._tick_length)
            next_loc, penalty = self._run_one_tick()
            score = score - penalty
            if self._verbose:
                print("\nCurrent Loc: " + str(self._player_loc) + " [" + self._ag_tile + "]\nLast Move: " + str(next_loc) + ", Cost: -" + str(penalty) + "\nScore: " + str(score) + "\n")
            if self._goal_test(self._player_loc):
                break
        
        if self._verbose:
            print("[!] Game Complete! Final Score: " + str(score))
        return score
    
    def test_move (self, move: tuple[int, int]) -> None:
        """
        Used for testing the agent's inferences from perceptions across movements.
        [!] Should be called ONLY within unit tests, not within the agent class
        
        Parameters:
            move (tuple[int, int]):
                Any maze location in the environment's frontier
        """
        if not move is None:
            self._make_move_request(move)
        self._agent.think(self._get_current_perception())
        
    def test_safety_check (self, loc: tuple[int, int]) -> Optional[bool]:
        """
        Attribute-safe getter for the agent's is_safe_tile method
        
        Returns:
            Optional[bool]:
                The agent's perceived safety of the given tile, which
                can be True if it is known to be safe, False if it is
                known to be a Pit, or None if its knowledge is
                inconclusive.
        """
        return self._agent.is_safe_tile(loc)
    
    ##################################################################
    # "Private" Helper Methods
    ##################################################################
    
    def _get_current_perception (self) -> dict:
        """
        Returns the current perception of the agent as a small dictionary with 2 keys:
          - loc:  the location of the agent as a (c,r) tuple
          - tile: the type of tile the agent is currently standing upon
        
        Returns:
            dict:
                The dictionary describing the player's current location and tile type
        """
        return {"loc": self._player_loc, "tile": self._ag_tile}
    
    def _get_wrn_num (self, loc: tuple[int, int]) -> int:
        """
        Returns the number of pits surrounding the given cell
        
        Returns:
            int:
                The number of pits surrounding the given location.
        """
        return len({adj_tile for adj_tile in self.get_cardinal_locs(loc, 1) if adj_tile in self._pits})
    
    def _update_display (self) -> None:
        """
        Prints the current state of the maze to the terminal; two mazes
        are printed:
        1. The environment's omniscient maze
        2. The agent's perception of the maze
        """
        for (rowIndex, row) in enumerate(self._maze):
            print(''.join(row) + "\t" + ''.join(self._ag_maze[rowIndex]))
            
    def _update_frontier (self, loc: tuple[int, int]) -> None:
        """
        Updates the environment's frontier with the player's latest move,
        removing newly-explored locations and adding new, unexplored,
        adjacent tiles to that.
        
        Parameters:
            loc (tuple[int, int]):
                The newly-explored location
        """
        self._frontier.update(self.get_cardinal_locs(loc, 1))
        self._frontier = self._frontier - self._explored
        
    def _wall_test (self, loc: tuple[int, int]) -> bool:
        """
        Determines whether or not the given location is a wall
        
        Parameters:
            loc (tuple[int, int]):
                The location to test
        
        Returns:
            bool:
                Whether or not that location is a wall
        """
        return loc in self._walls
    
    def _goal_test (self, loc: tuple[int, int]) -> bool:
        """
        Determines whether or not the given location is the goal
        
        Parameters:
            loc (tuple[int, int]):
                The location to test
        
        Returns:
            bool:
                Whether or not that location is the goal
        """
        return loc in self._goals
    
    def _pit_test (self, loc: tuple[int, int]) -> bool:
        """
        Determines whether or not the given location is a pit
        
        Parameters:
            loc (tuple[int, int]):
                The location to test
        
        Returns:
            bool:
                Whether or not that location is a pit
        """
        return loc in self._pits
        
    def _make_agent_maze (self) -> list:
        """
        Converts the 'true' maze into one with hidden tiles (?) for the agent
        to update as it learns
        
        Returns:
            list:
                Agent's maze mental-model representation
        """
        sub_regexp = "[" + Constants.PIT_BLOCK + Constants.SAFE_BLOCK + "".join(Constants.WRN_BLOCKS) + "]"
        return [list(re.sub(sub_regexp, Constants.UNK_BLOCK, r)) for r in self._maze]
    
    def _update_mazes (self, old_loc: tuple[int, int], new_loc: tuple[int, int]) -> None:
        """
        Performs updates on the maze objects maintained by the environment following a move
        
        Parameters:
            old_loc (tuple[int, int]):
                The location the player was in previous to the move
            new_loc (tuple[int, int]):
                The location the player was in after the move
        """
        self._maze[old_loc[1]][old_loc[0]] = self._og_maze[old_loc[1]][old_loc[0]]
        self._maze[new_loc[1]][new_loc[0]] = Constants.PLR_BLOCK
        self._ag_maze[old_loc[1]][old_loc[0]] = self._og_maze[old_loc[1]][old_loc[0]]
        self._ag_maze[new_loc[1]][new_loc[0]] = Constants.PLR_BLOCK
        self._ag_tile = self._og_maze[new_loc[1]][new_loc[0]]
        
    def _test_move_request (self, move: tuple[int, int]) -> bool:
        """
        Determines whether or not the given move location is a valid request. Valid move locations
        are those that are:
          - In the frontier
          - Not a wall
          
        Parameters:
            move (tuple[int, int]):
                The location into which the agent has requested to move
        
        Returns:
            bool:
                Whether or not that requested move location is valid
        """
        return move in self._frontier and not self._wall_test(move)
    
    def _make_move_request (self, move: tuple[int, int]) -> int:
        """
        Main workhorse helper for processing an agent's move request,
        first checking that it is valid, and then appropriately updating
        the environment's frontier and maze representation.
        
        Parameters:
            move (tuple[int, int]):
                The desired move location from the agent
                
        Returns:
            int:
                The cost of that move
        """
        old_loc = self._player_loc
        self._update_mazes(self._player_loc, move)
        self._player_loc = move
        self._explored.add(self._player_loc)
        self._update_frontier(self._player_loc)
        if self._verbose:
            self._update_display()
        return abs(old_loc[0] - move[0]) + abs(old_loc[1] - move[1])
        
    def _run_one_tick (self) -> tuple[tuple[int, int], int]:
        """
        Executes a single step of the game, from making a choice, to executing that move, to
        checking termination logic and keeping score
        
        Returns:
            tuple[tuple[int, int], int]:
                A 2-tuple consisting of:
                [0] The new location of the player after moving
                [1] The cost associated with that transition
        """
        # Return a perception for the agent to think about and plan next
        perception = {"loc": self._player_loc, "tile": self._ag_tile}
        next_loc = self._agent.think(perception)
        
        # Execute next move from agent's thinking
        if not self._test_move_request(next_loc):
            if self._verbose:
                print("\n [X] Provided an invalid move request (" + str(next_loc) + "); must choose from locations along the frontier.")
            return (next_loc, -Constants.get_min_score())
        dist = self._make_move_request(next_loc)
        
        # Assess the post-move penalty and whether or not the game is complete
        penalty = dist + (Constants.get_pit_penalty() if self._pit_test(self._player_loc) else 0)
        
        return (next_loc, penalty)

# Appears here to avoid circular dependency
from maze_agent import MazeAgent

if __name__ == "__main__":
    """
    Some example mazes with associated difficulties are
    listed below. The score thresholds given are for agents that actually use logic.
    Making a B-line for the goal on these mazes *may* satisfy the threshold listed here,
    but will not in general, more thorough tests.
    """
    mazes = [
        # Easy difficulty: Score > -20
        ["XXXXXX",
         "X...GX",
         "X..PPX",
         "X....X",
         "X..P.X",
         "X@...X",
         "XXXXXX"],
        
        # Medium difficulty: Score > -32
        ["XXXXXXXXX",
         "X..PGP..X",
         "X.......X",
         "X..P.P..X",
         "X.......X",
         "X..@....X",
         "XXXXXXXXX"],
        
        # Hard difficulty: Score > -40
        ["XXXXXXXXX",
         "X...G.PPX",
         "X...P...X",
         "X.......X",
         "XP......X",
         "XP.P.P.PX",
         "X...@...X",
         "XXXXXXXXX"],

        ["XXXXXXXXX",
         "X..P.P.GX",
         "X@......X",
         "X..P.P..X",
         "X.......X",
         "X.......X",
         "XXXXXXXXX"],

        ["XXXXXXXXX",
        "XG.P....X",
        "X.......X",
        "X.PP.PP.X",
        "XP.....PX",
        "X...@...X",
        "XXXXXXXXX"]
    ]
    
    # Pick your difficulty by changing out mazes[0] for one of the other
    # indexes! Make sure to run pitsweeper_tests.py for more comprehensive
    # unit testing.
    # Call with tick_length = 0 for instant games
    env = Environment(mazes[0], tick_length = 1, verbose = True)
    env.start_mission()
