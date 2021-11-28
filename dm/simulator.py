from dm.templates import Agent, DecisionMaker, ActionType
import game

class Simulator:
    def __init__(self,rando,alg):
        self.game = rando
        self.agent = Agent(rando,alg)

    def simulate_step(self):
        action = self.agent.policy()

        print(f'attempting to do {action}!')

        action_type = self.agent.decisionmaker.action_type;
        if action_type==ActionType.ACC_CHECKS:
            results,cost = self.game.attempt_accessible_check(action)
            if game.is_location(results):
                print(f'!stopped at {results}!')
            elif results != None:
                for result in results:
                    print(f'obtained {result}')
            else: 
                print('!!failed to get check!!')
        elif action_type==ActionType.CHECKS_LOCS:
            results,cost = self.game.attempt_action(action)
            if game.is_location(results):
                print(f'moved to {results}!')
            elif results != None:
                for result in results:
                    print(f'obtained {result}')
            else: 
                print('!!failed to get check!!')
    
    def simulate(self):
        while not self.game.is_finished():
            self.simulate_step()
            print(f'game time: {self.game.time:.1f}')
        print(f' completed game in {self.game.time:.2f}')

    def simulate_plot(self):
        while not self.game.is_finished():
            self.simulate_step()
            self.game.plot()
            print(f'game time: {self.game.time:.1f}')
        print(f' completed game in {self.game.time:.2f}')
