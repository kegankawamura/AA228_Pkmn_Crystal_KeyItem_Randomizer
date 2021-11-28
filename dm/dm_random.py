from dm.templates import DecisionMaker,ActionType
import numpy
from numpy.random import default_rng

class Random(DecisionMaker):
    action_type = ActionType.ACC_CHECKS

    def decide_action(self):
        return default_rng().choice(self.possible_actions())
