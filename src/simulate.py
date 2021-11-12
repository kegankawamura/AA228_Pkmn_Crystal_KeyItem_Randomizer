import constants
import createMap
import agent
import random


def run(mapConfigFile):
	crystalMap, startNode, goalNode = createMap.createMap(mapConfigFile)
	crystal = agent.Agent(startNode)
	turns = 0 # counts the number of turns it takes to get to goal. We want to minimize this
	history = [startNode] # state action pairs?
	while crystal.getCurrNode() != goalNode:
		# simulate game
		nextNode = crystal.chooseAction(crystalMap)
		turn = crystalMap[crystal.getCurrNode()][nextNode]["weight"]
		turns += turn
		crystal.setCurrNode(nextNode)
		history.push(nextNode)
		nextNode.doEvent(crystal)
		# state is updated
	return turns, history

def calculateExp(opponent):
	a = 1
	L = opponent.getLevel()
	b = 3
	C = 2	# artificial scale factor
	if isinstance(opponent, Trainer):
		a = 1.5
		C = 6

	return round(C*a*b*L/7)

def battle(trainer, bot):
	agentLvl = trainer.getLevel()
	botLvl = bot.getLevel()

	agentExp = Agent.totalExp(agentLvl)
	botExp = Agent.totalExp(botLvl)

	agentAdvantage = agentExp/(agentExp + botExp)

	if random.random() < agentAdvantage:
		bot.setDefeat(True)
		trainer.addExp(calculateExp(bot))
		return True
	else:
		return False


if __name__ == '__main__':
	if len(sys.argv) != 2:
        raise Exception("usage: python simulate.py <infile>.txt")

    inputfilename = sys.argv[1]
	numTurns, history = run(inputfilename)
