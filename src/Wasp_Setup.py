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

Source code is available at: xxxxx
-
Provided by Wasp 0.0.04
    Args:
        RUN: Setup all classes and variables required to run Wasp. Set it to True to start building.
    Returns:
        log: log
"""

ghenv.Component.Name = "Wasp_Setup"
ghenv.Component.NickName = 'WaspSetup'
ghenv.Component.Message = 'VER 0.0.04\nNOV_11_2017'
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
import scriptcontext as sc
#import rhinoscriptsyntax as rs
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
        
        #flip_pln_Y = rs.VectorReverse(plane.YAxis)
        flip_pln_Y = rg.Vector3d(plane.YAxis)
        flip_pln_Y.Reverse()
        
        #self.flip_pln = rs.PlaneFromFrame(plane.Origin, plane.XAxis, flip_pln_Y)
        self.flip_pln = rg.Plane(plane.Origin, plane.XAxis, flip_pln_Y)
        
        self.type = type
        self.part = part
        self.id = id
        
        self.rules_table = []
        self.active_rules = []
    
    ## return a transformed copy of the connection
    def transform(self, trans):
        #pln_trans = rs.PlaneFromFrame(self.pln.Origin, self.pln.XAxis, self.pln.YAxis)
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
    def __init__(self, name, geometry, connections, collider, attributes):
        
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
        
        self.tolerance = sc.sticky['model_tolerance']
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
        
        part_trans = Part(self.name, geo_trans, connections_trans, collider_trans, attributes_trans)
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
    def __init__(self, name, geometry, connections, collider, attributes, additional_collider, supports):
        
        super(self.__class__, self).__init__(name, geometry, connections, collider, attributes)
        
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
        
        part_trans = Constrained_Part(self.name, geo_trans, connections_trans, collider_trans, attributes_trans, add_collider_trans, supports_trans)
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
                if type(val) == rg.Point3d:
                    val_trans = rg.Point3d(val)
                else:
                    val_trans = val.Duplicate()
                val_trans.Transform(trans)
                values_trans.append(val_trans)
            attr_trans = Attribute(self.name, values_trans, self.transformable)
        else:
            attr_trans = Attribute(self.name, self.values, self.transformable)
        return attr_trans


#########################################################################
##                                 WIP                                 ##
#########################################################################

class Support(object):
    
    def __init__(self, support_directions):
        
        self.sup_dir = support_directions
    
    def is_intersecting(self, mesh):
        pass
    
    def transform(self, trans):
        sup_dir_trans = []
        for dir in self.sup_dir:
            dir_trans = dir.Duplicate()
            dir_trans.Transform(trans)
            sup_dir_trans.append(dir_trans)
        sup_trans = Support(sup_dir_trans)
        return sup_trans





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
    
    sc.sticky['model_tolerance'] = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance*5
    sc.sticky['WaspSetup'] = 1
    
    log.append("READY TO BUILD!")

else:
    log.append("Set RUN to True to initialize Wasp...")