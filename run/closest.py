import game
from dm.dm_closest import Closest
from dm.simulator import Simulator


rando = game.create()

sim = Simulator(rando,Closest)
sim.simulate()
