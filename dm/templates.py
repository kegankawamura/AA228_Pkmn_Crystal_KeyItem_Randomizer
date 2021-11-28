from abc import ABC,abstractmethod
from enum import Enum,auto

class ActionType(Enum):
    ACC_CHECKS  = auto()
    CHECKS_LOCS = auto()

class Agent:
    def __init__(self,true_game,alg):
        self.game = true_game
        self.decisionmaker = alg(true_game)
    def policy(self):
        return self.decisionmaker.decide_action()

class DecisionMaker(ABC):
    def __init__(self,true_game):
        self.game = true_game
    
    @property
    @abstractmethod
    def action_type(self):
        """ action_type defines what types of actions to choose from and which to use when simulating. One of:
    ACC_CHECKS  - actions are the set of all available checks, regardless of player location
    CHECKS_LOCS - actions are the checks at the player location and any locations immediately adjacent to player location 
    """

    @abstractmethod
    def decide_action(self):
        """ returns the action to make based on the game state
        represented in self.game """
    
    def possible_actions(self):
        """ returns a list of all possible actions that the DecisionMaker chooses from. """
        if self.action_type==ActionType.ACC_CHECKS:
            return self.game.get_accessible_checks()
        if self.action_type==ActionType.CHECKS_LOCS:
            return self.game.get_checks_here()+self.game.get_neighboring_locations()
        raise Exception('action_type invalid')

