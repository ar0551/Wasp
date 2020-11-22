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
Provided by Wasp 0.4
    Args:
        FIELD: Field object to extract isolines from
        PLN: Plane for isolines extraction (0: XY Plane, 1: YZ Plane, 2: XZ Plane)
        T: Z parameter where to extract isolines
        ISO: Isolevel of the curves
    Returns:
        CRV: Isocurves
"""

ghenv.Component.Name = "Wasp_Field Isolines"
ghenv.Component.NickName = 'FieldIso'
ghenv.Component.Message = 'VER 0.4.009'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory =  "5 | Fields"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import sys
import Rhino.Geometry as rg
import Grasshopper as gh
import math


## add Wasp install directory to system path
wasp_loaded = False
ghcompfolder = gh.Folders.DefaultAssemblyFolder
if ghcompfolder not in sys.path:
    sys.path.append(ghcompfolder)
try:
    from wasp import __version__
    wasp_loaded = True
except:
    msg = "Cannot import Wasp. Is the wasp folder available in " + ghcompfolder + "?"
    ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)

## if Wasp is installed correctly, load the classes required by the component
if wasp_loaded:
    pass



def main(field, plane, t, iso):
    contour_lookup = {"0000":-1, "0001":[[(0,0.5),(0.5,1)]], "0010":[[(0.5,1),(1,0.5)]], "0011":[[(0,0.5),(1,0.5)]],
                      "0100":[[(0.5,0),(1,0.5)]], "0101":[[(0,0.5),(0.5,0)], [(0.5,1),(1,0.5)]], "0110":[[(0.5,0),(0.5,1)]], "0111":[[(0,0.5),(0.5,0)]],
                      "1000":[[(0,0.5),(0.5,0)]], "1001":[[(0.5,0),(0.5,1)]], "1010":[[(0,0.5),(0.5,1)], [(0.5,0),(1,0.5)]], "1011":[[(0.5,0),(1,0.5)]],
                      "1100":[[(0,0.5),(1,0.5)]], "1101":[[(0.5,1),(1,0.5)]], "1110":[[(0,0.5),(0.5,1)]], "1111":-1}
    
    check_data = True
    
    ##check inputs
    if field is None:
        check_data = False
        msg = "No field provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if plane is None:
        plane = 0
    
    if t is None:
        check_data = False
        msg = "No parameter provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if iso is None:
        check_data = False
        msg = "No isolevel provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if check_data:
        binary_matrix = []
        contour_cases = []
        contours = []
        base_plane = None
        target_pt = field.bbox.PointAt(0,0,0)
        target_plane = None
        
        #XY Plane contouring
        if plane == 0:
            ## THRESHOLDING
            z = int(math.floor(field.z_count*t))
            if z == field.z_count:
                z -= 1
            
            for y in range(field.y_count):
                binary_matrix.append([])
                for x in range(field.x_count):
                    if field.vals[z][y][x] < iso:
                        binary_matrix[y].append("0")
                    else:
                        binary_matrix[y].append("1")
            
            ## CASES DEFINITION
            for y in range(0, field.y_count-1):
                contour_cases.append([])
                for x in range(0, field.x_count-1):
                    c_case = ""
                    c_case += binary_matrix[y][x]
                    c_case += binary_matrix[y][x+1]
                    c_case += binary_matrix[y+1][x+1]
                    c_case += binary_matrix[y+1][x]
                    contour_cases[y].append(c_case)
            
            ## CONTOURS GENERATION
            base_plane = rg.Plane.WorldXY
            target_pt += field.plane.ZAxis*(z*field.resolution)
            target_plane = rg.Plane(target_pt, field.plane.XAxis, field.plane.YAxis)
            
            for y in range(0, field.y_count-1):
                for x in range(0, field.x_count-1):
                    c_case = contour_cases[y][x]
                    c_shape = contour_lookup[c_case]
                    if c_shape != -1:
                        for shape in c_shape:
                            c_start = rg.Point3d(x + shape[0][0], y + shape[0][1], 0)
                            c_end = rg.Point3d(x + shape[1][0], y + shape[1][1], 0)
                            contour = rg.Line(c_start, c_end).ToNurbsCurve()
                            contours.append(contour)
        
        #YZ Plane contouring
        elif plane == 1:
            ## THRESHOLDING
            x = int(math.floor(field.x_count*t))
            if x == field.x_count:
                x -= 1
            
            for z in range(field.z_count):
                binary_matrix.append([])
                for y in range(field.y_count):
                    if field.vals[z][y][x] < iso:
                        binary_matrix[z].append("0")
                    else:
                        binary_matrix[z].append("1")
            
            ## CASES DEFINITION
            for z in range(0, field.z_count-1):
                contour_cases.append([])
                for y in range(0, field.y_count-1):
                    c_case = ""
                    c_case += binary_matrix[z][y]
                    c_case += binary_matrix[z][y+1]
                    c_case += binary_matrix[z+1][y+1]
                    c_case += binary_matrix[z+1][y]
                    contour_cases[z].append(c_case)
            
            ## CONTOURS GENERATION
            base_plane = rg.Plane.WorldYZ
            target_pt += field.plane.XAxis*(x*field.resolution)
            target_plane = rg.Plane(target_pt, field.plane.YAxis, field.plane.ZAxis)
            
            for z in range(0, field.z_count-1):
                for y in range(0, field.y_count-1):
                    c_case = contour_cases[z][y]
                    c_shape = contour_lookup[c_case]
                    if c_shape != -1:
                        for shape in c_shape:
                            c_start = rg.Point3d(0, y + shape[0][0], z + shape[0][1])
                            c_end = rg.Point3d(0, y + shape[1][0], z + shape[1][1])
                            contour = rg.Line(c_start, c_end).ToNurbsCurve()
                            contours.append(contour)
        
        #XZ Plane contouring
        elif plane == 2:
            ## THRESHOLDING
            y = int(math.floor(field.y_count*t))
            if y == field.y_count:
                y -= 1
            
            for z in range(field.z_count):
                binary_matrix.append([])
                for x in range(field.x_count):
                    if field.vals[z][y][x] < iso:
                        binary_matrix[z].append("0")
                    else:
                        binary_matrix[z].append("1")
            
            ## CASES DEFINITION
            for z in range(0, field.z_count-1):
                contour_cases.append([])
                for x in range(0, field.x_count-1):
                    c_case = ""
                    c_case += binary_matrix[z][x]
                    c_case += binary_matrix[z][x+1]
                    c_case += binary_matrix[z+1][x+1]
                    c_case += binary_matrix[z+1][x]
                    contour_cases[z].append(c_case)
            
            ## CONTOURS GENERATION
            base_plane = rg.Plane.WorldZX
            target_pt += field.plane.YAxis*(y*field.resolution)
            target_plane = rg.Plane(target_pt, field.plane.ZAxis, field.plane.XAxis)
            
            for z in range(0, field.z_count-1):
                for x in range(0, field.x_count-1):
                    c_case = contour_cases[z][x]
                    c_shape = contour_lookup[c_case]
                    if c_shape != -1:
                        for shape in c_shape:
                            c_start = rg.Point3d(x + shape[0][0], 0, z + shape[0][1])
                            c_end = rg.Point3d(x + shape[1][0], 0, z + shape[1][1])
                            contour = rg.Line(c_start, c_end).ToNurbsCurve()
                            contours.append(contour)
        
        contour_curves = rg.Curve.JoinCurves(contours)
        scale_transform = rg.Transform.Scale(rg.Point3d(0,0,0), field.resolution)
        
        orient_transform = rg.Transform.PlaneToPlane(base_plane, target_plane)
        for curve in contour_curves:
            curve.Transform(scale_transform)
            curve.Transform(orient_transform)
        
        return contour_curves
    else:
        return -1

result = main(FIELD, PLN, T, ISO)

if result != -1:
    CRV = result