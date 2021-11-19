# Implement agent's decision making process/model here
# Might want to separate this into rollout, MCTS, etc files
import constants
import agent


def currentState(_agent):
	level = _agent.level
	currNode = _agent.getCurrNode()
	keyItems = _agent.getKeyItems()

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

	keyItems = [0]*constants.NUMKEYS
	mask = 1
	for i in range(constants.NUMKEYS):
		keyItems[i] = keyState & mask
		mask *= 2

	return level, currNode, keyItems
