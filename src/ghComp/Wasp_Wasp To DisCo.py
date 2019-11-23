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
Export Wasp information for DisCo VR software.
DisCo (Discrete Choreography) is developed by Jan Philipp Drude at dMA Hannover - Prof. Mirco Becker.
Project DisCo is available at: http://www.project-disco.com/
--> WIP Component: might be incomplete or contain bugs <--
-
Provided by Wasp 0.3
    Args:
        PART: Parts to be aggregated in DisCo
        RULES: Aggregation rules
        COLL: OPTIONAL // Part collider. If not provided, part geometry will be used.
        PROB: OPTIONAL // Probability distribution for each part
        ADD_GEO: OPTIONAL // Additional geometry to import in DisCo (e.g., environment geometry)
        PATH: Path where to save the DisCo .json file
        NAME: Export file name
        SAVE: True to export
    Returns:
        TXT: ...
        FILE: ...
"""

ghenv.Component.Name = "Wasp_Wasp To DisCo"
ghenv.Component.NickName = 'Wasp2DisCo'
ghenv.Component.Message = 'VER 0.3.003'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "5 | DisCo VR"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import sys
import json
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
    from wasp import Collider


def MeshToString(mesh, name):
    mesh_text = []
    mesh_text.append(str("\no " + name + "\n"))
    
    for v in mesh.Vertices:
        line = "v "
        line += str(v.X) + " "
        line += str(v.Y) + " "
        line += str(v.Z) + "\n"
        mesh_text.append(line)
        
        
    for f in mesh.Faces:
        line = "f "
        t = f.A + 1
        line += str(t) + " "
        t = f.B + 1
        line += str(t) + " "
        t = f.C + 1
        line += str(t) + "\n"
        mesh_text.append(line)

        if (f.D != f.C):
            line = "f "
            t = f.A + 1
            line += str(t) + " "
            t = f.C + 1
            line += str(t) + " "
            t = f.D + 1
            line += str(t) + "\n"
            mesh_text.append(line)
    
    return ''.join(mesh_text)


def main(parts, rules, rule_groups, colliders, probabilities, spawn_number, additional_geometry, filepath, filename, save):
    
    check_data = True
    
    ## check inputs
    if len(parts) == 0:
        check_data = False
        msg = "No parts provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if len(rules) == 0:
        check_data = False
        msg = "No parts provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if len(colliders) == 0:
        msg = "No collider provided. Using the part collider. Be aware that DisCo does not support concave mesh colliders."
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if len(colliders) != 0 and len(colliders) != len(parts):
        check_data = False
        msg = "Different count of parts and colliders. Please provide one collider for each part"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if len(probabilities) != 0 and len(probabilities) != len(parts):
        msg = "Different count of parts and probabilities. Will assign equal probability to all parts."
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
        probabilities = []
    
    if len(spawn_number) != 0 and len(spawn_number) != len(parts):
        msg = "Different count of parts and spawn numbers. Spawn numbers will be ignored"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
        spawn_number = []
    
    
    if filepath is None:
        check_data = False
        msg = "No path provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if filename is None:
        check_data = False
        msg = "No filename provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if save is None:
        save = False
    
    if check_data:
        
        full_path = filepath + "\\" + filename + ".json"
        
        if save:
            data_dict = {}
            
            probability_total = 0
            for prob in probabilities:
                probability_total += prob
            
            
            parts_data = []
            part_count = 0
            for part in parts:
                part_dict = {}
                
                center_vector = rg.Vector3d.Subtract(rg.Vector3d(0,0,0), rg.Vector3d(part.center))
                center_transform = rg.Transform.Translation(center_vector)
                
                part = part.transform(center_transform)
                
                part_dict["Name"] = part.name
                part_dict["Geometry"] = MeshToString(part.geo, "Geo_" + part.name)
                
                connections_data = []
                for conn in part.connections:
                    conn_dict = {}
                    
                    conn_dict["ConID"] = conn.id
                    conn_dict["Part"] = part.name
                    conn_dict["ConType"] = conn.type
                    
                    conn_dict["PlaneOriginX"] = conn.pln.Origin.X
                    conn_dict["PlaneOriginY"] = conn.pln.Origin.Y
                    conn_dict["PlaneOriginZ"] = conn.pln.Origin.Z
                    conn_dict["PlaneXVecX"] = conn.pln.XAxis.X
                    conn_dict["PlaneXVecY"] = conn.pln.XAxis.Y
                    conn_dict["PlaneXVecZ"] = conn.pln.XAxis.Z
                    conn_dict["PlaneYVecX"] = conn.pln.YAxis.X
                    conn_dict["PlaneYVecY"] = conn.pln.YAxis.Y
                    conn_dict["PlaneYVecZ"] = conn.pln.YAxis.Z
                    
                    connections_data.append(conn_dict)
                
                part_dict["Connections"] = connections_data
                
                ## probabilities
                part_dict["Probability"] = 0
                if probability_total == 1:
                    part_dict["Probability"] = probabilities[part_count]
                elif probability_total == 0:
                    part_dict["Probability"] = 1.0/len(parts)
                else:
                    part_dict["Probability"] = probabilities[part_count]/probability_total
                
                if len(spawn_number) == 0:
                    part_dict["SpawnNumber"] = 0
                else:
                    part_dict["SpawnNumber"] = int(spawn_number[part_count])
                
                
                ## collider
                ## if no collider is provided, generate the collider from the collider geometry
                if len(colliders) == 0:
                    collider_data = ""
                    coll_count = 0
                    for coll_geo in part.collider.geometry:
                        collider_data += MeshToString(coll_geo, "Col_" + part.name + "_" + str(coll_count))
                        coll_count += 1
                    part_dict["Collider"] = collider_data
                    
                else:
                    current_collider = colliders[part_count]
                    if type(current_collider) == Collider:
                        current_collider = current_collider.transform(center_transform)
                        if len(current_collider.geometry) == 1:
                            part_dict["Collider"] = MeshToString(current_collider.geometry[0], "Col_" + part.name + "_0")
                        else:
                            collider_data = ""
                            coll_count = 0
                            for coll_geo in current_collider.geometry:
                                collider_data += MeshToString(current_collider.geometry[coll_count], "Col_" + part.name + "_" + str(coll_count))
                                coll_count += 1
                            part_dict["Collider"] = collider_data
                    else:
                        current_collider.Transform(center_transform)
                        part_dict["Collider"] = MeshToString(current_collider, "Col_" + part.name + "_0")
                
                part_dict["TemplateID"] = part_count
                part_count += 1
                
                parts_data.append(part_dict)
            
            data_dict["PartData"] = parts_data
            
            rules_data = []
            for rule in rules:
                rule_dict = {}
                
                rule_dict["Part1"] = rule.part1
                rule_dict["Conn1"] = rule.conn1
                rule_dict["Part2"] = rule.part2
                rule_dict["Conn2"] = rule.conn2
                
                rules_data.append(rule_dict)
            
            data_dict["RuleData"] = rules_data
            
            groups_data = []
            for group in rule_groups:
                group_dict = json.loads(group)
                groups_data.append(group_dict)
                
            data_dict["RuleGroupsData"] = groups_data
            
            
            add_geo_data = []
            add_geo_count = 0
            for add_geo in additional_geometry:
                add_geo_dict = {}
                
                add_geo_dict["Geometry"] = MeshToString(add_geo, "Additional_" + str(add_geo_count))
                add_geo_count += 1
                
                add_geo_data.append(add_geo_dict)
            
            data_dict["AdditionalGeometry"] = add_geo_data
            
            with open(full_path, "w") as outF:
                json.dump(data_dict, outF)
        
            return json.dumps(data_dict), full_path
        else:
            return "Set SAVE to True to generate the json file and save it to the choosen location", full_path
    else:
        return -1


result = main(PART, RULES, RULE_G, COLL, PROB, SPAWN_N, ADD_GEO, PATH, NAME, SAVE)

if result != -1:
    TXT = result[0]
    FILE = result[1]