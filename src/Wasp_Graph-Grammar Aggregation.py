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
Aggregate the given parts in a stochastic process, selecting parts and rules randomly at every step.
The component works additively, hence increasing the number of parts in an aggregation just adds new parts on the existing ones, without triggering recomputing of the previous element.
-
Provided by Wasp 0.1.0
    Args:
        PART: Parts to be aggregated (can be more than one)
        PREV: Previous aggregated parts. It is possible to input the results of a previous aggregation, or parts transformed with the TransformPart component
        RULES: Rules for the aggregation
        ID: OPTIONAL // Aggregation ID (to avoid overwriting when having different aggregation components in the same file)
    Returns:
        PART_OUT: Aggregated parts (includes both PREV input and newly aggregated parts)
"""
        
ghenv.Component.Name = "Wasp_Graph-Grammar Aggregation"
ghenv.Component.NickName = 'GraphAggr'
ghenv.Component.Message = 'VER 0.2.0'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "4 | Aggregation"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass
        
        
import scriptcontext as sc
import Rhino.Geometry as rg
import Grasshopper.Kernel as gh
import random as rnd
        
        
def main(parts, rules_sequence, aggregation_id, reset):
            
    ## check if Wasp is setup
    if sc.sticky.has_key('WaspSetup'):
                
        check_data = True
        ##check inputs
        if len(parts) == 0:
            check_data = False
            msg = "No parts provided"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                
        if len(rules_sequence) == 0:
            check_data = False
            msg = "No rules sequence provided"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                
        if aggregation_id is None:
            aggregation_id = 'Aggregation'
            msg = "Default name 'Aggregation' assigned"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, msg)
                
        if check_data:
                    
            if sc.sticky.has_key(aggregation_id) == False:
                sc.sticky[aggregation_id] = sc.sticky['Aggregation'](aggregation_id, parts, [], 0)
                    
            if reset:
                sc.sticky[aggregation_id] = sc.sticky['Aggregation'](aggregation_id, parts, [], 0)
                    
            else:
                sc.sticky[aggregation_id].aggregate_sequence(rules_sequence)
                    
            return sc.sticky[aggregation_id].aggregated_parts
                
        else:
            return -1
            
    else:
        ## throw warining
        msg = "You must run the SetupWasp component before starting to build!"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1
        
        
result = main(PART, RULE_S, ID, RESET)
        
if result != -1:
    PART_OUT = result
        
