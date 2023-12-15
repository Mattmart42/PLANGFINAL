from environment import *
from maze_clause import *
from constants import *
from maze_knowledge_base import *
from copy import deepcopy
from statistics import *
import unittest
import pytest

# Time in seconds given to complete mazes of different difficulty
# Can temporarily set these high for debugging
EASY_TIMEOUT = 10
MED_TIMEOUT  = 40
HARD_TIMEOUT = 60
OPT_ERR = "[X] Your agent's score was too low to pass this test"

# Set VERBOSE to True and TICK to something like 1 to see maze 
# played out, then run individual tests using the syntax like:
# pytest -k test_pitsweeper_easy1
VERBOSE = False
TICK    = 0

# Logs for grade reporting
easy_scores: dict[str, int] = dict()
med_scores: dict[str, int]  = dict()
hard_scores: dict[str, int] = dict()

class PitsweeperTests(unittest.TestCase):
    """
    The final set of tests for your MazeAgent and Pitsweeping!
    
    [!] Ensure that all MazeClause and MazeKnowledgeBase tests pass before
    moving onto this one!
    
    [!] Warning: the following is only a partial set of the grading unit
    tests! Make sure you test your agent adequately to give yourself the
    confidence that it behaves correctly!
    """
    
    def score_maze (self, threshold: int, score: int, dict_log: dict) -> None:
        """
        Logs the scores of your agent on each of the different test difficulties,
        and ensure that, individually, each passes the threshold minimum score.
        
        Parameters:
            threshold (int):
                The minimum score that passes the given maze.
            score (int):
                The score obtained by your agent on the given maze.
            dict_log (dict):
                The dictionary of scores in which to log the current one.
        """
        dict_log[self._testMethodName] = score
        self.assertLess(threshold, score, OPT_ERR)
    
    @classmethod
    def tearDownClass(cls: Any) -> None:
        """
        Simple reporting method that is called at the end of the unit tests to report
        scores; used for grading only.
        """
        if len(easy_scores) == 0 or len(med_scores) == 0 or len(hard_scores) == 0:
            return
        print("\n---------------------------------------------")
        print("[!] Tests completed:")
        print("    > Easy Test Average:\t" + str(mean(easy_scores.values())))
        print("    > Medium Test Average:\t" + str(mean(med_scores.values())))
        print("    > Hard Test Average:\t" + str(mean(hard_scores.values())))
    
    # EZ Tests
    # -----------------------------------------------------------------------------------------
    
    @pytest.mark.timeout(EASY_TIMEOUT)
    def test_pitsweeper_easy1(self) -> None:
        #    c-> 012345   # r
        maze = ["XXXXXX", # 0
                "X...GX", # 1
                "X...PX", # 2
                "X....X", # 3
                "X....X", # 4
                "X@...X", # 5
                "XXXXXX"] # 6
        env = Environment(maze, tick_length = TICK, verbose = VERBOSE)
        score = env.start_mission()
        # assertLess(threshold, score) where score must be > threshold to pass
        self.score_maze(-20, score, easy_scores)
        
    @pytest.mark.timeout(EASY_TIMEOUT)
    def test_pitsweeper_easy2(self) -> None:
        #    c-> 012345   # r
        maze = ["XXXXXX", # 0
                "X...GX", # 1
                "X...PX", # 2
                "X....X", # 3
                "X..P.X", # 4
                "X@...X", # 5
                "XXXXXX"] # 6
        env = Environment(maze, tick_length = TICK, verbose = VERBOSE)
        score = env.start_mission()
        self.score_maze(-20, score, easy_scores)
    
    # Medium Tests
    # -----------------------------------------------------------------------------------------
    
    @pytest.mark.timeout(MED_TIMEOUT)
    def test_pitsweeper_med1(self) -> None:
        maze = ["XXXXXXXXX",
                "X..PGP..X",
                "X.......X",
                "X..PPP..X",
                "X.......X",
                "X..@....X",
                "XXXXXXXXX"]
        env = Environment(maze, tick_length = TICK, verbose = VERBOSE)
        score = env.start_mission()
        self.score_maze(-32, score, med_scores)
        
    @pytest.mark.timeout(MED_TIMEOUT)
    def test_pitsweeper_med2(self) -> None:
        maze = ["XXXXXXXXX",
                "X..P.P.GX",
                "X@......X",
                "X..P.P..X",
                "X.......X",
                "X.......X",
                "XXXXXXXXX"]
        env = Environment(maze, tick_length = TICK, verbose = VERBOSE)
        score = env.start_mission()
        self.score_maze(-32, score, med_scores)
        
    # Hard Tests
    # -----------------------------------------------------------------------------------------
    
    @pytest.mark.timeout(HARD_TIMEOUT)
    def test_pitsweeper_hard1(self) -> None:
        maze = ["XXXXXXXXX",
                "X......GX",
                "X.......X",
                "X.PPPPPPX",
                "X.......X",
                "X......@X",
                "XXXXXXXXX"]
        env = Environment(maze, tick_length = TICK, verbose = VERBOSE)
        score = env.start_mission()
        self.score_maze(-35, score, hard_scores)
        
    @pytest.mark.timeout(HARD_TIMEOUT)
    def test_pitsweeper_hard2(self) -> None:
        maze = ["XXXXXXXXX",
                "XG.P....X",
                "X.......X",
                "X.PP.PP.X",
                "XP.....PX",
                "X...@...X",
                "XXXXXXXXX"]
        env = Environment(maze, tick_length = TICK, verbose = VERBOSE)
        score = env.start_mission()
        self.score_maze(-40, score, hard_scores)
        
if __name__ == "__main__":
    unittest.main()
