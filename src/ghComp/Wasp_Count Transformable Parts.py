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
Count the number of transformable parts in an aggregation (to determine the number of values for the Actuate Internal Transformations component.
-
Provided by Wasp 0.6
    Args:
        AGGR: Aggregation to evaluate
    Returns:
        COUNT: Number of parts with internal transformations
        NAME: Names of the parts with internal transformations
"""

ghenv.Component.Name = "Wasp_Count Transformable Parts"
ghenv.Component.NickName = 'CountTrParts'
ghenv.Component.Message = 'v0.6.001'
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
    from wasp.core import InternalTransform


def main(aggregation):
    
    check_data = True
    
    ##check inputs
    if aggregation is None:
        check_data = False
        msg = "No aggregation provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if check_data:
        transformable_parts_count = 0
        transformable_parts_ids = []
        
        for part in aggregation.aggregated_parts:
            for attr in part.attributes:
                if type(attr) == InternalTransform:
                    transformable_parts_count += 1
                    transformable_parts_ids.append(part.name)
                    break
        
        return transformable_parts_count, transformable_parts_ids
    else:
        return -1


result = main(AGGR)

if result != -1:
    COUNT = result[0]
    NAME = result[1]