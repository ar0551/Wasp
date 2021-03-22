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
Provided by Wasp 0.5
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
ghenv.Component.Message = 'VER 0.5.001'
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


def main(base_aggregation, id, remove_children, remove, reset, aggregation):
    
    def returnChildren(base_aggregation, part, list):
        if len(part.children) > 0:
            for child in part.children:
                list.append(child)
                returnChildren(base_aggregation, base_aggregation.aggregated_parts[child], list)
        return list
    
    
    check_data = True
    
    ##check inputs
    if base_aggregation is None:
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
        
        new_name = base_aggregation.name + "_edit"
        remove_ids = []
        current_part = None
        current_children = []
        
        if reset or aggregation is None:
            parts_list = [base_aggregation.parts[key] for key in base_aggregation.parts]
            aggregation = copy.deepcopy(base_aggregation)
            aggregation.name = new_name
        
        for i in range(len(aggregation.aggregated_parts)):
            if aggregation.aggregated_parts[i].id == id:
                current_part = aggregation.aggregated_parts[i]
                break
        
        if current_part is not None:
            remove_ids.append(id)
            if remove_children:
                remove_ids = returnChildren(aggregation, current_part, remove_ids)
            remove_ids.sort()
            
            if remove:
                for i in range(len(aggregation.aggregated_parts)-1, -1, -1):
                    if aggregation.aggregated_parts[i].id in remove_ids:
                        aggregation.aggregated_parts.pop(i)
            
            else:
                for i in range(len(aggregation.aggregated_parts)-1, -1, -1):
                    if aggregation.aggregated_parts[i].id in remove_ids:
                        if aggregation.aggregated_parts[i].id == id:
                            current_part = aggregation.aggregated_parts[i]
                        else:
                            current_children.append(aggregation.aggregated_parts[i])
        
        else:
            msg = "The provided id does not exist in the current aggregation. Might be out of range or already removed."
            ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
        
        return aggregation, current_part, current_children
    else:
        return -1

## create aggregation container in global variables dict
if 'aggregation_container' not in globals():
    aggregation_container = None

result = main(AGGR, ID, CHILD, REM, RESET, aggregation_container)

if result != -1:
    aggregation_container = result[0]
    
    AGGR_OUT = aggregation_container
    PART_OUT = aggregation_container.aggregated_parts
    C_PART = result[1]
    C_CHILD = result[2]

