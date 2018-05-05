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
Provided by Wasp 0.1.0
    Args:
        PART: Parts to be aggregated (can be more than one)
        PREV: Previous aggregated parts. It is possible to input the results of a previous aggregation, or parts transformed with the TransformPart component
        N: Number of parts to be aggregated (does not count parts provided in PREV)
        RULES: Rules for the aggregation
        COLL: OPTIONAL // Collision detection. By default is active and checks for collisions between the aggregated parts
        MODE: OPTIONAL // Switches between aggregation modes: 0 = Basic (Default: only parts collision check), 1 = Constrained (checks all constraints set on the part)
        GC: Global constraints to apply to aggregation
        ID: OPTIONAL // Aggregation ID (to avoid overwriting when having different aggregation components in the same file)
        RESET: Recompute the whole aggregation
    Returns:
        PART_OUT: Aggregated parts (includes both PREV input and newly aggregated parts)
"""

ghenv.Component.Name = "Wasp_Stochastic Aggregation"
ghenv.Component.NickName = 'RndAggr'
ghenv.Component.Message = 'VER 0.2.0'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "4 | Aggregation"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import Rhino.Geometry as rg
import Grasshopper.Kernel as gh
import random as rnd


def main(parts, previous_parts, num_parts, rules, aggregation_mode, global_constraints, aggregation_id, reset):
    
    ## check if Wasp is setup
    if sc.sticky.has_key('WaspSetup'):
        
        check_data = True
        
        ##check inputs
        if len(parts) == 0:
            check_data = False
            msg = "No parts provided"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
        if num_parts is None:
            check_data = False
            msg = "Provide number of aggregation iterations"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        else:
            if len(previous_parts) != 0:
                num_parts += len(previous_parts)
        
        if len(rules) == 0:
            check_data = False
            msg = "No rules provided"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
        if aggregation_mode is None:
            aggregation_mode = 0
        
        if aggregation_id is None:
            aggregation_id = 'myAggregation'
            msg = "Default name 'myAggregation' assigned"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, msg)
        
        if reset is None:
            reset = False
        
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
                sc.sticky[aggregation_id] = sc.sticky['Aggregation'](aggregation_id, parts, sc.sticky['rules'], aggregation_mode, _prev = previous_parts, _global_constraints = global_constraints)
            
            if reset:
                sc.sticky[aggregation_id] = sc.sticky['Aggregation'](aggregation_id, parts, sc.sticky['rules'], aggregation_mode, _prev = previous_parts, _global_constraints = global_constraints)
            
            if num_parts > sc.sticky[aggregation_id].p_count:
                sc.sticky[aggregation_id].aggregate_rnd(num_parts-sc.sticky[aggregation_id].p_count)
            
            elif num_parts < sc.sticky[aggregation_id].p_count:
                sc.sticky[aggregation_id].remove_elements(num_parts)
                
            return sc.sticky[aggregation_id].aggregated_parts
            
        else:
            return -1
    
    else:
        ## throw warining
        msg = "You must run the SetupWasp component before starting to build!"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1


result = main(PART, PREV, N, RULES, MODE, GC, ID, RESET)

if result != -1:
    PART_OUT = result