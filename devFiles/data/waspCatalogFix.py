# Wasp: Discrete Design with Grasshopper plug-in (GPL) initiated by Andrea Rossi
# 
# This file is part of Wasp.
# 
# Copyright (c) 2017, Andrea Rossi <a.rossi.andrea@gmail.com>
# Wasp is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Wasp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Wasp; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>
#
# Significant parts of Wasp have been developed by Andrea Rossi
# as part of research on digital materials and discrete design at:
# DDU Digital Design Unit - Prof. Oliver Tessmann
# Technische Universitat Darmstadt


#########################################################################
##								 IMPORTS							   ##
#########################################################################
import random
import math
import bisect
from Rhino.RhinoDoc import ActiveDoc
import Rhino.Geometry as rg

#########################################################################
##							GLOBAL VARIABLES						   ##
#########################################################################
global_tolerance = ActiveDoc.ModelAbsoluteTolerance*2

#########################################################################
##								 CLASSES							   ##
#########################################################################

#################################################################### Connection ####################################################################
class Connection(object):
	
	## constructor
	def __init__(self, _plane, _type, _part, _id):
		
		self.pln = _plane
		
		flip_pln_Y = rg.Vector3d(self.pln.YAxis)
		flip_pln_Y.Reverse()
		self.flip_pln = rg.Plane(self.pln.Origin, self.pln.XAxis, flip_pln_Y)
		
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
		pln_trans = rg.Plane(self.pln.Origin, self.pln.XAxis, self.pln.YAxis)
		conn_trans = Connection(pln_trans, self.type, self.part, self.id)
		conn_trans.pln.Transform(trans)
		conn_trans.flip_pln.Transform(trans)
		return conn_trans
	
	## return a copy of the connection
	def copy(self):
		pln_copy = rg.Plane(self.pln.Origin, self.pln.XAxis, self.pln.YAxis)
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
		
		self.transformation = rg.Transform.Identity
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
		part_trans.transformation = trans
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
		center_trans = rg.Point3d(self.center)
		center_trans.Transform(trans)
		return center_trans
	
	## return transformed collider
	def transform_collider(self, trans):
		return self.collider.transform(trans)


#################################################################### Constrained Part ####################################################################
class AdvancedPart(Part):
	
	## constructor
	def __init__(self, name, geometry, connections, collider, attributes, additional_collider, supports, dim = None, id=None, field=None, sub_parts=[]):
		
		super(self.__class__, self).__init__(name, geometry, connections, collider, attributes, dim=dim, id=id, field=field)
		
		self.add_collider = None
		if additional_collider != None:
			self.add_collider = additional_collider
		
		self.supports = []
		if len(supports) > 0:
			self.supports = supports
		
		## hierarchical sub-parts
		self.sub_parts = sub_parts
		self.hierarchy_level = 0
		if len(self.sub_parts) > 0:
			self.hierarchy_level = self.sub_parts[0].hierarchy_level + 1
	
	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspAdvPart [name: %s, id: %s]" % (self.name, self.id)
	
	## return all part data
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
			
		
		if transform_sub_parts and len(self.sub_parts) > 0 and sub_level > 0:
			sub_parts_trans = []
			for sp in self.sub_parts:
				sp_trans = sp.transform(trans, transform_sub_parts = True, sub_level = sub_level - 1)
				sub_parts_trans.append(sp_trans)
			part_trans = AdvancedPart(self.name, geo_trans, connections_trans, collider_trans, attributes_trans, add_collider_trans, supports_trans, dim=self.dim, id=self.id, field=self.field, sub_parts=sub_parts_trans)
			part_trans.transformation = trans
			part_trans.is_constrained = True
			return part_trans
		
		else:
			part_trans = AdvancedPart(self.name, geo_trans, connections_trans, collider_trans, attributes_trans, add_collider_trans, supports_trans, dim=self.dim, id=self.id, field=self.field, sub_parts=self.sub_parts)
			part_trans.transformation = trans
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
		
		if len(self.sub_parts) > 0:
			sub_parts_copy = []
			for sp in self.sub_parts:
				sp_copy = sp.copy()
				sub_parts_copy.append(sp_copy)
			part_copy = AdvancedPart(self.name, geo_copy, connections_copy, collider_copy, attributes_copy, add_collider_copy, supports_copy, dim=self.dim, id=self.id, field=self.field, sub_parts=sub_parts_copy)
			part_copy.transformation = self.transformation
			part_copy.is_constrained = True
			return part_copy
		
		else:
			part_copy = AdvancedPart(self.name, geo_copy, connections_copy, collider_copy, attributes_copy, add_collider_copy, supports_copy, dim=self.dim, id=self.id, field=self.field, sub_parts=self.sub_parts)
			part_copy.transformation = self.transformation
			part_copy.is_constrained = True
			return part_copy
			
	
	

#################################################################### Rule ####################################################################
class Rule(object):
	
	def __init__(self, _part1, _conn1, _part2, _conn2, _active = True):
		self.part1 = _part1
		self.conn1 = _conn1
		self.part2 = _part2
		self.conn2 = _conn2
		self.active = _active
	
	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspRule [%s|%s_%s|%s]" % (self.part1, self.conn1, self.part2, self.conn2)

#################################################################### Field ####################################################################
class Field(object):
	
	## constructor
	def __init__(self, name, boundaries, pts, count_vec, resolution, values = []):
		
		self.name = name
		self.resolution = resolution
		
		self.boundaries = boundaries
		self.pts = pts
		self.bbox = rg.BoundingBox(pts)
		
		self.x_count = int(count_vec.X)
		self.y_count = int(count_vec.Y)
		self.z_count = int(count_vec.Z)
		
		self.vals = []
		pts_count = 0
		
		self.is_tensor_field = False
		try:
			v = values[0][2]
			self.is_tensor_field = True
		except:
			pass
		
		if len(values) > 0:
			for z in range(0, self.z_count):
				self.vals.append([])
				for y in range(0, self.y_count):
					self.vals[z].append([])
					for x in range(0, self.x_count):
						if len(self.boundaries) > 0:
							inside = False
							for bou in self.boundaries:
								if bou.IsPointInside(self.pts[pts_count], global_tolerance, True) == True:
									self.vals[z][y].append(values[pts_count])
									inside = True
									break
							if inside == False:
								if self.is_tensor_field:
									self.vals[z][y].append(rg.Vector3d(0,0,0))
								else:
									self.vals[z][y].append(0.0)
						else:
							self.vals[z][y].append(values[pts_count])
						pts_count += 1
	
	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspField [name: %s, res: %s, count: %s]" % (self.name, self.resolution, len(self.pts))
	
	def return_values_list(self):
		values_list = []
		for z in range(0, self.z_count):
			for y in range(0, self.y_count):
				for x in range(0, self.x_count):
					values_list.append(self.vals[z][y][x])
		return values_list
						
	
	## return value associated to the closest point of the field to the given point
	def return_pt_val(self, pt):
		pt_trans = pt - self.bbox.Min
		x = int(math.floor(pt_trans.X/self.resolution))
		y = int(math.floor(pt_trans.Y/self.resolution))
		z = int(math.floor(pt_trans.Z/self.resolution))
		
		value = self.vals[z][y][x]
		return value
	
	## find and return highest value in the field
	def return_highest_pt(self, constraints = None):
		max_val = -1
		max_coords = None
		
		for z in range(0, self.z_count):
			for y in range(0, self.y_count):
				for x in range(0, self.x_count):
					value = self.vals[z][y][x]
					## tensor field aggregation (WIP)
					if self.is_tensor_field:
						if value.Length > max_val:
							if constraints is not None:
								constraint_check = False
								pt = rg.Point3d(x*self.resolution, y*self.resolution, z*self.resolution)
								pt += self.bbox.Min
								for constraint in constraints:
									if constraint.check_soft(pt) == False:
										constraint_check = True
										break
								if constraint_check == False:
									max_val = value.Length
									max_coords = (x,y,z)
							else:
								max_val = value.Length
								max_coords = (x,y,z)
					else:
						if value > max_val:
							if constraints is not None:
								constraint_check = False
								pt = rg.Point3d(x*self.resolution, y*self.resolution, z*self.resolution)
								pt += self.bbox.Min
								for constraint in constraints:
									if constraint.check_soft(pt) == False:
										constraint_check = True
										break
								if constraint_check == False:
									max_val = value
									max_coords = (x,y,z)
							else:
								max_val = value
								max_coords = (x,y,z)
		
		highest_pt = rg.Point3d(max_coords[0]*self.resolution, max_coords[1]*self.resolution, max_coords[2]*self.resolution)
		highest_pt = highest_pt + self.bbox.Min
		
		return highest_pt


#################################################################### Attribute ####################################################################
class Attribute(object):
	
	## constructor
	def __init__(self, name, values, transformable):
		self.name = name
		self.values = values
		self.transformable = transformable
	
	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspAttribute [name: %s]" % (self.name)
	
	## return a transformed copy of the attribute
	def transform(self, trans):
		if self.transformable == True:
			values_trans = []
			for val in self.values:
				val_trans = None
				if type(val) == rg.Point3d:
					val_trans = rg.Point3d(val)
				elif type(val) == rg.Plane:
					val_trans = rg.Plane(val)
				elif type(val) == rg.Line:
					val_trans = rg.Line(val.From, val.To)
				else:
					val_trans = val.Duplicate()
				val_trans.Transform(trans)
				values_trans.append(val_trans)
			attr_trans = Attribute(self.name, values_trans, self.transformable)
		else:
			attr_trans = Attribute(self.name, self.values, self.transformable)
		return attr_trans
	
	## return a copy of the attribute
	def copy(self):
		if self.transformable == True:
			values_copy = []
			for val in self.values:
				val_copy = None
				if type(val) == rg.Point3d:
					val_copy = rg.Point3d(val)
				elif type(val) == rg.Plane:
					val_copy = rg.Plane(val)
				elif type(val) == rg.Line:
					val_copy = rg.Line(val.From, val.To)
				else:
					val_copy = val.Duplicate()
				values_copy.append(val_copy)
			attr_copy = Attribute(self.name, values_copy, self.transformable)
		else:
			attr_copy = Attribute(self.name, self.values, self.transformable)
		return attr_copy

		
#################################################################### Support ####################################################################
class Support(object):
	
	## constructor
	def __init__(self, support_directions):
		self.sup_dir = support_directions
	
	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspSupport [len: %s]" % (len(self.sup_dir))
	
	## return a transformed copy of the support
	def transform(self, trans):
		sup_dir_trans = []
		for dir in self.sup_dir:
			dir = dir.ToNurbsCurve()
			start_trans = dir.PointAtStart
			end_trans = dir.PointAtEnd
			start_trans.Transform(trans)
			end_trans.Transform(trans)
			dir_trans = rg.Line(start_trans, end_trans)
			sup_dir_trans.append(dir_trans)
		sup_trans = Support(sup_dir_trans)
		return sup_trans
	
	## return a copy of the support
	def copy(self):
		sup_dir_copy = []
		for dir in self.sup_dir:
			dir = dir.ToNurbsCurve()
			start_copy = dir.PointAtStart
			end_copy = dir.PointAtEnd
			dir_copy = rg.Line(start_copy, end_copy)
			sup_dir_copy.append(dir_copy)
		sup_copy = Support(sup_dir_copy)
		return sup_copy
	

#################################################################### Aggregation ####################################################################
class Aggregation(object):
	
	## class constructor
	def __init__(self, _name, _parts, _rules, _mode, _prev = [], _coll_check = True, _field = [], _global_constraints = [], _catalog = None):
		
		## basic parameters
		self.name = _name
		
		self.parts = {}
		for part in _parts:
			self.parts[part.name] = part
		
		self.rules = _rules
		
		self.mode = _mode
		self.coll_check = _coll_check
		
		self.aggregated_parts = []
		
		## fields
		self.multiple_fields = False
		if len(_field) == 0 or _field is None:
			self.field = None
		elif len(_field) == 1:
			self.field = _field[0]
		else:
			self.field = {}
			for f in _field:
				self.field[f.name] = f
			self.multiple_fields = True
		
		## reset base parts
		self.reset_base_parts()
		
		## temp list to store possible colliders to newly added parts
		self.possible_collisions = []
		
		## aggregation queue, storing sorted possible next states in the form (part, f_val)
		self.aggregation_queue = []
		self.queue_values = []
		self.queue_count = 0
		
		## previous aggregated parts
		self.prev_num = 0
		if len(_prev) > 0:
			self.prev_num = len(_prev)
			for prev_p in _prev:
				prev_p_copy = prev_p.copy()
				prev_p_copy.reset_part(self.rules)
				prev_p_copy.id = len(self.aggregated_parts)
				self.aggregated_parts.append(prev_p_copy)
				if self.field is not None:
					self.compute_next_w_field(prev_p_copy)
		
		## global constraints applied to the aggregation
		self.global_constraints = _global_constraints
		
		self.catalog = _catalog
		
		#### WIP ####
		self.collision_shapes = []
		self.graph = None
	
	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspAggregation [name: %s, size: %s]" % (self.name, len(self.aggregated_parts))
	
	## reset base parts
	def reset_base_parts(self, new_parts = None):
		if new_parts != None:
			self.parts = {}
			for part in new_parts:
				self.parts[part.name] = part
		
		for p_key in self.parts:
			self.parts[p_key].reset_part(self.rules)
			
	## reset rules and regenerate rule tables for each part
	def reset_rules(self, rules):
		if rules != self.rules:
			self.rules = rules
			self.reset_base_parts()
			
			for part in self.aggregated_parts:
				part.reset_part(rules)
	
	## recompute aggregation queue
	def recompute_aggregation_queue(self):
		self.aggregation_queue = []
		self.queue_values = []
		self.queue_count = 0
		for part in self.aggregated_parts:
			self.compute_next_w_field(part)
	
	## trim aggregated parts list to a specific length
	def remove_elements(self, num):
		self.aggregated_parts = self.aggregated_parts[:num]
		for part in self.aggregated_parts:
			part.reset_part(self.rules)
		
		if self.field is not None:
			self.recompute_aggregation_queue()
	
	## compute all possible parts which can be placed given an existing part and connection
	def compute_possible_children(self, part_id, conn_id, check_constraints = False):
		
		possible_children = []
		current_part = self.aggregated_parts[part_id]
		
		if conn_id in current_part.active_connections:
			current_conn = current_part.connections[conn_id]
			for rule_id in current_conn.active_rules:
				rule = current_conn.rules_table[rule_id]
				
				next_part = self.parts[rule.part2]
				orientTransform = rg.Transform.PlaneToPlane(next_part.connections[rule.conn2].flip_pln, current_conn.pln)
				
				## boolean checks for all constraints
				coll_check = False
				add_coll_check = False
				valid_connections = []
				missing_sup_check = False
				global_const_check = False
				
				if check_constraints:
					## collision check
					self.possible_collisions = []
					coll_check = self.collision_check(next_part, orientTransform)
					
					## constraints check
					if self.mode == 1: ## only local constraints mode
						if coll_check == False and next_part.is_constrained:
							add_coll_check = self.additional_collider_check(next_part, orientTransform)
							
							if add_coll_check == False:
							   missing_sup_check = self.missing_supports_check(next_part, orientTransform)
					
					elif self.mode == 2: ## onyl global constraints mode
						if coll_check == False and len(self.global_constraints) > 0:
							global_const_check = self.global_constraints_check(next_part, orientTransform)
					
					elif self.mode == 3: ## local+global constraints mode
						if coll_check == False:
							if len(self.global_constraints) > 0:
								global_const_check = self.global_constraints_check(next_part, orientTransform)
							if global_const_check == False and next_part.is_constrained:
								add_coll_check = self.additional_collider_check(next_part, orientTransform)
								if add_coll_check == False:
								   missing_sup_check = self.missing_supports_check(next_part, orientTransform)
				
				if coll_check == False and add_coll_check == False and missing_sup_check == False and global_const_check == False:
					next_part_trans = next_part.transform(orientTransform)
					possible_children.append(next_part_trans)
			
			return possible_children	
		else:
			return -1
		
	
	## add a custom pre-computed part which has been already transformed in place and checked for constraints
	def add_custom_part(self, part_id, conn_id, next_part):
		next_part.reset_part(self.rules)
		next_part.id = len(self.aggregated_parts)
		
		self.aggregated_parts[part_id].children.append(next_part)
		next_part.parent = self.aggregated_parts[part_id]
		self.aggregated_parts.append(next_part)
		
		for i in range(len(self.aggregated_parts[part_id].active_connections)):
			if self.aggregated_parts[part_id].active_connections[i] == conn_id:
				self.aggregated_parts[part_id].active_connections.pop(i)
				break
	
	
	#### constraints checks ####
	
	## function grouping all constraints checks (not yet implemented)
	def constraints_check(self, part, trans):
		pass
	
	
	## overlap // part-part collision check
	def collision_check(self, part, trans):
		part_center = part.transform_center(trans)
		
		## overlap check
		coll_count = 0
		for ex_part in self.aggregated_parts:
			dist = ex_part.center.DistanceTo(part_center)
			if dist < global_tolerance:
				return True
			elif dist < ex_part.dim + part.dim:
				self.possible_collisions.append(coll_count)
			coll_count += 1
		
		## collision check
		if self.coll_check == True:
			part_collider = part.transform_collider(trans)
			if part_collider.check_collisions_by_id(self.aggregated_parts, self.possible_collisions):
				return True
		return False
	
	## additional collider check
	def additional_collider_check(self, part, trans):
		if part.add_collider != None:
			add_collider = part.add_collider.transform(trans, transform_connections=True, maintain_valid = False)
			if add_collider.check_collisions_w_parts(self.aggregated_parts):
				return True
			## assign computed valid connections according to collider location
			part.add_collider.valid_connections = list(add_collider.valid_connections)
		return False
	
	## support check
	def missing_supports_check(self, part, trans):
		if len(part.supports) > 0:
			for sup in part.supports:
				supports_count = 0
				sup_trans = sup.transform(trans)
				for dir in sup_trans.sup_dir:
					for id in self.possible_collisions:
						if self.aggregated_parts[id].collider.check_intersection_w_line(dir):
							supports_count += 1
							break
				if supports_count == len(sup_trans.sup_dir):
					return False
			return True
		else:
			return False
	
	## global constraints check
	def global_constraints_check(self, part, trans):
		for constraint in self.global_constraints:
			part_center = part.transform_center(trans)
			if constraint.soft:
				if constraint.check(pt = part_center) == False:
					return True
			else:
				part_collider = part.transform_collider(trans)
				if constraint.check(pt = part_center, collider = part_collider) == False:
					return True
		return False
	
	
	#### aggregation methods ####
	
	## sequential aggregation with Graph Grammar
	def aggregate_sequence(self, graph_rules):
		
		for rule in graph_rules:	
			## first part
			if len(self.aggregated_parts) == 0:
				aggr_rule = rule.split(">")[0]
				rule_parts = aggr_rule.split("_")
				part1 = str(rule_parts[0].split("|")[0])
				conn1 = int(rule_parts[0].split("|")[1])
				part2 = str(rule_parts[1].split("|")[0])
				conn2 = int(rule_parts[1].split("|")[1])
				
				rule_ids = rule.split(">")[1].split("_")
				
				first_part = self.parts[part1]
				first_part_trans = first_part.transform(rg.Transform.Identity)
				first_part_trans.id = rule_ids[0]
				
				next_part = self.parts[part2]
				
				orientTransform = rg.Transform.PlaneToPlane(next_part.connections[conn2].flip_pln, first_part.connections[conn1].pln)
				
				next_part_trans = next_part.transform(orientTransform)
				next_part_trans.id = rule_ids[1]
				
				## check additional collider (for fabrication constraints)
				self.additional_collider_check(next_part, orientTransform)
				
				## parent-child tracking
				first_part_trans.children.append(next_part_trans)
				next_part_trans.parent = first_part_trans
				
				self.aggregated_parts.append(first_part_trans)
				self.aggregated_parts.append(next_part_trans)
				
				first_part_trans.children.append(next_part_trans)
			
			else:
				aggr_rule = rule.split(">")[0]
				rule_parts = aggr_rule.split("_")
				part1_id = str(rule_parts[0].split("|")[0])
				conn1 = int(rule_parts[0].split("|")[1])
				part2 = str(rule_parts[1].split("|")[0])
				conn2 = int(rule_parts[1].split("|")[1])
				
				rule_ids = rule.split(">")[1].split("_")
				
				first_part = None
				for part in self.aggregated_parts:
					if part.id == part1_id:
						first_part = part
						break
				if first_part is not None:
					first_part.id = rule_ids[0]
					next_part = self.parts[part2]
					
					orientTransform = rg.Transform.PlaneToPlane(next_part.connections[conn2].flip_pln, first_part.connections[conn1].pln)
					next_part_trans = next_part.transform(orientTransform)
					next_part_trans.id = rule_ids[1]
					## parent-child tracking
					first_part.children.append(next_part_trans.id)
					next_part_trans.parent = first_part.id
					self.aggregated_parts.append(next_part_trans)
				else:
					pass ## implement error handling
	
	
	## stochastic aggregation
	def aggregate_rnd(self, num, use_catalog = False):
		added = 0
		loops = 0
		while added < num:
			loops += 1
			if loops > num*100:
				break
			## if no part is present in the aggregation, add first random part
			if len(self.aggregated_parts) == 0:
				
				first_part = None
				if use_catalog:
					first_part = self.parts[self.catalog.return_weighted_part()]
				else:
					first_part = self.parts[random.choice(self.parts.keys())]
				
				if first_part is not None:
					first_part_trans = first_part.transform(rg.Transform.Identity)
					for conn in first_part_trans.connections:
						conn.generate_rules_table(self.rules)
					first_part_trans.id = 0
					self.aggregated_parts.append(first_part_trans)
					added += 1
					if use_catalog:
						self.catalog.update(first_part_trans.name, -1)
				
				
			## otherwise add new random part
			else:
				next_rule = None
				part_01_id = -1
				conn_01_id = -1
				next_rule_id = -1
				new_rule_attempts = 0
				
				while new_rule_attempts < 1000:
					new_rule_attempts += 1
					next_rule = None
					if use_catalog:
						if self.catalog.is_empty:
							break
						next_part = self.parts[self.catalog.return_weighted_part()]
						if next_part is not None:
							part_01_id = random.randint(0,len(self.aggregated_parts)-1)
							part_01 = self.aggregated_parts[part_01_id]
							if len(part_01.active_connections) > 0:
								conn_01_id = part_01.active_connections[random.randint(0, len(part_01.active_connections)-1)]
								conn_01 = part_01.connections[conn_01_id]
								if len(conn_01.active_rules) > 0:
									next_rule_id = conn_01.active_rules[random.randint(0, len(conn_01.active_rules)-1)]
									next_rule = conn_01.rules_table[next_rule_id]
									if next_rule.part2 == next_part.name:
										break
					else:
						part_01_id = random.randint(0,len(self.aggregated_parts)-1)
						part_01 = self.aggregated_parts[part_01_id]
						if len(part_01.active_connections) > 0:
							conn_01_id = part_01.active_connections[random.randint(0, len(part_01.active_connections)-1)]
							conn_01 = part_01.connections[conn_01_id]
							if len(conn_01.active_rules) > 0:
								next_rule_id = conn_01.active_rules[random.randint(0, len(conn_01.active_rules)-1)]
								next_rule = conn_01.rules_table[next_rule_id]
								break
				
				if next_rule is not None:
					next_part = self.parts[next_rule.part2]
					orientTransform = rg.Transform.PlaneToPlane(next_part.connections[next_rule.conn2].flip_pln, conn_01.pln)
					
					## boolean checks for all constraints
					coll_check = False
					add_coll_check = False
					valid_connections = []
					missing_sup_check = False
					global_const_check = False
					
					## collision check
					self.possible_collisions = []
					coll_check = self.collision_check(next_part, orientTransform)
					
					## constraints check
					if self.mode == 1: ## only local constraints mode
						if coll_check == False and next_part.is_constrained:
							add_coll_check = self.additional_collider_check(next_part, orientTransform)
							
							if add_coll_check == False:
							   missing_sup_check = self.missing_supports_check(next_part, orientTransform)
					
					elif self.mode == 2: ## onyl global constraints mode
						if coll_check == False and len(self.global_constraints) > 0:
							global_const_check = self.global_constraints_check(next_part, orientTransform)
					
					elif self.mode == 3: ## local+global constraints mode
						if coll_check == False:
							if len(self.global_constraints) > 0:
								global_const_check = self.global_constraints_check(next_part, orientTransform)
							if global_const_check == False and next_part.is_constrained:
								add_coll_check = self.additional_collider_check(next_part, orientTransform)
								if add_coll_check == False:
								   missing_sup_check = self.missing_supports_check(next_part, orientTransform)
					
					
					if coll_check == False and add_coll_check == False and missing_sup_check == False and global_const_check == False:
						next_part_trans = next_part.transform(orientTransform)
						next_part_trans.reset_part(self.rules)
						for i in range(len(next_part_trans.active_connections)):
							if next_part_trans.active_connections[i] == next_rule.conn2:
								next_part_trans.active_connections.pop(i)
								break
						next_part_trans.id = len(self.aggregated_parts)
						
						## parent-child tracking
						self.aggregated_parts[part_01_id].children.append(next_part_trans.id)
						next_part_trans.parent = self.aggregated_parts[part_01_id].id
						self.aggregated_parts.append(next_part_trans)
						
						if use_catalog:
							self.catalog.update(next_part_trans.name, -1)
						
						for i in range(len(self.aggregated_parts[part_01_id].active_connections)):
							if self.aggregated_parts[part_01_id].active_connections[i] == conn_01_id:
								self.aggregated_parts[part_01_id].active_connections.pop(i)
								break
						added += 1
					## TO FIX --> do not remove rules when only caused by missing supports
					else:
						## remove rules if they cause collisions or overlappings
						for i in range(len(self.aggregated_parts[part_01_id].connections[conn_01_id].active_rules)):
							if self.aggregated_parts[part_01_id].connections[conn_01_id].active_rules[i] == next_rule_id:
								self.aggregated_parts[part_01_id].connections[conn_01_id].active_rules.pop(i)
								break
						## check if the connection is still active (still active rules available)
						if len(self.aggregated_parts[part_01_id].connections[conn_01_id].active_rules) == 0:
							for i in range(len(self.aggregated_parts[part_01_id].active_connections)):
								if self.aggregated_parts[part_01_id].active_connections[i] == conn_01_id:
									self.aggregated_parts[part_01_id].active_connections.pop(i)
									break
				else:
					## if no part is available, exit the aggregation routine and return an error message
					msg = "Could not place " + str(num-added) + " parts"
					return msg
	
	## stochastic aggregation with catalog
	def aggregate_rnd_catalog(self, catalog, num = None):
		added = 0
		loops = 0
		
		if num is None:
			num = catalog.parts_total
		
		while added < num:
			loops += 1
			if loops > num*100:
				break
			## if no part is present in the aggregation, add first random part
			if len(self.aggregated_parts) == 0:
				first_part = self.parts[catalog.return_weighted_part()]
				first_part_trans = first_part.transform(rg.Transform.Identity)
				for conn in first_part_trans.connections:
					conn.generate_rules_table(self.rules)
				first_part_trans.id = 0
				self.aggregated_parts.append(first_part_trans)
				catalog.update(first_part.name, -1)
				added += 1
			## otherwise add new random part
			else:
				next_rule = None
				part_01_id = -1
				conn_01_id = -1
				next_rule_id = -1
				new_rule_attempts = 0
				
				while new_rule_attempts < 10000:
					new_rule_attempts += 1
					
					selected_part = catalog.return_weighted_part()
					
					if selected_part is None or catalog.is_empty == True:
						break
					
					if len(part_01.active_connections) > 0:
						conn_01_id = part_01.active_connections[random.randint(0, len(part_01.active_connections)-1)]
						conn_01 = part_01.connections[conn_01_id]
						if len(conn_01.active_rules) > 0:
							next_rule_id = conn_01.active_rules[random.randint(0, len(conn_01.active_rules)-1)]
							if conn_01.rules_table[next_rule_id].part2 == selected_part:
								next_rule = conn_01.rules_table[next_rule_id]
								break
				
				if next_rule is not None:
					next_part = self.parts[next_rule.part2]
					orientTransform = rg.Transform.PlaneToPlane(next_part.connections[next_rule.conn2].flip_pln, conn_01.pln)
					
					## boolean checks for all constraints
					coll_check = False
					add_coll_check = False
					valid_connections = []
					missing_sup_check = False
					global_const_check = False
					
					## collision check
					self.possible_collisions = []
					coll_check = self.collision_check(next_part, orientTransform)
					
					## constraints check
					if self.mode == 1: ## only local constraints mode
						if coll_check == False and next_part.is_constrained:
							add_coll_check = self.additional_collider_check(next_part, orientTransform)
							
							if add_coll_check == False:
							   missing_sup_check = self.missing_supports_check(next_part, orientTransform)
					
					elif self.mode == 2: ## onyl global constraints mode
						if coll_check == False and len(self.global_constraints) > 0:
							global_const_check = self.global_constraints_check(next_part, orientTransform)
					
					elif self.mode == 3: ## local+global constraints mode
						if coll_check == False:
							if len(self.global_constraints) > 0:
								global_const_check = self.global_constraints_check(next_part, orientTransform)
							if global_const_check == False and next_part.is_constrained:
								add_coll_check = self.additional_collider_check(next_part, orientTransform)
								if add_coll_check == False:
								   missing_sup_check = self.missing_supports_check(next_part, orientTransform)
					
					
					if coll_check == False and add_coll_check == False and missing_sup_check == False and global_const_check == False:
						next_part_trans = next_part.transform(orientTransform)
						next_part_trans.reset_part(self.rules)
						for i in range(len(next_part_trans.active_connections)):
							if next_part_trans.active_connections[i] == next_rule.conn2:
								next_part_trans.active_connections.pop(i)
								break
						next_part_trans.id = len(self.aggregated_parts)
						
						## parent-child tracking
						self.aggregated_parts[part_01_id].children.append(next_part_trans.id)
						next_part_trans.parent = self.aggregated_parts[part_01_id].id
						self.aggregated_parts.append(next_part_trans)
						
						catalog.update(next_part_trans.name, -1)
						
						for i in range(len(self.aggregated_parts[part_01_id].active_connections)):
							if self.aggregated_parts[part_01_id].active_connections[i] == conn_01_id:
								self.aggregated_parts[part_01_id].active_connections.pop(i)
								break
						added += 1
					## TO FIX --> do not remove rules when only caused by missing supports
					else:
						## remove rules if they cause collisions or overlappings
						for i in range(len(self.aggregated_parts[part_01_id].connections[conn_01_id].active_rules)):
							if self.aggregated_parts[part_01_id].connections[conn_01_id].active_rules[i] == next_rule_id:
								self.aggregated_parts[part_01_id].connections[conn_01_id].active_rules.pop(i)
								break
						## check if the connection is still active (still active rules available)
						if len(self.aggregated_parts[part_01_id].connections[conn_01_id].active_rules) == 0:
							for i in range(len(self.aggregated_parts[part_01_id].active_connections)):
								if self.aggregated_parts[part_01_id].active_connections[i] == conn_01_id:
									self.aggregated_parts[part_01_id].active_connections.pop(i)
									break
				else:
					## if no part is available, exit the aggregation routine and return an error message
					msg = "Could not place " + str(num-added) + " parts"
					return msg
	
	
	## compute all possibilities for child-parts of the given part, and store them in the aggregation queue
	def compute_next_w_field(self, part):
		
		for i in xrange(len(part.active_connections)-1, -1, -1):
			conn_id = part.active_connections[i]
			conn = part.connections[conn_id]
			for i2 in xrange(len(conn.active_rules)-1, -1, -1):
				rule_id = conn.active_rules[i2]
				rule = conn.rules_table[rule_id]
				
				next_part = self.parts[rule.part2]
				
				next_center = rg.Point3d(next_part.center)
				orientTransform = rg.Transform.PlaneToPlane(next_part.connections[rule.conn2].flip_pln, conn.pln)
				next_center.Transform(orientTransform)
				
				if self.multiple_fields:
					f_name = next_part.field
					if self.field[f_name].bbox.Contains(next_center) == True:
						field_val = self.field[f_name].return_pt_val(next_center)
						
						queue_index = bisect.bisect_left(self.queue_values, field_val)
						queue_entry = (next_part.name, part.id, orientTransform)
						
						self.queue_values.insert(queue_index, field_val)
						self.aggregation_queue.insert(queue_index, queue_entry)
						self.queue_count += 1
					
				else:
					if self.field.bbox.Contains(next_center) == True:
						field_val = self.field.return_pt_val(next_center)
						
						queue_index = bisect.bisect_left(self.queue_values, field_val)
						queue_entry = (next_part.name, part.id, orientTransform)
						
						self.queue_values.insert(queue_index, field_val)
						self.aggregation_queue.insert(queue_index, queue_entry)
						self.queue_count += 1
	
	
	## field-driven aggregation
	def aggregate_field(self, num):
		
		added = 0
		loops = 0
		while added < num:
			## avoid endless loops
			loops += 1
			if loops > num*100:
				break
			
			## if no part is present in the aggregation, add first random part
			if len(self.aggregated_parts) == 0 and self.prev_num == 0:
				first_part = self.parts[random.choice(self.parts.keys())]
				start_point = None
				if self.multiple_fields:
					f_name = first_part.field
					if (self.mode == 2 or self.mode == 3) and len(self.global_constraints) > 0:
						start_point = self.field[f_name].return_highest_pt(constraints=self.global_constraints)
					else:
					   start_point = self.field[f_name].return_highest_pt()
				else:
					if (self.mode == 2 or self.mode == 3) and len(self.global_constraints) > 0:
						start_point = self.field.return_highest_pt(constraints=self.global_constraints)
					else:
					   start_point = self.field.return_highest_pt()
				
				mov_vec = rg.Vector3d.Subtract(rg.Vector3d(start_point), rg.Vector3d(first_part.center))
				move_transform = rg.Transform.Translation(mov_vec.X, mov_vec.Y, mov_vec.Z)
				first_part_trans = first_part.transform(move_transform)
				
				for conn in first_part_trans.connections:
					conn.generate_rules_table(self.rules)
				
				first_part_trans.id = 0
				self.aggregated_parts.append(first_part_trans)
				
				## compute all possible next parts and append to list
				self.compute_next_w_field(first_part_trans)
				added += 1
			
			else:
				## if no part is available, exit the aggregation routine and return an error message
				if self.queue_count == 0:
					msg = "Could not place " + str(num-added) + " parts"
					return msg
				
				next_data = self.aggregation_queue[self.queue_count-1]
				next_part = self.parts[next_data[0]]
				next_center = rg.Point3d(next_part.center)
				orientTransform = next_data[2]
				
				## boolean checks for all constraints
				coll_check = False
				add_coll_check = False
				missing_sup_check = False
				global_const_check = False
				
				## collision check
				self.possible_collisions = []
				coll_check = self.collision_check(next_part, orientTransform)
				
				## constraints check
				if self.mode == 1: ## only local constraints mode
					if coll_check == False and next_part.is_constrained:
						add_coll_check = self.additional_collider_check(next_part, orientTransform)
						if add_coll_check == False:
						   missing_sup_check = self.missing_supports_check(next_part, orientTransform)
				
				elif self.mode == 2: ## onyl global constraints mode
					if coll_check == False and len(self.global_constraints) > 0:
						global_const_check = self.global_constraints_check(next_part, orientTransform)
				
				elif self.mode == 3: ## local+global constraints mode
					if coll_check == False:
						if len(self.global_constraints) > 0:
							global_const_check = self.global_constraints_check(next_part, orientTransform)
						if global_const_check == False and next_part.is_constrained:
							add_coll_check = self.additional_collider_check(next_part, orientTransform)
							if add_coll_check == False:
							   missing_sup_check = self.missing_supports_check(next_part, orientTransform)
				
				
				if coll_check == False and add_coll_check == False and missing_sup_check == False and global_const_check == False:
					next_part_trans = next_part.transform(orientTransform)
					next_part_trans.reset_part(self.rules)
					
					for conn in next_part_trans.connections:
						conn.generate_rules_table(self.rules)
					
					next_part_trans.id = len(self.aggregated_parts)
					self.aggregated_parts[next_data[1]].children.append(next_part_trans.id)
					next_part_trans.parent = self.aggregated_parts[next_data[1]].id
					self.aggregated_parts.append(next_part_trans)
					
					## compute all possible next parts and append to list
					self.compute_next_w_field(next_part_trans)
					added += 1
				
				self.aggregation_queue.pop()
				self.queue_values.pop()
				self.queue_count -=1


#################################################################### Plane Constraint ####################################################################
class Plane_Constraint(object):
	
	## constructor
	def __init__(self, _plane, _positive = True, _soft = True):
		self.type = 'plane'
		self.plane = _plane
		self.positive = _positive
		self.soft = _soft
	
	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspPlaneConst [+: %s, soft: %s]" % (self.positive, self.soft)
	
	## constraint check method
	def check(self, pt = None, collider = None):
		if self.soft:
			return self.check_soft(pt)
		else:
			return self.check_hard(pt, collider)
	
	## hard constraint check method
	def check_hard(self, pt, collider):
		if self.check_soft(pt):
			for geo in collider.geometry:
				if rg.Intersect.Intersection.MeshPlane(geo, self.plane) is not None:
					return False
			return True
		else:
			return False
	
	## soft constraint check method
	def check_soft(self, pt):
		mapped_pt = self.plane.RemapToPlaneSpace(pt)[1]
		if self.positive:
			if mapped_pt.Z > 0:
				return True
		else:
			if mapped_pt.Z < 0:
				return True
		return False

#################################################################### Mesh Constraint ####################################################################
class Mesh_Constraint(object):
	
	## constructor
	def __init__(self, _geo, _inside = True, _soft = True):
		self.type = 'mesh_collider'
		self.geo = _geo
		self.inside = _inside
		self.soft = _soft
	
	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspMeshConst [in: %s, soft: %s]" % (self.inside, self.soft)
	
	## constraint check method
	def check(self, pt = None, collider = None):
		if self.soft:
			return self.check_soft(pt)
		else:
			return self.check_hard(pt, collider)
	
	## hard constraint check method
	def check_hard(self, pt, collider):
		if self.check_soft(pt):
			for geo in collider.geometry:
				if len(rg.Intersect.Intersection.MeshMeshFast(self.geo, geo)) > 0:
					return False
			return True
		else:
			return False
	
	## soft constraint check method
	def check_soft(self, pt):
		is_inside = self.geo.IsPointInside(pt, global_tolerance, False)
		if self.inside:
			if is_inside:
				return True
		else:
			if not is_inside:
				return True
		return False

#########################################################################
##								   WIP								   ##
#########################################################################


#################################################################### Collider ####################################################################
class Collider(object):
	
	## constructor
	def __init__(self, _geo, _multiple=False, _check_all = False, _connections=[], _valid_connections = []):
		self.geometry = _geo
		self.multiple = _multiple
		self.check_all = _check_all
		self.connections = _connections
		
		self.valid_connections = _valid_connections
		
		self.set_connections = False
		if len(self.connections) == len(self.geometry) and self.multiple == True:
			self.set_connections = True
	
	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspCollider"
	
	## return a transformed copy of the collider
	########################################################################### check if valid connections need to be transformed or re-generated!!!
	def transform(self, trans, transform_connections = False, maintain_valid = False):
		geometry_trans = []
		for geo in self.geometry:
			geo_trans = geo.Duplicate()
			geo_trans.Transform(trans)
			geometry_trans.append(geo_trans)
		
		connections_trans = []
		if transform_connections:
			for conn in self.connections:
				connections_trans.append(conn.transform(trans))
		
		if maintain_valid:
			valid_connection_trans = list(self.valid_connections)
			coll_trans = Collider(geometry_trans, _multiple=self.multiple, _check_all=self.check_all, _connections=connections_trans, _valid_connections=valid_connection_trans)
		else:
			coll_trans = Collider(geometry_trans, _multiple=self.multiple, _check_all=self.check_all, _connections=connections_trans)
		
		return coll_trans
	
	## return a copy of the collider
	def copy(self):
		geometry_copy = []
		for geo in self.geometry:
			geo_copy = geo.Duplicate()
			geometry_copy.append(geo_copy)
		
		connections_copy = []
		for conn in self.connections:
			connections_copy.append(conn.copy())
		
		valid_connection_copy = list(self.valid_connections)
		coll_copy = Collider(geometry_copy, _multiple=self.multiple, _check_all=self.check_all, _connections=connections_copy, _valid_connections=valid_connection_copy)
		
		return coll_copy
	
	## check collisions between collider and given part
	def check_collisions_w_parts(self, parts):
		## multiple collider with associated connections
		if self.multiple:
			valid_colliders = []
			self.valid_connections = []
			count = 0
			for geo in self.geometry:
				valid_coll = True
				for part in parts:
					for other_geo in part.collider.geometry:
						if len(rg.Intersect.Intersection.MeshMeshFast(geo, other_geo)) > 0:
							valid_coll = False
							break
					if valid_coll == False:
						break
				valid_colliders.append(valid_coll)
				if self.set_connections and valid_coll:
					self.valid_connections.append(count)
				if valid_coll and self.check_all == False:
					break
				count+=1
			
			if True in valid_colliders:
				return False
			return True
		
		## simple collider
		else:
			for geo in self.geometry:
				for part in parts:
					for other_geo in part.collider.geometry:
						if len(rg.Intersect.Intersection.MeshMeshFast(geo, other_geo)) > 0:
							return True
			return False
	
	## check collisions between collider and given ids in the given parts list
	def check_collisions_by_id(self, parts, ids):
		## multiple collider with associated connections
		if self.multiple:
			valid_colliders = []
			count = 0
			
			for geo in self.geometry:
				valid_coll = True
				for id in ids:
					for other_geo in parts[id].collider.geometry:
						if len(rg.Intersect.Intersection.MeshMeshFast(geo, other_geo)) > 0:
							valid_coll = False
							break
				valid_colliders.append(valid_coll)
				if valid_coll and self.check_all == False:
					break
				count+=1
			if True in valid_colliders:
				return False
			return True
		
		## simple collider
		else:
			for geo in self.geometry:
				for id in ids:
					for other_geo in parts[id].collider.geometry:
						if len(rg.Intersect.Intersection.MeshMeshFast(geo, other_geo)) > 0:
							return True
			return False

	## check intersection between collider and line (for supports check)
	def check_intersection_w_line(self, ln):
		for geo in self.geometry:
			if len(rg.Intersect.Intersection.MeshLine(geo, ln)[0]) > 0:
				return True
		return False

	#### WIP ####
	def check_global_constraints(self, constraint):
		return False


################################################################# Parts Catalog ##################################################################
class PartCatalog(object):
	##constructor
	def __init__(self, _parts, _amounts):
		
		self.parts = _parts
		self.amounts = _amounts
		
		self.dict = {}
		for i in xrange(len(self.parts)):
			self.dict[self.parts[i].name] = _amounts[i]
		
		self.is_empty = False
		self.parts_total = sum(self.dict.values())
	
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
		
	def update(self, part_name, difference):
		self.dict[part_name] += difference
		
		self.parts_total = sum(self.dict.values())
		if self.parts_total == 0:
			self.is_empty = True
	
	def copy(self):
		amounts = [self.dict[part.name] for part in self.parts]
		return PartCatalog(self.parts, amounts)



	
	
	