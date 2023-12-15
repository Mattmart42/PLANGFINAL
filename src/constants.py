class Constants:
    '''
    Simulation / Maze constants important for the Pitsweeper problem
    
    [!] IMPORTANT:
      - YOU MUST NOT TOUCH THIS FILE AT ALL, NO EDITS OR ADDITIONS!
        Any changes will be overwritten during testing
      - If you need additional constants shared between your files,
        make your own damn module
    '''
    
    # The following are staticmethods to prevent tampering,
    # I've got my eye on you, even if through this comment
    @staticmethod
    def get_min_score () -> int:
        """
        Returns the minimum score that, if reached, will end the game,
        and bring great shame to your agent
        """
        return -100
    
    @staticmethod
    def get_pit_penalty () -> int:
        """
        Returns the cost of stepping into a Pit... you're not dead just...
        like... really inconvenienced
        """
        return 20
    
    # Maze content constants
    WALL_BLOCK  = "X"
    GOAL_BLOCK  = "G"
    PIT_BLOCK   = "P"
    SAFE_BLOCK  = "."
    PLR_BLOCK   = "@"
    UNK_BLOCK   = "?"
    WRN_ZERO_BLOCK  = "0"
    WRN_ONE_BLOCK   = "1"
    WRN_TWO_BLOCK   = "2"
    WRN_THREE_BLOCK = "3"
    WRN_FOUR_BLOCK  = "4"
    WRN_BLOCKS  = {WRN_ZERO_BLOCK, WRN_ONE_BLOCK, WRN_TWO_BLOCK, WRN_THREE_BLOCK, WRN_FOUR_BLOCK}