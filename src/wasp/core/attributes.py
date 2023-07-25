"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.5.008

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
class InternalTransform(Attribute):
    
    def __init__(self, id, part1, part2, tr_type, tr_axis, tr_domain):
        
        super(InternalTransform, self).__init__(id, [part1, part2, tr_axis], True)
        
        self.transform_type = tr_type
        self.transform_domain = tr_domain
        self.current_pos = 0.5
    
    def ToString(self):
        return "WaspInternalTransform [name: %s]" % (self.name)
    
    def transform(self, trans):
        values_trans = []
        for val in self.values:
            val_trans = None
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
        
        it_trans = InternalTransform(self.name, values_trans[0], values_trans[1], self.transform_type, values_trans[2], self.transform_domain)
        return it_trans
    
    def copy(self):
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
        
        it_copy = InternalTransform(self.name, values_copy[0], values_copy[1], self.transform_type, values_copy[2], self.transform_domain)
        return it_copy