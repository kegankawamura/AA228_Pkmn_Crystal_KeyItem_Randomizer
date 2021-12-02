from dm.templates import Agent, DecisionMaker, ActionType
import game
from randomizer import Rule,Badge, Trash, Item, logical_rules
import numpy
import matplotlib
import matplotlib.pyplot as plt

class Simulator:
    def __init__(self,rando,alg):
        self.game = rando
        self.agent = Agent(rando,alg)
        self.recorder = Metrics()

    def simulate_step(self):
        action = self.agent.policy()

        print(f'attempting to do {action}!')

        action_type = self.agent.decisionmaker.action_type;
        if action_type==ActionType.ACC_CHECKS:
            results,cost = self.game.attempt_accessible_check(action)
            if game.is_location(results):
                print(f'!stopped at {results} at level {self.game.player.level}!')
            elif results != None:
                for result in results:
                    print(f'obtained {result}')
                    self.agent.observe(action,result)
            else: 
                print(f'!!failed to get check at level {self.game.player.level}!!')
        elif action_type==ActionType.CHECKS_LOCS:
            results,cost = self.game.attempt_action(action)
            if game.is_location(results):
                print(f'moved to {results}!')
            elif results != None:
                for result in results:
                    print(f'obtained {result}')
                    self.agent.observe(action,result)
            else: 
                print(f'!!failed to get check at level {self.game.player.level}!!')
        self.recorder.record_metrics(self.game)
    
    def simulate(self):
        while not self.game.is_finished():
            self.simulate_step()
            print(f'game time: {self.game.time/60:.2f} min')
        print(' completed game in '+convert_sec_to_str(self.game.time))

    def simulate_plot(self):
        while not self.game.is_finished():
            self.simulate_step()
            self.game.plot()
            print(f'game time: {self.game.time:.1f}')
        print(f' completed game in {self.game.time:.2f}')

# records time-series performance metrics of a game in metrics member
#   times: timestamp of each
#   available_checks: number of checks the agent can choose from
#   completed_checks: number of checks the agent has completed
#   level: player level
#   items: number of items
#   badges: number of badges the player has
#   trash: number of trash checks revealed

class Metrics:
    def __init__(self):
        self.metrics = dict( (
                ('times'            ,[]),
                ('available_checks' ,[]),
                ('completed_checks' ,[]),
                ('level'            ,[]),
                ('items'            ,[]),
                ('badges'           ,[]),
                ('trash'            ,[]),
                ));

        self.completion_time = -1;
        self.time_to_bike = -1;
        self.time_to_fly = -1;

    def record_metrics(self,game):
        metrics = self.metrics; 
        time = game.time
        items = game.player.key_items
        metrics['times'].append(time)
        metrics['available_checks'].append( len(game.get_accessible_checks() ))
        metrics['completed_checks'].append(len(game.player.completed_checks))
        metrics['level'].append(game.player.level)
        metrics['items'].append(len(items))
        metrics['badges'].append( sum(1 for i in items if isinstance(i,Badge)) )
        metrics['trash'].append( sum(1 for i in items if isinstance(i,Trash)) )
        if game.is_finished(): self.completion_time = time
        if self.time_to_bike<0:
            if Item.BICYCLE in items: self.time_to_bike = time
        if self.time_to_fly<0:
            logic_rules = logical_rules(items)
            if Rule.CANUSEFLY in logic_rules: self.time_to_fly = time

    def plot(self,metric,figure = None,prefix=''):
        if metric not in self.metrics.keys():
            return -1
        plt.plot(numpy.array(self.metrics['times'])/60,self.metrics[metric],label=prefix+metric,figure=figure)
        plt.xlabel('time (min)')
        #plt.xlim(0,self.metrics['times'][-1]/60)
        plt.gca().yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        plt.legend()



def convert_sec_to_str(sec):
    mins = sec//60
    hrs = int(mins//60)
    mins = int(mins%60)
    secs = sec-hrs*3600-mins*60
    return f'{hrs} h {mins} m {secs} s'

