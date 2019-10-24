from Rhino.Geometry.Intersect import Intersection

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
						if len(Intersection.MeshMeshFast(geo, other_geo)) > 0:
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
						if len(Intersection.MeshMeshFast(geo, other_geo)) > 0:
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
						if len(Intersection.MeshMeshFast(geo, other_geo)) > 0:
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
						if len(Intersection.MeshMeshFast(geo, other_geo)) > 0:
							return True
			return False

	## check intersection between collider and line (for supports check)
	def check_intersection_w_line(self, ln):
		for geo in self.geometry:
			if len(Intersection.MeshLine(geo, ln)[0]) > 0:
				return True
		return False

	#### WIP ####
	def check_global_constraints(self, constraint):
		return False