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
Extract all information stored in an Aggregation
-
Provided by Wasp 0.7
    Args:
        AGGR: Aggregation to deconstruct
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

ghenv.Component.Name = "Wasp_Deconstruct Aggregation"
ghenv.Component.NickName = 'DeAggregation'
ghenv.Component.Message = 'v0.7.001'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "6 | Aggregation"
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


def main(aggregation):
    
    check_data = True
    
    ##check inputs
    if aggregation is None:
        check_data = False
        msg = "No or null Aggregation provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if check_data:
        
        name = aggregation.name
        parts = aggregation.parts.values()
        rules = aggregation.rules
        aggregated_parts = aggregation.aggregated_parts
        graph = aggregation.graph
        
        fields = None
        if not aggregation.multiple_fields:
            fields = aggregation.field
        else:
            fields = aggregation.field.values()
        
        global_constraints = aggregation.global_constraints
        seed = aggregation.rnd_seed
        catalog = aggregation.catalog
        
        return name, parts, rules, aggregated_parts, graph, fields, global_constraints, seed, catalog
    else:
        return -1


result = main(AGGR)

if result != -1:
    NAME = result[0]
    PARTS = result[1]
    RULES = result[2]
    AGGR_PARTS = result[3]
    GRAPH = result[4]
    FIELD = result[5]
    GC = result[6]
    SEED = result[7]
    CAT = result[8]