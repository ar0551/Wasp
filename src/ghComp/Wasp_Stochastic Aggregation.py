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
Aggregate the given parts in a stochastic process, selecting parts and rules randomly at every step.
The component works additively, hence increasing the number of parts in an aggregation just adds new parts on the existing ones, without triggering recomputing of the previous element.
-
Provided by Wasp 0.2
    Args:
        PART: Parts to be aggregated (can be more than one)
        PREV: OPTIONAL // Previous aggregated parts. It is possible to input the results of a previous aggregation, or parts transformed with the TransformPart component
        N: Number of parts to be aggregated (does not count parts provided in PREV)
        RULES: Rules for the aggregation
        COLL: OPTIONAL // Collision detection. By default is active and checks for collisions between the aggregated parts
        MODE: OPTIONAL // Switches between aggregation modes: 0 = no constraints, 1 = local constraints, 2 = global constraints, 3 = local + global constraints
        GC: OPTIONAL // Global constraints to apply to aggregation
        ID: OPTIONAL // Aggregation ID
        RESET: Recompute the whole aggregation
    Returns:
        PART_OUT: Aggregated parts (includes both PREV input and newly aggregated parts)
"""

ghenv.Component.Name = "Wasp_Stochastic Aggregation"
ghenv.Component.NickName = 'StochasticAggregation'
ghenv.Component.Message = 'VER 0.2.04'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "4 | Aggregation"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import sys
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


def main(parts, previous_parts, num_parts, rules, aggregation_mode, global_constraints, aggregation_id, reset, aggregation):
    
    check_data = True
    
    ##check inputs
    if len(parts) == 0:
        check_data = False
        msg = "No parts provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if num_parts is None:
        check_data = False
        msg = "Provide number of aggregation iterations"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    else:
        if len(previous_parts) != 0:
            num_parts += len(previous_parts)
    
    if len(rules) == 0:
        check_data = False
        msg = "No rules provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if aggregation_mode is None:
        aggregation_mode = 0
    
    if aggregation_id is None:
        aggregation_id = 'myAggregation'
    
    if reset is None:
        reset = False
    
    if check_data:
        
        ## create aggregation in sticky dict
        if aggregation is None or aggregation == -1 or reset:
            aggregation = wasp.Aggregation(aggregation_id, parts, rules, aggregation_mode, _prev = previous_parts, _global_constraints = global_constraints)
        
        ## handle parameters changes
        #### parts
        if parts != aggregation.parts.values():
            aggregation.reset_base_parts(new_parts = parts)
            aggregation.reset_rules(rules)
        
        #### rules
        if rules != aggregation.rules:
            for part in parts:
                part.reset_part(rules)
            aggregation.rules = rules
            aggregation.reset_rules(rules)
        
        #### mode
        if aggregation_mode != aggregation.mode:
            aggregation.mode = aggregation_mode
        
        #### constraints
        if global_constraints != aggregation.global_constraints:
            aggregation.global_constraints = global_constraints
        
        ## add parts to aggregation
        if num_parts > len(aggregation.aggregated_parts):
            error_msg = aggregation.aggregate_rnd(num_parts-len(aggregation.aggregated_parts))
            if error_msg is not None:
                ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, error_msg)
        
        ## remove parts from aggregation
        elif num_parts < len(aggregation.aggregated_parts):
            aggregation.remove_elements(num_parts)
        
        ## return result
        return aggregation
        
    else:
        return -1


## create aggregation container in global variables dict
if 'aggregation_container' not in globals():
    aggregation_container = None

result = main(PART, PREV, N, RULES, MODE, GC, ID, RESET, aggregation_container)

if result != -1:
    aggregation_container = result
    
    AGGR = aggregation_container
    PART_OUT = aggregation_container.aggregated_parts