"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 1.0.001

Geometry classes
"""

from abc import ABCMeta, abstractmethod

from Rhino.Geometry import Plane, Vector3d, Line, BoundingBox
from Rhino.Geometry import AreaMassProperties
from Rhino.Geometry.Transform import Scale
from Rhino.Geometry.Intersect.Intersection import MeshMeshFast

from wasp import global_tolerance
from wasp.core.colliders import Collider, LineCollider


#################################################################### Mesh Geometry ####################################################################
class MeshGeometry(object):

    ## constructor
    def __init__(self, _mesh):
        self.geo = _mesh


    ## override Rhino .ToString() method (display name of the class in Gh)
    def ToString(self):
        return "WaspMeshGeometry"


    ## create class from data dictionary
    @classmethod
    def from_data(cls, data):
        pass


    ## return the data dictionary representing the part
    def to_data(self):
        pass


    ## return a transformed copy of the part
    def transform(self, trans):
        geo_trans = self.geo.Duplicate()
        geo_trans.Transform(trans)
        part_geo_trans = MeshGeometry(geo_trans)
        return part_geo_trans


    ## return a copy of the part
    def copy(self):
        geo_copy = self.geo.Duplicate()
        part_geo_copy = MeshGeometry(geo_copy)
        return part_geo_copy


    ## compute the geometry center (for overlaps evaluation)
    def get_geometry_center(self):
        return AreaMassProperties.Compute(self.geo).Centroid


    ## return the original geometry data stored
    def get_geometry(self):
        return self.geo
    

    ## compute a collider from the geometry
    def compute_collider(self):
        collider_geo = self.geo.Duplicate().Offset(global_tolerance)
        collider_intersection = MeshMeshFast(collider_geo, self.geo)
        if len(collider_intersection) > 0:
            collider_geo = None
            collider_geo = self.geo.Duplicate()
            center = self.geo.GetBoundingBox(True).Center
            scale_plane = Plane(center, Vector3d(1,0,0), Vector3d(0,1,0))
            scale_transform = Scale(scale_plane, 1-global_tolerance, 1-global_tolerance, 1-global_tolerance)
            collider_geo.Transform(scale_transform)
            collider_intersection = MeshMeshFast(collider_geo, self.geo)
            if len(collider_intersection) > 0:
                collider_geo = None
                return None
        
        if collider_geo is not None:
            collider = Collider([collider_geo])
            return collider


#################################################################### Mesh Geometry ####################################################################
class PolylineGeometry(object):

    ## constructor
    def __init__(self, _lines, _sizes):
        self.geo = _lines
        self.sizes = _sizes


    ## override Rhino .ToString() method (display name of the class in Gh)
    def ToString(self):
        return "WaspPolylineGeometry"


    ## create class from data dictionary
    @classmethod
    def from_data(cls, data):
        pass


    ## return the data dictionary representing the part
    def to_data(self):
        pass


    ## return a transformed copy of the part
    def transform(self, trans):
        geo_trans = []
        for l in self.geo:
            l_trans = Line(l.From, l.To)
            l_trans.Transform(trans)
            geo_trans.append(l_trans)
        part_geo_trans = PolylineGeometry(geo_trans, self.sizes)
        return part_geo_trans


    ## return a copy of the part
    def copy(self):
        geo_copy = []
        for l in self.geo:
            l_copy = Line(l.From, l.To)
            geo_copy.append(l_copy)
        part_geo_copy = PolylineGeometry(geo_copy, self.sizes)
        return part_geo_copy


    ## compute the geometry center (for overlaps evaluation)
    def get_geometry_center(self):
        pts = []
        for l in self.geo:
            pts.append(l.From)
            pts.append(l.To)
        return BoundingBox(pts).Center


    ## return the original geometry data stored
    def get_geometry(self):
        return (self.geo, self.sizes)
    

    ## compute a collider from the geometry
    def compute_collider(self):
        return LineCollider(self.geo, self.sizes)