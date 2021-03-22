"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.5.001

Connection class
"""

from Rhino.Geometry import Plane
from Rhino.Geometry import Vector3d

from wasp.utilities import plane_from_data, plane_to_data

import math

#################################################################### Connection ####################################################################
class Connection(object):
	'''
	Connection class. Stores the connection plane as well as information about types and rules.

	Args:
		_plane (Plane): Connection plane
		_type (str): Connection type (for automated rules generation)
		_part (str): Name of the part the connection belongs to
		_id (int): Connection ID (unique within each part)

	Attributes:
		pln (Plane): Connection plane
		flip_pln (Plane): Connection plane with Y-axis flipped (in order to connect to another connection)
		type (str): Connection type (for automated rules generation)
		part (str): Name of the part the connection belongs to
		id (int): Connection ID (unique within each part)
		rule_table ([]): List of Wasp rules compatible with this connection
		active_rules ([int]): Indexes of still active rules in the rule_table list
	'''

	
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
	

	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		c_pln = plane_from_data(data['plane'])
		return cls(c_pln, data['type'], data['part'], int(data['id']))

		
	## return the data dictionary representing the connection
	def to_data(self):
		data = {}
		data['plane'] = plane_to_data(self.pln)
		data['type'] = self.type
		data['part'] = self.part
		data['id'] = self.id
		#### rules_table and active_rules NOT IMPLEMENTED
		return data	

	
	## return a transformed copy of the connection
	def transform(self, trans):
		'''
		Returns a transformed connection

		Args:
			trans (Transformation): Transformation to apply to the Connection

		Returns:
			conn_trans (Connection): Transformed copy of the Connection
		'''
		pln_trans = Plane(self.pln.Origin, self.pln.XAxis, self.pln.YAxis)
		pln_trans.Transform(trans)
		
		conn_trans = Connection(pln_trans, self.type, self.part, self.id)
		return conn_trans
	
	## return a copy of the connection
	def copy(self):
		'''
		Returns a copy of the Connection

		Returns:
			conn_copy (Connection): Connection copy
		'''
		pln_copy = Plane(self.pln.Origin, self.pln.XAxis, self.pln.YAxis)
		conn_copy = Connection(pln_copy, self.type, self.part, self.id)
		return conn_copy
	
	## generate the rules-table for the connection
	def generate_rules_table(self, rules):
		'''
		Generates the Connection rule_table, given a set of rules

		Args:
			rules ([]): list of available rules
		'''
		count = 0
		self.rules_table = []
		self.active_rules = []
		for rule in rules:
			if rule.part1 == self.part and rule.conn1 == self.id:
				self.rules_table.append(rule)
				self.active_rules.append(count)
				count += 1