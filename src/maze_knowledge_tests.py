from environment import *
from maze_clause import *
from maze_knowledge_base import *
from copy import deepcopy
import unittest

class MazeKnowledgeTests(unittest.TestCase):
    """
    Tests for the MazeKnowledgeBase class.
    
    [!] Ensure that all tests pass here before moving onto the MazeAgent and Pitsweeper tests!
    """
    
    # MazeKB Tests
    # -----------------------------------------------------------------------------------------
    
    def test_mazekb1(self) -> None:
        kb = MazeKnowledgeBase()
        kb.tell(MazeClause([(("X", (1, 1)), True)]))
        self.assertTrue(kb.ask(MazeClause([(("X", (1, 1)), True)])))
        
    def test_mazekb2(self) -> None:
        kb = MazeKnowledgeBase()
        kb.tell(MazeClause([(("X", (1, 1)), False)]))
        kb.tell(MazeClause([(("X", (1, 1)), True), (("Y", (1, 1)), True)]))
        self.assertTrue(kb.ask(MazeClause([(("Y", (1, 1)), True)])))
        
    def test_mazekb3(self) -> None:
        kb = MazeKnowledgeBase()
        kb.tell(MazeClause([(("X", (1, 1)), False), (("Y", (1, 1)), True)]))
        kb.tell(MazeClause([(("Y", (1, 1)), False), (("Z", (1, 1)), True)]))
        kb.tell(MazeClause([(("W", (1, 1)), True), (("Z", (1, 1)), False)]))
        kb.tell(MazeClause([(("X", (1, 1)), True)]))
        self.assertTrue(kb.ask(MazeClause([(("W", (1, 1)), True)])))
        self.assertFalse(kb.ask(MazeClause([(("Y", (1, 1)), False)])))
    
    # Added from the skeleton
    def test_mazekb4(self) -> None:
        # The Great Forneybot Uprising!
        kb = MazeKnowledgeBase()
        kb.tell(MazeClause([(("M", (1, 1)), False), (("D", (1, 1)), True), (("P", (1, 1)), True)]))
        kb.tell(MazeClause([(("D", (1, 1)), False), (("M", (1, 1)), True)]))
        kb.tell(MazeClause([(("P", (1, 1)), False), (("M", (1, 1)), True)]))
        kb.tell(MazeClause([(("R", (1, 1)), False), (("W", (1, 1)), True), (("S", (1, 1)), True)]))
        kb.tell(MazeClause([(("R", (1, 1)), False), (("D", (1, 1)), True)]))
        kb.tell(MazeClause([(("D", (1, 1)), False), (("R", (1, 1)), True)]))
        kb.tell(MazeClause([(("P", (1, 1)), False), (("F", (1, 1)), True)]))
        kb.tell(MazeClause([(("F", (1, 1)), False), (("P", (1, 1)), True)]))
        kb.tell(MazeClause([(("F", (1, 1)), False), (("S", (1, 1)), False)]))
        kb.tell(MazeClause([(("F", (1, 1)), False), (("W", (1, 1)), False)]))
        kb.tell(MazeClause([(("S", (1, 1)), False), (("W", (1, 1)), False)]))
        kb.tell(MazeClause([(("M", (1, 1)), True)]))
        kb.tell(MazeClause([(("F", (1, 1)), True)]))
        
        # asking alpha = !D ^ P should return True; KB does entail alpha
        kb1 = deepcopy(kb)
        kb1.tell(MazeClause([(("D", (1, 1)), False)]))
        self.assertTrue(kb1.ask(MazeClause([(("P", (1, 1)), True)])))

        kb2 = deepcopy(kb)
        kb2.tell(MazeClause([(("P", (1, 1)), True)]))
        self.assertTrue(kb2.ask(MazeClause([(("D", (1, 1)), False)])))

    def test_mazekb5(self) -> None:
        kb = MazeKnowledgeBase()
        # If it is raining, then the sidewalk is wet. !R v S
        kb.tell(MazeClause([(("R", (1, 1)), False), (("S", (1, 1)), True)]))

        # It's raining; KB entails that sidewalk is wet
        kb1 = deepcopy(kb)
        kb1.tell(MazeClause([(("R", (1, 1)), True)]))
        self.assertTrue(kb1.ask(MazeClause([(("S", (1, 1)), True)])))

        # The sidewalk's wet; KB does not entail that it's raining
        kb2 = deepcopy(kb)
        kb2.tell(MazeClause([(("S", (1, 1)), True)]))
        self.assertFalse(kb2.ask(MazeClause([(("R", (1, 1)), True)])))

    def test_mazekb6(self) -> None:
        kb = MazeKnowledgeBase()
        kb.tell(MazeClause([(("X", (0, 0)), True), (("Z", (0, 0)), True), (("Y", (0, 0)), True)]))
        kb.tell(MazeClause([(("Z", (0, 0)), False), (("W", (0, 0)), True), (("X", (0, 0)), True)]))
        kb.tell(MazeClause([(("X", (0, 0)), False), (("W", (0, 0)), True)]))
        kb.tell(MazeClause([(("W", (0, 0)), False)]))

        # KB does entail alpha = !X ^ Y
        kb.tell(MazeClause([(("X", (0, 0)), False)]))
        self.assertTrue(kb.ask(MazeClause([(("Y", (0, 0)), True)])))
    
    # MazeInference Tests
    # -----------------------------------------------------------------------------------------

    def test_inference1(self) -> None:
        #    c-> 012345   # r
        maze = ["XXXXXX", # 0
                "X...GX", # 1
                "X..PPX", # 2
                "X....X", # 3
                "X..P.X", # 4
                "X@...X", # 5
                "XXXXXX"] # 6
        env = Environment(maze, tick_length = 0, verbose = False)
        # The starting tile should be known as safe
        self.assertEqual(True, env.test_safety_check((1,5)))
         
        # Given that the perception will be a 0 tile on the initial space, we also
        # know that surrounding tiles are
        self.assertEqual(True, env.test_safety_check((1,4)))
        self.assertEqual(True, env.test_safety_check((2,5)))
        
        # If that's the only perception, however, other tiles won't be known safe
        self.assertEqual(None, env.test_safety_check((2,4)))
        self.assertEqual(None, env.test_safety_check((4,2)))
         
        # Still, the goal should always be safe
        self.assertEqual(True, env.test_safety_check((4,1)))
        
    def test_inference2(self) -> None:
        #    c-> 012345   # r
        maze = ["XXXXXX", # 0
                "X...GX", # 1
                "X..PPX", # 2
                "X....X", # 3
                "X..P.X", # 4
                "X.@..X", # 5
                "XXXXXX"] # 6
        env = Environment(maze, tick_length = 0, verbose = False)
        
        # Won't know whether or not there's a pit near the start to begin with
        self.assertEqual(None, env.test_safety_check((3,4)))
        
        # ...but if you move up twice...
        env.test_move((2,4))
        env.test_move((2,3))
        
        # We know the pit's in 1 of two places, neither of which are safe:
        self.assertEqual(None, env.test_safety_check((3,4)))
        self.assertEqual(None, env.test_safety_check((1,4)))
        
        # Learn a lot of safe spaces too
        self.assertEqual(True, env.test_safety_check((2,3)))
        self.assertEqual(True, env.test_safety_check((2,4)))
        self.assertEqual(True, env.test_safety_check((1,5)))
        
        # Trickier deductions here: make sure your added clauses to the KB during think
        # are right to pass these!
        self.assertEqual(True, env.test_safety_check((3,5)))
        self.assertEqual(True, env.test_safety_check((3,3)))
        self.assertEqual(True, env.test_safety_check((1,3)))
        
        # Only after moving once more do we get the truth!
        env.test_move((1,3))
        self.assertEqual(False, env.test_safety_check((3,4))) # Pit here!
        self.assertEqual(True, env.test_safety_check((1,4)))  # No pit here!
        
    def test_inference3(self) -> None:
        #    c-> 012345   # r
        maze = ["XXXXXX", # 0
                "X...GX", # 1
                "X..PPX", # 2
                "X.P..X", # 3
                "X..P.X", # 4
                "X.@..X", # 5
                "XXXXXX"] # 6
        env = Environment(maze, tick_length = 0, verbose = False)
        
        # Let's do a little square dancing
        env.test_move((2,4))
        
        # Saw a 2, so there are 3 possible combos of pits in the surrounding
        # tile, none of which we can currently conclude are safe
        self.assertEqual(None, env.test_safety_check((3,4)))
        self.assertEqual(None, env.test_safety_check((2,3)))
        self.assertEqual(None, env.test_safety_check((1,4)))
        
        # ... until we move to the bottom-left
        env.test_move((1,5))
        
        # Then we know!
        self.assertEqual(False, env.test_safety_check((3,4)))
        self.assertEqual(False, env.test_safety_check((2,3)))
        self.assertEqual(True, env.test_safety_check((1,4)))
        
    def test_inference4(self) -> None:
        #    c-> 012345   # r
        maze = ["XXXXXX", # 0
                "XP@.GX", # 1
                "XXXXXX"] # 2
        env = Environment(maze, tick_length = 0, verbose = False)
        
        # Remember: we know that at *least* one tile around the Goal is safe,
        # so starting on a 1 warning tile here isn't a problem
        self.assertEqual(False, env.test_safety_check((1,1)))
        self.assertEqual(True, env.test_safety_check((2,1)))
        self.assertEqual(True, env.test_safety_check((3,1)))
        
    def test_inference5(self) -> None:
        #    c-> 012345   # r
        maze = ["XXXXXX", # 0
                "X..PGX", # 1
                "X....X", # 2
                "X.P..X", # 3
                "XP.P.X", # 4
                "X.@..X", # 5
                "XXXXXX"] # 6
        env = Environment(maze, tick_length = 0, verbose = False)
        
        # About to walk into a corridor of pain:
        env.test_move((2,4))
        
        # We'll know immediately that we're surrounded by pits
        self.assertEqual(False, env.test_safety_check((1,4)))
        self.assertEqual(False, env.test_safety_check((2,3)))
        self.assertEqual(False, env.test_safety_check((3,4)))
        
        # Beating a hasty retreat, we should have a way out:
        env.test_move((3,5))
        self.assertEqual(True, env.test_safety_check((4,5)))
        
        env.test_move((4,5))
        self.assertEqual(True, env.test_safety_check((4,4)))

        env.test_move((4,4))
        self.assertEqual(True, env.test_safety_check((4,3)))
        
    def test_inference6(self) -> None:
        #    c-> 012345   # r
        maze = ["XXXXXX", # 0
                "X..PGX", # 1
                "X....X", # 2
                "X....X", # 3
                "XP.PPX", # 4
                "X.@..X", # 5
                "XXXXXX"] # 6
        env = Environment(maze, tick_length = 0, verbose = False)
        
        # We might be faced with an unavoidable risk scenario
        env.test_move((2,4))
        self.assertEqual(None, env.test_safety_check((1,4)))
        self.assertEqual(None, env.test_safety_check((2,3)))
        self.assertEqual(None, env.test_safety_check((3,4)))
        
        # ...and choose poorly
        env.test_move((3,4))
        self.assertEqual(None, env.test_safety_check((1,4)))
        self.assertEqual(None, env.test_safety_check((2,3)))
        self.assertEqual(False, env.test_safety_check((3,4)))
        
        # ...but a safe exploration will yield certainty
        env.test_move((1,5))
        self.assertEqual(False, env.test_safety_check((1,4)))
        self.assertEqual(True, env.test_safety_check((2,3)))
        self.assertEqual(False, env.test_safety_check((3,4)))
      
        
if __name__ == "__main__":
    unittest.main()