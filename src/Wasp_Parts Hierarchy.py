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
        LEVEL: ...
    Returns:
        SUB_P: Parts at the selected hierarchy level
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

def main(parts, hierarchy_level):
    
    ## check if Wasp is setup
    if sc.sticky.has_key('WaspSetup'):
        
        check_data = True
        
        ##check inputs
        if len(parts) == 0:
            check_data = False
            msg = "No parts provided"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
        if hierarchy_level is None:
            hierarchy_level = 0
        
        if check_data:
            current_parts = parts
            sub_parts = []
            
            current_level = 0
            
            if hierarchy_level == 0:
                return parts
            else:
                while current_level < hierarchy_level:
                    current_level += 1
                    
                    for part in current_parts:
                        if len(part.sub_parts) > 0:
                            for sp in part.sub_parts:
                                sp_trans = sp.transform(part.transformation)
                                sub_parts.append(sp_trans)
                            current_parts = sub_parts
                        else:
                            msg = "The selected hierarchy level does not exist in the provided parts"
                            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, msg)
                            return -1
                    
                return sub_parts
        else:
            return -1
    
    else:
        ## throw warining
        msg = "You must run the SetupWasp component before starting to build!"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1

result = main(PART, LEVEL)

if result != -1:
    SUB_P = result

