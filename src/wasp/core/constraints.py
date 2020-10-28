"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.4.006

Constraints classes
"""

from Rhino.Geometry.Intersect import Intersection
from Rhino.Geometry import Point3d, Line

from wasp import global_tolerance
from wasp.utilities import plane_from_data, plane_to_data, mesh_from_data, mesh_to_data

#################################################################### Plane Constraint ####################################################################
class Plane_Constraint(object):
	
	## constructor
	def __init__(self, _plane, _positive = True, _soft = True, _required = True):
		self.type = 'plane'
		self.plane = _plane
		self.positive = _positive
		self.soft = _soft
		self.required = _required
	

	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspPlaneConst [+: %s, soft: %s, required: %s]" % (self.positive, self.soft, self.required)
	

	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		return cls(plane_from_data(data['plane']), _positive=data['positive'], _soft=data['soft'], _required=data['required'])

		
	## return the data dictionary representing the constraint
	def to_data(self):
		data = {}
		data['type'] = self.type
		data['plane'] = plane_to_data(self.plane)
		data['positive'] = self.positive
		data['soft'] = self.soft
		data['required'] = self.required
		return data	
	
	
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
				if Intersection.MeshPlane(geo, self.plane) is not None:
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
	def __init__(self, _geo, _inside = True, _soft = True, _required = True):
		self.type = 'mesh_collider'
		self.geo = _geo
		self.inside = _inside
		self.soft = _soft
		self.required = _required
	

	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspMeshConst [in: %s, soft: %s, required: %s]" % (self.inside, self.soft, self.required)
	
	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		return cls(mesh_from_data(data['geometry']), inside=data['inside'], _soft=data['soft'], _required=data['required'])

		
	## return the data dictionary representing the constraint
	def to_data(self):
		data = {}
		data['type'] = self.type
		data['geometry'] = mesh_to_data(self.geo)
		data['inside'] = self.inside
		data['soft'] = self.soft
		data['required'] = self.required
		return data	


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
				if len(Intersection.MeshMeshFast(self.geo, geo)) > 0:
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


#################################################################### Adjacency Constraint ####################################################################
class Adjacency_Constraint(object):

	## constructor
	def __init__(self, _dir, _is_adjacency, _names = []):
		self.directions = _dir
		self.is_adjacency = _is_adjacency

		self.names = _names
		self.name_independent = False
		if len(self.names) == 0:
			self.name_independent = True
	

	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspAdjacencyConst [size: %s, type: %s]" % (len(self.directions), "Adjacency" if self.is_adjacency else "Exclusion")
	

	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		d_directions = []
		for d_data in data['directions']:
			d = Line(d_data['start'][0], d_data['start'][1], d_data['start'][2], d_data['end'][0], d_data['end'][1], d_data['end'][2])
			d_directions.append(d)
		return cls(d_directions, data['is_adjacency'], _names=data['names'])

		
	## return the data dictionary representing the constraint
	def to_data(self):
		data = {}
		data['directions'] = []
		for d in self.directions:
			d_data = {}
			d_data['start'] = [d.FromX, d.FromY, d.FromZ]
			d_data['end'] = [d.ToX, d.ToY, d.ToZ]
			data['directions'].append(d_data)
		data['is_adjacency'] = self.is_adjacency
		data['names'] = self.names
		return data	

	## return a transformed copy of the support
	def transform(self, trans):
		directions_trans = []
		for d in self.directions:
			d = d.ToNurbsCurve()
			start_trans = d.PointAtStart
			end_trans = d.PointAtEnd
			start_trans.Transform(trans)
			end_trans.Transform(trans)
			d_trans = Line(start_trans, end_trans)
			directions_trans.append(d_trans)
		adj_constraint_trans = Adjacency_Constraint(directions_trans, self.is_adjacency, self.names)
		return adj_constraint_trans
	

	## return a copy of the support
	def copy(self):
		directions_copy = []
		for d in self.directions:
			d = d.ToNurbsCurve()
			start_copy = d.PointAtStart
			end_copy = d.PointAtEnd
			d_copy = Line(start_copy, end_copy)
			directions_copy.append(d_copy)
		adj_constraint_copy = Adjacency_Constraint(directions_copy, self.is_adjacency, self.names)
		return adj_constraint_copy
	

	## check against a list of parts
	def check(self, parts, possible_ids):
		## check adjacencies
		if self.is_adjacency:
			required_adjacencies = len(self.directions)
			for i in range(len(self.directions)):
				for id in possible_ids:
					if self.name_independent:
						if parts[id].collider.check_intersection_w_line(self.directions[i]):
							required_adjacencies -= 1
							break
					else:
						if parts[id].name == self.names[i]:
							if parts[id].collider.check_intersection_w_line(self.directions[i]):
								required_adjacencies -= 1
								break
			
			if required_adjacencies == 0:
				return True
		
		## check exclusions
		else:
			for i in range(len(self.directions)):
				for id in possible_ids:
					if self.name_independent:
						if parts[id].collider.check_intersection_w_line(self.directions[i]):
							return False
					else:
						if parts[id].name == self.names[i]:
							if parts[id].collider.check_intersection_w_line(self.directions[i]):
								return False
			return True

		return False