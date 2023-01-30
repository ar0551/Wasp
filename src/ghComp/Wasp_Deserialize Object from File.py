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
Load a Wasp class from a serialized .json file.
-
Provided by Wasp 0.5
    Args:
        FILE: File where the object is saved (.json)
        LOAD: True to reload the saved file
    Returns:
        OBJ: Loaded Wasp object
"""

ghenv.Component.Name = "Wasp_Deserialize Object from File"
ghenv.Component.NickName = 'DeSerialize'
ghenv.Component.Message = 'v0.5.007'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "X | Experimental"
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass


import sys
import os
import Rhino.Geometry as rg
import Grasshopper as gh
import json


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
    from wasp.core.connection import *
    from wasp.core.parts import *
    from wasp.core.rules import *
    ##from wasp.core.attributes import *  ### NOT IMPLEMENTED
    from wasp.core.aggregation import *
    from wasp.core.constraints import *
    from wasp.core.colliders import *
    from wasp.core.graph import *
    from wasp.field import *
    from wasp.disco.player import *
    from wasp.disco.constraints import *
    from wasp.disco.environment import *
    from wasp.disco.setup import *

def main(file_path, load_file, obj):
    
    check_data = True
    
    ## check inputs
    if file_path is None:
        check_data = False
        msg = "No file path provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if load_file is None:
        load_file = False
    
    if check_data:
        class_data = {}
        ## load json data
        with open(file_path, "r") as inF:
            txt_data = inF.read()
            class_data = json.loads(txt_data)
        
        object_type = class_data["object_type"]
        
        if obj is None or load_file:
            ## Aggregation
            if object_type == "Aggregation":
                obj = Aggregation.from_data(class_data)
            
            ## Collider
            elif object_type == "Collider":
                obj = Collider.from_data(class_data)
            
            ## Connection
            elif object_type == "Connection":
                obj = Connection.from_data(class_data)
            
            ## Plane_Constraint
            elif object_type == "PlaneConstraint":
                obj = Plane_Constraint.from_data(class_data)
            
            ## Mesh_Constraint
            elif object_type == "MeshConstraint":
                obj = Mesh_Constraint.from_data(class_data)
            
            ## Adjacency_Constraint
            elif object_type == "AdjacencyConstraint":
                obj = Adjacency_Constraint.from_data(class_data)
            
            ## Orientation_Constraint NOT IMPLEMENTED
            
            ## Graph
            elif object_type == "Graph":
                obj = Graph.from_data(class_data)
            
            ## Part
            elif object_type == "Part":
                obj = Part.from_data(class_data)
            
            ## AdvancedPart
            elif object_type == "AdvancedPart":
                obj = AdvancedPart.from_data(class_data)
            
            ## PartCatalog
            elif object_type == "PartCatalog":
                obj = PartCatalog.from_data(class_data)
            
            ## Rule
            elif object_type == "Rule":
                obj = Rule.from_data(class_data)
            
            ## Field
            elif object_type == "Field":
                obj = Field.from_data(class_data)
            
            else:
                obj = None
                msg = "Object type not recognized"
                ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)
        
        return obj
    else:
        return -1


## create object container in global variables dict
if 'object_container' not in globals():
    object_container = None

result = main(FILE, LOAD, object_container)

if result != -1:
    OBJ = result