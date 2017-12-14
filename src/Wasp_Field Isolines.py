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
# Technische Universitt Darmstadt


#########################################################################
##                            COMPONENT INFO                           ##
#########################################################################

"""
Draws isolines across a field object
--> WIP Component: might be incomplete or contain bugs! <--
-
Provided by Wasp 0.0.04
    Args:
        FIELD: Field object to extract isolines from
        t: Z parameter where to extract isolines
        ISO: Isolevel of the curves
    Returns:
        CRV: Isocurves
"""

ghenv.Component.Name = "Wasp_Field Isolines"
ghenv.Component.NickName = 'FieldIso'
ghenv.Component.Message = 'VER 0.0.04\nDEC_13_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "X | Experimental"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
import Rhino.Geometry as rg
import Grasshopper.Kernel as gh
import math




contour_lookup = {"0000":-1, "0001":[[(0,0.5),(0.5,1)]], "0010":[[(0.5,1),(1,0.5)]], "0011":[[(0,0.5),(1,0.5)]],
                  "0100":[[(0.5,0),(1,0.5)]], "0101":[[(0,0.5),(0.5,0)], [(0.5,1),(1,0.5)]], "0110":[[(0.5,0),(0.5,1)]], "0111":[[(0,0.5),(0.5,0)]],
                  "1000":[[(0,0.5),(0.5,0)]], "1001":[[(0.5,0),(0.5,1)]], "1010":[[(0,0.5),(0.5,1)], [(0.5,0),(1,0.5)]], "1011":[[(0.5,0),(1,0.5)]],
                  "1100":[[(0,0.5),(1,0.5)]], "1101":[[(0.5,1),(1,0.5)]], "1110":[[(0,0.5),(0.5,1)]], "1111":-1}

## THRESHOLDING
binary_matrix = []

z = int(math.floor(FIELD.z_count*t))
if z == FIELD.z_count:
    z -= 1


for y in range(FIELD.y_count):
    binary_matrix.append([])
    for x in range(FIELD.x_count):
        
        if FIELD.vals[z][y][x] < ISO:
            binary_matrix[y].append("0")
        else:
            binary_matrix[y].append("1")

## CASES DEFINITION
contour_cases = []
for y in range(0, FIELD.y_count-1):
    contour_cases.append([])
    
    for x in range(0, FIELD.x_count-1):
        
        c_case = ""
        c_case += binary_matrix[y][x]
        c_case += binary_matrix[y][x+1]
        c_case += binary_matrix[y+1][x+1]
        c_case += binary_matrix[y+1][x]
        contour_cases[y].append(c_case)

## CONTOURS GENERATION
contours = []

base_pt = FIELD.pts[z][0][0]
res = FIELD.resolution

for y in range(0, FIELD.y_count-1):
    for x in range(0, FIELD.x_count-1):
        
        c_case = contour_cases[y][x]
        c_shape = contour_lookup[c_case]
        
        if c_shape != -1:
            for shape in c_shape:
                
                c_start = rg.Point3d(base_pt.X + x*res + res*shape[0][0], base_pt.Y + y*res + res*shape[0][1], base_pt.Z)
                c_end = rg.Point3d(base_pt.X + x*res + res*shape[1][0], base_pt.Y + y*res + res*shape[1][1], base_pt.Z)
                
                contour = rg.Line(c_start, c_end).ToNurbsCurve()
                contours.append(contour)

CRV = rg.Curve.JoinCurves(contours)