"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.4.001

Attribute classes and utilities
"""

from Rhino.Geometry import Point3d
from Rhino.Geometry import Plane
from Rhino.Geometry import Line

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
				## !!!! add try..except.. block for other geometry types (?)
				if type(val) == Point3d:
					val_trans = Point3d(val)
				elif type(val) == Plane:
					val_trans = Plane(val)
				elif type(val) == Line:
					val_trans = Line(val.From, val.To)
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
				if type(val) == Point3d:
					val_copy = Point3d(val)
				elif type(val) == Plane:
					val_copy = Plane(val)
				elif type(val) == Line:
					val_copy = Line(val.From, val.To)
				else:
					val_copy = val.Duplicate()
				values_copy.append(val_copy)
			attr_copy = Attribute(self.name, values_copy, self.transformable)
		else:
			attr_copy = Attribute(self.name, self.values, self.transformable)
		return attr_copy


#################################################################### Attribute ####################################################################
class SmartAttribute(Attribute):
	
	## constructor
	def __init__(self, name, values, transformable, connections = [], conn_mask = []):
		super(SmartAttribute, self).__init__(name, values, transformable)

		self.connections = connections
		self.conn_mask = conn_mask
	
	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspSmartAttribute [name: %s]" % (self.name)
	
	## return a transformed copy of the attribute
	def transform(self, trans):
		if self.transformable == True:
			values_trans = []
			for val in self.values:
				val_trans = None
				## !!!! add try..except.. block for other geometry types (?)
				if type(val) == Point3d:
					val_trans = Point3d(val)
				elif type(val) == Plane:
					val_trans = Plane(val)
				elif type(val) == Line:
					val_trans = Line(val.From, val.To)
				else:
					val_trans = val.Duplicate()
				val_trans.Transform(trans)
				values_trans.append(val_trans)
			attr_trans = SmartAttribute(self.name, values_trans, self.transformable, self.connections, self.conn_mask)
		else:
			attr_trans = SmartAttribute(self.name, self.values, self.transformable, self.connections, self.conn_mask)
		return attr_trans
	
	## return a copy of the attribute
	def copy(self):
		if self.transformable == True:
			values_copy = []
			for val in self.values:
				val_copy = None
				if type(val) == Point3d:
					val_copy = Point3d(val)
				elif type(val) == Plane:
					val_copy = Plane(val)
				elif type(val) == Line:
					val_copy = Line(val.From, val.To)
				else:
					val_copy = val.Duplicate()
				values_copy.append(val_copy)
			attr_copy = SmartAttribute(self.name, values_copy, self.transformable, self.connections, self.conn_mask)
		else:
			attr_copy = SmartAttribute(self.name, self.values, self.transformable, self.connections, self.conn_mask)
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
			dir_trans = Line(start_trans, end_trans)
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
			dir_copy = Line(start_copy, end_copy)
			sup_dir_copy.append(dir_copy)
		sup_copy = Support(sup_dir_copy)
		return sup_copy