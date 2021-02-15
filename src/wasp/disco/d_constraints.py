"""
(C) 2017-2021 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.4.015

DisCo geometric constraints classes
"""


#################################################################### Point Constraint ####################################################################
class DisCoPointConstraint(object):

    ## constructor
    def __init__(self, name):
        pass


    ## override Rhino .ToString() method (display name of the class in Gh)
    def ToString(self):
        return "DisCo Point Constraint"
    

    ## create class from data dictionary
    @classmethod
    def from_data(cls, data):
        return None
    

    ## return the data dictionary representing the class
	def to_data(self):
        data = {}

        return data


#################################################################### Point Constraint ####################################################################
class DisCoCurveConstraint(object):

    ## constructor
    def __init__(self, name):
        pass


    ## override Rhino .ToString() method (display name of the class in Gh)
    def ToString(self):
        return "DisCo Curve Constraint"
    

    ## create class from data dictionary
    @classmethod
    def from_data(cls, data):
        return None
    

    ## return the data dictionary representing the class
	def to_data(self):
        data = {}

        return data


#################################################################### Point Constraint ####################################################################
class DisCoBoxConstraint(object):

    ## constructor
    def __init__(self, name):
        pass


    ## override Rhino .ToString() method (display name of the class in Gh)
    def ToString(self):
        return "DisCo Box Constraint"
    

    ## create class from data dictionary
    @classmethod
    def from_data(cls, data):
        return None
    

    ## return the data dictionary representing the class
	def to_data(self):
        data = {}

        return data