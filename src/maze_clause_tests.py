from environment import *
from maze_clause import *
from maze_knowledge_base import *
from copy import deepcopy
import unittest

class MazeClauseTests(unittest.TestCase):
    """
    Tests for the MazeClause class.
    
    [!] Ensure that all tests pass here FIRST before advancing to
    the MazeKnowledgeBase problems.
    """
    
    
    # MazeClause Construction Tests
    # -----------------------------------------------------------------------------------------
    def test_mazeclause_construction1(self) -> None:
        mc = MazeClause([(("X", (1, 1)), True), (("X", (2, 1)), True), (("Y", (1, 2)), False)])
        self.assertTrue(mc.get_prop(("X", (1, 1))))
        self.assertTrue(mc.get_prop(("X", (2, 1))))
        self.assertFalse(mc.get_prop(("Y", (1, 2))))
        self.assertEqual(None, mc.get_prop(("X", (2, 2))))
        self.assertFalse(mc.is_empty())
        
    def test_mazeclause_construction2(self) -> None:
        mc = MazeClause([(("X", (1, 1)), True), (("X", (1, 1)), True)])
        self.assertTrue(mc.get_prop(("X", (1, 1))))
        self.assertFalse(mc.is_empty())
        
    def test_mazeclause_construction3(self) -> None:
        mc = MazeClause([(("X", (1, 1)), True), (("Y", (2, 1)), True), (("X", (1, 1)), False)])
        self.assertTrue(mc.is_valid())
        self.assertEqual(None, mc.get_prop(("X", (1, 1))))
        self.assertFalse(mc.is_empty())
        
    def test_mazeclause_construction4(self) -> None:
        mc = MazeClause([])
        self.assertFalse(mc.is_valid())
        self.assertTrue(mc.is_empty())
    
    # MazeClause Resolution Tests
    # -----------------------------------------------------------------------------------------
    def test_mazeclause_resolution1(self) -> None:
        mc1 = MazeClause([(("X", (1, 1)), True)])
        mc2 = MazeClause([(("X", (1, 1)), True)])
        res = MazeClause.resolve(mc1, mc2)
        self.assertEqual(len(res), 0)
        
    def test_mazeclause_resolution2(self) -> None:
        mc1 = MazeClause([(("X", (1, 1)), True)])
        mc2 = MazeClause([(("X", (1, 1)), False)])
        res = MazeClause.resolve(mc1, mc2)
        self.assertEqual(len(res), 1)
        self.assertTrue(MazeClause([]) in res)
          
    def test_mazeclause_resolution3(self) -> None:
        mc1 = MazeClause([(("X", (1, 1)), True), (("Y", (1, 1)), True)])
        mc2 = MazeClause([(("X", (1, 1)), False), (("Y", (2, 2)), True)])
        res = MazeClause.resolve(mc1, mc2)
        self.assertEqual(1, len(res))
        self.assertTrue(MazeClause([(("Y", (1, 1)), True), (("Y", (2, 2)), True)]) in res)

    def test_mazeclause_resolution4(self) -> None:
        mc1 = MazeClause([(("X", (1, 1)), True), (("Y", (1, 1)), False)])
        mc2 = MazeClause([(("X", (1, 1)), False), (("Y", (1, 1)), True)])
        res = MazeClause.resolve(mc1, mc2)
        self.assertEqual(0, len(res))
        
    def test_mazeclause_resolution5(self) -> None:
        mc1 = MazeClause([(("X", (1, 1)), True), (("Y", (1, 1)), False), (("Z", (1, 1)), True)])
        mc2 = MazeClause([(("X", (1, 1)), False), (("Y", (1, 1)), True), (("W", (1, 1)), False)])
        res = MazeClause.resolve(mc1, mc2)
        self.assertEqual(0, len(res))
        
    def test_mazeclause_resolution6(self) -> None:
        mc1 = MazeClause([(("X", (1, 1)), True), (("Y", (1, 1)), False), (("Z", (1, 1)), True)])
        mc2 = MazeClause([(("X", (1, 1)), False), (("Y", (1, 1)), False), (("W", (1, 1)), False)])
        res = MazeClause.resolve(mc1, mc2)
        self.assertEqual(1, len(res))
        self.assertTrue(MazeClause([(("Y", (1, 1)), False), (("Z", (1, 1)), True), (("W", (1, 1)), False)]) in res)
        
    def test_mazeclause_resolution7(self) -> None:
        mc = MazeClause([(("A", (1, 0)), True), (("A", (0, 0)), False)])
        self.assertTrue(mc.get_prop(("A", (1, 0))))
        self.assertFalse(mc.get_prop(("A", (0, 0))))
        self.assertFalse(mc.is_valid())

    def test_mazeclause_resolution8(self) -> None:
        mc = MazeClause([(("B", (1, 4)), True), (("B", (1, 4)), True)])
        self.assertTrue(mc.get_prop(("B", (1, 4))))
        self.assertFalse(mc.is_valid())
        self.assertFalse(mc.is_empty())

    def test_mazeclause_resolution9(self) -> None:
        mc = MazeClause([(("A", (1, 0)), True), (("A", (0, 0)), False), (("B", (1, 4)), True), (("B", (1, 4)), False)])
        self.assertTrue(mc.is_valid())
        self.assertFalse(mc.is_empty())

    def test_mazeclause_resolution10(self) -> None:
        mc1 = MazeClause([(("A", (1, 0)), True), (("A", (0, 0)), False), (("A", (1, 4)), True), (("A", (2, 0)), False)])
        res = MazeClause.resolve(mc1, mc1)
        self.assertEqual(0, len(res))

    def test_mazeclause_resolution11(self) -> None:
        mc1 = MazeClause([(("A", (1, 0)), True), (("A", (0, 0)), False), (("A", (1, 4)), True), (("A", (2, 0)), False)])
        mc2 = MazeClause([(("A", (1, 0)), True), (("A", (0, 0)), False), (("A", (1, 4)), False), (("A", (2, 0)), False)])
        res = MazeClause.resolve(mc1, mc2)
        self.assertEqual(1, len(res))
        self.assertTrue(MazeClause([(("A", (1, 0)), True), (("A", (0, 0)), False), (("A", (2, 0)), False)]) in res)

    def test_mazeclause_resolution12(self) -> None:
        mc1 = MazeClause([(("A", (1, 0)), True), (("A", (0, 0)), False), (("A", (1, 4)), True), (("A", (2, 0)), False)])
        mc2 = MazeClause([(("A", (1, 0)), True), (("A", (0, 0)), False), (("A", (1, 4)), False), (("A", (2, 0)), True)])
        res = MazeClause.resolve(mc1, mc2)
        self.assertEqual(0, len(res))


if __name__ == "__main__":
    unittest.main()