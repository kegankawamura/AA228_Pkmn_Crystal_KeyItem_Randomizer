import NetWorkX as nx
import random
import constants

'''
Create the crystal map through a networkx, undirected graph, defined
by the input configuration file.
'''
def createMap(inputFile):

	with open(inputfile, 'r') as f:
		content = f.readlines()

	crystalMap = nx.Graph()

	for line in content:
		pass

		#figure out how to interpret config file
		#create nodes in networkx

	return crystalMap, startNode, goalNode


'''
A function to calculate experience points earned based on the
opponent defeated.
'''
def calculateExp(opponent):
	a = 1
	L = opponent.level
	b = 3
	C = 2	# artificial scale factor
	if isinstance(opponent, Trainer):
		a = 1.5
		C = 6
	return round(C*a*b*L/7)


'''
A function that simulates a pokemon battle between two agents.
The probability of winning is based on the level.
'''
def battle(trainer, bot):

	agentExp = Agent.totalExp(trainer.level)
	botExp = Agent.totalExp(bot.level)

	agentAdvantage = agentExp/(agentExp + botExp)

	if random.random() < agentAdvantage:
		if isinstance(opponent, Trainer):
			bot.setDefeat(True)
		trainer.addExp(calculateExp(bot))
		return True
	else:
		return False


'''
Parent class for all node classes contained within the crystal map
'''
class DefaultNode:
	def __init__(self,name,selfEdge):
		self._name = name
		self._selfEdge = selfEdge

	@property
	def name(self):
		return self._name

	@property
	def revisitCost(self):
		return self._selfEdge


'''
Default class used for nodes in graph.
May specify a list of Trainer objects, neighboring nodes that are blocked,
a list of candidate checks, and a function that specifies the condition for
the check to be collected.
'''
class Location(DefaultNode):

	def __init__(self, name, selfEdge, trainers = [], blockedNodes = [], \
				 checkCandidates = [], checkCondition = None):
		DefaultNode.__init__(self,name,selfEdge)
		self._trainers = trainers
		self._blockedNodes = blockedNodes
		self._checkCand = checkCandidates
		self._checkCond = checkCondition

	def hasCheck(self):
		return not bool(self._checkCand)

	def hasTrainer(self):
		return not bool(self._trainers)

	def getTrainers(self):
		return self._trainers.copy()

	def getBlockedNeighbors(self):
		return self._blockedNodes.copy()

	def doEvent(self, agent):
		if self.hasTrainers():
			for trainer in self._trainers:
				if not trainer.isDefeated() and battle(agent, trainer):
					self._trainers.pop(0)
				else:
					break
			if not self.hasTrainers():
				self._blockedNodes = []
		if self._checkCond and self.checkCond(self):
			keyItem = random.choice(self._checkCand)
			self._checkCand = []
			return keyItem
		return


'''
Specialized class used for nodes in graph.
Each visit allows an encounter with a generic Opponent instance that
represents a wild pokemon. The range of levels is specified in construction.
'''
class TallGrassLocation(DefaultNode):
	def __init__(self, name, selfEdge, lvlRange):
		DefaultNode.__init__(self,name,selfEdge)
		self._lvlRange = range(lvlRange[0], lvlRange[1]+1)

	def doEvent(self, agent):
		pokemonLvl = random.choice(self.lvlRange)
		wildPokemon = Opponent(pokemonLvl)
		battle(agent,wildPokemon)
		return


'''
Represents an opponent that our agent can battle to level up.
Generally used to represent wild pokemon.
'''
class Opponent:
	def __init__(self, lvl):
		self._lvl = lvl

	@property
	def level(self):
		return self._lvl


'''
A specialized opponent that can be fought by our agent only once.
Generally used to represent pokemon trainers.
'''
class Trainer(Opponent):
	def __init__(self, lvl):
		Opponent.__init__(self, lvl)
		self._defeated = False

	def setDefeat(self, battleOutcome):
		self._defeated = battleOutcome

	def isDefeated(self):
		return self._defeated
