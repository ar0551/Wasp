"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.4.001

Constraints classes
"""

from Rhino.Geometry.Intersect import Intersection
from wasp import global_tolerance

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