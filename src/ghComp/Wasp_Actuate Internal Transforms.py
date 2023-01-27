# Wasp: Discrete Design with Grasshopper plug-in (LGPL) initiated by Andrea Rossi
# 
# This file is part of Wasp.
# 
# Copyright (c) 2017, Andrea Rossi <a.rossi.andrea@gmail.com>
# Wasp is free software; you can redistribute it and/or modify 
# it under the terms of the GNU Lesser General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Wasp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with Wasp; If not, see <http://www.gnu.org/licenses/>.
# 
# @license LGPL-3.0 https://www.gnu.org/licenses/lgpl-3.0.html
#
# Significant parts of Wasp have been developed by Andrea Rossi
# as part of research on digital materials and discrete design at:
# DDU Digital Design Unit - Prof. Oliver Tessmann
# Technische Universitt Darmstadt


#########################################################################
##                            COMPONENT INFO                           ##
#########################################################################

"""
Actuates predefined internal transformations, chaining them to transform the full aggregation while maintaining connectivity.
NB! At the current stage only open chains are supported, closed loops might be broken.
-
Provided by Wasp 0.5
    Args:
        AGGR: Aggregation to transform
        VAL: Transformation values (0-1). Can use a single value for all parts, or a value for each transformable part
        RESET: True to reset the transformation process. Necessary when the input aggregation changes
    Returns:
        AGGR_OUT: Transformed aggregation
        PART_OUT: Transformed parts
        COLL_ID: IDs of colliding parts
"""

ghenv.Component.Name = "Wasp_Actuate Internal Transforms"
ghenv.Component.NickName = 'ActIntTrans'
ghenv.Component.Message = 'v0.5.007'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "X | Experimental"
try: ghenv.Component.AdditionalHelpFromDocStrings = "6"
except: pass

import sys
import copy
import scriptcontext as sc
import Rhino.Geometry as rg
import Grasshopper as gh
import random as rnd
import math

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


def main(base_aggregation, input_values, reset, aggregation):
    
    def transform_children(part, trans, count):
        
        if count == 0:
            count += 1
        else:
            aggregation.aggregated_parts[part.id] = part.transform(trans)
        
        aggregation.aggregated_parts[part.id].parent = part.parent
        aggregation.aggregated_parts[part.id].children = part.children
        
        for child_id in part.children:
            transform_children(aggregation.aggregated_parts[child_id], trans, count)
    
    
    def remap(old_value, old_min, old_max, new_min, new_max):
        old_range = (old_max - old_min)
        if (old_range == 0):
            new_value = new_min
        else:
            new_range = (new_max - new_min)  
            new_value = (((old_value - old_min) * new_range) / old_range) + new_min
        return new_value
    
    
    check_data = True
    
    ##check inputs
    
    ## count number of active modules
    active_modules_count = 0
    if base_aggregation is None:
        check_data = False
        msg = "No aggregation provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    else:
        for part in base_aggregation.aggregated_parts:
                if part.name[:3] == "ACT":
                    active_modules_count += 1
    
    tr_values = []
    if len(input_values) == 0:
        check_data = False
        msg = "Provide angle for transformation"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    elif len(input_values) == 1:
        tr_value = input_values[0]
        for part in base_aggregation.aggregated_parts:
            if part.name[:3] == "ACT":
                tr_values.append(tr_value)
            else:
                tr_values.append(0)
    
    elif len(input_values) == active_modules_count:
        input_count = 0
        for part in base_aggregation.aggregated_parts:
            if part.name[:3] == "ACT":
                tr_values.append(input_values[input_count])
                input_count += 1
            else:
                tr_values.append(0)
    
    elif len(input_values) != active_modules_count:
        check_data = False
        msg = "Number of angles and active parts do not match"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)
    
    if reset is None:
        reset = False
    
    if check_data:
        new_name = base_aggregation.name + "_edit"
        colliding_ids = []
        
        if reset or aggregation is None:
            parts_list = [base_aggregation.parts[key] for key in base_aggregation.parts]
            aggregation = copy.deepcopy(base_aggregation)
            aggregation.name = new_name
            
            sc.sticky[new_name + "_angle"] = []
            for i in xrange(len(aggregation.aggregated_parts)):
                sc.sticky[new_name + "_angle"].append(0)
        
        
            
        ## transform aggregation
        for i in xrange(len(aggregation.aggregated_parts)):
            
            if aggregation.aggregated_parts[i].name[:3] == "ACT":
                
                int_transform = aggregation.aggregated_parts[i].attributes[0]
                
                ## translation
                if int_transform.transform_type == 0:
                    axis_line = int_transform.values[2]
                    current_pt = axis_line.PointAtNormalizedLength(int_transform.current_pos)
                    target_pt = axis_line.PointAtNormalizedLength(tr_values[i])
                    
                    #########################################################3 CHECK ORDER!
                    move_vec = rg.Vector3d.Subtract(rg.Vector3d(target_pt), rg.Vector3d(current_pt))
                    translation_transform = rg.Transform.Translation(move_vec)
                    
                    int_transform.values[1].Transform(translation_transform)
                    transform_children(aggregation.aggregated_parts[i], translation_transform, 0)
                    
                    int_transform.current_pos = tr_values[i]
                
                ## rotation
                elif int_transform.transform_type == 1:
                    current_angle = remap(int_transform.current_pos, 0,1, int_transform.transform_domain[0], int_transform.transform_domain[1])
                    target_angle = remap(tr_values[i], 0,1, int_transform.transform_domain[0], int_transform.transform_domain[1])
                    angle_diff = math.radians(target_angle-current_angle)
                    
                    axis_line = int_transform.values[2]
                    axis_vec = rg.Vector3d.Subtract(rg.Vector3d(axis_line.PointAtEnd), rg.Vector3d(axis_line.PointAtStart))
                    rotation_transform = rg.Transform.Rotation(angle_diff, axis_vec, axis_line.PointAtStart)
                    
                    int_transform.values[1].Transform(rotation_transform)
                    transform_children(aggregation.aggregated_parts[i], rotation_transform, 0)
                    
                    int_transform.current_pos = remap(target_angle, int_transform.transform_domain[0], int_transform.transform_domain[1], 0,1)
        
       ## check for collisions
        parts_ids = xrange(len(aggregation.aggregated_parts))
        for part in aggregation.aggregated_parts:
            collision_ids = list(parts_ids)
            collision_ids.remove(part.id)
            if part.parent in collision_ids:
                collision_ids.remove(part.parent)
            for ch in part.children:
                if ch in collision_ids:
                    collision_ids.remove(ch)
            if part.collider.check_collisions_by_id(aggregation.aggregated_parts, collision_ids):
                colliding_ids.append(part.id)
            
        return aggregation, colliding_ids
        
    else:
        return -1

## create aggregation container in global variables dict
if 'aggregation_container' not in globals():
    aggregation_container = None

result = main(AGGR, VAL, RESET, aggregation_container)

if result != -1:
    AGGR_OUT = result[0]
    PART_OUT = result[0].aggregated_parts
    COLL_ID = result[1]