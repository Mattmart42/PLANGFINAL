from maze_clause import MazeClause
import itertools
from copy import deepcopy

class MazeKnowledgeBase:
    '''
    Specifies a simple, Conjunctive Normal Form Propositional
    Logic Knowledge Base for use in Grid Maze pathfinding problems
    with side-information.
    '''
    
    def __init__ (self) -> None:
        """
        Initializes a new MazeKnowledgeBase, which will be used to track the
        locations of pits and safe tiles (i.e., "not" pits) throughout the
        Pitsweeper exercise, but is also structured more generally to track
        MazeClauses of any kind.
        
        It begins as an empty knowledgebase with no contained clauses.
        """
        self.clauses: set["MazeClause"] = set()
    
    def tell (self, clause: "MazeClause") -> None:
        """
        Adds the given clause to the CNF MazeKnowledgeBase
        [!] Note: we expect that no clause added this way will ever
        make the KB inconsistent, but this naive assumption is done
        to save on computational efficiency and relies on your clauses
        being constructed correctly. Test carefully!
        
        Parameters:
            clause (MazeClause):
                A new MazeClause to add to this knowledgebase
        """
        self.clauses.add(clause)
        
    def ask (self, query: "MazeClause") -> bool:
        """
        Given a MazeClause query, returns True if the KB entails the query, 
        False otherwise. Uses the proof by contradiction technique detailed
        during the lectures.
        
        Parameters:
            query (MazeClause):
                The query clause to determine if this is entailed by the KB
        
        Returns:
            bool:
                True if the KB entails the query, False otherwise
        """
        # [!] TODO: Implement the proof-by-contradiction knowledgebase
        # query procedure here!
        clauses: set["MazeClause"] = self.clauses.copy()
        negatedProps: dict[tuple[str, tuple[int, int]], bool] = {key: not value for key, value in query.props.items()}
        contradiction: "MazeClause" = MazeClause(negatedProps.items())
        clauses.add(contradiction)
        new = set()
        
        while True:
            clauses_list = list(clauses)
            for i in range(len(clauses_list)):
                for j in range(i + 1, len(clauses_list)):
                    resolvents = query.resolve(clauses_list[i],clauses_list[j])
                    if MazeClause([]) in resolvents:
                        return True
                    new.update(resolvents)
            if new.issubset(clauses):
                return False
            clauses.update(new)

    def __len__ (self) -> int:
        """
        Returns the number of clauses currently stored in the KB
        
        Returns:
            int:
                The number of stored clauses
        """
        return len(self.clauses)
    
    def __str__ (self) -> str:
        """
        Converts the KB into its string presentation, printing out ALL
        contained clauses in set format.
        
        [!] Warning: use only for small KBs or the results will be
        overwhelming and uninformative
        
        Returns:
            str:
                All clauses in the KB converted to their str format
        """
        return str([str(clause) for clause in self.clauses])

    # Methods Useful for Optimization in Part 2
    # -----------------------------------------------------------------------------------------

    def simplify_self (self, known_pits: set[tuple[int, int]], known_safe: set[tuple[int, int]]) -> None:
        """
        Condenses the number and size of clauses in the knowledgebase based on
        knowledge of where known pits and safe tiles have been deduced / found.
        
        [!] Should only be called when new information has been added to the known
            pit or safe tile locations
        
        Example:
            KB = {(P(1,1) v ~P(2,1)) ^ (~P(1,1) v P(1,2))}
            known_pits = {(1,1)}
            The KB can thus be condensed to:
            KB = {(P(1,1)) ^ (P(1,2))}
        
        Paramters:
            known_pits (set[tuple[int, int]]):
                The known locations of pits in the maze
            known_safe (set[tuple[int, int]]):
                The known locations of safe tiles (i.e., not containing pits) in the maze
        """
        self.clauses = MazeKnowledgeBase.simplify_from_known_locs(self.clauses, known_pits, known_safe)
    
    @staticmethod
    def simplify_from_known_locs (clauses: set["MazeClause"], known_pits: set[tuple[int, int]], known_safe: set[tuple[int, int]]) -> set["MazeClause"]:
        """
        Given a set of MazeClauses and a set of known pit and safe tile locations, condenses the logic
        of the clauses such that the clauses are smaller and less numerous, where possible.
        
        See:
            simplify_self method
        
        Parameters:
            clauses (set[MazeClause]):
                The set of MazeClauses that we are attempting to simplify
            known_pits (set[tuple[int, int]]):
                The known locations of pits in the maze
            known_safe (set[tuple[int, int]]):
                The known locations of safe tiles (i.e., not pits) in the maze
        
        Returns:
            A simplified set of the input clauses that may be less numerous and complex as the original
        """
        for loc in known_pits | known_safe:
            clauses = MazeKnowledgeBase.get_simplified_clauses(clauses, loc, loc in known_pits)
        return clauses
    
    @staticmethod
    def get_simplified_clauses (clauses: set["MazeClause"], loc: tuple[int, int], is_pit: bool) -> set["MazeClause"]:
        """
        Simplifies a set of MazeClauses given the knowledge that the specified location
        either is certainly a pit or certainly not a pit.
        
        See:
            simplify_from_known_locs method
            
        Parameters:
            clauses (set[MazeClause]):
                The set of MazeClauses that we are attempting to simplify
            loc (tuple[int, int]):
                The location in the maze that we know either is or is not a pit
            is_pit (bool):
                Whether or not the given loc is a pit
        
        Returns:
            A simplified set of the input clauses that may be less numerous and complex as the original
        """
        to_add = set()
        to_rem = set()
        sani_clause = MazeClause([(("P", loc), is_pit)])
        for clause in clauses:
            if len(clause) == 1:
                continue
            if clause.get_prop(("P", loc)) == is_pit:
                to_rem.add(clause)
                break
            to_add.update(MazeClause.resolve(clause, sani_clause))
            
        clauses = clauses | to_add
        clauses = clauses - to_rem
        return clauses