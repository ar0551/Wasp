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
Changes the base plane of the field, with the effect of creating a transformed copy.
-
Provided by Wasp 0.5
    Args:
        FIELD: Field to be transformed
        PLN: Target plane
    Returns:
        F_TR: Transformed field
"""

ghenv.Component.Name = "Wasp_Orient Field"
ghenv.Component.NickName = 'FieldOrient'
ghenv.Component.Message = 'v0.5.002'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "5 | Fields"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import sys
import Grasshopper as gh
import Rhino.Geometry as rg
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
    from wasp.core import Part


def main(field, target_plane):
    
    check_data = True
    
    ##check inputs
    if field is None:
        check_data = False
        msg = "Please provide a valid field to be transformed"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if target_plane is None:
        check_data = False
        msg = "Please provide a valid transformation"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if check_data:
        ## create a plane-to-plane transformation
        orient_transform = rg.Transform.PlaneToPlane(field.plane, target_plane)
        ## transform part
        field_trans = field.transform(orient_transform)
        
        ## flip part if negative scaling occurs
        if orient_transform.M00 * orient_transform.M11 * orient_transform.M22 < 0:
            ## geometry
            for bou in field_trans.boundaries:
                bou.Flip(True, True, True)
        
        return field_trans
    else:
        return -1


result = main(FIELD, PLN)

if result != -1:
    F_TR = result
