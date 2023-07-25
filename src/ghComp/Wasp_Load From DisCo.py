# Wasp: Discrete Design with Grasshopper plug-in (LGPL) initiated by Andrea Rossi
# 
# This file is part of Wasp.
# 
# Copyright (c) 2017-2023, Andrea Rossi <a.rossi.andrea@gmail.com>
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
# Early development of Wasp has been carried out by Andrea Rossi
# as part of research on digital materials and discrete design at:
# DDU Digital Design Unit - Prof. Oliver Tessmann
# Technische Universitt Darmstadt


#########################################################################
##                            COMPONENT INFO                           ##
#########################################################################

"""
Loads an aggregation from a DisCo-generated .json file (e.g., a saved game session).
-
Provided by Wasp 0.5
    Args:
        PART: Parts definition for the aggregation
        FILE: File where the DisCo aggregation is saved (.json)
        RENUM: True to renumber ids coming from DisCo. This is necessary to allow correct import of aggregations where the delete commands have been used (True by default)
    Returns:
        PART_OUT: Imported aggregation parts
"""

ghenv.Component.Name = "Wasp_Load From DisCo"
ghenv.Component.NickName = 'DisCoLoad'
ghenv.Component.Message = 'v0.5.008'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "7 | DisCo VR"
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


import sys
import Rhino.Geometry as rg
import Grasshopper as gh
import json
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
    from wasp.core import Aggregation, Graph, Attribute


def main(parts, file_path, renumber):
        
    check_data = True
    
    ## check inputs
    if len(parts) == 0:
        check_data = False
        msg = "No parts provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if file_path is None:
        check_data = False
        msg = "No path provided for the file to load"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if renumber is None:
        renumber = True
    
    ## execute main code if all needed inputs are available
    if check_data:
        
        loaded_parts = []
        loaded_graph = Graph()
        
        parts_copy = []
        for part in parts:
            parts_copy.append(part.copy())
        loaded_aggregation = Aggregation('', parts_copy, [], 0)
        
        aggr_dict = {}
        
        ## load json data
        with open(FILE, "r") as inF:
            txt_data = inF.read()
            aggr_dict = json.loads(txt_data)
        
        ## sort part ids
        part_ids = [int(id) for id in aggr_dict['parts'].keys()]
        part_ids.sort()
        
        ## create new ids for renumbering
        renumbered_ids = None
        if renumber:
            renumbered_ids = range(len(part_ids))
        
        ## load parts
        for i in range(len(part_ids)):
            id = part_ids[i]
            part_data = aggr_dict['parts'][str(id)]
            
            if renumber:
                id = i
            
            ## part name
            name = part_data['name']
            
            ## part active connections
            active_conn = part_data['active_connections']
            parent = part_data['parent']
            if renumber:
                try:
                    parent = part_ids.index(parent)
                except:
                    parent = None
            
            children = part_data['children']
            if renumber:
                children = [part_ids.index(child) for child in children]
            
            if parent is not None:
                loaded_graph.add_node(parent)
                
                loaded_graph.add_edge(parent, id, part_data['parentCon'], part_data['connection_to_parent'])
            
            ## part transform
            trans = rg.Transform(0)
            trans.M00 = part_data['transform']['M00']
            trans.M01 = part_data['transform']['M01']
            trans.M02 = part_data['transform']['M02']
            trans.M03 = part_data['transform']['M03']
            
            trans.M10 = part_data['transform']['M10']
            trans.M11 = part_data['transform']['M11']
            trans.M12 = part_data['transform']['M12']
            trans.M13 = part_data['transform']['M13']
            
            trans.M20 = part_data['transform']['M20']
            trans.M21 = part_data['transform']['M21']
            trans.M22 = part_data['transform']['M22']
            trans.M23 = part_data['transform']['M23']
            
            trans.M30 = part_data['transform']['M30']
            trans.M31 = part_data['transform']['M31']
            trans.M32 = part_data['transform']['M32']
            trans.M33 = part_data['transform']['M33']
            
            constrained = part_data['is_constrained']
            
            new_part = None
            for part in parts:
                if part.name == name:
                    
                    new_part = part.transform(trans)
                    
                    ## flip part if negative scaling occurs
                    if trans.M00 * trans.M11 * trans.M22 < 0:
                        ## geometry
                        new_part.geo.Flip(True, True, True)
                        ## connections
                        for conn in new_part.connections:
                            pass
                            conn.pln.Flip()
                            conn.pln.Rotate(math.pi/2, conn.pln.ZAxis)
                        ## collider
                        for geo in new_part.collider.geometry:
                            geo.Flip(True, True, True)
                    
                    new_part.id = id
                    break
            
            owner_id_attr = None
            if part_data.has_key("ownerID"):
                owner_id_attr = Attribute("ownerID", [part_data["ownerID"]], False)
            
            owner_name_attr = None
            if part_data.has_key("ownerName"):
                owner_name_attr = Attribute("ownerName", [part_data["ownerName"]], False)
            
            freeze_time_attr = None
            if part_data.has_key("freezeTime"):
                freeze_time_attr = Attribute("freezeTime", [part_data["freezeTime"]], False)
            
            if new_part is not None:
                new_part.active_connections = active_conn
                new_part.parent = parent
                new_part.children = children
                new_part.is_constrained = constrained
                
                if owner_id_attr is not None:
                    new_part.attributes.append(owner_id_attr)
                
                if owner_name_attr is not None:
                    new_part.attributes.append(owner_name_attr)
                
                if freeze_time_attr is not None:
                    new_part.attributes.append(freeze_time_attr)
                
                loaded_parts.append(new_part)
        
        loaded_aggregation.graph = loaded_graph
        loaded_aggregation.aggregated_parts = loaded_parts
        
        return loaded_aggregation, loaded_parts
    else:
        return -1

result = main(PART, FILE, RENUM)

if result != -1:
    AGGR = result[0]
    PART_OUT = result[1]