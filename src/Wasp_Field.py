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
Generates a scalar field given a grid of points and their relative scalar values
-
Provided by Wasp 0.1.0
    Args:
        BOU: List of geometries defining the boundaries of the field. Geometries must be closed breps or meshes. All points of the field outside the geometries will be assigned a 0 value
        PTS: 3d point grid (from FieldPts component)
        COUNT: Vector storing cell counts for each axis (from FieldPts component)
        RES: Resolution of cell grid
        VAL: Values to assign to each cell
    Returns:
        FIELD: Field object (to be used to drive the FieldAggr component)
"""

ghenv.Component.Name = "Wasp_Field"
ghenv.Component.NickName = 'Field'
ghenv.Component.Message = 'VER 0.2.0'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "4 | Aggregation"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import Rhino.Geometry as rg
import Grasshopper.Kernel as gh


def main(name, boundaries, pts, count, resolution, values):
    
    ## check if Wasp is setup
    if sc.sticky.has_key('WaspSetup'):
        
        check_data = True
        
        ##check inputs
        if name is None:
            name = "myField"
            msg = "Default field name set to 'myField'"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, msg)
        
        if len(boundaries) == 0:
            boundaries.append(rg.BoundingBox(pts).ToBrep())
            msg = "No boundary provided. Boundary set to point grid bounding box"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, msg)
        
        if len(pts) == 0:
            check_data = False
            msg = "No point grid provided"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            
        elif len(values) == 0:
            check_data = False
            msg = "No field values provided"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            
        elif len(pts) != len(values):
            check_data = False
            msg = "Points and Values lists are not matching. Please provide two lists with same number of elements"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, msg)
        
        if count is None:
            check_data = False
            msg = "No axis count provided"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
        if resolution is None and check_data == True:
            resolution = pts[0].DistanceTo(pts[1])
            msg = "No resolution provided. Calculated resolution is %0.2f"%(resolution)
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, msg)
        
        if check_data:
            field = sc.sticky['Field'](name, boundaries, pts, count, resolution, values)
            return field
        else:
            return -1
    
    else:
        ## throw warining
        msg = "You must run the SetupWasp component before starting to build!"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1


result = main(NAME, BOU, PTS, COUNT, RES, VAL)

if result != -1:
    FIELD = result