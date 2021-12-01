import networkx as nx
import random
import numpy as np
import randomizer
from randomizer import Item, Trash, Badge, Hm, Rule
import game as gm
import dm.rewards as rw
from copy import deepcopy

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


def item_error_message(elementEnum, lenEnum):

    if elementEnum > lenEnum or elementEnum < 1:
        print(f"Redefine enumeration for {elementEnum}")
        return True
    return False

'''
Monte Carlo Tree Search Class
'''
class MCTS:

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
    def __init__(self, crystalGame, discount, rolloutPolicy=None,numParticles = 3):
        self._game = crystalGame
        self._Q = dict()
        self._N = dict()
        self._U = dict()
        self._gamma = discount
        self._observations = []
        if rolloutPolicy:
            self.rolloutPolicy = rolloutPolicy
        else:
            self.rolloutPolicy = MCTS.randomStep

        self._particles = \
            gm.create_from_observations( \
                self._observations, \
                crystalGame.player, \
                count=numParticles)


    '''
    Given a set of actions, Monte Carlo Tree Search will choose the best action
        actions: set of possible actions
        m: the number of simulations per particle
    '''
    def chooseAction(self, actions, m = 5):

        s = state(self._game)
        for p in self._particles:
            gm.copy_game_state(p, self._game)
            for k in range(m):
                virtualGame = deepcopy(self._game)
                self.simulate(virtualGame, actions, d = 10)

        return np.argmax([self._Q[(s,a)] for a in actions])


    '''
    Adds an observation to the class instance for generating new particles
        o: tuple of (action, result)
        numParticles: number of "particles", or different game states,
                        to generate from the updated generative model
    '''
    def addObservation(self, o, numParticles=0):
        if numParticles == 0:
            numParticles = len(self._particles)
        self._observations.append(o)
        self._particles = \
            gm.copy_with_observations( \
                self._game, self._observations, count=numParticles)


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

            ret += self._gamma**t * r
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
                self._N[(s,a)] = 0
                self._Q[(s,a)] = 0.0
        a_idx = np.argmax([self._Q[(s,a)] + self.UCB1_bonus(self._N[(s,a)], Ns, c=3000) for a in actions])
        return actions[a_idx]

    '''
    Simulation function for MCTS
    '''
    def simulate(self, vgame, actions, d = 5):

        s = state(vgame)
        if d <= 0:
            if s not in self._U:
                self._U[s] = self.rollout(vgame, actions,  8)
            return self._U[s]


        if (s,actions[0]) not in self._N:
            for a in actions:
                self._N[(s,a)] = 0
                self._Q[(s,a)] = 0.0
                print(f'Adding {(s,a)}')
            self._U[s] = self.rollout(vgame, actions,  8)
            return self._U[s]

        a = self.explore(s, actions)

        results,cost = vgame.attempt_action(a)

        r = -1*cost
        if isinstance(results, list) and gm.is_item(results[0]):
            for item in results:
                r += rw.chkToReward[item]

        actions = []
        actions += vgame.get_checks_here()
        actions += vgame.get_neighboring_locations()

        q = r + self._gamma*self.simulate(vgame, actions, d-1)
        self._N[(s,a)] += 1
        self._Q[(s,a)] += (q - self._Q[(s,a)])/self._N[(s,a)]
        return q
