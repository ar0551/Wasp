"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.6.001

Rule class and (WIP) rules generation utilities
"""

class Rule(object):
	
	## constructor
	def __init__(self, _part1, _conn1, _part2, _conn2, _active = True):
		self.part1 = _part1
		self.conn1 = _conn1
		self.part2 = _part2
		self.conn2 = _conn2
		self.active = _active
	

	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspRule [%s|%s_%s|%s]" % (self.part1, self.conn1, self.part2, self.conn2)
	

	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		return cls(data['part1'], int(data['conn1']), data['part1'], int(data['conn1']), _active = data['active'])

		
	## return the data dictionary representing the rule
	def to_data(self):
		data = {}
		data['part1'] = self.part1
		data['conn1'] = self.conn1
		data['part2'] = self.part2
		data['conn2'] = self.conn2
		data['active'] = self.active
		return data


class Recipe(object):

	## constructor
	def __init__(self, _aggregation, _start_conns, _start_mask):
		self.aggregation = _aggregation
		self.start_connections = _start_conns
		self.start_mask = _start_mask
	

	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspRecipe [%d]" % (len(self.aggregation.aggregated_parts))
	

	## create class from data dictionary (NOT IMPLEMENTED)
	@classmethod
	def from_data(cls, data):
		return None

		
	## return the data dictionary representing the class (NOT IMPLEMENTED)
	def to_data(self):
		data = {}
		return data
	

	## find all possible start locations in a given aggregation
	def filter_start_locations(self, aggr_in):
		valid_start_locations = []

		for i in range(len(aggr_in.aggregated_parts)):
			part = aggr_in.aggregated_parts[i]
			if part.name == self.aggregation.aggregated_parts[0].name:
				p_matrix = aggr_in.check_blocked_connections(part)
				is_valid = True

				for i2 in range(len(self.start_mask)):
					if self.start_mask[i2] == 1:
						if self.start_connections[i2].id not in p_matrix:
							is_valid = False
							break
					elif self.start_mask[i2] == -1:
						if self.start_connections[i2].id in p_matrix:
							is_valid = False
							break
				if is_valid:
					valid_start_locations.append(part)

		return valid_start_locations
	

	## return the rules sequence
	def return_rules_sequence(self):
		rules = []
		graph_edges = self.aggregation.graph.get_edges_attributes()
		
		for edge in graph_edges:
			start_p = self.aggregation.aggregated_parts[int(edge['start'])].name
			end_p = self.aggregation.aggregated_parts[int(edge['end'])].name
			start_conn = edge['conn_start']
			end_conn = edge['conn_end']

			rule = "{}|{}_{}|{}".format(start_p, start_conn, end_p, end_conn)
			rules.append(rule)
			
		return rules
		
