import constants
import createMap
import agent
import random

'''
Simulation of pokemon crystal.
'''
def run(mapConfigFile):
	crystalMap, startNode, goalNode = createMap.createMap(mapConfigFile)
	crystal = agent.Agent(startNode)
	turns = 0 # counts the number of turns it takes to get to goal. We want to minimize this
	history = [startNode] # state action pairs?
	while crystal.getCurrNode() != goalNode:
		# simulate game
		currNode = crystal.getCurrNode()
		nextNode = crystal.chooseAction(crystalMap)
		turn = transitionCost(currNode, nextNode, crystalMap)
		reward = -turn
		turns += turn
		crystal.setCurrNode(nextNode)
		history.push(nextNode)
		check = nextNode.doEvent(crystal)
		if check:
			crystal.addKeyItem(check.name)
			reward += check.reward
		crystal.update(nextNode, currNode, reward)
		# state is updated
	return turns, history


'''
Given current node and next node, compute the cost to transition
'''
def transitionCost(currNode, nextNode, crystalMap):
	if currNode == nextNode:
		return nextNode.revisitCost
	else:
		return crystalMap[currNode][nextNode]["weight"]


'''
Main
'''
if __name__ == '__main__':
	if len(sys.argv) != 2:
        raise Exception("usage: python simulate.py <infile>.txt")

    inputfilename = sys.argv[1]
	numTurns, history = run(inputfilename)
	with open('pkmnHistoryData.txt') as f:
		f.write(f"{numTurns}\n")
		for state_action in history:
			f.write(f"{state_action}\n")
