from dm.templates import Agent, DecisionMaker, ActionType
from copy import deepcopy
import game
from randomizer import Rule,Badge, Trash, Item, logical_rules
import numpy
import matplotlib
import matplotlib.pyplot as plt
import time

class Simulator:
    def __init__(self,rando,alg):
        self.game = rando
        self.agent = Agent(rando,alg)
        self.recorder = Metrics()
        self.history_action = []
        self.history_level = []
        self.history_turns = []
        self.history_items = []

    def simulate_step(self):
        action = self.agent.policy()

        self.history_action.append((self.game.player.location, action))
        self.history_level.append(self.game.player.level)
        self.history_turns.append(self.game.time)
        self.history_items.append([item.name for item in self.game.player.key_items])

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
    
    def simulate(self, outputFile=None,plot=False):
        self.history_action = []
        self.history_level = []
        self.history_items = []
        self.history_turns = []

        while not self.game.is_finished():
            try:
                self.simulate_step()
                print(f'game time: {self.game.time/60:.2f} min')
            except KeyboardInterrupt:
                print('ending game early...')
                break

        print(' completed game in '+convert_sec_to_str(self.game.time))
        if outputFile:
            with open(outputFile, 'w') as f:
                print("writing to data file")
                f.write(f'Total time: {self.game.time}\n')
                f.write('Loc/Action, Level, Time, Items\n')
                for i in range(len(self.history_turns)):
                    f.write(f"{self.history_action[i]}, ")
                    f.write(f"{self.history_level[i]}, ")
                    f.write(f"{self.history_turns[i]}, ")
                    f.write(f"{self.history_items[i]}\n")
        if plot:
            self.game.plot()



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
                ('comp_time'        ,[]),
                ));
        self.comp_time_start = time.time()
        self.completion_time = -1;
        self.time_to_bike = -1;
        self.time_to_fly = -1;

    def record_metrics(self,game):
        metrics = self.metrics; 
        metrics['comp_time'].append(time.time()-self.comp_time_start)
        self.comp_time_start = time.time()


        game_time = game.time
        items = game.player.key_items
        metrics['times'].append(game_time)
        metrics['available_checks'].append( len(game.get_accessible_checks() ))
        metrics['completed_checks'].append(len(game.player.completed_checks))
        metrics['level'].append(game.player.level)
        metrics['items'].append(len(items))
        metrics['badges'].append( sum(1 for i in items if isinstance(i,Badge)) )
        metrics['trash'].append( sum(1 for i in items if isinstance(i,Trash)) )
        if game.is_finished(): self.completion_time = game_time
        if self.time_to_bike<0:
            if Item.BICYCLE in items: self.time_to_bike = game_time
        if self.time_to_fly<0:
            logic_rules = logical_rules(items)
            if Rule.CANUSEFLY in logic_rules: self.time_to_fly = game_time

    def plot(self,metric,figure = None,label=''):
        if metric not in self.metrics.keys():
            return -1
        plt.plot(numpy.array(self.metrics['times'])/60,self.metrics[metric],label=label,figure=figure)
        plt.title(metric)
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
