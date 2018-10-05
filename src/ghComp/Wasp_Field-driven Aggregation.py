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
Aggregate the given parts according to a given scalar field. New parts are added following higher values in the field.
The component works additively, hence increasing the number of parts in an aggregation just adds new parts on the existing ones, without triggering recomputing of the previous element
-
Provided by Wasp 0.2.0
    Args:
        PART: Parts to be aggregated (can be more than one)
        PREV: Previous aggregated parts. It is possible to input the results of a previous aggregation, or parts transformed with the TransformPart component
        N: Number of parts to be aggregated (does not count parts provided in PREV)
        RULES: Rules for the aggregation
        FIELD: Scalar field to drive the aggregation (parts will be added following higher values in the field)
        THRES: OPTIONAL // If set, used to define a threshold value above which the placement of next part is accepted. If not set, aggregation will look for part with highest value in the whole field. Setting a low threshold helds less accurate results, but highly speeds up calculations
        COLL: OPTIONAL // Collision detection. By default is active and checks for collisions between the aggregated parts
        MODE: OPTIONAL // Switches between aggregation modes: 0 = Basic (Default: only parts collision check), 1 = Constrained (checks all constraints set on the part)
        ID: OPTIONAL // Aggregation ID (to avoid overwriting when having different aggregation components in the same file)
        RESET: Recompute the whole aggregation
    Returns:
        AGGR: Aggregation object
        PART_OUT: Aggregated parts (includes both PREV input and newly aggregated parts)
"""

ghenv.Component.Name = "Wasp_Field-driven Aggregation"
ghenv.Component.NickName = 'FieldAggregation'
ghenv.Component.Message = "VER 0.2.1"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "4 | Aggregation"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import sys
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


## Main code execution
def main(parts, previous_parts, num_parts, rules, aggregation_mode, global_constraints, aggregation_id, reset, fields):
    
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
        aggregation_id = 'myFieldAggregation'
    
    if reset is None:
        reset = False
    
    if len(fields) == 0:
        check_data = False
        msg = "Provide a valid scalar field"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    elif len(fields) > 1:
        field_names = [f.name for f in fields]
        for part in parts:
            if part.field is None:
                part.field = fields[0].name
                msg = "Part " + part.name + " does not have a vaild field name assigned. Field " + part.field + " assigned by default."
                ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Remark, msg)
                
            elif part.field not in field_names:
                check_data = False
                msg = "Part " + part.name + " does not have a vaild field name assigned."
                ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if check_data:
        ## store rules in sticky dict
        if sc.sticky.has_key('rules') == False:
            sc.sticky['rules'] = rules
        
        ## if rules changed, reset parts and recompute rule tables
        if rules != sc.sticky['rules']:
            for part in parts:
                part.reset_part(rules)
            sc.sticky['rules'] = rules
            if sc.sticky.has_key(aggregation_id):
                sc.sticky[aggregation_id].reset_rules(rules)
        
        ## create aggregation in sticky dict
        if sc.sticky.has_key(aggregation_id) == False:
            sc.sticky[aggregation_id] = wasp.Aggregation(aggregation_id, parts, sc.sticky['rules'], aggregation_mode, _prev = previous_parts, _global_constraints = global_constraints, _field = fields)
            
        ## reset aggregation
        if reset:
            sc.sticky[aggregation_id] = wasp.Aggregation(aggregation_id, parts, sc.sticky['rules'], aggregation_mode, _prev = previous_parts, _global_constraints = global_constraints, _field = fields)
        
        if num_parts > sc.sticky[aggregation_id].p_count:
            #sc.sticky[aggregation_id].aggregate_field(num_parts-sc.sticky[aggregation_id].p_count, field, threshold)
            error_msg = sc.sticky[aggregation_id].aggregate_field(num_parts-sc.sticky[aggregation_id].p_count)
            print error_msg
            if error_msg is not None:
                ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, error_msg)
            """
            if len(sc.sticky[aggregation_id]) < num_parts:
                msg = "Could not place " + str(num_parts - len(sc.sticky[aggregation_id])) + " parts"
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            """
        elif num_parts < sc.sticky[aggregation_id].p_count:
            
            sc.sticky[aggregation_id].remove_elements(num_parts)
        
        return sc.sticky[aggregation_id]
        
    else:
        return -1


result = main(PART, PREV, N, RULES, MODE, GC, ID, RESET, FIELD)

if result != -1:
    AGGR = result
    PART_OUT = result.aggregated_parts