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
Deconstruct a collider object.
-
Provided by Wasp 0.2
    Args:
        COLL: Collider object
    Returns:
        GEO: Collider geometry
        CONN: If collider is Multiple, connections associated with the collider
        VC: If collider is Multiple, valid connections not causing collisions
"""

ghenv.Component.Name = "Wasp_Deconstruct Collider"
ghenv.Component.NickName = 'DeColl'
ghenv.Component.Message = 'VER 0.2.04'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "1 | Elements"
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


import sys
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


def main(collider):
        
    check_data = True
    
    ## check inputs
    if collider is None:
        check_data = False
        msg = "No collider provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    ## execute main code if all needed inputs are available
    if check_data:
        return collider.geometry, collider.connections, collider.valid_connections
    else:
        return -1

result = main(COLL)

if result != -1:
    GEO = result[0]
    CONN = result[1]
    V_CONN = result[2]



