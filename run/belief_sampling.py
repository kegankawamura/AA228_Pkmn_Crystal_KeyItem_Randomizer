import game
from dm.dm_belief_sampling import BeliefSampling
from dm.simulator import Simulator

if __name__=="__main__":

    rando = game.create()

    sim = Simulator(rando,BeliefSampling)
    sim.simulate()
