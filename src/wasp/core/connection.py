"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.4.001

Connection classes
"""

from Rhino.Geometry import Plane
from Rhino.Geometry import Vector3d

#################################################################### Connection ####################################################################
class Connection(object):
	
	## constructor
	def __init__(self, _plane, _type, _part, _id):
		
		self.pln = _plane
		
		flip_pln_Y = Vector3d(self.pln.YAxis)
		flip_pln_Y.Reverse()
		self.flip_pln = Plane(self.pln.Origin, self.pln.XAxis, flip_pln_Y)
		
		self.type = _type
		self.part = _part
		self.id = _id
		
		self.rules_table = []
		self.active_rules = []
	
	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspConnection [id: %s, type: %s]" % (self.id, self.type)
	
	
	## return a transformed copy of the connection
	def transform(self, trans):
		pln_trans = Plane(self.pln.Origin, self.pln.XAxis, self.pln.YAxis)
		conn_trans = Connection(pln_trans, self.type, self.part, self.id)
		conn_trans.pln.Transform(trans)
		conn_trans.flip_pln.Transform(trans)
		return conn_trans
	
	## return a copy of the connection
	def copy(self):
		pln_copy = Plane(self.pln.Origin, self.pln.XAxis, self.pln.YAxis)
		conn_copy = Connection(pln_copy, self.type, self.part, self.id)
		return conn_copy
	
	## generate the rules-table for the connection
	def generate_rules_table(self, rules):
		count = 0
		self.rules_table = []
		self.active_rules = []
		for rule in rules:
			if rule.part1 == self.part and rule.conn1 == self.id:
				self.rules_table.append(rule)
				self.active_rules.append(count)
				count += 1