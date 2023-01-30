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
Extract all information stored in a part. Useful for visualization or for further geometry processing
-
Provided by Wasp 0.5
    Args:
        PART: Parts to deconstruct
    Returns:
        NAME: Name of the part
        ID: Pard ID
        GEO: Geometry of the part (as mesh). If Brep geometry is needed, can be stored in the component as attribute, or obtained by transforming the original geometry with the TR output.
        CONN: Part connections
        COLL: Part collider
        TR: Transformation applied to the part. Can be used to transform other geometries in a similar way (eg. replace a low poly component with a more detailed one)
        PARENT: Parent of the part
        CHILD: Children parts attached to the part
        ADD_COLL: Additional collider applied to the part
        ATTR: Part attributes
"""

ghenv.Component.Name = "Wasp_Deconstruct Part"
ghenv.Component.NickName = 'DePart'
ghenv.Component.Message = 'v0.5.007'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "2 | Parts"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import sys
import Grasshopper as gh
import ghpythonlib.treehelpers as th


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
    from wasp.core import Aggregation


def main(part):
    
    check_data = True
    
    ##check inputs
    if part is None:
        check_data = False
        msg = "No or null part provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if check_data:
        
        data_dict = part.return_part_data()
        
        name = data_dict['name']
        id = data_dict['id']
        geometry = data_dict['geo']
        connections = data_dict['connections']
        collider = data_dict['collider']
        center = data_dict['center']
        
        transform = None
        if "transform" in data_dict.keys():
            transform = data_dict['transform']
        
        add_collider = None
        if "add_collider" in data_dict.keys():
            add_collider = data_dict['add_collider']
        
        parent = None
        if "parent" in data_dict.keys():
            parents = data_dict['parent']
        
        children = None
        if "children" in data_dict.keys():
            children = data_dict['children']
        
        attributes = None
        if "attributes" in data_dict.keys():
            attributes = data_dict['attributes']
        
        return name, id, geometry, connections, collider, center, transform, parents, children, add_collider, attributes
    else:
        return -1


result = main(PART)

if result != -1:
    NAME = result[0]
    ID = result[1]
    GEO = result[2]
    CONN = result[3]
    COLL = result[4]
    CENTER = result[5]
    TR = result[6]
    PARENT = result[7]
    CHILD = result[8]
    ADD_COLL = result[9]
    ATTR = result[10]