# Wasp: Discrete Design with Grasshopper plug-in (LGPL) initiated by Andrea Rossi
# 
# This file is part of Wasp.
# 
# Copyright (c) 2017-2023, Andrea Rossi <a.rossi.andrea@gmail.com>
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
# Early development of Wasp has been carried out by Andrea Rossi
# as part of research on digital materials and discrete design at:
# DDU Digital Design Unit - Prof. Oliver Tessmann
# Technische Universitt Darmstadt


#########################################################################
##                            COMPONENT INFO                           ##
#########################################################################

"""
Internal transformation object, allowing to make a part transformable after aggregation.
Currently support only rotations and translations.
-
Provided by Wasp 0.5
    Args:
        ID: Name if the internal transformation
        L1: Geometry of the first link
        L2: Geometry of the second link
        TYP: Transformation type: 0 = translation, 1 = rotation
        AX: Transformation axis. For translations, the second link will move along this line. For rotations, the second link will revolve around this axis.
        TD: OPTIONAL // Only for rotations, allowed angle range for the transformation (in degrees)
    Returns:
        TA: Internal transformation object (to plug in the part attributes input)
"""

ghenv.Component.Name = "Wasp_Internal Transformation"
ghenv.Component.NickName = 'InternalTr'
ghenv.Component.Message = 'v0.5.007'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "X | Experimental"
try: ghenv.Component.AdditionalHelpFromDocStrings = "6"
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
    from wasp.core import InternalTransform


def main(id, part1, part2, tr_type, tr_axis, tr_domain):
    
    check_data = True
    
    ##check inputs
    if id is None:
        check_data = False
        msg = "Please provide a name for the transformation"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if part1 is None or part2 is None:
        check_data = False
        msg = "Please provide valid geometries for both parts of the transformation"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if tr_type is None:
        check_data = False
        msg = "Please provide a transformation type"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
        
    if tr_axis is None:
        check_data = False
        msg = "Please provide a valid axis line for the transformation"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if tr_type is not None:
        if tr_type == 1 and tr_domain is None:
            check_data = False
            msg = "Please provide a valid transformation angle domain"
            ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if check_data:
        internal_trans = InternalTransform(id, part1, part2, tr_type, tr_axis, tr_domain)
        return internal_trans
    else:
        return -1


result = main(ID, L1, L2, TYP, AX, TD)

if result != -1:
    TA = result