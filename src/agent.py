import numpy as np


NumKeys = 32 # make this a static global variable

Class agent():

	def __init__(self, _start_node):
		self.curr_node = _start_node
		self.lvl = 5
		self.exp = 0
		self.keyItems = [0]*NumKeys #number of key items
		# include policy as input if we use offline planning?

	def getLevel(self):
		return self.lvl

	def getCurrNode(self):
		return self.curr_node

	def setCurrNode(self, node, crystalMap):
		if crystalMap.has_node(node):
			self.curr_node = node

	def getKeyItems(self):
		return self.getKeyItems

	def addKeyItem(self, keyItemIdx):
		if keyItemIdx < 0 or keyItemIdx >=	NumKeys

	def chooseAction(self, crystalMap):
		pass
		#nextNodes = crystalMap.neighbors(crystal.getCurrNode())
		# use current state and networkx graph to decide on next action

	# exp to level function
	def totalExp(level):
		return level**3

	def addExp(self, new_exp):
		if lvl >= 100:
			return
		self.exp += new_exp
		lvlUp_exp = self.totalExp(lvl+1) - self.totalExp(lvl)
		if self.exp >= lvlUp_exp:
			self.lvl += 1
			self.exp %= lvlUp_exp
