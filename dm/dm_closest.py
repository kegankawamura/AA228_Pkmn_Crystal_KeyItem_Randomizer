from dm.templates import DecisionMaker,ActionType

class Closest(DecisionMaker):
    action_type = ActionType.ACC_CHECKS

    def decide_action(self):
        actions = self.possible_actions()
        costs = [self.game.get_cost_action(a) for a in actions]
        sorted_actions = [x for _,x in sorted(zip(costs,actions),key=lambda pair: pair[0])]
        return sorted_actions[0]
