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
Generate a collider for a given geometry.
-
Provided by Wasp 0.2
    Args:
        GEO: Geometry of the collider(s)
        MUL: OPTIONAL // Set to True if you are using multiple colliders and it is sufficient for one of them not to collide (False by default)
        ALL: OPTIONAL // If MUL is set to True, set to True to check all colliders (False by default, search will stop after finding a valid collider)
        CONN: OPTIONAL // If MUL is set to True, associate a connection to each collider (e.g. a picking position for the tool collider).
    Returns:
        COLL: Collider instance
"""

ghenv.Component.Name = "Wasp_Collider"
ghenv.Component.NickName = 'Collider'
ghenv.Component.Message = 'VER 0.2.04'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "1 | Elements"
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass

import sys
import Rhino.Geometry as rg
import Grasshopper as gh

## add Wasp install directory to system path
ghcompfolder = gh.Folders.DefaultAssemblyFolder
wasp_path = ghcompfolder + "Wasp"
if wasp_path not in sys.path:
    sys.path.append(wasp_path)
try:
    import wasp
except:
    msg = "Cannot import Wasp. Is the wasp.py module installed in " + wasp_path + "?"
    ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)


def main(geometry, multiple, check_all, connections):
    
    check_data = True
    
    ##check inputs
    if len(geometry) == 0:
        check_data = False
        msg = "No geometry provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if multiple is None:
        multiple = False
    
    if check_all is None:
        check_all = False
    
    if len(connections) > 0 and len(connections) != len(geometry):
        check_data = False
        msg = "Please provide the same amount of collider geometries and connections."
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if len(geometry) > 0:
        faces_count = 0
        for geo in geometry:
            faces_count += geo.Faces.Count
        if faces_count > 1000:
            msg = "The given collider has a high faces count. Consider providing a low poly collider to improve performance"
            ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if check_data:
        collider = wasp.Collider(geometry, multiple, check_all, connections)
        return collider
    else:
        return -1


result = main(GEO, MUL, ALL, CONN)

if result != -1:
    COLL = result