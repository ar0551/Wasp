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
Access sub-parts stored at different aggregation hierarchy levels
--> WIP Component: might be incomplete or contain bugs <--
-
Provided by Wasp 0.3
    Args:
        AGGR: Aggregation from which to extract hierarchical parts
        LEVEL: Hierarchy level (0 to return the same parts in input)
    Returns:
        SUB_P: Parts at the selected hierarchy level
"""

ghenv.Component.Name = "Wasp_Get Parts Hierarchy"
ghenv.Component.NickName = 'GetHierarchy'
ghenv.Component.Message = 'VER 0.3.01'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "X | Experimental"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import sys
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
    msg = "Cannot import Wasp. Is the wasp.py module installed in " + wasp_path + "?"
    ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)

## if Wasp is installed correctly, load the classes required by the component
if wasp_loaded:
    from wasp import Part


def main(aggregation, hierarchy_level):
    
    check_data = True
    
    ##check inputs
    if aggregation is None:
        check_data = False
        msg = "No aggregation provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if check_data:
        
        if hierarchy_level == 0:
            return aggregation.aggregated_parts
        else:
            
            current_parts = []
            for part in aggregation.aggregated_parts:
                base_part = aggregation.parts[part.name]
                part_trans = base_part.transform(part.transformation, transform_sub_parts = True, sub_level = hierarchy_level+1)
                current_parts.append(part_trans)
            
            sub_parts = []
            current_level = 0
            
            while current_level < hierarchy_level:
                current_level += 1
                
                for part in current_parts:
                    if len(part.sub_parts) > 0:
                        for sp in part.sub_parts:
                            sub_parts.append(sp)
                    else:
                        msg = "The selected hierarchy level does not exist in the provided aggregation"
                        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
                        return aggregation.aggregated_parts
                
                current_parts = []
                for sp in sub_parts:
                    current_parts.append(sp)
                sub_parts = []
                
            
            return current_parts
    else:
        return -1


result = main(AGGR, LEVEL)

if result != -1:
    SUB_P = result

