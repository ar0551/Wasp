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
-
Provided by Wasp 0.1.0
    Args:
        PART: Parts
        ID: ...
        CHILD: ...
        REM: ...
        RESET: ...
    Returns:
        AGGR_OUT: edited aggregation object
        PART_OUT: edited parts
"""

ghenv.Component.Name = "Wasp_Parts Hierarchy"
ghenv.Component.NickName = 'PartHie'
ghenv.Component.Message = 'VER 0.2.0'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "X | Experimental"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import Rhino.Geometry as rg
import Grasshopper.Kernel as gh
import random as rnd

def main(aggregation, id, child, remove, reset):
    
    ## check if Wasp is setup
    if sc.sticky.has_key('WaspSetup'):
        
        check_data = True
        
        ##check inputs
        if aggregation is None:
            check_data = False
            msg = "No aggregation provided"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
        ##check inputs
        if aggregation is None:
            check_data = False
            msg = "No aggregation provided"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
        if child is None:
            child = False
        
        if remove is None:
            remove = False
        
        if reset is None:
            reset = False
        
        if check_data:
            
            new_name = aggregation.name + "_edit"
            
            if reset:
                new_name = aggregation.name + "_edit"
                sc.sticky[new_name] = aggregation
            
            if remove:
                
                if child:
                    current_part = None
                
                sc.sticky[new_name].aggregated_parts.pop(id)
            
            
            return sc.sticky[new_name]
        else:
            return -1
    
    else:
        ## throw warining
        msg = "You must run the SetupWasp component before starting to build!"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1

result = main(AGGR, ID, CHILD, REM, RESET)

if result != -1:
    AGGR_OUT = result
    PART_OUT = result.aggregated_parts

