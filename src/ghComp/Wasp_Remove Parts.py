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
Remove specific parts from an aggregation.
--> WIP Component: might be incomplete or contain bugs <--
-
Provided by Wasp 0.2.2
    Args:
        AGGR: Aggregation to edit
        ID: ID of the part to remove
        CHILD: OPTIONAL // Remove also all children of the part (False by default)
        REM: True to remove the part from the aggregation
        RESET: Reset the aggregation to the initial state
    Returns:
        AGGR_OUT: Edited aggregation object
        PART_OUT: Edited parts
        C_PART: Currently selected part (for visualization).
        C_CHILD: Children of the selected part (for visualization).
"""

ghenv.Component.Name = "Wasp_Remove Parts"
ghenv.Component.NickName = 'RemovePart'
ghenv.Component.Message = 'VER 0.2.2'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "X | Experimental"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import sys
import copy
import scriptcontext as sc
import Rhino.Geometry as rg
import Grasshopper as gh
import random as rnd

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


def main(aggregation, id, remove_children, remove, reset):
    
    def returnChildren(aggregation, part, list):
        if len(part.children) > 0:
            for child in part.children:
                list.append(child)
                returnChildren(aggregation, aggregation.aggregated_parts[child], list)
        return list
    
    
    check_data = True
    
    ##check inputs
    if aggregation is None:
        check_data = False
        msg = "No aggregation provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    ##check inputs
    if aggregation is None:
        check_data = False
        msg = "No aggregation provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if remove_children is None:
        remove_children = False
    
    if remove is None:
        remove = False
    
    if reset is None:
        reset = False
    
    if check_data:
        
        new_name = aggregation.name + "_edit"
        remove_ids = []
        current_part = None
        current_children = []
        
        if reset or sc.sticky.has_key(new_name) == False:
            parts_list = [aggregation.parts[key] for key in aggregation.parts]
            sc.sticky[new_name] = copy.deepcopy(aggregation)
            sc.sticky[new_name].name = new_name
        
        for i in range(len(sc.sticky[new_name].aggregated_parts)):
            if sc.sticky[new_name].aggregated_parts[i].id == id:
                current_part = sc.sticky[new_name].aggregated_parts[i]
                break
        
        if current_part is not None:
            remove_ids.append(id)
            if remove_children:
                remove_ids = returnChildren(sc.sticky[new_name], current_part, remove_ids)
            remove_ids.sort()
            
            if remove:
                for i in range(len(sc.sticky[new_name].aggregated_parts)-1, -1, -1):
                    if sc.sticky[new_name].aggregated_parts[i].id in remove_ids:
                        sc.sticky[new_name].aggregated_parts.pop(i)
            
            else:
                for i in range(len(sc.sticky[new_name].aggregated_parts)-1, -1, -1):
                    if sc.sticky[new_name].aggregated_parts[i].id in remove_ids:
                        if sc.sticky[new_name].aggregated_parts[i].id == id:
                            current_part = sc.sticky[new_name].aggregated_parts[i]
                        else:
                            current_children.append(sc.sticky[new_name].aggregated_parts[i])
        
        else:
            msg = "The provided id does not exist in the current aggregation. Might be out of range or already removed."
            ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
        
        return sc.sticky[new_name], current_part, current_children
    else:
        return -1

result = main(AGGR, ID, CHILD, REM, RESET)

if result != -1:
    AGGR_OUT = result[0]
    PART_OUT = result[0].aggregated_parts
    C_PART = result[1]
    C_CHILD = result[2]

