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
ADD specific parts to an aggregation.
--> WIP Component: might be incomplete or contain bugs <--
-
Provided by Wasp 0.2.3
    Args:
        AGGR: Aggregation to edit
        ID: ID of the part to remove
        CHILD: OPTIONAL // Remove also all children of the part (False by default)
        REM: True to remove the part from the aggregation
        RESET: Reset the aggregation to the initial state
    Returns:
        AGGR_OUT: Edited aggregation object
        PART_OUT: Edited parts
        C_PART: Geometry of the currently selected part (for visualization).
        C_CHILD: Geometry of the children of the selected part (for visualization).
"""

ghenv.Component.Name = "Wasp_Add Parts"
ghenv.Component.NickName = 'AddPart'
ghenv.Component.Message = 'VER 0.2.3'
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


def main(aggregation, part_id, connection_id, next_part, check_constraints, add, reset):
    
    check_data = True
    
    ##check inputs
    if aggregation is None:
        check_data = False
        msg = "No aggregation provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if part_id is None:
        check_data = False
        msg = "No part id provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if connection_id is None:
        check_data = False
        msg = "No connection id provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if next_part is None:
        check_data = False
        msg = "No index for next part provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if add is None:
        add = False
    
    if reset is None:
        reset = False
    
    if check_data:
        
        new_name = aggregation.name + "_edit"
        remove_ids = []
        current_part = None
        current_connection = None
        
        if reset or sc.sticky.has_key(new_name) == False:
            parts_list = [aggregation.parts[key] for key in aggregation.parts]
            sc.sticky[new_name] = copy.deepcopy(aggregation)
            sc.sticky[new_name].name = new_name
        
        for i in range(len(sc.sticky[new_name].aggregated_parts)):
            if sc.sticky[new_name].aggregated_parts[i].id == part_id:
                current_part = sc.sticky[new_name].aggregated_parts[i]
                break
        
        if current_part is not None:
            
            for i in range(len(current_part.connections)):
                if current_part.connections[i].id == connection_id:
                    current_connection = current_part.connections[i]
                    break
            
            if current_connection is not None:
                possible_next_parts = sc.sticky[new_name].compute_possible_children(part_id, connection_id, check_constraints)
                
                if possible_next_parts != -1:
                    if len(possible_next_parts) > next_part:
                        
                        if add:
                            sc.sticky[new_name].add_custom_part(part_id, connection_id, possible_next_parts[next_part])
                        
                        return sc.sticky[new_name], current_part, current_connection, possible_next_parts[next_part]
                    else:
                        msg = "The provided index for the next part exceeds the number of available possible parts."
                        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
                        return sc.sticky[new_name], current_part, current_connection, None
                else:
                    msg = "The chosen connection does not provide any valid part to be placed."
                    ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
                    return sc.sticky[new_name], current_part, current_connection, None
        
            else:
                msg = "The provided id does not exist in the current part connections. Might be out of range."
                ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
                return sc.sticky[new_name], current_part, None, None
        
        else:
            msg = "The provided id does not exist in the current aggregation. Might be out of range."
            ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
            return sc.sticky[new_name], None, None, None
    else:
        return -1

result = main(AGGR, PID, CID, NEXT, CHECK, ADD, RESET)

if result != -1:
    AGGR_OUT = result[0]
    PART_OUT = result[0].aggregated_parts
    C_PART = result[1]
    C_CONN = result[2]
    NEXT_P = result[3]

