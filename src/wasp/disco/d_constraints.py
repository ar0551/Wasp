"""
(C) 2017-2021 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.4.015

DisCo geometric constraints classes
"""

from Rhino.Geometry import Point3d


#################################################################### Point Constraint ####################################################################
class DisCoPointConstraint(object):

	## constructor
	def __init__(self, _x, _y, _z):
		self.x = _x
		self.y = _y
		self.z = _z


	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "DisCoPointConstraint [x: %.3f, y: %.3f, z: %.3f]" % (self.x, self.y, self.z)
	

	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		return cls(data['x'], data['y'], data['z'])
	

	## return the data dictionary representing the class
	def to_data(self):
		data = {}
		data['x'] = self.x
		data['y'] = self.y
		data['z'] = self.z
		return data
	
	
	## create class from Rhino Point3d
	@classmethod
	def from_point(cls, pt):
		return cls(pt.X, pt.Y, pt.Z)


#################################################################### Point Constraint ####################################################################
class DisCoCurveConstraint(object):

	## constructor
	def __init__(self, _pts):
		self.pts = _pts


	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "DisCoCurveConstraint [count: %s]" % (len(self.pts))
	

	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		pts = []
		for pt_data in data['controlPoints']:
			pt = Point3d(pt_data['x'], pt_data['y'], pt_data['z'])
			pts.append(pt)
		return cls(pts)
	

	## return the data dictionary representing the class
	def to_data(self):
		data = {}
		pts_data
		for pt in self.pts:
			pt_data = {'x': pt.X, 'y' : pt.Y, 'z': pt.Z}
			pts_data.append(pt_data)
		data['controlPoints'] = pts_data
		return data
	
	
	## create class from Rhino curve
	@classmethod
	def from_curve(cls, crv, sample=None):	 
		count = 100
		if sample is not None:
			l = crv.GetLength()
			count = max(int(l/sample), 1)

		crv_params = crv.DivideByCount(count, True)
		pts = []
		for p in crv_params:
			pts.append(crv.PointAt(p))
		
		return cls(pts)		   


#################################################################### Point Constraint ####################################################################
class DisCoBoxConstraint(object):

	## constructor
	def __init__(self, _min_x, _max_x, _min_y, _max_y, _min_z, _max_z):
		self.min_x = _min_x
		self.max_x = _max_x
		self.min_y = _min_y
		self.max_y = _max_y
		self.min_z = _min_z
		self.max_z = _max_z


	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "DisCoBoxConstraint [min: %.2f, %.2f, %.2f, max: %.2f, %.2f, %.2f]" % (self.min_x, self.min_y, self.min_z, self.max_x, self.max_y, self.max_z)
	

	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		min_x = data['minX']
		max_x = data['maxX']
		min_y = data['minY']
		max_y = data['maxY']
		min_z = data['minZ']
		max_z = data['maxZ']
		return cls(min_x, max_x, min_y, max_y, min_z, max_z)
	

	## return the data dictionary representing the class
	def to_data(self):
		data = {}
		data['minX'] = self.min_x
		data['maxX'] = self.max_x
		data['minY'] = self.min_y
		data['maxY'] = self.max_y
		data['minZ'] = self.min_z
		data['maxZ'] = self.max_z
		return data