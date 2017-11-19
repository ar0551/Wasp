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
Provided by Wasp 0.0.04
    Args:
        PART: Parts to be aggregated (can be more than one)
        PREV: Previous aggregated parts. It is possible to input the results of a previous aggregation, or parts transformed with the TransformPart component
        N: Number of parts to be aggregated (does not count parts provided in PREV)
        RULES: Rules for the aggregation
        FIELD: Scalar field to drive the aggregation (parts will be added following higher values in the field)
        THRES: OPTIONAL // If set, used to define a threshold value above which the placement of next part is accepted. If not set, aggregation will look for part with highest value in the whole field. Setting a low threshold helds less accurate results, but highly speeds up calculations
        COLL: OPTIONAL // Collision detection. By default is active and checks for collisions between the aggregated parts
        ID: OPTIONAL // Aggregation ID (to avoid overwriting when having different aggregation components in the same file)
        RESET: Recompute the whole aggregation
    Returns:
        PART_OUT: Aggregated parts (includes both PREV input and newly aggregated parts)
"""

ghenv.Component.Name = "Wasp_Field-driven Aggregation"
ghenv.Component.NickName = 'FieldAggregation'
ghenv.Component.Message = 'VER 0.0.04\nNOV_19_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "0 | Wasp"
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass


import scriptcontext as sc
import Rhino.Geometry as rg
import Grasshopper.Kernel as gh
import random as rnd
import math
import copy


## find the rule that creates a component as closest as possible to the target surface
def findBestRule(aggr_id, aggr_parts, aggr_field, thres, aggr_coll):
    max_val = 0
    best_rule = None
    best_conn = None
    best_conn_id = -1
    
    for i in range(len(sc.sticky[aggr_id])):
        part_01 = sc.sticky[aggr_id][i]
        for i2 in range(len(part_01.active_connections)-1, -1, -1):
            conn_01_id = part_01.active_connections[i2]
            conn_01 = part_01.connections[conn_01_id]
            for i3 in range(len(conn_01.active_rules)-1, -1, -1):
                rule_id = conn_01.active_rules[i3]
                rule = conn_01.rules_table[rule_id]
                
                next_part = None
                for part in aggr_parts:
                    if part.name == rule.part2:
                        next_part = part
                        break
                        
                next_center = rg.Point3d(next_part.center)
                orientTransform = rg.Transform.PlaneToPlane(next_part.connections[rule.conn2].flip_pln, conn_01.pln)
                next_center.Transform(orientTransform)
                
                if aggr_field.bbox.Contains(next_center) == True:
                    current_target_val = aggr_field.return_pt_val(next_center)
                    if current_target_val > max_val:
                        close_neighbour_check = False
                        for ex_part in sc.sticky[aggr_id]:
                            dist = ex_part.center.DistanceTo(next_center)
                            if dist < sc.sticky['model_tolerance']:
                                close_neighbour_check = True
                                break
                        
                        collision_check = False
                        if aggr_coll == True and close_neighbour_check == False:
                            next_part_collider = next_part.transform_collider(orientTransform)
                            for ex_part in sc.sticky[aggr_id]:
                                if len(rg.Intersect.Intersection.MeshMeshFast(ex_part.collider, next_part_collider)) > 0:
                                    collision_check = True
                                    break
                        
                        if close_neighbour_check == False and collision_check == False:
                            max_val = current_target_val
                            best_rule = rule
                            best_conn = conn_01
                            best_part_id = i
                            best_conn_id = conn_01_id
                            
                            if thres is not None and max_val > thres:
                                break
                            
                        else:
                            ## remove rules if they cause collisions or overlappings
                            for i4 in range(len(sc.sticky[aggr_id][i].connections[conn_01_id].active_rules)):
                               if sc.sticky[aggr_id][i].connections[conn_01_id].active_rules[i4] == rule_id:
                                   sc.sticky[aggr_id][i].connections[conn_01_id].active_rules.pop(i4)
                                   break
                            ## check if the connection is still active (still active rules available)
                            if len(sc.sticky[aggr_id][i].connections[conn_01_id].active_rules) == 0:
                               for i4 in range(len(sc.sticky[aggr_id][i].active_connections)):
                                if sc.sticky[aggr_id][i].active_connections[i4] == conn_01_id:
                                    sc.sticky[aggr_id][i].active_connections.pop(i4)
                                    break
            if thres is not None and max_val > thres:
                break
        if thres is not None and max_val > thres:
            break
    
    if best_rule is not None:
        return best_conn, best_part_id, best_conn_id, best_rule.part2, best_rule.conn2, best_rule
    else:
        return -1, -1, -1, -1, -1, -1



def aggregate_field(aggr_id, aggr_parts, aggr_rules, aggr_field, aggr_threshold, aggr_coll, iter):
    count = 0
    loops = 0
    while count < iter:
        ## if no part is present in the aggregation, add first random part
        if len(sc.sticky[aggr_id]) == 0:
            count += 1
            first_part = aggr_parts[rnd.randint(0, len(aggr_parts)-1)]
            
            start_point = aggr_field.highest_pt
            mov_vec = rg.Vector3d.Subtract(rg.Vector3d(start_point), rg.Vector3d(first_part.center))
            move_transform = rg.Transform.Translation(mov_vec.X, mov_vec.Y, mov_vec.Z)
            first_part_trans = first_part.transform(move_transform)
            
            for conn in first_part_trans.connections:
                conn.generate_rules_table(aggr_rules)
            
            sc.sticky[aggr_id].append(first_part_trans)
        
        else:
            ## select part-rule couple creating next part in the highest point of field
            conn_01, part_01_id, conn_01_id, next_part_name, next_conn_id, next_rule = findBestRule(aggr_id, aggr_parts, aggr_field, aggr_threshold, aggr_coll)
            
            if conn_01_id == -1:
                msg = "aborted after " + str(count) + " iterations"
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                break
            
            next_part = None
            for part in aggr_parts:
                if part.name == next_part_name:
                    next_part = part
            
            orientTransform = rg.Transform.PlaneToPlane(next_part.connections[next_conn_id].flip_pln, conn_01.pln)
            next_part_center = next_part.transform_center(orientTransform)
            
            next_part_trans = next_part.transform(orientTransform)
            next_part_trans.reset_part(aggr_rules)
            for i in range(len(next_part_trans.active_connections)):
                if next_part_trans.active_connections[i] == next_rule.conn2:
                    next_part_trans.active_connections.pop(i)
                    break
            sc.sticky[aggr_id].append(next_part_trans)
            
            count += 1
            if count == iter:
                print "successfully completed all " + str(count) + " iterations"



def main(parts, previous_parts, num_parts, rules, field, threshold, collision, aggregation_id, reset):
    
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
        
        if field is None:
            check_data = False
            msg = "Provide a valid scalar field"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
        if collision is None:
            collision = True
        
        if aggregation_id is None:
            aggregation_id = 'Aggregation'
        
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
                aggregate_field(aggregation_id, parts, rules, field, threshold, collision, num_parts - len(sc.sticky[aggregation_id]))
            
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


result = main(PART, PREV, N, RULES, FIELD, THRES, COLL, ID, RESET)

if result != -1:
    PART_OUT = result