import networkx as nx
import random
import numpy as np
import ../randomizer

def state(agent):
    pass

# actions are just possible nodes to visit
def possibleActions(agent, map):
    #l = map[agent.location]["location"]
    actions = [l for l in map.neighbors(agent.location)]
    actions.append(agent.location)
    # if agent can use fly, include flypoints
    return actions

def allPossibleActions(agent, map):
    pass
    # returns all possible actions assuming all rules and blocks are removed
    # not needed if rules, location, etc are included in state


class MCTS:

    def __init__(self, discount, rolloutPolicy=None):
        self._Q = dict()
        self._N = dict()
        self._U = dict()
        self._gamma = discount
        if rolloutPolicy:
            self.rolloutPolicy = rolloutPolicy
        else:
            self.rolloutPolicy = MCTS.randomStep



    def randomStep(agent, map):
        actions = possibleActions(agent, map)
        return random.choice(actions)

    def rollout(self, agent, map, d):
        ret = 0.0
        for t in range(d):
            a = self.rolloutPolicy(agent, map)
            # move agent to location specified by a
            # do whatever event at new location
            # receive reward r
            ret += self._gamma**t * r
        return ret


    def UCB1_bonus(Nsa, Ns):
        if Nsa == 0:
            return np.inf
        else:
            return sqrt(Ns/Nsa)

    def explore(agent, map):
        s = state(agent)
        actions = possibleActions(agent, map)
        c = 10
        Ns = sum([N[(s,a)] for a in actions])
        a_idx = np.argmax([Q[(s,a)+c*UCB1_bonus(N[(s,a), Ns]) for a in actions])
        return actions[a_idx]

    def simulate(self, agent, map, d = 5):

        s = state(agent)

        if d <= 0:
            if s not in self._U:
                self._U(s) = rollout(agent, map, 8)
            return self._U(s)


        actions = possibleActions(agent, map)

        # assume that the allowable actions for a certain state s don't
        # change with time. This requires that we include the access rules for
        # locations in the state somehow
        if (s,actions[0]) not in N:
            for a in actions:
                N[(s,a)] = 0
                Q[(s,a)] = 0.0

        a = explore(agent,map)
        # move agent to location specified by a
        # do whatever event at new location
        # receive reward r
        q = r + self._gamma*self.simulate(agent, map, d-1)
        N[(s,a)] += 1
        Q[(s,a)] += (q - Q[(s,a)])/N[(s,a)]
        return q
