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
This components initialized all classes and variables required by Wasp to run.
You must run this component before starting to work with Wasp, or other components will not work properly.

-
Wasp: Discrete Design with Grasshopper plug-in (GPL) initiated by Andrea Rossi
You should have received a copy of the GNU General Public License
along with Wasp; If not, see <http://www.gnu.org/licenses/>.

@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

Source code is available at: https://github.com/ar0551/Wasp
-
Provided by Wasp 0.1.0
    Args:
        RUN: Setup all classes and variables required to run Wasp. Set it to True to start building.
    Returns:
        log: log
"""

ghenv.Component.Name = "Wasp_Setup"
ghenv.Component.NickName = 'WaspSetup'
ghenv.Component.Message = 'VER 0.2.0'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "0 | Wasp"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass



#########################################################################
##                               IMPORTS                               ##
#########################################################################
import random as rnd
import math
import bisect as bs
import scriptcontext as sc
import Rhino.Geometry as rg
import Rhino
import Grasshopper.Kernel as gh

#########################################################################
##                               CLASSES                               ##
#########################################################################

#################################################################### Connection
class Connection(object):
    
    ## constructor
    def __init__(self, plane, type, part, id):
        
        self.pln = plane
        
        flip_pln_Y = rg.Vector3d(plane.YAxis)
        flip_pln_Y.Reverse()
        self.flip_pln = rg.Plane(plane.Origin, plane.XAxis, flip_pln_Y)
        
        self.type = type
        self.part = part
        self.id = id
        
        self.rules_table = []
        self.active_rules = []
    
    ## return a transformed copy of the connection
    def transform(self, trans):
        pln_trans = rg.Plane(self.pln.Origin, self.pln.XAxis, self.pln.YAxis)
        conn_trans = Connection(pln_trans, self.type, self.part, self.id)
        conn_trans.pln.Transform(trans)
        conn_trans.flip_pln.Transform(trans)
        return conn_trans
    
    ## generate the rules-table for the connection
    def generate_rules_table(self, rules):
        count = 0
        self.rules_table = []
        self.active_rules = []
        for rule in rules:
            if rule.part1 == self.part and rule.conn1 == self.id:
                self.rules_table.append(rule)
                self.active_rules.append(count)
                count += 1

#################################################################### Base Component
class Part(object):
    
    ## constructor
    def __init__(self, name, geometry, connections, collider, attributes, dim=None):
        
        self.name = name
        self.geo = geometry
        
        self.connections = []
        self.active_connections = []
        count = 0
        for conn in connections:
            conn.part = self.name
            conn.id = count
            self.connections.append(conn)
            self.active_connections.append(count)
            count += 1
        
        self.transformation = rg.Transform.Identity
        self.center = self.geo.GetBoundingBox(False).Center
        self.collider = collider
        
        ##part size
        if dim is not None:
            self.dim = dim
        else:
            max_collider_dist = None
            for v in self.collider.Vertices:
                dist = self.center.DistanceTo(v)
                if dist > max_collider_dist or max_collider_dist is None:
                    max_collider_dist = dist
            
            self.dim = max_collider_dist
        
        self.children = []
        
        self.attributes = []
        if len(attributes) > 0:
            self.attributes = attributes
        
        self.is_constrained = False
    
    def reset_part(self, rules):
        count = 0
        self.active_connections = []
        for conn in self.connections:
            conn.generate_rules_table(rules)
            self.active_connections.append(count)
            count += 1
    
    def return_part_data(self):
        data_dict = {}
        data_dict['name'] = self.name
        data_dict['geo'] = self.geo
        data_dict['connections'] = self.connections
        data_dict['transform'] = self.transformation
        data_dict['center'] = self.center
        data_dict['children'] = self.children
        data_dict['attributes'] = self.attributes
        return data_dict
    
    ## function to transform part
    def transform(self, trans):
        geo_trans = self.geo.Duplicate()
        geo_trans.Transform(trans)
        
        collider_trans = self.collider.Duplicate()
        collider_trans.Transform(trans)
        
        connections_trans = []
        for conn in self.connections:
            connections_trans.append(conn.transform(trans))
        
        attributes_trans = []
        if len(self.attributes) > 0:
            for attr in self.attributes:
                attributes_trans.append(attr.transform(trans))
        
        part_trans = Part(self.name, geo_trans, connections_trans, collider_trans, attributes_trans, dim = self.dim)
        part_trans.transformation = trans
        return part_trans
    
    ## return transformed center point
    def transform_center(self, trans):
        center_trans = rg.Point3d(self.center)
        center_trans.Transform(trans)
        return center_trans
    
    ## return transformed collider mesh
    def transform_collider(self, trans):
        collider_trans = self.collider.Duplicate()
        collider_trans.Transform(trans)
        return collider_trans


#################################################################### Constrained Component
class Constrained_Part(Part):
    
    ## constructor
    def __init__(self, name, geometry, connections, collider, attributes, additional_collider, supports, dim = None):
        
        super(self.__class__, self).__init__(name, geometry, connections, collider, attributes, dim)
        
        self.add_collider = None
        if additional_collider != None:
            self.add_collider = additional_collider
        
        self.supports = []
        if len(supports) > 0:
            self.supports = supports
    
    ## function to transform component
    def transform(self, trans):
        geo_trans = self.geo.Duplicate()
        geo_trans.Transform(trans)
        
        collider_trans = self.collider.Duplicate()
        collider_trans.Transform(trans)
        
        connections_trans = []
        for conn in self.connections:
            connections_trans.append(conn.transform(trans))
        
        attributes_trans = []
        if len(self.attributes) > 0:
            for attr in self.attributes:
                attributes_trans.append(attr.transform(trans))
        
        add_collider_trans = None
        if(self.add_collider != None):
            add_collider_trans = self.add_collider.Duplicate()
            add_collider_trans.Transform(trans)
            
        supports_trans = []
        if len(self.supports) > 0:
            for sup in self.supports:
                sup_trans = sup.transform(trans)
                supports_trans.append(sup_trans)
        
        part_trans = Constrained_Part(self.name, geo_trans, connections_trans, collider_trans, attributes_trans, add_collider_trans, supports_trans, dim = self.dim)
        part_trans.transformation = trans
        part_trans.is_constrained = True
        return part_trans


#################################################################### Rule
class Rule(object):
    
    def __init__(self, _part1, _conn1, _part2, _conn2, _active = True, GH_Component = None):
        
        self.gh = GH_Component
        
        self.part1 = _part1
        self.conn1 = _conn1
        self.part2 = _part2
        self.conn2 = _conn2
        self.active = _active


#################################################################### Field
class Field(object):
    
    def __init__(self, boundaries, pts, count_vec, resolution, values):
        
        self.resolution = resolution
        
        self.bbox = rg.BoundingBox(pts)
        
        self.x_count = int(count_vec.X)
        self.y_count = int(count_vec.Y)
        self.z_count = int(count_vec.Z)
        
        self.pts = []
        self.vals = []
        pts_count = 0
        
        self.is_tensor_field = False
        try:
            v = values[0][2]
            self.is_tensor_field = True
        except:
            pass
        
        for z in range(0, self.z_count):
            self.pts.append([])
            self.vals.append([])
            for y in range(0, self.y_count):
                self.pts[z].append([])
                self.vals[z].append([])
                for x in range(0, self.x_count):
                    self.pts[z][y].append(pts[pts_count])
                    if len(boundaries) > 0:
                        inside = False
                        for bou in boundaries:
                            if bou.IsPointInside(pts[pts_count], sc.sticky['model_tolerance'], True) == True:
                                self.vals[z][y].append(values[pts_count])
                                inside = True
                                break
                        if inside == False:
                            if self.is_tensor_field:
                                self.vals[z][y].append(rg.Vector3d(0,0,0))
                            else:
                                self.vals[z][y].append(0.0)
                    else:
                        self.vals[z][y].append(values[pts_count])
                    pts_count += 1
        
        self.highest_pt = self.return_highest_pt()
    
    
    def return_pt_val(self, pt):
        pt_trans = pt - self.bbox.Min
        x = int(math.floor(pt_trans.X/self.resolution))
        y = int(math.floor(pt_trans.Y/self.resolution))
        z = int(math.floor(pt_trans.Z/self.resolution))
        
        value = self.vals[z][y][x]
        return value
    
    def return_highest_pt(self):
        max_val = -1
        highest_pt = None
        
        for z in range(0, self.z_count):
            for y in range(0, self.y_count):
                for x in range(0, self.x_count):
                    value = self.vals[z][y][x]
                    if self.is_tensor_field:
                        if value.Length > max_val:
                            max_val = value
                            highest_pt = self.pts[z][y][x]
                    else:
                        if value > max_val:
                            max_val = value
                            highest_pt = self.pts[z][y][x]
        
        return highest_pt


#################################################################### Attribute
class Attribute(object):
    
    def __init__(self, name, values, transformable):
        
        self.name = name
        self.values = values
        self.transformable = transformable
    
    def transform(self, trans):
        if self.transformable == True:
            values_trans = []
            for val in self.values:
                val_trans = None
                if type(val) == rg.Point3d:
                    val_trans = rg.Point3d(val)
                elif type(val) == rg.Plane:
                    val_trans = rg.Plane(val)
                else:
                    val_trans = val.Duplicate()
                val_trans.Transform(trans)
                values_trans.append(val_trans)
            attr_trans = Attribute(self.name, values_trans, self.transformable)
        else:
            attr_trans = Attribute(self.name, self.values, self.transformable)
        return attr_trans


#################################################################### Support
class Support(object):
    
    def __init__(self, support_directions):
        self.sup_dir = support_directions
    
    def transform(self, trans):
        sup_dir_trans = []
        for dir in self.sup_dir:
            start_trans = dir.PointAtStart
            end_trans = dir.PointAtEnd
            start_trans.Transform(trans)
            end_trans.Transform(trans)
            dir_trans = rg.Line(start_trans, end_trans)
            sup_dir_trans.append(dir_trans)
        sup_trans = Support(sup_dir_trans)
        return sup_trans


#########################################################################
##                                 WIP                                 ##
#########################################################################

## Aggregation class
class Aggregation(object):
    
    ## class constructor
    def __init__(self, name, parts, rules, mode, prev = None, coll_check = True, field = None):
        
        ## basic parameters
        self.name = name
        
        self.parts = {}
        for part in parts:
            self.parts[part.name] = part
        
        self.rules = rules
        
        self.reset_parts()
        
        self.mode = mode
        self.coll_check = coll_check
        
        self.field = field
        
        ## lists
        self.aggregated_parts = []
        self.p_count = 0
        
        ## aggregation queue, storing sorted possible next states in the form (part, f_val)
        self.aggregation_queue = []
        self.queue_values = []
        self.queue_count = 0
        
        ## previous aggregated parts
        self.prev_num = 0
        if prev is not None:
            self.prev_num = len(prev)
            for prev_p in prev:
                prev_p.reset_part(self.rules)
                self.aggregated_parts.append(prev_p)
                
                if self.field is not None:
                    self.compute_next_w_field(prev_p, self.p_count)
                
                self.p_count += 1
        
        ## WIP
        self.collision_shapes = []
        self.graph = None
    
    ## reset entire aggregation
    def reset(self):
        self.aggregated_parts = []
        self.p_count = 0
        self.aggregation_queue = []
        self.queue_values = []
        self.queue_count = 0
        
        self.reset_parts()
        
        if prev is not None:
            for prev_p in prev:
                prev_p.reset_part(self.rules)
                self.aggregated_parts.append(prev_p)
                
                if self.field is not None:
                    self.compute_next_w_field(prev_p, self.p_count)
                
                self.p_count += 1
    
    ## reset all base parts
    def reset_parts(self):
        for p_key in self.parts:
            self.parts[p_key].reset_part(self.rules)
    
    ## reset rules and regenerate rule tables for each part
    def reset_rules(self, rules):
        if rules != self.rules:
            self.rules = rules
            self.reset_parts()
    
    ## trim aggregated parts list to a specific length
    def remove_elements(self, num):
        self.aggregated_parts = self.aggregated_parts[:num]
        
        self.aggregation_queue = []
        self.queue_values = []
        self.queue_count = 0
        
        for part in self.aggregated_parts:
            part.reset_part(self.rules)
            if self.field is not None:
                self.compute_next_w_field(part, self.p_count)
            
        self.p_count -= (self.p_count - num)
    
    ## stochastic aggregation (BASIC)
    def aggregate_rnd(self, num):
        added = 0
        loops = 0
        while added < num:
            loops += 1
            if loops > num*100:
                break
            ## if no part is present in the aggregation, add first random part
            if self.p_count == 0:
                first_part = self.parts[rnd.choice(self.parts.keys())]
                for conn in first_part.connections:
                    conn.generate_rules_table(self.rules)
                self.aggregated_parts.append(first_part)
                added += 1
                self.p_count += 1
            ## otherwise add new random part
            else:
                next_rule = None
                part_01_id = -1
                conn_01_id = -1
                next_rule_id = -1
                new_rule_attempts = 0
                
                while new_rule_attempts < 1000:
                    new_rule_attempts += 1
                    part_01_id = rnd.randint(0,self.p_count-1)
                    part_01 = self.aggregated_parts[part_01_id]
                    if len(part_01.active_connections) > 0:
                        conn_01_id = part_01.active_connections[rnd.randint(0, len(part_01.active_connections)-1)]
                        conn_01 = part_01.connections[conn_01_id]
                        if len(conn_01.active_rules) > 0:
                            next_rule_id = conn_01.active_rules[rnd.randint(0, len(conn_01.active_rules)-1)]
                            next_rule = conn_01.rules_table[next_rule_id]
                            break
                """
                if next_rule == None:
                    msg = "aborted after " + str(count) + " iterations"
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    break
                """
                if next_rule is not None:
                    next_part = self.parts[next_rule.part2]
                    orientTransform = rg.Transform.PlaneToPlane(next_part.connections[next_rule.conn2].flip_pln, conn_01.pln)
                    next_part_center = next_part.transform_center(orientTransform)
                    
                    ## overlap check
                    close_neighbour_check = False
                    possible_collisions = []
                    coll_count = 0
                    for ex_part in self.aggregated_parts:
                        dist = ex_part.center.DistanceTo(next_part_center)
                        if dist < sc.sticky['model_tolerance']:
                            close_neighbour_check = True
                            break
                        elif dist < ex_part.dim + next_part.dim:
                            possible_collisions.append(coll_count)
                        coll_count += 1
                    
                    ## collision check
                    collision_check = False
                    if self.coll_check == True and close_neighbour_check == False:
                        next_part_collider = next_part.transform_collider(orientTransform)
                        for id in possible_collisions:
                            if len(rg.Intersect.Intersection.MeshMeshFast(self.aggregated_parts[id].collider, next_part_collider)) > 0:
                                collision_check = True
                                break
                    
                    ## constraints check
                    add_collision_check = False
                    missing_supports_check = False
                    if self.mode == 1:
                        if close_neighbour_check == False and collision_check == False:
                            if next_part.is_constrained:
                                
                                ## additional collider check
                                if next_part.add_collider != None:
                                    add_collider = next_part.add_collider.Duplicate()
                                    add_collider.Transform(orientTransform)
                                    for ex_part in self.aggregated_parts:
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
                                            sup_trans = sup.transform(orientTransform)
                                            for dir in sup_trans.sup_dir:
                                                for id in possible_collisions:
                                                    if len(rg.Intersect.Intersection.MeshLine(self.aggregated_parts[id].collider, dir)[0]) > 0:
                                                        supports_count += 1
                                                        break
                                            if supports_count == len(sup_trans.sup_dir):
                                                missing_supports_check = False
                                                break
                    
                    if close_neighbour_check == False and collision_check == False and add_collision_check == False and missing_supports_check == False:
                        next_part_trans = next_part.transform(orientTransform)
                        next_part_trans.reset_part(self.rules)
                        for i in range(len(next_part_trans.active_connections)):
                            if next_part_trans.active_connections[i] == next_rule.conn2:
                                next_part_trans.active_connections.pop(i)
                                break
                        self.aggregated_parts.append(next_part_trans)
                        self.aggregated_parts[part_01_id].children.append(next_part_trans)
                        for i in range(len(self.aggregated_parts[part_01_id].active_connections)):
                            if self.aggregated_parts[part_01_id].active_connections[i] == conn_01_id:
                                self.aggregated_parts[part_01_id].active_connections.pop(i)
                                break
                        added += 1
                        self.p_count += 1
                    else:
                       ## remove rules if they cause collisions or overlappings
                       for i in range(len(self.aggregated_parts[part_01_id].connections[conn_01_id].active_rules)):
                           if self.aggregated_parts[part_01_id].connections[conn_01_id].active_rules[i] == next_rule_id:
                               self.aggregated_parts[part_01_id].connections[conn_01_id].active_rules.pop(i)
                               break
                       ## check if the connection is still active (still active rules available)
                       if len(self.aggregated_parts[part_01_id].connections[conn_01_id].active_rules) == 0:
                           for i in range(len(self.aggregated_parts[part_01_id].active_connections)):
                            if self.aggregated_parts[part_01_id].active_connections[i] == conn_01_id:
                                self.aggregated_parts[part_01_id].active_connections.pop(i)
                                break
    
    ## Field-driven aggregation (BASIC)
    def aggregate_field(self, num, field, thres):
        def findBestRule():
            max_val = None
            best_rule = None
            best_conn = None
            best_conn_id = -1
            
            for i in xrange(self.p_count):
                part_01 = self.aggregated_parts[i]
                for i2 in xrange(len(part_01.active_connections)-1, -1, -1):
                    conn_01_id = part_01.active_connections[i2]
                    conn_01 = part_01.connections[conn_01_id]
                    for i3 in xrange(len(conn_01.active_rules)-1, -1, -1):
                        rule_id = conn_01.active_rules[i3]
                        rule = conn_01.rules_table[rule_id]
                        
                        next_part = self.parts[rule.part2]
                        
                        next_center = rg.Point3d(next_part.center)
                        orientTransform = rg.Transform.PlaneToPlane(next_part.connections[rule.conn2].flip_pln, conn_01.pln)
                        next_center.Transform(orientTransform)
                            
                        if field.bbox.Contains(next_center) == True:
                            current_target_val = field.return_pt_val(next_center)
                            
                            if current_target_val > max_val or max_val == None:
                                
                                ## overlap check
                                close_neighbour_check = False
                                possible_colliders = []
                                count = 0
                                for ex_part in self.aggregated_parts:
                                    dist = ex_part.center.DistanceTo(next_center)
                                    if dist < sc.sticky['model_tolerance']:
                                        close_neighbour_check = True
                                        break
                                    elif dist < ex_part.dim + next_part.dim:
                                        possible_colliders.append(count)
                                    count += 1
                                
                                ## collision check
                                collision_check = False
                                if self.coll_check == True and close_neighbour_check == False:
                                    next_part_collider = next_part.transform_collider(orientTransform)
                                    for id in possible_colliders:
                                        if len(rg.Intersect.Intersection.MeshMeshFast(self.aggregated_parts[id].collider, next_part_collider)) > 0:
                                            collision_check = True
                                            break
                                
                                ## constraints check
                                add_collision_check = False
                                missing_supports_check = False
                                if self.mode == 1:
                                    if close_neighbour_check == False and collision_check == False:
                                        if next_part.is_constrained:
                                            
                                            ## additional collider check
                                            if next_part.add_collider != None:
                                                add_collider = next_part.add_collider.Duplicate()
                                                add_collider.Transform(orientTransform)
                                                for ex_part in self.aggregated_parts:
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
                                                        sup_trans = sup.transform(orientTransform)
                                                        for dir in sup_trans.sup_dir:
                                                            for id in possible_colliders:
                                                                if len(rg.Intersect.Intersection.MeshLine(self.aggregated_parts[id].collider, dir)[0]) > 0:
                                                                    supports_count += 1
                                                                    break
                                                        if supports_count == len(sup.sup_dir):
                                                            missing_supports_check = False
                                                            break
                                
                                
                                if close_neighbour_check == False and collision_check == False and add_collision_check == False and missing_supports_check == False:
                                    max_val = current_target_val
                                    best_rule = rule
                                    best_conn = conn_01
                                    best_part_id = i
                                    best_conn_id = conn_01_id
                                    
                                    if thres is not None and max_val > thres:
                                        break
                                    
                                elif missing_supports_check == False:
                                    ## remove rules if they cause collisions or overlappings
                                    for i4 in range(len(self.aggregated_parts[i].connections[conn_01_id].active_rules)):
                                       if self.aggregated_parts[i].connections[conn_01_id].active_rules[i4] == rule_id:
                                           self.aggregated_parts[i].connections[conn_01_id].active_rules.pop(i4)
                                           break
                                    ## check if the connection is still active (still active rules available)
                                    if len(self.aggregated_parts[i].connections[conn_01_id].active_rules) == 0:
                                       for i4 in range(len(self.aggregated_parts[i].active_connections)):
                                        if self.aggregated_parts[i].active_connections[i4] == conn_01_id:
                                            self.aggregated_parts[i].active_connections.pop(i4)
                                            break
                    if thres is not None and max_val > thres:
                        break
                if thres is not None and max_val > thres:
                    break
            
            if best_rule is not None:
                return best_conn, best_part_id, best_conn_id, best_rule.part2, best_rule.conn2, best_rule
            else:
                return -1, -1, -1, -1, -1, -1
        
        added = 0
        loops = 0
        while added < num:
            ## avoid endless loops
            loops += 1
            if loops > num*100:
                break
            
            ## if no part is present in the aggregation, add first random part
            if self.p_count == 0:
                
                first_part = self.parts[rnd.choice(self.parts.keys())]
                
                start_point = field.highest_pt
                mov_vec = rg.Vector3d.Subtract(rg.Vector3d(start_point), rg.Vector3d(first_part.center))
                move_transform = rg.Transform.Translation(mov_vec.X, mov_vec.Y, mov_vec.Z)
                first_part_trans = first_part.transform(move_transform)
                
                for conn in first_part_trans.connections:
                    conn.generate_rules_table(self.rules)
                
                self.aggregated_parts.append(first_part_trans)
                added += 1
                self.p_count += 1
            
            else:
                ## select part-rule couple creating next part in the highest point of field
                conn_01, part_01_id, conn_01_id, next_part_name, next_conn_id, next_rule = findBestRule()
                
                if conn_01_id == -1:
                    msg = "aborted after " + str(count) + " iterations"
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    break
                
                next_part = self.parts[next_part_name]
                
                orientTransform = rg.Transform.PlaneToPlane(next_part.connections[next_conn_id].flip_pln, conn_01.pln)
                next_part_center = next_part.transform_center(orientTransform)
                
                next_part_trans = next_part.transform(orientTransform)
                next_part_trans.reset_part(self.rules)
                for i in range(len(next_part_trans.active_connections)):
                    if next_part_trans.active_connections[i] == next_rule.conn2:
                        next_part_trans.active_connections.pop(i)
                        break
                self.aggregated_parts.append(next_part_trans)
                added += 1
                self.p_count += 1
    
    ##
    def compute_next_w_field(self, part, part_id):
        
        for i in xrange(len(part.active_connections)-1, -1, -1):
            conn_id = part.active_connections[i]
            conn = part.connections[conn_id]
            for i2 in xrange(len(conn.active_rules)-1, -1, -1):
                rule_id = conn.active_rules[i2]
                rule = conn.rules_table[rule_id]
                
                next_part = self.parts[rule.part2]
                
                next_center = rg.Point3d(next_part.center)
                orientTransform = rg.Transform.PlaneToPlane(next_part.connections[rule.conn2].flip_pln, conn.pln)
                next_center.Transform(orientTransform)
                    
                if self.field.bbox.Contains(next_center) == True:
                    field_val = self.field.return_pt_val(next_center)
                    
                    queue_index = bs.bisect_left(self.queue_values, field_val)
                    queue_entry = (next_part.name, part_id, orientTransform)
                    
                    self.queue_values.insert(queue_index, field_val)
                    self.aggregation_queue.insert(queue_index, queue_entry)
                    self.queue_count += 1
    
    
    ## Field-driven aggregation with aggregation queue
    def aggregate_field_DEV(self, num):
        
        added = 0
        loops = 0
        while added < num:
            ## avoid endless loops
            loops += 1
            if loops > num*100:
                break
            
            ## if no part is present in the aggregation, add first random part
            if self.p_count == 0 and self.prev_num == 0:
                
                first_part = self.parts[rnd.choice(self.parts.keys())]
                
                start_point = field.highest_pt
                mov_vec = rg.Vector3d.Subtract(rg.Vector3d(start_point), rg.Vector3d(first_part.center))
                move_transform = rg.Transform.Translation(mov_vec.X, mov_vec.Y, mov_vec.Z)
                first_part_trans = first_part.transform(move_transform)
                
                for conn in first_part_trans.connections:
                    conn.generate_rules_table(self.rules)
                
                self.aggregated_parts.append(first_part_trans)
                
                ## compute all possible next parts and append to list
                self.compute_next_w_field(first_part_trans, self.p_count)
                added += 1
                self.p_count += 1
            
            else:
                if self.queue_count == 0:
                    break
                next_data = self.aggregation_queue[self.queue_count-1]
                
                next_part = self.parts[next_data[0]]
                
                next_center = rg.Point3d(next_part.center)
                orientTransform = next_data[2]
                next_center.Transform(orientTransform)
                
                
                ## overlap check
                close_neighbour_check = False
                possible_colliders = []
                count = 0
                for ex_part in self.aggregated_parts:
                    dist = ex_part.center.DistanceTo(next_center)
                    if dist < sc.sticky['model_tolerance']:
                        close_neighbour_check = True
                        break
                    elif dist < ex_part.dim + next_part.dim:
                        possible_colliders.append(count)
                    count += 1
                
                ## collision check
                collision_check = False
                if self.coll_check == True and close_neighbour_check == False:
                    next_part_collider = next_part.transform_collider(orientTransform)
                    for id in possible_colliders:
                        if len(rg.Intersect.Intersection.MeshMeshFast(self.aggregated_parts[id].collider, next_part_collider)) > 0:
                            collision_check = True
                            break
                        
                ## constraints check
                add_collision_check = False
                missing_supports_check = False
                if self.mode == 1:
                    if close_neighbour_check == False and collision_check == False:
                        if next_part.is_constrained:
                            
                            ## additional collider check
                            if next_part.add_collider != None:
                                add_collider = next_part.add_collider.Duplicate()
                                add_collider.Transform(orientTransform)
                                for ex_part in self.aggregated_parts:
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
                                        sup_trans = sup.transform(orientTransform)
                                        for dir in sup_trans.sup_dir:
                                            for id in possible_colliders:
                                                if len(rg.Intersect.Intersection.MeshLine(self.aggregated_parts[id].collider, dir)[0]) > 0:
                                                    supports_count += 1
                                                    break
                                        if supports_count == len(sup.sup_dir):
                                            missing_supports_check = False
                                            break
                            
                            
                if close_neighbour_check == False and collision_check == False and add_collision_check == False and missing_supports_check == False:
                    
                    next_part_trans = next_part.transform(orientTransform)
                    next_part_trans.reset_part(self.rules)
                    
                    for conn in next_part_trans.connections:
                        conn.generate_rules_table(self.rules)
                    self.aggregated_parts.append(next_part_trans)
                    
                    
                    ## compute all possible next parts and append to list
                    self.compute_next_w_field(next_part_trans, self.p_count)
                    added += 1
                    self.p_count += 1
                
                self.aggregation_queue.pop()
                self.queue_values.pop()
                self.queue_count -=1
                


## Voxel class
## Graph class

#########################################################################
##                                 RUN                                 ##
#########################################################################

log = []

## add classes to scriptcontext (to make it available to other Gh components)
if RUN:
    
    sc.sticky['Connection'] = Connection
    log.append("Connection class created...")
    sc.sticky['Part'] = Part
    log.append("Part class created...")
    sc.sticky['Constrained_Part'] = Constrained_Part
    log.append("Constrained_Part class created...")
    sc.sticky['Rule'] = Rule
    log.append("Rule class created...")
    sc.sticky['Field'] = Field
    log.append("Field class created...")
    sc.sticky['Attribute'] = Attribute
    log.append("Attribute class created...")
    sc.sticky['Support'] = Support
    log.append("Support class created...")
    sc.sticky['Aggregation'] = Aggregation
    log.append("Aggregation class created...")
    
    sc.sticky['model_tolerance'] = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance*5
    sc.sticky['WaspSetup'] = 1
    
    log.append("READY TO BUILD!")

else:
    log.append("Set RUN to True to initialize Wasp...")