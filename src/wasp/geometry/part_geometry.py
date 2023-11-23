"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 1.0.001

Geometry classes
"""

from abc import ABCMeta, abstractmethod

from Rhino.Geometry import Plane, Vector3d
from Rhino.Geometry import AreaMassProperties
from Rhino.Geometry.Transform import Scale
from Rhino.Geometry.Intersect.Intersection import MeshMeshFast

from wasp import global_tolerance
from wasp.core.colliders import Collider

#################################################################### Base Geometry ####################################################################
"""
class PartGeometry(object):

    """
    ## constructor
    def __init__(self):
        pass
    """

    __metaclass__ = ABCMeta

    ## override Rhino .ToString() method (display name of the class in Gh)
    @abstractmethod
    def ToString(self):
        pass

    ## create class from data dictionary
    @abstractmethod
    @classmethod
    def from_data(cls, data):
        pass

    ## return the data dictionary representing the part
    @abstractmethod
    def to_data(self):
        pass

    ## return a transformed copy of the part
    @abstractmethod
    def transform(self):
        pass

    ## return a copy of the part
    @abstractmethod
    def copy(self):
        pass

    ## compute the geometry center (for overlaps evaluation)
    @abstractmethod
    def get_geomety_center(self):
        pass

    ## return the original geometry data stored
    @abstractmethod
    def get_geometry(self):
        pass

    ## compute a collider from the geometry
    @abstractmethod
    def compute_collider(self):
        pass
"""


#################################################################### Base Geometry ####################################################################
class MeshPartGeometry(object):

    ## constructor
    def __init__(self, _mesh):
        self.geo = _mesh


    ## override Rhino .ToString() method (display name of the class in Gh)
    def ToString(self):
        return "WaspMeshPartGeometry"


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
        part_geo_trans = MeshPartGeometry(geo_trans)
        return part_geo_trans


    ## return a copy of the part
    def copy(self):
        geo_copy = self.geo.Duplicate()
        part_geo_copy = MeshPartGeometry(geo_copy)
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
    