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
Saves current status of an aggregation to a .json file.
-
Provided by Wasp 0.5
    Args:
        AGGR: Aggregation to save
        PATH: Path where to save the aggregation
        NAME: Name of the exported file
        SAVE: True to export
    Returns:
        TXT: Text representation of the aggregation
        FILE: Path to the saved file
"""

ghenv.Component.Name = "Wasp_Save Aggregation to File"
ghenv.Component.NickName = 'SaveAggr'
ghenv.Component.Message = 'v0.5.008'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "6 | Aggregation"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
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
    pass


def main(aggregation, path, filename, save):
        
    check_data = True
    
    ## check inputs
    if aggregation is None:
        check_data = False
        msg = "No aggregation provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if path is None:
        check_data = False
        msg = "No path provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if filename is None:
        check_data = False
        msg = "No filename provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if save is None:
        save = False
    
    ## execute main code if all needed inputs are available
    if check_data:
        
        aggr_dict = {}
        aggr_dict['aggregation_name'] = aggregation.name
        aggr_dict['parts'] = {}
        for part in aggregation.aggregated_parts:
            
            part_dict = {}
            
            part_dict['name'] = part.name
            part_dict['active_connections'] = part.active_connections
            part_dict['parent'] = part.parent
            part_dict['children'] = part.children
            
            
            part_dict['transform'] = {}
            part_dict['transform']['M00'] = part.transformation.M00
            part_dict['transform']['M01'] = part.transformation.M01
            part_dict['transform']['M02'] = part.transformation.M02
            part_dict['transform']['M03'] = part.transformation.M03
            
            part_dict['transform']['M10'] = part.transformation.M10
            part_dict['transform']['M11'] = part.transformation.M11
            part_dict['transform']['M12'] = part.transformation.M12
            part_dict['transform']['M13'] = part.transformation.M13
            
            part_dict['transform']['M20'] = part.transformation.M20
            part_dict['transform']['M21'] = part.transformation.M21
            part_dict['transform']['M22'] = part.transformation.M22
            part_dict['transform']['M23'] = part.transformation.M23
            
            part_dict['transform']['M30'] = part.transformation.M30
            part_dict['transform']['M31'] = part.transformation.M31
            part_dict['transform']['M32'] = part.transformation.M32
            part_dict['transform']['M33'] = part.transformation.M33
            
            part_dict['is_constrained'] = part.is_constrained
            
            aggr_dict['parts'][part.id] = part_dict
        
        full_path = os.path.join(path, filename + ".json")
        
        if save:
            with open(full_path, "w") as outF:
                json.dump(aggr_dict, outF)
        
        return json.dumps(aggr_dict), full_path
    else:
        return -1

result = main(AGGR, PATH, NAME, SAVE)

if result != -1:
    TXT = result[0]
    FILE = result[1]