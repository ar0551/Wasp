"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.4.005

Utilities
"""

from Rhino.Geometry import Mesh


#################################################################### Utilities ####################################################################
def mesh_to_dict(mesh):
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


def mesh_from_dict(data):
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