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
Sequential aggregation based on graph-grammars.
--> WIP Component: might be incomplete or contain bugs <--
-
Provided by Wasp 0.5
    Args:
        PART: Parts to be aggregated (can be more than one)
        PREV: Previous aggregated parts. It is possible to input the results of a previous aggregation, or parts transformed with the TransformPart component
        RULES: Rules sequence in text form (WIP)
        ID: OPTIONAL // Aggregation ID (to avoid overwriting when having different aggregation components in the same file)
        RESET: Recompute the whole aggregation
    Returns:
        AGGR: Aggregation object
        PART_OUT: Aggregated parts (includes both PREV input and newly aggregated parts)
"""
        
ghenv.Component.Name = "Wasp_Graph-Grammar Aggregation"
ghenv.Component.NickName = 'GraphAggr'
ghenv.Component.Message = 'v0.5.003'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "6 | Aggregation"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
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
    msg = "Cannot import Wasp. Is the wasp folder available in " + ghcompfolder + "?"
    ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)

## if Wasp is installed correctly, load the classes required by the component
if wasp_loaded:
    from wasp.core import Aggregation


def main(parts, previous_parts, rules_sequence, aggregation_id, reset, aggregation):
    
    check_data = True
    ##check inputs
    if len(parts) == 0:
        check_data = False
        msg = "No parts provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
            
    if len(rules_sequence) == 0:
        check_data = False
        msg = "No rules sequence provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
            
    if aggregation_id is None:
        aggregation_id = 'mySequence'
            
    if check_data:
        if aggregation is None or aggregation == -1 or reset:
            
            ## copy parts to avoid editing the original parts
            parts_copy = []
            for part in parts:
                parts_copy.append(part.copy())
            
            aggregation = Aggregation(aggregation_id, parts_copy, [], 0, _prev = previous_parts)
            
            error_msg = aggregation.aggregate_sequence(rules_sequence)
            if error_msg is not None:
                ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, error_msg)
        
        return aggregation
    else:
        return -1

## create aggregation container in global variables dict
if 'aggregation_container' not in globals():
    aggregation_container = None

result = main(PART, PREV, RULES, ID, RESET, aggregation_container)

if result != -1:
    aggregation_container = result
    
    AGGR = aggregation_container
    PART_OUT = aggregation_container.aggregated_parts
