import networkx as nx
import random
import numpy as np
import randomizer
from randomizer import Item, Trash, Badge, Hm, Rule
import game as gm
import dm.rewards as rw
from copy import deepcopy

from dm.templates import DecisionMaker,ActionType

itemIdx = dict()
i = 1
for item in Item:
    itemIdx[item] = i
    i += 1

i = 1
for trash in Trash:
    itemIdx[trash] = i
    i += 1

i = 1
for badge in Badge:
    itemIdx[badge] = i
    i += 1

i = 1
for hm in Hm:
    itemIdx[hm] = i
    i += 1

i = 1
for rule in Rule:
    itemIdx[rule] = i
    i += 1


def state(game):
    state = game.player.level-1
    i = 0
    for l in game.locations:
        if l.name == game.player.location:
            break
        i += 1

    state += i * 100
    # need 17 bits to cover above number 2^17-1 = 131,071
    # up to 130 locations allowed

    # order: Item, Trash, Badge, Hm
    # could potentially save some space if we identify
    # certain items as items that don't change the state
    # i.e. do not contribute to any rules, don't change simulation mechanics
    item_s = 0

    l_item = len(Item) # 13
    l_trash = len(Trash) # 1
    l_badge = len(Badge) # 16
    l_hm = len(Hm) # 7
    l_rule = len(Rule) # 24

    # assume that elements range from 1:length(Enum)
    for item in game.player.key_items:
        if isinstance(item, Item) and not item_error_message(itemIdx[item], l_item):
            item_s += 2**(itemIdx[item] - 1)
        elif isinstance(item, Badge) and not item_error_message(itemIdx[item], l_badge):
            item_s += 2**(itemIdx[item] - 1 + l_item)
        elif isinstance(item, Hm) and not item_error_message(itemIdx[item], l_hm):
            item_s += 2**(itemIdx[item] - 1 + l_item + l_badge)
        elif isinstance(item, Rule) and not item_error_message(itemIdx[item], l_rule):
            item_s += 2**(itemIdx[item] - 1 + l_item + l_badge + l_hm)

    # item_s should be covered by 60 bits
    # TODO: consider returning a tuple instead of one large number of type int64
    return (state, item_s)

def decodeState(game, state):
    level = state[0] % 100 + 1
    loc_idx = (state[0] - level + 1)/100
    location = game.locations[loc_idx]
    item_s = state[1]
    items = []
    i = 0
    Item_list = list(Item)
    Badge_list = list(Badge)
    Hm_list = list(Hm)
    Rule_list = list(Rule)

    l_item = len(Item) # 13
    l_badge = len(Badge) # 16
    l_hm = len(Hm) # 7
    l_rule = len(Rule) # 24
    while item_s > 0:
        if i < len_item and item_s % 2 == 1:
            items.append(Item_list[i])
        elif i < len_item+len_badge and item_s % 2 == 1:
            items.append(Badge_list[i-l_item])
        elif i < len_item+len_badge+l_hm and item_s % 2 == 1:
            items.append(Hm_list[i-l_item-l_badge])
        elif i < len_item+len_badge+l_hm+l_rule and item_s % 2 == 1:
            items.append(Rule_list[i-l_item-l_badge-l_hm])

        i += 1
        item_s >>= 1
    return level, location, items

def item_error_message(elementEnum, lenEnum):

    if elementEnum > lenEnum or elementEnum < 1:
        print(f"Redefine enumeration for {elementEnum}")
        return True
    return False

'''
Monte Carlo Tree Search Class
'''
class MCTS(DecisionMaker):

    action_type = ActionType.ACC_CHECKS
    '''
    Constructor Method
        crystalGame: instance of Game class agent is playing on
        discount: discount factor for Bellman Equation
        rolloutPolicy: rollout policy for determining U(s).
                        Must have an input for a game instance and set of
                        possible actions.
                        Default is a random policy.
        numParticles: number of "particles", or different game states,
                        to simulate on
    '''
    def __init__(self, crystalGame, \
                    discount=1, \
                    rolloutPolicy=None, \
                    numParticles = 3, \
                    numSim = 5):
        DecisionMaker.__init__(self, crystalGame)
        self.gamma = discount
        if rolloutPolicy:
            self.rolloutPolicy = rolloutPolicy
        else:
            self.rolloutPolicy = MCTS.randomStep
        self._numParticles = numParticles
        self.m = numSim

        self._Q = dict()
        self._N = dict()
        self._U = dict()
        self._numObs = 0

        self.d_sim = 5
        self.d_rollout = 5

        self._particles = \
            gm.create_from_observations( \
                self.observations, \
                crystalGame.player, \
                count=numParticles)


    @property
    def numParticles(self):
        return self._numParticles

    @numParticles.setter
    def numParticles(self, n):
        if n > 0:
            self._numParticles = n
            self._particles = \
                gm.create_from_observations( \
                self.observations, \
                self.game.player, \
                count=self._numParticles)



    def setSimDepth(self, dd):
        d_sim, d_rollout = dd
        if d_sim > 0:
            self.d_sim = d_sim
        if d_rollout > 0:
            self.d_rollout = d_rollout

    '''
    Given a set of actions, Monte Carlo Tree Search will choose the best action
        actions: set of possible actions
        m: the number of simulations per particle
    '''
    def decide_action(self):
        if self._numObs < len(self.observations):
            self._numObs = len(self.observations)
            self.resampleParticles()
        s = state(self.game)
        actions = self.possible_actions()
        i = 0
        for p in self._particles:
            gm.copy_game_state(p, self.game)
            for k in range(self.m):
                virtualGame = deepcopy(p)
                self.simulate(virtualGame, i, actions, self.d_sim)
            i += 1

        return actions[np.argmax([self._Q[(s,a)] for a in actions])]


    '''
    Adds an observation to the class instance for generating new particles
        o: tuple of (action, result)
        numParticles: number of "particles", or different game states,
                        to generate from the updated generative model
    '''
    def resampleParticles(self):
        self._particles = \
            gm.copy_with_observations( \
                self.game, self.observations, count=self._numParticles)


    @staticmethod
    def randomStep(vgame, actions):
        return random.choice(actions)

    '''
    Rollout for simulation on virtual game
    '''
    def rollout(self, vgame, actions, d):
        ret = 0.0
        for t in range(d):
            a = self.rolloutPolicy(vgame, actions)

            results,cost = vgame.attempt_action(a)
            r = -1*cost
            if isinstance(results, list) and gm.is_item(results[0]):
                for item in results:
                    r += rw.chkToReward[item]

            ret += self.gamma**t * r
        return ret


    def UCB1_bonus(self, Nsa, Ns, c=1):
        if Nsa == 0:
            return np.inf
        else:
            return c*np.sqrt(Ns/Nsa)

    '''
    Method for choosing the next action in MCTS. Employs UCB1 heuristic
    '''
    def explore(self, s, actions):
        Ns = 0
        for a in actions:
            try:
                Ns += self._N[(s,a)]
            except KeyError:
                print(f"Key Error during explore for {(s,a)}")
                self._N[(s,a)] = 0
                self._Q[(s,a)] = 0.0
        a_idx = np.argmax([self._Q[(s,a)] + self.UCB1_bonus(self._N[(s,a)], Ns, c=400) for a in actions])
        return actions[a_idx]

    '''
    Simulation function for MCTS
    '''
    def simulate(self, vgame, pNum, actions, d):

        s = state(vgame)
        if d <= 0:
            if s not in self._U:
                self._U[s] = [self.rollout(vgame, actions, self.d_rollout), {pNum}]
            elif pNum not in self._U[s][1]:
                self._U[s][1].add(pNum)
                U = self.rollout(vgame, actions,  self.d_rollout)
                self._U[s][0] += 1/len(self._U[s][1]) * (U - self._U[s][0])
            return self._U[s][0]


        if (s,actions[0]) not in self._N:
            for a in actions:
                self._N[(s,a)] = 0
                self._Q[(s,a)] = 0.0
                #print(f'Adding {(s,a)}')
            self._U[s] = [self.rollout(vgame, actions, self.d_rollout), {pNum}]
            return self._U[s][0]

        a = self.explore(s, actions)

        results,cost = vgame.attempt_accessible_check(a)

        r = -1*cost
        if isinstance(results, list) and gm.is_item(results[0]):
            for item in results:
                r += rw.chkToReward[item]

        actions = self.possible_actions()

        q = r + self.gamma*self.simulate(vgame, pNum, actions, d-1)
        self._N[(s,a)] += 1
        self._Q[(s,a)] += (q - self._Q[(s,a)])/self._N[(s,a)]
        return q
