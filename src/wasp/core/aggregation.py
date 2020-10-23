"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.4.005

Aggregation class and functions
"""

import random
import bisect
import time

from Rhino.Geometry import Transform
from Rhino.Geometry import Point3d
from Rhino.Geometry import Vector3d

from wasp import global_tolerance


#################################################################### Aggregation ####################################################################
class Aggregation(object):
	

	## class constructor
	def __init__(self, _name, _parts, _rules, _mode, _prev = [], _coll_check = True, _field = [], _global_constraints = [], _rnd_seed = None, _catalog = None):
		
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
		
		## random seed
		if _rnd_seed is None:
			random.seed(int(time.time()))
		else:
			random.seed(_rnd_seed)
		
		## parts catalog
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
		## if using and limited, update the catalog by adding back the removed parts
		if self.catalog is not None:
			if self.catalog.is_limited:
				self.removed_parts = self.aggregated_parts[num:]
				for p in self.removed_parts:
					self.catalog.update(p.name, 1)

		## trim the list to the desired length
		self.aggregated_parts = self.aggregated_parts[:num]

		## reset the remaining parts (reactivate all connections, who might have been blocked by removed parts)
		for part in self.aggregated_parts:
			part.reset_part(self.rules)
		
		## if using a field, recompute the whole aggregation queue
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
				orientTransform = Transform.PlaneToPlane(next_part.connections[rule.conn2].flip_pln, current_conn.pln)
				
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
	## function grouping all collsion and constraints checks
	def check_all_constraints(self, part, trans):
		
		## boolean checks for all constraints
		coll_check = False
		add_coll_check = False
		missing_sup_check = False
		adjacencies_check = False
		global_const_check = False

		## variables to store already computed colliders
		part_center_trans = None
		part_collider_trans = None

		## check overlaps/collisions with previously placed parts
		coll_check, part_center_trans, part_collider_trans = self.collision_check(part, trans)

		if coll_check == False:
			## check constraints
			## only local constraints mode
			if self.mode == 1:
				if part.is_constrained:
					add_coll_check = self.additional_collider_check(part, trans)
					
					if add_coll_check == False:
						missing_sup_check = self.missing_supports_check(part, trans)

						if missing_sup_check == False:
							adjacencies_check = self.adjacencies_check(part, trans)

			
			## onyl global constraints mode
			elif self.mode == 2:
				if len(self.global_constraints) > 0:
					global_const_check = self.global_constraints_check(part, trans, part_center_trans, part_collider_trans)
			
			## local+global constraints mode
			elif self.mode == 3:
				if len(self.global_constraints) > 0:
					global_const_check = self.global_constraints_check(part, trans, part_center_trans, part_collider_trans)
				if global_const_check == False and part.is_constrained:
					add_coll_check = self.additional_collider_check(part, trans)
					if add_coll_check == False:
						missing_sup_check = self.missing_supports_check(part, trans)
						if missing_sup_check == False:
							adjacencies_check = self.adjacencies_check(part, trans)

		## combine all constraints check result
		global_check = coll_check or add_coll_check or missing_sup_check or global_const_check or adjacencies_check

		return global_check, coll_check, add_coll_check, missing_sup_check, global_const_check

	
	## overlap // part-part collision check
	def collision_check(self, part, trans, part_center=None, part_collider=None):

		self.possible_collisions = []
		if part_center is None:
			part_center = part.transform_center(trans)
		
		## overlap check
		coll_count = 0
		for ex_part in self.aggregated_parts:
			dist = ex_part.center.DistanceTo(part_center)
			if dist < global_tolerance:
				return True, None, None
			elif dist < ex_part.dim + part.dim:
				self.possible_collisions.append(coll_count)
			coll_count += 1
		
		## collision check
		if self.coll_check == True:
			if part_collider is None:
				part_collider = part.transform_collider(trans)
			if part_collider.check_collisions_by_id(self.aggregated_parts, self.possible_collisions):
				return True, None, None
		return False, part_center, part_collider
	
	
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
	

	## adjacencies/exclusions check
	def adjacencies_check(self, part, trans):
		if len(part.adjacency_const) > 0:
			for aec in part.adjacency_const:
				aec_trans = aec.transform(trans)
				if not aec_trans.check(self.aggregated_parts, self.possible_collisions):
					return True
			return False
		else:
			return False
	

	## global constraints check
	def global_constraints_check(self, part, trans, part_center=None, part_collider=None):
		valid_constraints = len(self.global_constraints)
		for constraint in self.global_constraints:
			if part_center is None:
				part_center = part.transform_center(trans)
			if constraint.soft:
				if constraint.check(pt = part_center) == False:
					if constraint.required:
						return True
					else:
						valid_constraints -= 1
			else:
				if part_collider is None:
					part_collider = part.transform_collider(trans)
				if constraint.check(pt = part_center, collider = part_collider) == False:
					if constraint.required:
						return True
					else:
						valid_constraints -= 1
		
		if valid_constraints == 0:
			return True
		
		return False
	
	
	## check all connections for validity against the give constraints
	def check_all_connections(self):
		for part in self.aggregated_parts:
			if len(part.active_connections) > 0:
				for conn_id in part.active_connections:
					conn = part.connections[conn_id]
					if len(conn.active_rules) > 0:
						for rule_id in conn.active_rules:
							next_rule = conn.rules_table[rule_id]

							next_part = self.parts[next_rule.part2]
							orientTransform = Transform.PlaneToPlane(next_part.connections[next_rule.conn2].flip_pln, conn.pln)
							_, coll_check, _, _, _ = self.check_all_constraints(next_part, orientTransform)
							if coll_check:
								conn.active_rules.remove(rule_id)
								if len(conn.active_rules) == 0: 
									part.active_connections.remove(conn_id)
	
	
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
				first_part_trans = first_part.transform(Transform.Identity)
				first_part_trans.id = rule_ids[0]
				
				next_part = self.parts[part2]
				
				orientTransform = Transform.PlaneToPlane(next_part.connections[conn2].flip_pln, first_part.connections[conn1].pln)
				
				next_part_trans = next_part.transform(orientTransform)
				next_part_trans.id = rule_ids[1]
				
				## check additional collider (for fabrication constraints)
				## self.additional_collider_check(next_part, orientTransform)
				
				## parent-child tracking
				first_part_trans.children.append(next_part_trans)
				next_part_trans.parent = first_part_trans
				
				self.aggregated_parts.append(first_part_trans)
				self.aggregated_parts.append(next_part_trans)
				
				first_part_trans.children.append(next_part_trans)
			
			elif len(self.aggregated_parts) < len(graph_rules) + 1:
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
					
					orientTransform = Transform.PlaneToPlane(next_part.connections[conn2].flip_pln, first_part.connections[conn1].pln)
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
				
				## choose first part
				first_part = None
				if use_catalog:
					first_part = self.parts[self.catalog.return_weighted_part()]
				else:
					first_part = self.parts[random.choice(self.parts.keys())]		

				if first_part is not None:
					first_part_trans = first_part.transform(Transform.Identity)
					for conn in first_part_trans.connections:
						conn.generate_rules_table(self.rules)
					first_part_trans.id = 0
					self.aggregated_parts.append(first_part_trans)
					added += 1
					if use_catalog and self.catalog.is_limited:
						self.catalog.update(first_part_trans.name, -1)
			## otherwise add new random part
			else:
				next_rule = None
				part_01_id = -1
				conn_01_id = -1
				next_rule_id = -1
				new_rule_attempts = 0
				
				while new_rule_attempts < 10000:
					new_rule_attempts += 1
					next_rule = None
					if use_catalog:
						if self.catalog.is_limited and self.catalog.is_empty:
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
					orientTransform = Transform.PlaneToPlane(next_part.connections[next_rule.conn2].flip_pln, conn_01.pln)
					
					global_check, coll_check, add_coll_check, missing_sup_check, global_const_check = self.check_all_constraints(next_part, orientTransform)
					
					if not global_check:
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

						## update catalog if using one
						if use_catalog and self.catalog.is_limited:
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
	
	
	## compute all possibilities for child-parts of the given part, and store them in the aggregation queue
	def compute_next_w_field(self, part):
		
		for i in xrange(len(part.active_connections)-1, -1, -1):
			conn_id = part.active_connections[i]
			conn = part.connections[conn_id]
			for i2 in xrange(len(conn.active_rules)-1, -1, -1):
				rule_id = conn.active_rules[i2]
				rule = conn.rules_table[rule_id]
				
				next_part = self.parts[rule.part2]
				
				next_center = Point3d(next_part.center)
				orientTransform = Transform.PlaneToPlane(next_part.connections[rule.conn2].flip_pln, conn.pln)
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
				
				mov_vec = Vector3d.Subtract(Vector3d(start_point), Vector3d(first_part.center))
				move_transform = Transform.Translation(mov_vec.X, mov_vec.Y, mov_vec.Z)
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
				next_center = Point3d(next_part.center)
				orientTransform = next_data[2]
				
				global_check, coll_check, add_coll_check, missing_sup_check, global_const_check = self.check_all_constraints(next_part, orientTransform)
					
				if not global_check:
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
				
				## TO FIX --> do not remove rules when only caused by missing supports
				self.aggregation_queue.pop()
				self.queue_values.pop()
				self.queue_count -=1