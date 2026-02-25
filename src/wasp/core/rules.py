"""
(C) 2017-2026 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.7.001

Rule class and (WIP) rules generation utilities
"""

#################################################################### Rule ####################################################################
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


#################################################################### Graph Rule ####################################################################
class GraphRule(Rule):
	
	## constructor
	def __init__(self, _part1, _conn1, _part2, _conn2, _part1_id, _part2_id, _active = True):
		super(GraphRule, self).__init__(_part1, _conn1, _part2, _conn2, _active)
		self.part1_id = _part1_id
		self.part2_id = _part2_id
	

	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspGraphRule [%s|%s_%s|%s>%s_%s]" % (self.part1, self.conn1, self.part2, self.conn2, self.part1_id, self.part2_id)
	

	## create class from data dictionary (NOT IMPLEMENTED)
	@classmethod
	def from_data(cls, data):
		return cls(data['part1'], int(data['conn1']), data['part1'], int(data['conn1']), _active = data['active'])

		
	## return the data dictionary representing the rule (NOT IMPLEMENTED)
	def to_data(self):
		data = {}
		data['part1'] = self.part1
		data['conn1'] = self.conn1
		data['part2'] = self.part2
		data['conn2'] = self.conn2
		data['active'] = self.active
		return data


#################################################################### Recipe ####################################################################
class Recipe(object):

	## constructor
	def __init__(self, _name, _aggregation, _start_conns, _start_mask):
		self.name = _name
		self.aggregation = _aggregation
		self.start_connections = _start_conns
		self.start_mask = _start_mask
		self.id_converter = {}
		for part in self.aggregation.aggregated_parts:
			self.id_converter[part.id] = part.id
	

	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspRecipe [name: %s, count: %d]" % (self.name, len(self.aggregation.aggregated_parts))
	

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
		
		for part in self.aggregation.aggregated_parts:
			for neighbour in self.aggregation.graph.graph_dict[part.id]:
				edge = self.aggregation.graph.graph_dict[part.id][neighbour]
				start_p = self.aggregation.aggregated_parts[int(edge['start'])].name
				end_p = self.aggregation.aggregated_parts[int(edge['end'])].name
				start_conn = edge['conn_start']
				end_conn = edge['conn_end']

				rule = GraphRule(start_p, start_conn, end_p, end_conn, edge['start'], edge['end'])
				rules.append(rule)
		
		return sorted(rules , key=lambda x: x.part2_id)
	

	## return the rules sequence
	def return_rules_sequence_OLD(self):
		rules = []
		graph_edges = self.aggregation.graph.get_edges_attributes()
		
		for edge in graph_edges:
			start_p = self.aggregation.aggregated_parts[int(edge['start'])].name
			end_p = self.aggregation.aggregated_parts[int(edge['end'])].name
			start_conn = edge['conn_start']
			end_conn = edge['conn_end']

			rule = GraphRule(start_p, start_conn, end_p, end_conn, edge['start'], edge['end'])
			rules.append(rule)
			
		return rules
	

	## return a copy of the first part
	def return_start_part(self):
		return self.aggregation.aggregated_parts[0].copy()


	## update ids according to position in aggregation
	def update_ids(self, start_id, aggr_count):
		for i in range(len(self.aggregation.aggregated_parts)):
			if i == 0:
				self.id_converter[i] = start_id
			else:
				self.id_converter[i] = aggr_count + i - 1