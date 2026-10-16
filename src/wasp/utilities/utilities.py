"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.7.002

Utilities
"""

from Rhino.Geometry import Mesh
from Rhino.Geometry import Plane
from Rhino.Geometry import Vector3d, Point3d, Line, BoundingBox, Box, Interval
from Rhino.Geometry import LineCurve
from Rhino.Geometry import Transform

from Rhino.Runtime import CommonObject
from Rhino.FileIO import SerializationOptions

from System.Drawing import Color


#################################################################### Utilities ####################################################################
reserved_chars = "_|> "

def mesh_to_data(mesh):
	data = {}
	vertices = []
	for v in mesh.Vertices:
		vl = []
		vl.append(float(v.X))
		vl.append(float(v.Y))
		vl.append(float(v.Z))
		vertices.append(vl)
	data["vertices"] = vertices
	faces = []
	for f in mesh.Faces:
		fl =[]
		fl.append(f.A)
		fl.append(f.B)
		fl.append(f.C)
		if f.IsQuad:
			fl.append(f.D)
		faces.append(fl)
	data["faces"] = faces
	return data


def mesh_from_data(data):
	mesh = Mesh()
	for vl in data["vertices"]:
		mesh.Vertices.Add(vl[0], vl[1], vl[2])
	for fl in data["faces"]:
		if len(fl) == 3:
			mesh.Faces.AddFace(fl[0], fl[1], fl[2])
		else:
			mesh.Faces.AddFace(fl[0], fl[1], fl[2], fl[3])
	mesh.RebuildNormals()
	return mesh


def plane_to_data(pln):
	data = {}
	data['origin'] = [pln.Origin.X,pln.Origin.Y, pln.Origin.Z]
	data['xaxis'] = [pln.XAxis.X, pln.XAxis.Y, pln.XAxis.Z]
	data['yaxis'] = [pln.YAxis.X, pln.YAxis.Y, pln.YAxis.Z]
	return data


def plane_from_data(data):
	origin = Point3d(data['origin'][0], data['origin'][1], data['origin'][2])
	x_axis = Vector3d(data['xaxis'][0], data['xaxis'][1], data['xaxis'][2])
	y_axis = Vector3d(data['yaxis'][0], data['yaxis'][1], data['yaxis'][2])
	return Plane(origin, x_axis, y_axis)


def transform_to_data(trans):
	data = {}
	data['M00'] = trans.M00
	data['M01'] = trans.M01
	data['M02'] = trans.M02
	data['M03'] = trans.M03		
	data['M10'] = trans.M10
	data['M11'] = trans.M11
	data['M12'] = trans.M12
	data['M13'] = trans.M13		 
	data['M20'] = trans.M20
	data['M21'] = trans.M21
	data['M22'] = trans.M22
	data['M23'] = trans.M23	 
	data['M30'] = trans.M30
	data['M31'] = trans.M31
	data['M32'] = trans.M32
	data['M33'] = trans.M33
	return data


def transform_from_data(data):
	trans = Transform(0)
	trans.M00 = float(data['M00'])
	trans.M01 = float(data['M01'])
	trans.M02 = float(data['M02'])
	trans.M03 = float(data['M03'])
	trans.M10 = float(data['M10'])
	trans.M11 = float(data['M11'])
	trans.M12 = float(data['M12'])
	trans.M13 = float(data['M13'])
	trans.M20 = float(data['M20'])
	trans.M21 = float(data['M21'])
	trans.M22 = float(data['M22'])
	trans.M23 = float(data['M23'])
	trans.M30 = float(data['M30'])
	trans.M31 = float(data['M31'])
	trans.M32 = float(data['M32'])
	trans.M33 = float(data['M33'])
	return trans

def attribute_value_to_data(val):
	val_data = {}
	val_data['valid'] = False
	if isinstance(val, str):
		val_data['type'] = 'String'
		val_data['value'] = val
		val_data['valid'] = True
	elif isinstance(val, bool):
		val_data['type'] = 'Boolean'
		val_data['value'] = val
		val_data['valid'] = True
	elif isinstance(val, (int, float)):
		val_data['type'] = 'Number'
		val_data['value'] = val
		val_data['valid'] = True
	elif isinstance(val, dict):
		val_data['type'] = 'Dictionary'
		val_data['value'] = val
		val_data['valid'] = is_serializable(val)
	elif isinstance(val, Color):
		val_data['type'] = 'Color'
		val_data['value'] = [val.A, val.R, val.G, val.B]
		val_data['valid'] = True
	elif isinstance(val, Vector3d):
		val_data['type'] = 'Vector'
		val_data['value'] = [val.X, val.Y, val.Z]
		val_data['valid'] = True
	elif isinstance(val, Point3d):
		val_data['type'] = 'Point'
		val_data['value'] = [val.X, val.Y, val.Z]
		val_data['valid'] = True
	elif isinstance(val, Plane):
		val_data['type'] = 'Plane'
		val_data['value'] = plane_to_data(val)
		val_data['valid'] = True
	elif isinstance(val, Line):
		val_data['type'] = 'Line'
		val_data['value'] = {'from': [val.From.X, val.From.Y, val.From.Z], 'to': [val.To.X, val.To.Y, val.To.Z]}
		val_data['valid'] = True
	elif isinstance(val, BoundingBox):
		val_data['type'] = 'BoundingBox'
		val_data['value'] = {'min': [val.Min.X, val.Min.Y, val.Min.Z], 'max': [val.Max.X, val.Max.Y, val.Max.Z]}
		val_data['valid'] = True
	elif isinstance(val, Box):
		val_data['type'] = 'Box'
		val_data['value'] = {'plane': plane_to_data(val.Plane), 'min': [val.X.T0, val.Y.T0, val.Z.T0], 'max': [val.X.T1, val.Y.T1, val.Z.T1]}
		val_data['valid'] = True
	elif isinstance(val, Mesh):
		val_data['type'] = 'Mesh'
		val_data['value'] = mesh_to_data(val)
		val_data['valid'] = True
	elif isinstance(val, CommonObject):
		val_data['type'] = 'RhinoCommonObject'
		val_data['value'] = val.ToJSON(SerializationOptions())
		val_data['valid'] = True
	else:
		if is_serializable(val):
			val_data['type'] = 'Unknown'
			val_data['value'] = val
			val_data['valid'] = True
		else:
			val_data['type'] = 'Unknown'
			val_data['value'] = str(val)
			val_data['valid'] = False
	return val_data


def attribute_value_from_data(val_data):
	val = None
	if val_data['valid']:
		if val_data['type'] == 'String' or val_data['type'] == 'Boolean' or val_data['type'] == 'Number' or val_data['type'] == 'Dictionary':
			val = val_data['value']
		
		elif val_data['type'] == 'Color':
			val = Color.FromArgb(*val_data['value'])
		elif val_data['type'] == 'Vector':
			val = Vector3d(*val_data['value'])
		elif val_data['type'] == 'Point':
			val = Point3d(*val_data['value'])
		elif val_data['type'] == 'Plane':
			val = plane_from_data(val_data['value'])
		elif val_data['type'] == 'BoundingBox':
			val = BoundingBox(Point3d(*val_data['value']['min']), Point3d(*val_data['value']['max']))
		elif val_data['type'] == 'Box':
			plane = plane_from_data(val_data['value']['plane'])
			x_interval = Interval(val_data['value']['min'][0], val_data['value']['max'][0])
			y_interval = Interval(val_data['value']['min'][1], val_data['value']['max'][1])
			z_interval = Interval(val_data['value']['min'][2], val_data['value']['max'][2])
			val = Box(plane, x_interval, y_interval, z_interval)
		elif val_data['type'] == 'Line':
			val = Line(Point3d(*val_data['value']['from']), Point3d(*val_data['value']['to']))
		elif val_data['type'] == 'Mesh':
			val = mesh_from_data(val_data['value'])
		elif val_data['type'] == 'RhinoCommonObject':
			val = CommonObject.FromJSON(val_data['value'])
		elif val_data['type'] == 'Unknown':
			val = val_data['value']
	return val


def is_serializable(obj):
	try:
		import json
		json.dumps(obj)
		return True
	except:
		return False