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
Mesh collision global constraint
-
Provided by Wasp 0.2.2
    Args:
        GEOMETRY: Geometry of the collision shape
        IN: OPTIONAL // False to check only for intersections, True to check also for inclusion (True by default)
    Returns:
        GC: Mesh constraint
"""

ghenv.Component.Name = "Wasp_Mesh Constraint"
ghenv.Component.NickName = 'MeshConst'
ghenv.Component.Message = "VER 0.2.2"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "4 | Aggregation"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import sys
import scriptcontext as sc
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


## Main code execution
def main(geometry, inside):
    
    check_data = True
    ##check inputs
    if geometry is None:
        check_data = False
        msg = "Provide a valid geometry"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if inside is None:
        inside == True
    
    if inside == True:
        naked_edges = geometry.GetNakedEdges()
        if naked_edges is not None:
            check_data = False
            msg = "The provided geometry is not closed!"
            ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    
    if check_data:
        geo_constraint = wasp.Mesh_Constraint(geometry, inside)
        return geo_constraint
    else:
        return -1


result = main(GEO, IN)

if result != -1:
    GC = result