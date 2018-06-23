# Wasp: Discrete Design with Grasshopper plug-in (GPL) initiated by Andrea Rossi
# 
# This file is part of Wasp.
# 
# Copyright (c) 2017, Andrea Rossi <a.rossi.andrea@gmail.com>
# Wasp is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Wasp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Wasp; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>
#
# Significant parts of Wasp have been developed by Andrea Rossi
# as part of research on digital materials and discrete design at:
# DDU Digital Design Unit - Prof. Oliver Tessmann
# Technische Universitat Darmstadt


#########################################################################
# 
# Wasp 0.2.1
# Wasp Geometry classses - Rhino / Grasshopper
#
# This file implements the basic geometry classes needed to run Wasp.
# The implementation relies on RhinoCommon.
# The aim of these classes is to allow easy implementation of Wasp for other platforms.
# By implementing all the classes and methods of this file in a different engine,
# it is possible to run Wasp outside of Grasshopper.
#
#########################################################################

#########################################################################
##								 IMPORTS							   ##
#########################################################################
import Rhino


#########################################################################
##							GLOBAL VARIABLES						   ##
#########################################################################
model_tolerance = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance*5


#########################################################################
##							GEOMETRY CLASSES						   ##
#########################################################################

## Point / Vector3d class
class WVector3:
	def __init__(self, _x, _y, _z):
		self.pt = Rhino.Geometry.Point3d(_x, _y, _z)
	
	def toVector3d(self):
		return Rhino.Geometry.Vector3d(self.pt.x, self.pt.y, self.pt.z)
	
	def reverse(self):
		return self.toVector3d().Reverse()
	
	def transform(self, trans):
		self.pt.Transform(trans)
	
	def transform_copy(self, trans):
		pt_trans = Rhino.Geometry.Point3d(self.pt.x, self.pt.y, self.pt.z)
		pt_trans.Transform(trans)
		wVec_trans = WVector3(pt_trans.x, pt_trans.y, pt_trans.z)
		return wVec_trans
	
	def distanceTo(self, wVec2):
		return self.pt.DistanceTo(wVec2.pt)
		

## Plane class
class WPlane:
	def __init__(self, _origin, _xAxis, _yAxis):
		self.pln = Rhino.Geometry.Plane(_origin.pt, _xAxis.toVector3d(), _yAxis.toVector3d())
	
	def transform(self, trans):
		

class WLine:
	def __init__(self):
		pass
	
	def transform(self):
		pass

class WTransform(self):
	def __init__(self):
		pass

		
## Box class
class WBox:
	def __init__(self):
		pass
		
## Mesh class
class WMesh:
	def __init__(self):
		pass
	
	def transform(self):
		pass
	
	def intersectLine(self, line):
		pass
	
	def intersectMesh(self, mesh):
		pass
	
	def pointInside(self, point):
		pass
	

## Generic Geometry class (for attributes)
class WGeometry:
	def __init__(self):
		pass
	
	def transform(self):
		pass


		


	
		
	


