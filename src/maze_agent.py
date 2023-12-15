import time
import random
import math
from queue import Queue
from constants import *
from maze_clause import *
from maze_knowledge_base import *

class MazeAgent:
    '''
    BlindBot MazeAgent meant to employ Propositional Logic,
    Planning, and Active Learning to navigate the Pitsweeper
    Problem. Have fun!
    '''
    
    def __init__ (self, env: "Environment", perception: dict) -> None:
        """
        Initializes the MazeAgent with any attributes it will need to
        navigate the maze.
        [!] Add as many attributes as you see fit!
        
        Parameters:
            env (Environment):
                The Environment in which the agent is operating; make sure
                to see the spec / Environment class for public methods that
                your agent will use to solve the maze!
            perception (dict):
                The starting perception of the agent, which is a
                small dictionary with keys:
                  - loc:  the location of the agent as a (c,r) tuple
                  - tile: the type of tile the agent is currently standing upon
        """
        self.env: "Environment" = env
        self.goal: tuple[int, int] = env.get_goal_loc()
        self.start: tuple[int, int] = env.get_player_loc()
        self.maze: list = env.get_agent_maze()
        self.kb: "MazeKnowledgeBase" = MazeKnowledgeBase()
        self.possible_pits: set[tuple[int, int]] = set()
        self.pit_tiles: set[tuple[int, int]] = set()
        self.safe_tiles: set[tuple[int, int]] = set()
        self.safe_tiles.add(self.start)
        self.safe_tiles.add(self.goal)
        for tile in env.get_cardinal_locs(self.start, 1):
            self.safe_tiles.add(tile)
        
    ##################################################################
    # Methods
    ##################################################################
    
    def think(self, perception: dict) -> tuple[int, int]:
        """
        The main workhorse method of how your agent will process new information
        and use that to make deductions and decisions. In gist, it should follow
        this outline of steps:
        1. Process the given perception, i.e., the new location it is in and the
           type of tile on which it's currently standing (e.g., a safe tile, or
           warning tile like "1" or "2")
        2. Update the knowledge base and record-keeping of where known pits and
           safe tiles are located, as well as locations of possible pits.
        3. Query the knowledge base to see if any locations that possibly contain
           pits can be deduced as safe or not.
        4. Use all of the above to prioritize the next location along the frontier
           to move to next.
        
        Parameters:
            perception (dict):
                A dictionary providing the agent's current location
                and current tile type being stood upon, of the format:
                {"loc": (x, y), "tile": tile_type}
        
        Returns:
            tuple[int, int]:
                The maze location along the frontier that your agent will try to
                move into next.
        """
        self.kb.tell(MazeClause([(("P", self.goal), False)]))
        self.safe_tiles.add(self.goal)
        location: tuple[int, int] = perception.get("loc") #location of current tile
        tile_type: str = perception.get("tile") #current tile type
        frontier: set[tuple[int, int]] = self.env.get_frontier_locs()
        best_score: float() = float("inf")
        best_location: tuple[int, int] = None
        assigned: bool() = False
        scores: dict() = dict()

        if self.goal in self.env.get_frontier_locs():
            return self.goal
        
        if tile_type == 'P':
            clause: MazeClause() = MazeClause([(("P", location), True)])
            self.kb.tell(clause)
            self.possible_pits.discard(location)
            self.pit_tiles.add(location)

        elif tile_type == '.':                #If current tile is safe
            self.kb.tell(MazeClause([(("P", location), False)]))
            self.safe_tiles.add(location)
            self.possible_pits.discard(location)
            adjacent_tiles: set[tuple[int, int]] = self.env.get_cardinal_locs(location, 1)
            
            for tile in adjacent_tiles:
                 self.safe_tiles.add(tile)
                 self.possible_pits.discard(tile)                           #Add all adjacent tiles as safe in knowledge base
                 self.kb.tell(MazeClause([(("P", tile), False)]))

        else:
            self.warning_tile_clause(tile_type, location)                                          #Else, warning tile
            self.safe_tiles.add(location)
            self.possible_pits.discard(location)
            possible_pits: set[tuple[int, int]] = self.env.get_cardinal_locs(location, 1)    #Possible pits

            for coordinates in possible_pits:
                if coordinates not in self.safe_tiles:   #If possible pit coordinates are not in explored locations or safe tiles
                    self.possible_pits.add(coordinates)

        self.kb.simplify_self(self.pit_tiles, self.safe_tiles)
        
        for loc in frontier:
            if self.kb.ask(MazeClause([(("P", loc), True)])):
                self.pit_tiles.add(loc)
                self.possible_pits.discard(loc)
            if self.kb.ask(MazeClause([(("P", loc), False)])):
                self.safe_tiles.add(loc)
                self.possible_pits.discard(loc)

            if loc in self.pit_tiles: #known pit
                scores[loc]: int() = self.get_manhattan_dist(loc) + 20
                assigned: bool() = True
            else: #not known pit
                if loc not in self.possible_pits and loc in self.safe_tiles: #safe
                        scores[loc]: int() = self.get_manhattan_dist(loc)
                        assigned: bool() = True
                else: #possible pit
                    scores[loc]: int() = self.get_manhattan_dist(loc) + 15
                    assigned: bool() = True
            
        for loc in scores:
            if scores[loc] < best_score:
                best_score: int() = scores[loc]
                best_location: tuple[int, int] = loc

        if assigned and best_score:
            return best_location
        print("randy!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return random.choice(list(frontier))
        
    def is_safe_tile (self, loc: tuple[int, int]) -> Optional[bool]:
        """
        Determines whether or not the given maze location can be concluded as
        safe (i.e., not containing a pit), following the steps:
        1. Check to see if the location is already a known pit or safe tile,
           responding accordingly
        2. If not, performs the necessary queries on the knowledge base in an
           attempt to deduce its safety
        
        Parameters:
            loc (tuple[int, int]):
                The maze location in question
        
        Returns:
            One of three return values:
            1. True if the location is certainly safe (i.e., not pit)
            2. False if the location is certainly dangerous (i.e., pit)
            3. None if the safety of the location cannot be currently determined
        """
        #FROM SPEC: "As such, your agent will ALWAYS start on a safe tile, and will never have to make a guess starting from a warning block."
        if loc in self.safe_tiles: return True
        if loc in self.pit_tiles: return False
        if self.kb.ask(MazeClause([(("P", loc), True)])): return False
        if self.kb.ask(MazeClause([(("P", loc), False)])): return True
        return None
        
    def get_manhattan_dist(self, loc: tuple[int,int]) -> int:
        return abs(loc[0] - self.goal[0]) + abs(loc[1] - self.goal[1])
    
    def warning_tile_clause(self, warning_num, loc: tuple[int,int]):
        adjacent_tiles: set[tuple[int, int]] = self.env.get_cardinal_locs(loc,1) #minus the tiles that we already know about
        adj_list: list() = [tile for tile in adjacent_tiles if tile not in self.safe_tiles]

        if warning_num == '3':                        #if warning_num == 3 then all the adjacent tiles are pits besides the tile you just came from
            for tile in adjacent_tiles:
                clause: MazeClause() = MazeClause([(("P", tile), True)])
                self.pit_tiles.add(tile)
                self.kb.tell(clause)

        elif warning_num == '2':
            if len(adj_list) == 2:
                self.kb.tell(MazeClause([(("P", adj_list[0]), True)]))
                self.kb.tell(MazeClause([(("P", adj_list[1]), True)]))
                self.pit_tiles.add(adj_list[0])
                self.pit_tiles.add(adj_list[1])
            else:
                for i in range(len(adj_list)):
                    for j in range(i+1, len(adj_list)):
                        clause: list() = []
                        clause.append((("P", adj_list[i]), True))
                        clause.append((("P", adj_list[j]), True))
                        self.kb.tell(MazeClause(clause))
                
                triple: list() = []
                for i in range(len(adj_list)):
                    triple.append((("P", adj_list[i]), False))
                self.kb.tell(MazeClause(triple))
    
        elif warning_num == '1':
            if len(adj_list) == 1:
                self.kb.tell(MazeClause([(("P", adj_list[0]), True)]))
                self.pit_tiles.add(adj_list[0])
            else:
                for i in range(len(adj_list)):
                    for j in range(i+1, len(adj_list)):
                        clause = []
                        clause.append((("P", adj_list[i]), False))
                        clause.append((("P", adj_list[j]), False))
                        self.kb.tell(MazeClause(clause))
                
                triple = []
                for i in range(len(adj_list)):
                    triple.append ((("P", adj_list[i]), True))
                self.kb.tell(MazeClause(triple))
        self.kb.simplify_self(self.pit_tiles, self.safe_tiles)

# Declared here to avoid circular dependency
from environment import Environment