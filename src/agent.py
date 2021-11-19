import numpy as np
import constants
import decision_making as dm

'''
Class that represents our agent (Crystal) exploring the pokemon crystal map.
'''
Class Agent:

	def __init__(self, start_node):
		self._curr_node = start_node
		self._lvl = 5
		self._exp = 0
		self._keyItems = {} #number of key items
		for check in constants.keyItems:
			self._keyItems[check] = 0
		# include policy as input if we use offline planning?

	@property
	def level(self):
		return self._lvl

	def getCurrNode(self):
		return self._curr_node

	def setCurrNode(self, node, crystalMap):
		if crystalMap.has_node(node):
			self._curr_node = node

	def getKeyItems(self):
		return self._keyItems.copy()

	def addKeyItem(self, keyItemEnum):
		if self._keyItems.has_key(keyItemEnum):
			self._keyItems[keyItemEnum] = 1
		else:
			println("Key Item not found")

	def chooseAction(self, crystalMap):
		pass
		#nextNodes = crystalMap.neighbors(crystal.getCurrNode())
		# use current state and networkx graph to decide on next action


	def update(self, nextNode, currNode, r):
		pass

	def addExp(self, new_exp):
		if lvl >= 100:
			return
		self._exp += new_exp
		lvlUp_exp = self.totalExp(lvl+1) - self.totalExp(lvl)
		if self._exp >= lvlUp_exp:
			self._lvl += 1
			self._exp %= lvlUp_exp

	# exp to level function
	def totalExp(level):
		return level**3
