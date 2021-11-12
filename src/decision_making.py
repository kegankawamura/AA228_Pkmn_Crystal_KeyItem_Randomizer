# Implement agent's decision making process/model here
# Might want to separate this into rollout, MCTS, etc files
import constants
import agent


def currentState(agent):
	level = agent.getLevel()
	currNode = agent.getCurrNode()
	keyItems = agent.getKeyItems()

	state = level
	state += 100*currNode
	keyState = 0
	for item in keyitems:
		keyState = keyState << 1
		keyState += item
	state += keyState*4096
	return state

def decodeState(state):
	keyState = state >> 12
	state -= keyState *4096
	level = ((state - 1) % 100) + 1
	currNode = (state - level)/100

	keyItems = [0]*NumKeys
	mask = 1
	for i in range(NumKeys):
		keyItems[i] = keyState & mask
		mask *= 2

	return level, currNode, keyItems
