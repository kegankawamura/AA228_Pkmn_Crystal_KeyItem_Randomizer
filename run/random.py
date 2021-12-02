import game
from dm.dm_random import Random
from dm.simulator import Simulator

if __name__=='__main__':
    rando = game.create()
    sim = Simulator(rando,Random)
    sim.simulate()
