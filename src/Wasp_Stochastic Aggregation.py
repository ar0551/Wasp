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
        ID: OPTIONAL // Aggregation ID (to avoid overwriting when having different aggregation components in the same file)
        RESET: Recompute the whole aggregation
    Returns:
        PART_OUT: Aggregated parts (includes both PREV input and newly aggregated parts)
"""

ghenv.Component.Name = "Wasp_Stochastic Aggregation"
ghenv.Component.NickName = 'RndAggr'
ghenv.Component.Message = 'VER 0.1.0\nDEC_22_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "4 | Aggregation"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import Rhino.Geometry as rg
import Grasshopper.Kernel as gh
import random as rnd


def aggregate(aggr_id, aggr_parts, aggr_rules, iter, aggr_coll, aggr_mode):
    count = 0
    loops = 0
    while count < iter:
        loops += 1
        if loops > iter*100:
            break
        ## if no part is present in the aggregation, add first random part
        if len(sc.sticky[aggr_id]) == 0:
            count += 1
            first_part = aggr_parts[rnd.randint(0, len(aggr_parts)-1)]
            for conn in first_part.connections:
                conn.generate_rules_table(aggr_rules)
            sc.sticky[aggr_id].append(first_part)
        
        else:
            next_rule = None
            part_01_id = -1
            conn_01_id = -1
            next_rule_id = -1
            new_rule_attempts = 0
            
            while new_rule_attempts < 1000:
                new_rule_attempts += 1
                part_01_id = rnd.randint(0, len(sc.sticky[aggr_id])-1)
                part_01 = sc.sticky[aggr_id][part_01_id]
                if len(part_01.active_connections) > 0:
                    conn_01_id = part_01.active_connections[rnd.randint(0, len(part_01.active_connections)-1)]
                    conn_01 = part_01.connections[conn_01_id]
                    if len(conn_01.active_rules) > 0:
                        next_rule_id = conn_01.active_rules[rnd.randint(0, len(conn_01.active_rules)-1)]
                        next_rule = conn_01.rules_table[next_rule_id]
                        break
            
            if next_rule == None:
                msg = "aborted after " + str(count) + " iterations"
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                break
            
            next_part = None
            for part in aggr_parts:
                if part.name == next_rule.part2:
                    next_part = part
            
            orientTransform = rg.Transform.PlaneToPlane(next_part.connections[next_rule.conn2].flip_pln, conn_01.pln)
            next_part_center = next_part.transform_center(orientTransform)
            
            ## overlap check
            close_neighbour_check = False
            for ex_part in sc.sticky[aggr_id]:
                dist = ex_part.center.DistanceTo(next_part_center)
                if dist < sc.sticky['model_tolerance']:
                    close_neighbour_check = True
                    break
            
            ## collision check
            collision_check = False
            if aggr_coll == True and close_neighbour_check == False:
                next_part_collider = next_part.transform_collider(orientTransform)
                for ex_part in sc.sticky[aggr_id]:
                    intersections = rg.Intersect.Intersection.MeshMeshFast(ex_part.collider, next_part_collider)
                    if len(intersections) > 0:
                        collision_check = True
                        break
            
            ## constraints check
            add_collision_check = False
            missing_supports_check = False
            if aggr_mode == 1:
                if close_neighbour_check == False and collision_check == False:
                    if next_part.is_constrained:
                        
                        ## additional collider check
                        if next_part.add_collider != None:
                            add_collider = next_part.add_collider.Duplicate()
                            add_collider.Transform(orientTransform)
                            for ex_part in sc.sticky[aggr_id]:
                                intersections = rg.Intersect.Intersection.MeshMeshFast(ex_part.collider, add_collider)
                                if len(intersections) > 0:
                                    add_collision_check = True
                                    break
                        
                        ## supports check
                        if add_collision_check == False:
                            if len(next_part.supports) > 0:
                                for sup in next_part.supports:
                                    missing_supports_check = True
                                    supports_count = 0
                                    for dir in sup.sup_dir:
                                        dir_trans = dir.Duplicate()
                                        dir_trans.Transform(orientTransform)
                                        
                                        for ex_part in sc.sticky[aggr_id]:
                                            if len(rg.Intersect.Intersection.MeshPolyline(ex_part.collider, dir_trans)[0]) > 0:
                                                supports_count += 1
                                                break
                                    if supports_count == len(sup.sup_dir):
                                        missing_supports_check = False
                                        break
            
            if close_neighbour_check == False and collision_check == False and add_collision_check == False and missing_supports_check == False:
                next_part_trans = next_part.transform(orientTransform)
                next_part_trans.reset_part(aggr_rules)
                for i in range(len(next_part_trans.active_connections)):
                    if next_part_trans.active_connections[i] == next_rule.conn2:
                        next_part_trans.active_connections.pop(i)
                        break
                sc.sticky[aggr_id].append(next_part_trans)
                sc.sticky[aggr_id][part_01_id].children.append(next_part_trans)
                for i in range(len(sc.sticky[aggr_id][part_01_id].active_connections)):
                    if sc.sticky[aggr_id][part_01_id].active_connections[i] == conn_01_id:
                        sc.sticky[aggr_id][part_01_id].active_connections.pop(i)
                        break
                count += 1
            else:
               ## remove rules if they cause collisions or overlappings
               for i in range(len(sc.sticky[aggr_id][part_01_id].connections[conn_01_id].active_rules)):
                   if sc.sticky[aggr_id][part_01_id].connections[conn_01_id].active_rules[i] == next_rule_id:
                       sc.sticky[aggr_id][part_01_id].connections[conn_01_id].active_rules.pop(i)
                       break
               ## check if the connection is still active (still active rules available)
               if len(sc.sticky[aggr_id][part_01_id].connections[conn_01_id].active_rules) == 0:
                   for i in range(len(sc.sticky[aggr_id][part_01_id].active_connections)):
                    if sc.sticky[aggr_id][part_01_id].active_connections[i] == conn_01_id:
                        sc.sticky[aggr_id][part_01_id].active_connections.pop(i)
                        break


def main(parts, previous_parts, num_parts, rules, collision, aggregation_mode, aggregation_id, reset):
    
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
        
        if collision is None:
            collision = True
        
        if aggregation_mode is None:
            aggregation_mode = 0
        
        if aggregation_id is None:
            aggregation_id = 'Aggregation'
            msg = "Default name 'Aggregation' assigned"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, msg)
        
        if reset is None:
            reset = False
        
        if check_data:
            if sc.sticky.has_key(aggregation_id) == False:
                sc.sticky[aggregation_id] = []
            
            if reset:
                sc.sticky[aggregation_id] = []
                
                for part in parts:
                    part.reset_part(rules)
                
                if len(previous_parts) > 0:
                    for part in previous_parts:
                        part.reset_part(rules)
                        sc.sticky[aggregation_id].append(part)
            
            if num_parts > len(sc.sticky[aggregation_id]):
                aggregate(aggregation_id, parts, rules, num_parts - len(sc.sticky[aggregation_id]), collision, aggregation_mode)
                if len(sc.sticky[aggregation_id]) < num_parts:
                    msg = "Could not place " + str(num_parts - len(sc.sticky[aggregation_id])) + " parts"
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    
            
            elif num_parts < len(sc.sticky[aggregation_id]):
                sc.sticky[aggregation_id] = sc.sticky[aggregation_id][:num_parts]
                for part in sc.sticky[aggregation_id]:
                    part.reset_part(rules)
                
                for part in parts:
                    part.reset_part(rules)
            
            return sc.sticky[aggregation_id]
            
        else:
            return -1
    
    else:
        ## throw warining
        msg = "You must run the SetupWasp component before starting to build!"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1


result = main(PART, PREV, N, RULES, COLL, MODE, ID, RESET)

if result != -1:
    PART_OUT = result