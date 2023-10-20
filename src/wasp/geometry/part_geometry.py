"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 1.0.001

Geometry classes
"""

from abc import ABC, abstractmethod

#################################################################### Base Geometry ####################################################################
class PartGeometry(ABC, object):

    ## constructor
    def __init__(self):
        pass

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
    
    