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
Provided by Wasp 0.3
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
ghenv.Component.Message = 'VER 0.3.01'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "4 | Aggregation"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import sys
import Rhino.Geometry as rg
import Grasshopper as gh


## add Wasp install directory to system path
wasp_loaded = False
ghcompfolder = gh.Folders.DefaultAssemblyFolder
if ghcompfolder not in sys.path:
    sys.path.append(ghcompfolder)
try:
    from wasp import __version__
    wasp_loaded = True
except:
    msg = "Cannot import Wasp. Is the wasp.py module installed in " + wasp_path + "?"
    ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)

## if Wasp is installed correctly, load the classes required by the component
if wasp_loaded:
    from wasp import Field


def main(name, empty_field, values):
    
    check_data = True
    
    ##check inputs
    if name is None:
        name = "field"
    
    if empty_field is None:
        check_data = False
        msg = "No base empty field provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    else:
        
        values_count = empty_field.x_count*empty_field.y_count*empty_field.z_count
        
        if len(values) == 0:
            check_data = False
            msg = "No field values provided"
            ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
            
        elif values_count != len(values):
            check_data = False
            msg = "Field points and Values lists are not matching. Please provide a number of values matching the number of points in the base field."
            ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)
    
    if check_data:
        count_vec = rg.Vector3d(empty_field.x_count, empty_field.y_count, empty_field.z_count)
        field = Field(name, empty_field.boundaries, empty_field.pts, count_vec, empty_field.resolution, values)
        return field
    else:
        return -1


result = main(NAME, E_FIELD, VAL)

if result != -1:
    FIELD = result