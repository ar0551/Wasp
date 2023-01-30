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
Setup aggregation information for DisCo
-
Provided by Wasp 0.5
    Args:
        PART: Parts to be aggregated in DisCo
        RULES: Aggregation rules
        RULE_G: OPTIONAL // Rule groups for filtering
        PROB: OPTIONAL // Probability distribution for each part
        SPAWN_N: OPTIONAL // Number of each part created at start-up
    Returns:
        SETUP: DisCo setup data
"""

ghenv.Component.Name = "Wasp_DisCo Aggregation Setup"
ghenv.Component.NickName = 'DisCoSetup'
ghenv.Component.Message = 'v0.5.007'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "7 | DisCo VR"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import sys
import json
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
    from wasp.disco import DisCoSetup


def main(parts, rules, rule_groups, probabilities, spawn_amounts):
    
    check_data = True
    
    ## check inputs
    if len(parts) == 0:
        check_data = False
        msg = "No parts provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if len(rules) == 0:
        check_data = False
        msg = "No parts provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if len(probabilities) != 0 and len(probabilities) != len(parts):
        msg = "Different count of parts and probabilities. Will assign equal probability to all parts."
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
        probabilities = []
    
    if len(spawn_amounts) != 0 and len(spawn_amounts) != len(parts):
        msg = "Different count of parts and spawn numbers. Spawn numbers will be ignored"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
        spawn_amounts = []
    
    if check_data:
        
        if len(probabilities) == 0:
            probabilties = [0 for p in parts]
        
        if len(spawn_amounts) == 0:
            spawn_amounts = [0 for p in parts]
        
        setup = DisCoSetup(parts, rules, rule_groups, probabilities, spawn_amounts)
        return setup
    
    else:
        return -1


result = main(PART, RULES, RULE_G, PROB, SPAWN_N)

if result != -1:
    SETUP = result