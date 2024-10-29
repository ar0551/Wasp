"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.6.001

Graph class and utilities
"""


from wasp import global_tolerance


#################################################################### Graph ####################################################################
class Graph(object):

	def __init__(self):
		self.graph_dict = {}

		## CURRENTLY NOT IMPLEMENTED
		self.nodes_attributes = {}
		self.edges_attributes = {}

	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspGraph [nodes: %s, edges: %s]" % (len(self.graph_dict.keys()), self.count_edges())
	

	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		g = cls()
		g.graph_dict = data
		return g


	## return the data dictionary representing the field
	def to_data(self, use_attributes=False):
		data = {}
		if use_attributes:
			pass # NOT IMPLEMENTED
		else:
			data = self.graph_dict
		return data
	

	## create a graph from a given aggregation
	@classmethod
	def from_aggregation(cls, aggr, full_graph=True, tolerance=global_tolerance, filter_by_rules=False, custom_rules=[]):
		g = cls()
		
		if full_graph:

			filtering_rules = aggr.rules
			if len(custom_rules) > 0:
				filtering_rules = custom_rules

			for i in range(len(aggr.aggregated_parts)):
				
				if aggr.aggregated_parts[i].id not in g.graph_dict:
					g.graph_dict[aggr.aggregated_parts[i].id] = {}
				
				## check for neighbours
				neighbours = []
				## find all parts within a neghibouring range
				for i2 in range(len(aggr.aggregated_parts)):
					if aggr.aggregated_parts[i].id != aggr.aggregated_parts[i2].id:
						p_dist = aggr.aggregated_parts[i].center.DistanceTo(aggr.aggregated_parts[i2].center)
						if p_dist < (aggr.aggregated_parts[i].dim + aggr.aggregated_parts[i2].dim) + tolerance:
							neighbours.append(i2)
				
				## check all connections for neighbouring parts
				for i2 in range(len(aggr.aggregated_parts[i].connections)):
					for i3 in neighbours:
						if aggr.aggregated_parts[i3].id != aggr.aggregated_parts[i].id:
							for i4 in range(len(aggr.aggregated_parts[i3].connections)):
								c_dist = aggr.aggregated_parts[i].connections[i2].pln.Origin.DistanceTo(aggr.aggregated_parts[i3].connections[i4].pln.Origin)
								if c_dist < tolerance:
									
									## check if the connection is allowed by the aggregation rules
									allowed_connection = True
									if filter_by_rules:
										allowed_connection = False
										for r in filtering_rules:
											if aggr.aggregated_parts[i].name == r.part1 and i2 == r.conn1 and aggr.aggregated_parts[i3].name == r.part2 and i4 == r.conn2:
												allowed_connection = True
												break

									if allowed_connection:
										edge_dict = {}
										edge_dict["start"] = aggr.aggregated_parts[i].id
										edge_dict["end"] = aggr.aggregated_parts[i3].id
										edge_dict["conn_start"] = i2
										edge_dict["conn_end"] = i4

										g.graph_dict[aggr.aggregated_parts[i].id][aggr.aggregated_parts[i3].id] = edge_dict
		else:
			g = aggr.graph

		return g

	## add a new node
	def add_node(self, id):
		if id not in self.graph_dict:
			self.graph_dict[id] = {}
	

	## add a new edges
	def add_edge(self, start_id, end_id, start_conn, end_conn):
		if start_id not in self.graph_dict:
			self.graph_dict[start_id] = {}
			
		if end_id not in self.graph_dict[start_id]:
			edge_dict = {}
			edge_dict["start"] = start_id
			edge_dict["end"] = end_id
			edge_dict["conn_start"] = start_conn
			edge_dict["conn_end"] = end_conn
			self.graph_dict[start_id][end_id] = edge_dict		
	
	## remove a node and all its relative edges
	def remove_node(self, id):
		# delete the node
		if id in self.graph_dict:
			del self.graph_dict[id]
		
		# delete the edges associated with the node
		for node in self.graph_dict:
			if id in self.graph_dict[node]:
				del self.graph_dict[node][id]		


	## count the number of edges (!!! add check for duplicates)
	def count_edges(self):
		count = 0
		for node in self.graph_dict:
			for neighbour in self.graph_dict[node]:
				count+=1
		return count
	

	## get a list of all nodes
	def get_nodes(self):
		return self.graph_dict.keys()
	

	## get a list of all edge pairs
	def get_edges(self, flatten = True):
		edges = []
		if flatten:
			for node in self.graph_dict:
				for neighbour in self.graph_dict[node]:
					edges.append([node, neighbour])
		else:
			n_count = 0
			for node in self.graph_dict:
				edges.append([])
				for neighbour in self.graph_dict[node]:
					edges[n_count].append([node, neighbour])
				n_count +=1

		return edges
	
	
	## get a list of all edge attributes
	def get_edges_attributes(self, flatten = True):
		edges_attr = []
		if flatten:
			for node in self.graph_dict:
				for neighbour in self.graph_dict[node]:
					edges_attr.append(self.graph_dict[node][neighbour])
		else:
			n_count = 0
			for node in self.graph_dict:
				edges_attr.append([])
				for neighbour in self.graph_dict[node]:
					edges_attr[n_count].append(self.graph_dict[node][neighbour])
				n_count +=1

		return edges_attr


