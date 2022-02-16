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
Add specific parts to an aggregation.
--> WIP Component: might be incomplete or contain bugs <--
-
Provided by Wasp 0.5
    Args:
        AGGR: Aggregation to edit
        PID: ID of the parent part
        CID: ID of the parent connection
        NEXT: Index of the next part among the available ones
        CHECK: OPTIONAL // True to check for the constraints set in the aggregation, False to return all possibilities ignoring constraints (True by default)
        ADD: Add the part to the aggregation
        RESET: Reset the aggregation to the initial state
    Returns:
        AGGR_OUT: Edited aggregation object
        PART_OUT: Edited parts
        C_PART: Parent part
        C_CONN: Parent connection
        NEXT_P: Part to be added
"""

ghenv.Component.Name = "Wasp_Add Parts"
ghenv.Component.NickName = 'AddPart'
ghenv.Component.Message = 'v0.5.005'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "X | Experimental"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import sys
import copy
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


def main(base_aggregation, part_id, connection_id, next_part, check_constraints, add, reset, aggregation):
    
    check_data = True
    
    ##check inputs
    if base_aggregation is None:
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
        
        new_name = base_aggregation.name + "_edit"
        remove_ids = []
        current_part = None
        current_connection = None
        
        if reset or aggregation is None:
            parts_list = [base_aggregation.parts[key] for key in base_aggregation.parts]
            aggregation = copy.deepcopy(base_aggregation)
            aggregation.name = new_name
        
        for i in range(len(aggregation.aggregated_parts)):
            if aggregation.aggregated_parts[i].id == part_id:
                current_part = aggregation.aggregated_parts[i]
                break
        
        if current_part is not None:
            
            for i in range(len(current_part.connections)):
                if current_part.connections[i].id == connection_id:
                    current_connection = current_part.connections[i]
                    break
            
            if current_connection is not None:
                possible_next_parts = aggregation.compute_possible_children(part_id, connection_id, check_constraints)
                
                if possible_next_parts != -1:
                    if len(possible_next_parts) > next_part:
                        
                        if add:
                            aggregation.add_custom_part(part_id, connection_id, possible_next_parts[next_part])
                        
                        return aggregation, current_part, current_connection, possible_next_parts[next_part]
                    else:
                        msg = "The provided index for the next part exceeds the number of available possible parts."
                        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
                        return aggregation, current_part, current_connection, None
                else:
                    msg = "The chosen connection does not provide any valid part to be placed."
                    ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
                    return aggregation, current_part, current_connection, None
        
            else:
                msg = "The provided id does not exist in the current part connections. Might be out of range."
                ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
                return aggregation, current_part, None, None
        
        else:
            msg = "The provided id does not exist in the current aggregation. Might be out of range."
            ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
            return aggregation, None, None, None
    else:
        return -1

## create aggregation container in global variables dict
if 'aggregation_container' not in globals():
    aggregation_container = None

result = main(AGGR, PID, CID, NEXT, CHECK, ADD, RESET, aggregation_container)

if result != -1:
    aggregation_container = result[0]
    
    AGGR_OUT = aggregation_container
    PART_OUT = aggregation_container.aggregated_parts
    C_PART = result[1]
    C_CONN = result[2]
    NEXT_P = result[3]

