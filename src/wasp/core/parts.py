"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.4.015

Part classes and utilities
"""

from Rhino.Geometry import Transform
from Rhino.Geometry import Point3d

from wasp.utilities import mesh_from_data, mesh_to_data
from wasp.utilities import transform_from_data, transform_to_data
from wasp.core import Connection
from wasp.core.colliders import Collider
from wasp.core.constraints import Adjacency_Constraint

import random


#################################################################### Base Part ####################################################################
class Part(object):
	
	## constructor
	def __init__(self, name, geometry, connections, collider, attributes, dim=None, id=None, field=None):
		
		self.name = name
		self.id = id
		self.geo = geometry
		
		self.field = field
		
		self.connections = []
		self.active_connections = []

		count = 0
		for conn in connections:
			conn.part = self.name
			conn.id = count
			self.connections.append(conn)
			self.active_connections.append(count)
			count += 1
		
		self.transformation = Transform.Identity
		self.center = self.geo.GetBoundingBox(False).Center
		self.collider = collider
		
		##part size
		if dim is not None:
			self.dim = dim
		else:
			max_collider_dist = None
			for coll_geo in self.collider.geometry:
				for v in coll_geo.Vertices:
					dist = self.center.DistanceTo(v)
					if dist > max_collider_dist or max_collider_dist is None:
						max_collider_dist = dist
			
			self.dim = max_collider_dist
		
		self.parent = None
		self.children = []
		
		self.attributes = []
		if len(attributes) > 0:
			self.attributes = attributes
		
		self.is_constrained = False
	

	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspPart [name: %s, id: %s]" % (self.name, self.id)
	

	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		p_name = data['name']
		p_geometry = mesh_from_data(data['geometry'])
		p_connections = [Connection.from_data(c_data) for c_data in data['connections']]
		p_collider = Collider.from_data(data['collider'])
		p_attributes = [] #### ATTRIBUTES NOT IMPLEMENTED
		p_dim = float(data['dim'])
		
		p_id = None
		try:
			p_id = int(data['id'])
		except:
			p_id = data['id']
		p_field = data['field']

		part = cls(p_name, p_geometry, p_connections, p_collider, p_attributes, dim=p_dim, id=p_id, field=p_field)

		part.transformation = transform_from_data(data['transform'])
		part.parent = data['parent']
		
		for child_data in data['children']:
			child_id = None
			try:
				part.children.append(int(child_data))
			except:
				part.children.append(child_data)
		
		return part

		
	## return the data dictionary representing the part
	def to_data(self):
		data = {}
		## class types
		data['class_type'] = 'Part'
		## shared parameters
		data['name'] = self.name
		data['id'] = self.id
		data['geometry'] = mesh_to_data(self.geo)
		data['field'] = self.field
		data['connections'] = [conn.to_data() for conn in self.connections]
		data['active_connections'] = self.active_connections
		data['collider'] = self.collider.to_data()
		data['transform'] = transform_to_data(self.transformation)
		data['dim'] = self.dim
		data['parent'] = self.parent
		data['children'] = self.children
		return data	


	## reset the part and connections according to new provided aggregation rules
	def reset_part(self, rules):
		count = 0
		self.active_connections = []
		for conn in self.connections:
			conn.generate_rules_table(rules)
			self.active_connections.append(count)
			count += 1
	
	
	## return a dictionary containing all part data
	def return_part_data(self):
		data_dict = {}
		data_dict['name'] = self.name
		data_dict['id'] = self.id
		data_dict['geo'] = self.geo
		data_dict['connections'] = self.connections
		data_dict['transform'] = self.transformation
		data_dict['collider'] = self.collider
		data_dict['center'] = self.center
		data_dict['parent'] = self.parent
		data_dict['children'] = self.children
		data_dict['attributes'] = self.attributes
		return data_dict
	

	## return a transformed copy of the part
	def transform(self, trans, transform_sub_parts=False):
		geo_trans = self.geo.Duplicate()
		geo_trans.Transform(trans)
		
		collider_trans = self.collider.transform(trans)
		
		connections_trans = []
		for conn in self.connections:
			connections_trans.append(conn.transform(trans))
		
		attributes_trans = []
		if len(self.attributes) > 0:
			for attr in self.attributes:
				attributes_trans.append(attr.transform(trans))
		
		part_trans = Part(self.name, geo_trans, connections_trans, collider_trans, attributes_trans, dim=self.dim, id=self.id, field=self.field)
		
		part_trans.transformation = Transform.Multiply(trans, self.transformation)
		return part_trans
	
	## return a copy of the part
	def copy(self):
		geo_copy = self.geo.Duplicate()
		
		collider_copy = self.collider.copy()
		
		connections_copy = []
		for conn in self.connections:
			connections_copy.append(conn.copy())
		
		attributes_copy = []
		if len(self.attributes) > 0:
			for attr in self.attributes:
				attributes_copy.append(attr.copy())
		
		part_copy = Part(self.name, geo_copy, connections_copy, collider_copy, attributes_copy, dim=self.dim, id=self.id, field=self.field)
		part_copy.transformation = self.transformation
		return part_copy
	
	## return transformed center point of the part
	def transform_center(self, trans):
		center_trans = Point3d(self.center)
		center_trans.Transform(trans)
		return center_trans
	
	## return transformed collider
	def transform_collider(self, trans):
		return self.collider.transform(trans)


#################################################################### Constrained Part ####################################################################
class AdvancedPart(Part):
	
	## constructor
	def __init__(self, name, geometry, connections, collider, attributes, additional_collider, supports, dim = None, id=None, field=None, sub_parts=[], adjacency_const = [], orientation_const=[]):
		
		super(AdvancedPart, self).__init__(name, geometry, connections, collider, attributes, dim=dim, id=id, field=field)
		
		self.add_collider = additional_collider
		self.supports = supports
		self.adjacency_const = adjacency_const
		self.orientation_const = orientation_const

		if self.add_collider is not None or len(self.supports) > 0 or len(self.adjacency_const) > 0 or len(self.orientation_const) > 0:
			self.is_constrained = True 
		
		## hierarchical sub-parts
		self.sub_parts = sub_parts
		self.hierarchy_level = 0
		if len(self.sub_parts) > 0:
			self.hierarchy_level = self.sub_parts[0].hierarchy_level + 1
	

	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspAdvPart [name: %s, id: %s]" % (self.name, self.id)
	

	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		p_name = data['name']
		p_geometry = mesh_from_data(data['geometry'])
		p_connections = [Connection.from_data(c_data) for c_data in data['connections']]
		p_collider = Collider.from_data(data['collider'])
		p_attributes = [] #### ATTRIBUTES NOT IMPLEMENTED
		p_dim = float(data['dim'])

		p_id = None
		try:
			p_id = int(data['id'])
		except:
			p_id = data['id']
		p_field = data['field']

		#### AdvPart parameters
		p_add_collider = None
		if data['add_collider'] is not None:
			p_add_collider = Collider.from_data(data['add_collider'])
		p_supports = [] ## Supports not implemented (WILL BE REMOVED IN NEXT VERSION)
		p_sub_parts = [AdvancedPart.from_data(sp_data) for sp_data in data['sub_parts']]
		p_adjacency_const = [Adjacency_Constraint.from_data(adj_data) for adj_data in data['adjacency_const']]

		adv_part = cls(p_name, p_geometry, p_connections, p_collider, p_attributes, p_add_collider, p_supports, dim=p_dim, id=p_id, field=p_field, sub_parts=p_sub_parts, adjacency_const=p_adjacency_const)

		adv_part.transformation = transform_from_data(data['transform'])
		adv_part.parent = data['parent']
		
		for child_data in data['children']:
			child_id = None
			try:
				adv_part.children.append(int(child_data))
			except:
				adv_part.children.append(child_data)
		
		return adv_part

		
	## return the data dictionary representing the part
	def to_data(self):
		data = {}
		## class types
		data['class_type'] = 'AdvancedPart'
		## shared parameters
		data['name'] = self.name
		data['id'] = self.id
		data['geometry'] = mesh_to_data(self.geo)
		data['field'] = self.field
		data['connections'] = [conn.to_data() for conn in self.connections]
		data['active_connections'] = self.active_connections
		data['collider'] = self.collider.to_data()
		data['transform'] = transform_to_data(self.transformation)
		data['dim'] = self.dim
		data['parent'] = self.parent
		data['children'] = self.children
		#### AdvPart parameters
		data['add_collider'] = None
		if self.add_collider is not None:
			data['add_collider'] = self.add_collider.to_data()
		## Supports not implemented (WILL BE REMOVED IN NEXT VERSION)
		data['adjacency_const'] = [const.to_data() for const in self.adjacency_const]
		## Orientation Constraints not implemented
		data['sub_parts'] = [sub_p.to_data() for sub_p in self.sub_parts]
		return data


	## return all part data
	######################################## add returs for adjacency constraints
	def return_part_data(self):
		data_dict = {}
		data_dict['name'] = self.name
		data_dict['id'] = self.id
		data_dict['geo'] = self.geo
		data_dict['connections'] = self.connections
		data_dict['transform'] = self.transformation
		data_dict['collider'] = self.collider
		data_dict['center'] = self.center
		data_dict['parent'] = self.parent
		data_dict['children'] = self.children
		data_dict['attributes'] = self.attributes
		data_dict['add_collider'] = self.add_collider
		return data_dict
	

	## return a transformed copy of the part
	def transform(self, trans, transform_sub_parts=False, sub_level = 0):
		geo_trans = self.geo.Duplicate()
		geo_trans.Transform(trans)
		
		collider_trans = self.collider.transform(trans)
		
		connections_trans = []
		for conn in self.connections:
			connections_trans.append(conn.transform(trans))
		
		attributes_trans = []
		if len(self.attributes) > 0:
			for attr in self.attributes:
				attributes_trans.append(attr.transform(trans))
		
		add_collider_trans = None
		if(self.add_collider != None):
			add_collider_trans = self.add_collider.transform(trans, transform_connections=True, maintain_valid=True)
			
		supports_trans = []
		if len(self.supports) > 0:
			for sup in self.supports:
				sup_trans = sup.transform(trans)
				supports_trans.append(sup_trans)

		adjacency_const_trans = []
		if len(self.adjacency_const) > 0:
			for ac in self.adjacency_const:
				ac_trans = ac.transform(trans)
				adjacency_const_trans.append(ac_trans)
		
		orient_const_trans = []
		if len(self.orientation_const) > 0:
			for oc in self.orientation_const:
				oc_trans = oc.transform(trans)
				orient_const_trans.append(oc_trans)

		if transform_sub_parts and len(self.sub_parts) > 0 and sub_level > 0:
			sub_parts_trans = []
			for sp in self.sub_parts:
				sp_trans = sp.transform(trans, transform_sub_parts = True, sub_level = sub_level - 1)
				sub_parts_trans.append(sp_trans)
			part_trans = AdvancedPart(self.name, geo_trans, connections_trans, collider_trans, attributes_trans, add_collider_trans, supports_trans, dim=self.dim, id=self.id, field=self.field, sub_parts=sub_parts_trans, adjacency_const = adjacency_const_trans, orientation_const=orient_const_trans)
			part_trans.transformation = Transform.Multiply(trans, self.transformation)
			part_trans.is_constrained = True
			return part_trans
		
		else:
			part_trans = AdvancedPart(self.name, geo_trans, connections_trans, collider_trans, attributes_trans, add_collider_trans, supports_trans, dim=self.dim, id=self.id, field=self.field, sub_parts=self.sub_parts, adjacency_const = adjacency_const_trans, orientation_const=orient_const_trans)
			part_trans.transformation = Transform.Multiply(trans, self.transformation)
			part_trans.is_constrained = True
			return part_trans
	
	
	## return a copy of the part		
	def copy(self):
		geo_copy = self.geo.Duplicate()
		
		collider_copy = self.collider.copy()
		
		connections_copy = []
		for conn in self.connections:
			connections_copy.append(conn.copy())
		
		attributes_copy = []
		if len(self.attributes) > 0:
			for attr in self.attributes:
				attributes_copy.append(attr.copy())
		
		add_collider_copy = None
		if(self.add_collider != None):
			add_collider_copy = self.add_collider.copy()
			
		supports_copy = []
		if len(self.supports) > 0:
			for sup in self.supports:
				sup_copy = sup.copy()
				supports_copy.append(sup_copy)
		
		adjacency_const_copy = []
		if len(self.adjacency_const) > 0:
			for ac in self.adjacency_const:
				ac_copy = ac.copy()
				adjacency_const_copy.append(ac_copy)
		
		orient_const_copy = []
		if len(self.orientation_const) > 0:
			for oc in self.orientation_const:
				oc_copy = oc.copy()
				orient_const_copy.append(oc_copy)

		if len(self.sub_parts) > 0:
			sub_parts_copy = []
			for sp in self.sub_parts:
				sp_copy = sp.copy()
				sub_parts_copy.append(sp_copy)
			part_copy = AdvancedPart(self.name, geo_copy, connections_copy, collider_copy, attributes_copy, add_collider_copy, supports_copy, dim=self.dim, id=self.id, field=self.field, sub_parts=sub_parts_copy, adjacency_const=adjacency_const_copy, orientation_const=orient_const_copy)
			part_copy.transformation = self.transformation
			part_copy.is_constrained = True
			return part_copy
		
		else:
			part_copy = AdvancedPart(self.name, geo_copy, connections_copy, collider_copy, attributes_copy, add_collider_copy, supports_copy, dim=self.dim, id=self.id, field=self.field, sub_parts=self.sub_parts, adjacency_const=adjacency_const_copy, orientation_const=orient_const_copy)
			part_copy.transformation = self.transformation
			part_copy.is_constrained = True
			return part_copy


################################################################# Parts Catalog ##################################################################
class PartCatalog(object):
	##constructor
	def __init__(self, _parts, _amounts, _is_limited=True, _is_adaptive=False):
		
		self.parts = _parts
		self.amounts = _amounts
		self.is_limited = _is_limited
		self.is_adaptive = _is_adaptive
		
		self.dict = {}
		for i in xrange(len(self.parts)):
			self.dict[self.parts[i]] = _amounts[i]
		
		self.is_empty = False
		self.parts_total = sum(self.dict.values())
	

	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspPartCatalog [%s]" % (self.dict)
	
	
	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		return cls(data['parts'], [int(a) for a in data['amounts']], _is_limited=data['is_limited'], _is_adaptive=data['is_adaptive'])

		
	## return the data dictionary representing the catalog
	def to_data(self):
		data = {}
		data['parts'] = self.parts
		data['amounts'] = self.amounts
		data['is_limited'] = self.is_limited
		data['is_adaptive'] = self.is_adaptive
		return data	
	

	## return a random part type
	def return_random_part(self):
		choices = [key for key in self.dict.keys() if self.dict[key] > 0]
		if len(choices) > 0:
			return random.choice(choices)
		else:
			self.is_empty = True
			return None
	

	## return a weighted-choice between the available parts, give the available parts amounts
	def return_weighted_part(self):
		if self.parts_total == 0:
			self.is_empty = True
			return None
		n = random.uniform(0, self.parts_total)
		for key in self.dict:
			if n < self.dict[key]:
				return key
			n = n - self.dict[key]
		return None

	## add or remove parts from the catalog	
	def update(self, part_name, difference):
		if self.is_limited:
			self.dict[part_name] += difference
			self.parts_total = sum(self.dict.values())
			if self.parts_total == 0:
				self.is_empty = True
			else:
				self.is_empty = False
		elif self.is_adaptive:
			self.dict[part_name] += difference
			prev_parts_total = self.parts_total
			self.parts_total = sum(self.dict.values())
			for key in self.dict:
				self.dict[key] = (self.dict[key] * prev_parts_total) / (self.parts_total)
			self.parts_total = sum(self.dict.values())
		else:
			pass
	
	## return a copy of the catalog
	def copy(self):
		amounts = [self.dict[part] for part in self.parts]
		return PartCatalog(self.parts, amounts, _is_limited=self.is_limited, _is_adaptive=self.is_adaptive)
