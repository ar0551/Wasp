"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.5.008

Collider classes and utilities
"""

from Rhino.Geometry.Intersect import Intersection
from wasp import is_rh7
from wasp.core import Connection
from wasp.utilities import mesh_from_data, mesh_to_data


#################################################################### Collider ####################################################################
class Collider(object):
	
	## constructor
	def __init__(self, _geo, _multiple=False, _check_all = False, _connections=[], _valid_connections = []):
		self.geometry = _geo
		self.multiple = _multiple
		self.check_all = _check_all
		self.connections = _connections

		self.faces_count = 0
		for geo in self.geometry:
			self.faces_count += geo.Faces.Count
		
		self.valid_connections = _valid_connections
		
		self.set_connections = False
		if len(self.connections) == len(self.geometry) and self.multiple == True:
			self.set_connections = True
	
	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspCollider"
	

	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		c_geo = [mesh_from_data(m) for m in data['geometry']]
		c_multiple = data['multiple']
		c_check_all = data['check_all']
		c_connections = [Connection.from_data(c_data) for c_data in data['connections']]
		c_valid_connections = [int(vc) for vc in data['valid_connections']]
		return cls(c_geo, _multiple=c_multiple, _check_all=c_check_all, _connections=c_connections, _valid_connections=c_valid_connections)

		
	## return the data dictionary representing the collider
	def to_data(self):
		data = {}
		data['geometry'] = [mesh_to_data(m) for m in self.geometry]
		data['multiple'] = self.multiple
		data['check_all'] = self.check_all
		data['connections'] = [conn.to_data() for conn in self.connections]
		data['valid_connections'] = self.valid_connections
		return data


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
			if is_rh7:
				if len(Intersection.MeshLine(geo, ln)) > 0:
					return True
			else:
				if len(Intersection.MeshLine(geo, ln)[0]) > 0:
					return True
		return False
	

	#### WIP ####
	def check_global_constraints(self, constraint):
		return False