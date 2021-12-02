import game
from dm.dm_mcts import MCTS
from dm.simulator import Simulator

if __name__=="__main__":

    rando = game.create()

    sim = Simulator(rando,MCTS)

    sim.agent.decisionmaker.numParticles = 50
    sim.agent.decisionmaker.setSimDepth = (5, 3)
    sim.agent.decisionmaker.m = 5

    sim.simulate(outputFile='data_mcts_p50_d5_3_m5.txt')
