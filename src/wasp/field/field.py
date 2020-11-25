"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.4.010

Classes and utilities for voxel fields generation
"""


import math

from Rhino.Geometry import BoundingBox
from Rhino.Geometry import Vector3d, Point3d
from Rhino.Geometry import Plane, Box
from Rhino.Geometry import Transform
from Rhino.Geometry import Mesh

from wasp import global_tolerance
from wasp.utilities import mesh_from_data, mesh_to_data, plane_from_data, plane_to_data


#################################################################### Field ####################################################################
class Field(object):
	
	## constructor
	def __init__(self, name, pts, count, resolution, plane = Plane.WorldXY, values = [], boundaries = []):
		
		self.name = name
		self.pts = pts
		self.resolution = resolution
		self.plane = plane
		
		self.bbox = Box(self.plane, self.pts)
		
		self.x_count = count[0]
		self.y_count = count[1]
		self.z_count = count[2]
		
		self.vals = []
		self.boundaries = boundaries
		
		self.is_tensor_field = False

		if len(values) > 0:
			self.set_values(values, self.boundaries)
	

	## generate plane from a list of boundaries
	@classmethod
	def from_boundaries(cls, _boundaries, _resolution, _plane = Plane.WorldXY):
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
		
		empty_field = cls(None, pts, count, _resolution, plane = s_plane, boundaries = _boundaries)
		
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
		
		field = cls(data["name"], pts_in, data["count"], data["resolution"], plane = plane_from_data(data['plane']), boundaries = boundaries_in)

		## set values
		field.set_values(data["values"])

		return field
		
	## return the data dictionary representing the field
	def to_data(self):
		data = {}
		data['name'] = self.name
		data['pts'] = self.return_pts_list()
		data['count'] = self.return_count_vec()
		data['resolution'] = self.resolution
		data['plane'] = plane_to_data(self.plane)
		data['values'] = self.return_values_list()
		data['boundaries'] = []
		for bou in self.boundaries:
			data['boundaries'].append(mesh_to_data(bou))
		return data			
	

	## return a transformed copy of the field
	def transform(self, trans):
		pts_trans = [Point3d(pt) for pt in self.pts]
		for pt in pts_trans:
			pt.Transform(trans)
		plane_trans = Plane(self.plane)
		plane_trans.Transform(trans)
		boundaries_trans = [b.Duplicate() for b in self.boundaries]
		for bt in boundaries_trans:
			bt.Transform(trans)
		
		field_trans = Field(self.name, pts_trans, self.return_count_vec(), self.resolution, plane=plane_trans, values=self.return_values_list(), boundaries = boundaries_trans)
		return field_trans
	

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
	def set_values(self, values, use_boundaries = False):
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
						if use_boundaries and len(self.boundaries) > 0:
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


	## return value associated to the closest point of the field to the given point
	def return_pt_val(self, pt):
		pt_trans = self.plane.RemapToPlaneSpace(pt)[1]
		
		x = int(math.floor(pt_trans.X/self.resolution))
		y = int(math.floor(pt_trans.Y/self.resolution))
		z = int(math.floor(pt_trans.Z/self.resolution))
		
		value = self.vals[z][y][x]
		return value


	## find and return highest value in the field ########################### TO FIX FOR ORIENTABLE FIELD!!!
	def return_highest_pt(self, constraints = None):
		max_val = -1
		max_coords = None
		max_count = -1
		count = 0
		highest_pt = None
		
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
								max_count = count
					count += 1

		highest_pt = Plane(self.pts[max_count], self.plane.XAxis, self.plane.YAxis)
		return highest_pt
	

	def compute_voxel_mesh(self, iso, cap = True):
		voxel_mesh = Mesh()
		for z in xrange(self.z_count):
			for y in xrange(self.y_count):
				for x in xrange(self.x_count):
					if self.vals[z][y][x] > iso:
						if x == 0:
							if cap:
								index = voxel_mesh.Vertices.Count
								voxel_mesh.Vertices.Add(x,y,z)
								voxel_mesh.Vertices.Add(x,y+1,z)
								voxel_mesh.Vertices.Add(x,y+1,z+1)
								voxel_mesh.Vertices.Add(x,y,z+1)
								voxel_mesh.Faces.AddFace(index + 2, index + 1, index + 0)
								voxel_mesh.Faces.AddFace(index + 3, index + 2, index + 0)
						elif self.vals[z][y][x-1] < iso:
							index = voxel_mesh.Vertices.Count
							voxel_mesh.Vertices.Add(x,y,z)
							voxel_mesh.Vertices.Add(x,y+1,z)
							voxel_mesh.Vertices.Add(x,y+1,z+1)
							voxel_mesh.Vertices.Add(x,y,z+1)
							voxel_mesh.Faces.AddFace(index + 2, index + 1, index + 0)
							voxel_mesh.Faces.AddFace(index + 3, index + 2, index + 0)
							
						if x == self.x_count-1:
							if cap:
								index = voxel_mesh.Vertices.Count
								voxel_mesh.Vertices.Add(x+1,y,z)
								voxel_mesh.Vertices.Add(x+1,y+1,z)
								voxel_mesh.Vertices.Add(x+1,y+1,z+1)
								voxel_mesh.Vertices.Add(x+1,y,z+1)
								voxel_mesh.Faces.AddFace(index + 0, index + 1, index + 2)
								voxel_mesh.Faces.AddFace(index + 0, index + 2, index + 3)
						elif self.vals[z][y][x+1] < iso:
							index = voxel_mesh.Vertices.Count
							voxel_mesh.Vertices.Add(x+1,y,z)
							voxel_mesh.Vertices.Add(x+1,y+1,z)
							voxel_mesh.Vertices.Add(x+1,y+1,z+1)
							voxel_mesh.Vertices.Add(x+1,y,z+1)
							voxel_mesh.Faces.AddFace(index + 0, index + 1, index + 2)
							voxel_mesh.Faces.AddFace(index + 0, index + 2, index + 3)
							
						if y == 0:
							if cap:
								index = voxel_mesh.Vertices.Count
								voxel_mesh.Vertices.Add(x,y,z)
								voxel_mesh.Vertices.Add(x+1,y,z)
								voxel_mesh.Vertices.Add(x+1,y,z+1)
								voxel_mesh.Vertices.Add(x,y,z+1)
								voxel_mesh.Faces.AddFace(index + 0, index + 1, index + 2)
								voxel_mesh.Faces.AddFace(index + 0, index + 2, index + 3)
						elif self.vals[z][y-1][x] < iso:
							index = voxel_mesh.Vertices.Count
							voxel_mesh.Vertices.Add(x,y,z)
							voxel_mesh.Vertices.Add(x+1,y,z)
							voxel_mesh.Vertices.Add(x+1,y,z+1)
							voxel_mesh.Vertices.Add(x,y,z+1)
							voxel_mesh.Faces.AddFace(index + 0, index + 1, index + 2)
							voxel_mesh.Faces.AddFace(index + 0, index + 2, index + 3)
							
						if y == self.y_count - 1:
							if cap:
								index = voxel_mesh.Vertices.Count
								voxel_mesh.Vertices.Add(x,y+1,z)
								voxel_mesh.Vertices.Add(x+1,y+1,z)
								voxel_mesh.Vertices.Add(x+1,y+1,z+1)
								voxel_mesh.Vertices.Add(x,y+1,z+1)
								voxel_mesh.Faces.AddFace(index + 2, index + 1, index + 0)
								voxel_mesh.Faces.AddFace(index + 3, index + 2, index + 0)
						elif self.vals[z][y+1][x] < iso:
							index = voxel_mesh.Vertices.Count
							voxel_mesh.Vertices.Add(x,y+1,z)
							voxel_mesh.Vertices.Add(x+1,y+1,z)
							voxel_mesh.Vertices.Add(x+1,y+1,z+1)
							voxel_mesh.Vertices.Add(x,y+1,z+1)
							voxel_mesh.Faces.AddFace(index + 2, index + 1, index + 0)
							voxel_mesh.Faces.AddFace(index + 3, index + 2, index + 0)
							
						if z == 0:
							if cap:
								index = voxel_mesh.Vertices.Count
								voxel_mesh.Vertices.Add(x,y,z)
								voxel_mesh.Vertices.Add(x+1,y,z)
								voxel_mesh.Vertices.Add(x+1,y+1,z)
								voxel_mesh.Vertices.Add(x,y+1,z)
								voxel_mesh.Faces.AddFace(index + 2, index + 1, index + 0)
								voxel_mesh.Faces.AddFace(index + 3, index + 2, index + 0)
						elif self.vals[z-1][y][x] < iso:
							index = voxel_mesh.Vertices.Count
							voxel_mesh.Vertices.Add(x,y,z)
							voxel_mesh.Vertices.Add(x+1,y,z)
							voxel_mesh.Vertices.Add(x+1,y+1,z)
							voxel_mesh.Vertices.Add(x,y+1,z)
							voxel_mesh.Faces.AddFace(index + 2, index + 1, index + 0)
							voxel_mesh.Faces.AddFace(index + 3, index + 2, index + 0)
							
						if z == self.z_count - 1:
							if cap:
								index = voxel_mesh.Vertices.Count
								voxel_mesh.Vertices.Add(x,y,z+1)
								voxel_mesh.Vertices.Add(x+1,y,z+1)
								voxel_mesh.Vertices.Add(x+1,y+1,z+1)
								voxel_mesh.Vertices.Add(x,y+1,z+1)
								voxel_mesh.Faces.AddFace(index + 0, index + 1, index + 2)
								voxel_mesh.Faces.AddFace(index + 0, index + 2, index + 3)
						elif self.vals[z+1][y][x] < iso:
							index = voxel_mesh.Vertices.Count
							voxel_mesh.Vertices.Add(x,y,z+1)
							voxel_mesh.Vertices.Add(x+1,y,z+1)
							voxel_mesh.Vertices.Add(x+1,y+1,z+1)
							voxel_mesh.Vertices.Add(x,y+1,z+1)
							voxel_mesh.Faces.AddFace(index + 0, index + 1, index + 2)
							voxel_mesh.Faces.AddFace(index + 0, index + 2, index + 3)
							
		voxel_mesh.Weld(math.pi)

		scale_transform = Transform.Scale(Point3d(0,0,0), self.resolution) 
		voxel_mesh.Transform(scale_transform)

		s_pt = self.bbox.PointAt(0,0,0)
		s_plane = Plane(s_pt, self.plane.XAxis, self.plane.YAxis)
		orient_transform = Transform.PlaneToPlane(Plane.WorldXY, s_plane)
		voxel_mesh.Transform(orient_transform)
		voxel_mesh.Translate(-self.resolution/2, -self.resolution/2, -self.resolution/2)

		voxel_mesh.RebuildNormals()
		return voxel_mesh