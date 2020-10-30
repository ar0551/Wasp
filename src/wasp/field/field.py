"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.4.006

Classes and utilities for voxel fields generation
"""


import math

from Rhino.Geometry import BoundingBox
from Rhino.Geometry import Vector3d
from Rhino.Geometry import Point3d
from Rhino.Geometry import Plane, Box
from Rhino.Geometry import Transform

from wasp import global_tolerance
from wasp.utilities import mesh_from_data, mesh_to_data


#################################################################### Field ####################################################################
class Field(object):
	
	## constructor
	def __init__(self, name, pts, count, resolution, values = [], boundaries = [], plane = None):
		
		self.name = name
		self.resolution = resolution
		
		self.pts = pts
		self.bbox = BoundingBox(pts)
		
		self.x_count = count[0]
		self.y_count = count[1]
		self.z_count = count[2]
		
		self.vals = []
		self.boundaries = boundaries
		self.plane = plane

		self.is_tensor_field = False

		if len(values) > 0:
			self.set_values(values, self.boundaries)
	

	@classmethod
	def from_boundaries(cls, _boundaries, _resolution, _plane = None):
		empty_field = None
		if _plane is None:
			global_bbox = None
			for geo in _boundaries:
				bbox = geo.GetBoundingBox(True)
				
				if global_bbox is None:
					global_bbox = bbox
				else:
					global_bbox.Union(bbox)
			
			x_size = global_bbox.Max.X - global_bbox.Min.X
			x_count = int(math.ceil(x_size / _resolution)) + 1
			y_size = global_bbox.Max.Y - global_bbox.Min.Y
			y_count = int(math.ceil(y_size / _resolution)) + 1
			z_size = global_bbox.Max.Z - global_bbox.Min.Z
			z_count = int(math.ceil(z_size / _resolution)) + 1
			
			count = [x_count, y_count, z_count]
			
			pts = []
			s_pt = global_bbox.Min
			
			for z in range(z_count):
				for y in range(y_count):
					for x in range(x_count):
						pt = Point3d(s_pt.X + x*_resolution, s_pt.Y + y*_resolution, s_pt.Z + z*_resolution)
						pts.append(pt)
			
			empty_field = cls(None, pts, count, _resolution, boundaries = _boundaries)

		else:
			global_bbox = None
			for geo in _boundaries:
				if global_bbox is None:
					global_bbox = Box(_plane, geo)
				else:
					new_box = Box(_plane, geo)
					for corner in new_box.GetCorners():
						global_bbox.Union(corner)
			
			x_size = global_bbox.X.Max - global_bbox.X.Min
			x_count = int(math.ceil(x_size / _resolution)) + 1
			y_size = global_bbox.Y.Max - global_bbox.Y.Min
			y_count = int(math.ceil(y_size / _resolution)) + 1
			z_size = global_bbox.Z.Max - global_bbox.Z.Min
			z_count = int(math.ceil(z_size / _resolution)) + 1
			
			count = [x_count, y_count, z_count]
			
			pts = []
			s_pt = global_bbox.PointAt(0,0,0)
			s_plane = Plane(s_pt, _plane.XAxis, _plane.YAxis)
			orient_transform = Transform.PlaneToPlane(Plane.WorldXY, s_plane)
			
			for z in range(z_count):
				for y in range(y_count):
					for x in range(x_count):
						pt = Point3d(x*_resolution, y*_resolution, z*_resolution)
						pt.Transform(orient_transform)
						pts.append(pt)
			
			empty_field = cls(None, pts, count, _resolution, boundaries = _boundaries, plane = _plane)
		
		return empty_field

	
	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspField [name: %s, res: %s, count: %s]" % (self.name, self.resolution, len(self.pts))
	
	
	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		## recreate empty field
		pts_in = []
		for pl in data["pts"]:
			pts_in.append(Point3d(pl[0], pl[1], pl[2]))
		
		boundaries_in = []
		for bl in data["boundaries"]:
			boundaries_in.append(mesh_from_data(bl))
		
		field = cls(data["name"], pts_in, data["count"], data["resolution"], boundaries = boundaries_in)

		## set values
		field.set_values(data["values"])

		return field
		
	## return the data dictionary representing the field
	def to_data(self):
		data = {}
		data["name"] = self.name
		data["pts"] = self.return_pts_list()
		data["count"] = self.return_count_vec()
		data["resolution"] = self.resolution
		data["values"] = self.return_values_list()
		data["boundaries"] = []
		for bou in self.boundaries:
			data["boundaries"].append(mesh_to_data(bou))
		return data			
	

	## return values as flattened list
	def return_values_list(self):
		values_list = []
		for z in range(0, self.z_count):
			for y in range(0, self.y_count):
				for x in range(0, self.x_count):
					values_list.append(self.vals[z][y][x])
		return values_list
	

	## return xyz counts vector
	def return_count_vec(self):
		return [self.x_count, self.y_count, self.z_count]
	

	## return points as python list of lists
	def return_pts_list(self):
		return [[pt.X, pt.Y, pt.Z] for pt in self.pts]
	

	## set values in an empty field
	def set_values(self, values, boundaries = []):
		try:
			v = values[0][2]
			self.is_tensor_field = True
		except:
			self.is_tensor_field = False
		
		pts_count = 0
		
		if len(values) > 0:
			for z in range(0, self.z_count):
				self.vals.append([])
				for y in range(0, self.y_count):
					self.vals[z].append([])
					for x in range(0, self.x_count):
						if len(boundaries) > 0:
							inside = False
							for bou in boundaries:
								if bou.IsPointInside(self.pts[pts_count], global_tolerance, True) == True:
									self.vals[z][y].append(values[pts_count])
									inside = True
									break
							if inside == False:
								if self.is_tensor_field:
									self.vals[z][y].append(Vector3d(0,0,0))
								else:
									self.vals[z][y].append(0.0)
						else:
							self.vals[z][y].append(values[pts_count])
						pts_count += 1

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
								pt = Point3d(x*self.resolution, y*self.resolution, z*self.resolution)
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
								pt = Point3d(x*self.resolution, y*self.resolution, z*self.resolution)
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
		
		highest_pt = Point3d(max_coords[0]*self.resolution, max_coords[1]*self.resolution, max_coords[2]*self.resolution)
		highest_pt = highest_pt + self.bbox.Min
		
		return highest_pt