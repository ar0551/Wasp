"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.4.001

Classes and utilities for voxel fields generation
"""


import math

from Rhino.Geometry import BoundingBox
from Rhino.Geometry import Vector3d
from Rhino.Geometry import Point3d

from wasp import global_tolerance


#################################################################### Field ####################################################################
class Field(object):
	
	## constructor
	def __init__(self, name, boundaries, pts, count_vec, resolution, values = []):
		
		self.name = name
		self.resolution = resolution
		
		self.boundaries = boundaries
		self.pts = pts
		self.bbox = BoundingBox(pts)
		
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
									self.vals[z][y].append(Vector3d(0,0,0))
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