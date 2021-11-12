import NetWorkX as nx
import random

def createMap(inputFile):

	with open(inputfile, 'r') as f:
		content = f.readlines()

	crystalMap = nx.DiGraph()

	for line in content:
		pass

		#figure out how to interpret config file
		#create nodes in networkx

	return crystalMap, startNode, goalNode




# Potential classes to use in nodes

class Location:

	def __init__(self, name, trainers = [], blockedNodes = [], \
				 checkCandidates = [], checkCondition = None):
		self.name = name
		self.trainers = trainers
		self.blockedNodes = blockedNodes
		self.checkCand = checkCandidates
		self.checkCond = checkCondition

	def hasCheck(self):
		return not bool(self.checkCand)

	def hasTrainer(self):
		return not bool(self.trainers)

	def getBlockedNeighbors(self):
		return self.blockedNodes

	def doEvent(self, agent):
		if self.hasTrainers():
			for trainer in self.trainers:
				if not trainer.isDefeated() and battle(agent, trainer):
					self.trainers.pop(0)
				else:
					break
			if not self.hasTrainers():
				self.blockedNodes = []
		if self.checkCond and self.checkCond(self):
			keyItem = random.choice(self.checkCand)
			self.checkCand = []
			return keyItem
		return

class TallGrassLocation:
	def __init__(self, name, lvlRange):
		self.name = name
		self.lvlRange = range(lvlRange[0], lvlRange[1]+1)

	def doEvent(self, agent):
		pokemonLvl = random.choice(self.lvlRange)
		wildPokemon = Opponent(pokemonLvl)
		battle(agent,wildPokemon)
		return

class Opponent:
	def __init__(self, lvl):
		self.lvl = lvl

	def getLevel(self):
		return self.lvl

class Trainer(Opponent):
	def __init__(self, lvl):
		Opponent.__init__(self, lvl)
		self.defeated = False

	def setDefeat(self, battleOutcome):
		self.defeated = battleOutcome

	def isDefeated(self):
		return self.defeated
