# Wasp: Discrete Design with Grasshopper plug-in (LGPL) initiated by Andrea Rossi
# 
# This file is part of Wasp.
# 
# Copyright (c) 2017, Andrea Rossi <a.rossi.andrea@gmail.com>
# Wasp is free software; you can redistribute it and/or modify 
# it under the terms of the GNU Lesser General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Wasp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with Wasp; If not, see <http://www.gnu.org/licenses/>.
# 
# @license LGPL-3.0 https://www.gnu.org/licenses/lgpl-3.0.html
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
Provided by Wasp 0.5
    Args:
        FIELD: Field to deconstruct
    Returns:
        NAME: Field name
        RES: Field resolution
        BOU: Field boundaries
        PTS: Field points
        VAL: Field values
        COUNT: Points count on x,y,z axes
"""

ghenv.Component.Name = "Wasp_Deconstruct Field"
ghenv.Component.NickName = 'DeField'
ghenv.Component.Message = 'v0.5.007'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "5 | Fields"
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
    msg = "Cannot import Wasp. Is the wasp folder available in " + ghcompfolder + "?"
    ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)

## if Wasp is installed correctly, load the classes required by the component
if wasp_loaded:
    pass


def main(field):
    
    check_data = True
    
    ##check inputs
    if field is None:
        check_data = False
        msg = "No field provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if check_data:
        count_vec = rg.Vector3d(field.x_count, field.y_count, field.z_count)
        return field.name, field.pts, count_vec, field.resolution, field.plane, field.return_values_list(), field.boundaries, field.bbox
    else:
        return -1


result = main(FIELD)

if result != -1:
    NAME = result[0]
    PTS = result[1]
    COUNT = result[2]
    RES = result[3]
    PLN = result[4]
    VAL = result[5]
    BOU = result[6]
    BB = result[7]