# implementation of lookahead with rollouts
import numpy
import game
from .rewards import chkToReward
import copy

class RolloutPolicy:
    def __init__(self):
        return
    # selects a random action
    def action(self,virt_game):
        #actions = virt_game.get_checks_here() + virt_game.get_neighboring_locations()
        actions = virt_game.get_accessible_checks()
        return numpy.random.choice(actions)

def is_consistent(game,observations):
    for o in observations:
        for loc in game.locations:
            for chk in loc.checks:
                if chk==o[0]:
                    if o[1] not in chk.item:
                        return False
    return True;

def rollout(policy,belief,observations,actions,depth):
    if depth==0: return 0
    rand_state = numpy.random.choice(belief)
    action = policy.action(rand_state)
    actions.append(action)
    reward = 0
    #results,cost = rand_state.attempt_action(action)
    results,cost = rand_state.attempt_accessible_check(action)
    reward += -cost
    #print(f'taking action {action}')
    #print(f'gave result {results}')
    if results == None:
        return rollout(policy,belief,observations,actions,depth-1) +reward
    if game.is_location(results):
        [g.attempt_accessible_check(action) for g in belief if g != rand_state]
        return rollout(policy,belief,observations,actions,depth-1) +reward
    else:
        for result in results:
            observations.append((action,result))
            posterior = [particle for particle in belief if is_consistent(particle,observations)]
            if len(posterior)!=len(belief):
                posterior += game.create_from_observations(observations,rand_state.player,
                            count=len(belief)-len(posterior))
            if result in chkToReward.keys():
                reward+=chkToReward[result]
        return rollout(policy,posterior,observations,actions,depth-1) \
                +reward

def policy(belief_orig,observations,num_rollouts=100):
    depth = 2
    # incremental mean estimation?
    U = dict();
    M = dict();
    for n in range(num_rollouts):
        belief = copy.deepcopy(belief_orig)
        actions = []
        rollout_policy = RolloutPolicy()
        reward = rollout(rollout_policy, belief, list(observations), actions,depth)
        action = actions[0]
        if action not in U.keys():
            U[action] = reward;
            M[action] = 1;
        else:
            alpha = 1/M[action]**1.5
            U[action] += alpha*(reward-U[action])
            M[action] += 1
            print(f'Updated utility of action {action}: {U[action]:.2f}')
    for a,u in U.items():
        print(f'U[{a}] = {u:.2f}')
    # take greedy action

    return max(U,key=U.get)
