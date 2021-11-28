import networkx as nx
import random
import numpy as np
import randomizer
from ../randomizer import Item, Trash, Badge, Hm
import ../game as gm
import rewards as rw
from copy import deepcopy

def state(game):
    state = game.player.level
    state += len(game.locations) * 100
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

    # assume that elements range from 1:length(Enum)
    for item in game.player.key_items:
        if isinstance(item, Item) and not item_error_message(item, l_item):
            item_s += 2**(item.value-1)
        elif isinstance(item, Trash) and not item_error_message(item, l_trash):
            item_s += 2**(item.value - 1 + l_item)
        elif isinstance(item, Badge) and not item_error_message(item, l_badge):
            item_s += 2**(item.value - 1 + l_item + l_trash)
        elif isinstance(item, Hm) and not item_error_message(item, l_hm):
            item_s += 2**(item.value - 1 + l_item + l_trash + l_badge)

    item_s *= 2**17

    # total should be covered by 54 bits
    # TODO: consider returning a tuple instead of one large number of type int64
    return state + item_s


def item_error_message(elementEnum, lenEnum):
    if elementEnum.value > lenEnum or item.value < 1:
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

        self._particles = game.create_from_observations(self._observations,count=numParticles)


    '''
    Given a set of actions, Monte Carlo Tree Search will choose the best action
        actions: set of possible actions
        m: the number of simulations per particle
    '''
    def chooseAction(self, actions, m = 5):

        for p in self._particles:
            copy_game_state(p, self._game)
            for k in range(m):
                virtualGame = copy.deepcopy(self._game)
                self.simulate(virtualGame, actions)

        return np.argmax([Q[(s,a)] for a in actions])


    '''
    Adds an observation to the class instance for generating new particles
        o: tuple of (action, result)
        numParticles: number of "particles", or different game states,
                        to generate from the updated generative model
    '''
    def addObservation(self, o, numParticles=len(self._particles)):
        self._observations.append(o)
        self._particles = game.create_from_observations(self._observations,count=numParticles)
        for p in self._particles:
            game.copy_game_state(p, self._game)

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


    def UCB1_bonus(Nsa, Ns, c=1):
        if Nsa == 0:
            return np.inf
        else:
            return c*sqrt(Ns/Nsa)

    '''
    Method for choosing the next action in MCTS. Employs UCB1 heuristic
    '''
    def explore(self, s, actions):
        Ns = sum([N[(s,a)] for a in actions])
        a_idx = np.argmax([Q[(s,a)+UCB1_bonus(N[(s,a)], Ns, c=10) for a in actions])
        return actions[a_idx]

    '''
    Simulation function for MCTS
    '''
    def simulate(self, vgame, actions, d = 5):

        s = state(vgame)

        if d <= 0:
            if s not in self._U:
                self._U(s) = rollout(vgame, actions,  8)
            return self._U(s)


        if (s,actions[0]) not in N:
            for a in actions:
                N[(s,a)] = 0
                Q[(s,a)] = 0.0

        a = explore(s, actions)

        results,cost = vgame.attempt_action(a)

        r = -1*cost
        if isinstance(results, list) and gm.is_item(results[0]):
            for item in results:
                r += rw.chkToReward[item]

        actions = []
        actions += vgame.get_checks_here()
        actions += vgame.get_neighboring_locations()

        q = r + self._gamma*self.simulate(vgame, actions, d-1)
        N[(s,a)] += 1
        Q[(s,a)] += (q - Q[(s,a)])/N[(s,a)]
        return q