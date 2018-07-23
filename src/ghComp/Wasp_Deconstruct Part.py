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
Extract all information stored in a part. Useful for visualization or for further geometry processing
-
Provided by Wasp 0.1.0
    Args:
        PART: Parts to deconstruct
    Returns:
        NAME: Name of the part
        GEO: Geometry of the part (as mesh). If Brep geometry is needed, can be stored in the component as attribute, or obtained by transforming the original geometry with the TR output.
        CONN: Part connections
        CONN_PLN: planes for each part connection
        TR: Transformation applied to the part. Can be used to transform other geometries in a similar way (eg. replace a low poly component with a more detailed one)
        PARENT: Parent of the part
        CHILD: Children parts attached to the part
        ATTR: Part attributes
"""

ghenv.Component.Name = "Wasp_Deconstruct Part"
ghenv.Component.NickName = 'DePart'
ghenv.Component.Message = 'VER 0.2.1'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "2 | Parts"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import sys
import scriptcontext as sc
import Grasshopper as gh

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


## from http://www.chenjingcheng.com/grasshopper-python-datatree-list-conversion/
def listToDataTree(list):
    rl = list
    result = gh.DataTree[object]()
    for i in range(len(rl)):
        temp = []
        for j in range(len(rl[i])):
            temp.append(rl[i][j])
        path = gh.Kernel.Data.GH_Path(i)
        result.AddRange(temp, path)
    return result


def main(parts):
    
    check_data = True
    
    ##check inputs
    if len(parts) == 0:
        check_data = False
        msg = "No parts provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if check_data:
        
        names = []
        ids = []
        geometries = []
        transforms = []
        add_colliders = []
        parents = []
        
        conn_list = []
        conn_pln_list = []
        children_list = []
        attributes_list = []
        
        for part in parts:
            data_dict = part.return_part_data()
            names.append(data_dict['name'])
            ids.append(data_dict['id'])
            geometries.append(data_dict['geo'])
            conn_list.append(data_dict['connections'])
            
            conn_pln_list.append([])
            for conn in data_dict['connections']:
                conn_pln_list[len(conn_pln_list)-1].append(conn.pln)
            
            if "transform" in data_dict.keys():
                transforms.append(data_dict['transform'])
            
            if "add_collider" in data_dict.keys():
                add_colliders.append(data_dict['add_collider'])
            
            if "parent" in data_dict.keys():
                parents.append(data_dict['parent'])
            
            if "children" in data_dict.keys():
                children_list.append(data_dict['children'])
            
            if "attributes" in data_dict.keys():
                attributes_list.append(data_dict['attributes'])
        
        connections = listToDataTree(conn_list)
        connection_planes = listToDataTree(conn_pln_list)
        children = listToDataTree(children_list)
        attributes = listToDataTree(attributes_list)
        
        return names, ids, geometries, transforms, add_colliders, connections, connection_planes, parents, children, attributes
    else:
        return -1


result = main(PART)

if result != -1:
    NAME = result[0]
    ID = result[1]
    GEO = result[2]
    TR = result[3]
    ADD_COLL = result[4]
    CONN = result[5]
    CONN_PLN = result[6]
    PARENT = result[7]
    CHILD = result[8]
    ATTR = result[9]