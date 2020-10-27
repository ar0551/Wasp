"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.4.005

Utilities
"""

from Rhino.Geometry import Mesh
from Rhino.Geometry import Plane
from Rhino.Geometry import Vector3d, Point3d


#################################################################### Utilities ####################################################################
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
    pass


def transform_from_data(data):
    pass