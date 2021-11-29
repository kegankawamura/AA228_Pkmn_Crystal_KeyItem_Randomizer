# merging of lookahead+rollouts and sparse_sampling
import numpy
import game
import randomizer
from randomizer import Item,Badge,Hm,Rule,ImpTown
from .rewards import chkToReward
import copy
# were gonna try something
from multiprocessing import Pool

from dm.templates import DecisionMaker,ActionType
import numpy
from numpy.random import default_rng

class BeliefSampling(DecisionMaker):
    num_particles = 100
    depth = 2
    num_samples = 30
    action_type = ActionType.ACC_CHECKS

    def decide_action(self):
        # create a belief from the current game
        belief = game.create_from_observations(self.observations,self.game.player,count=self.num_particles)
        # use a dict to maintain an estimate of the rewards 
        U = dict()
        M = dict()
        # attempt to use pool
        pool = Pool(8)
        particles = numpy.random.default_rng().choice(belief,self.num_samples)
        smapiter = zip(particles,[self.depth]*self.num_particles)
        ret_pool = pool.starmap(get_best_action,smapiter)
        actions = list(zip(*ret_pool))[0]
        rewards = list(zip(*ret_pool))[1]

        for n in range(self.num_samples):
            if actions[n]==None:
                import pdb; pdb.set_trace()
            action = actions[n][0]
            reward = rewards[n]
            if action not in U.keys():
                U[action] = reward;
                M[action] = 1;
            else:
                alpha = 1/M[action]**1.25
                U[action] += alpha*(reward-U[action])
                M[action] += 1
        for action,reward in U.items():
            print(f'Expected utility of action {action}: {reward:.2f}')

        # take greedy action
        return max(U,key=U.get)

# given a game, finds the optimal series of actions up to depth
# returns:
#   series of actions 
#   resulting reward value
#   future game state after optimal actions
def get_best_action(game,depth):
    #print('  ',end='')
    if depth == 0 or game.is_finished():
        #print('end')
        return (None,0,game)
    best = (None,-numpy.inf,None)
    for action in game.get_accessible_checks():
        g = copy.deepcopy(game);
        (results,cost) = g.attempt_accessible_check(action)
        cost /= game.prob_success(action)
        reward = get_reward(results,action,game,g) - cost
        future_action,future_reward,future_game = get_best_action(g,depth-1)
        reward += future_reward
        if reward > best[1]:
            if future_action != None:
                best = ([action]+[*future_action],reward,future_game)
            else:
                best = ([action],reward,future_game)
    #import pdb; pdb.set_trace()
    if best[1]==numpy.inf:
        return get_best_action(game,depth)
    return best

# defines a reward based on a state transition 
# also lets rewards be dependent on the game state
def get_reward(results,action,game_prev,game_next):
    reward = 0;
    prob_success = game_prev.prob_success(action)
    # reward gaining levels
    reward += ( 15*(game_next.player.level-game_prev.player.level) )*prob_success
    # reward unlocking more checks
    #reward += 30*(len(game_next.get_accessible_checks())-\
    #           len(game_prev.get_accessible_checks()));
    # reward can be based on game logic 
    logic_prev = randomizer.in_logic(game_prev.player.key_items,is_player=True)
    logic_next = randomizer.in_logic(game_next.player.key_items,is_player=True)
    reward += 15*(len(logic_next)-len(logic_prev))
    
    # reward based on actual item
    if results==None:
        return reward
    elif  game.is_location(results):
        return reward
    for result in results:
        if result in chkToReward.keys():
            reward+= chkToReward[result]*prob_success
            if result==game.randomizer.Trash.TRASH:
                reward += -500
    return reward
