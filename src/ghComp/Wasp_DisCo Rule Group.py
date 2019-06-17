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
Export Wasp information for DisCo VR software.
DisCo (Discrete Choreography) is developed by Jan Philipp Drude at dMA Hannover - Prof. Mirco Becker.
Project DisCo is available at: http://www.project-disco.com/
--> WIP Component: might be incomplete or contain bugs <--
-
Provided by Wasp 0.2
    Args:
        PART: Parts to be aggregated in DisCo
        RULES: Aggregation rules
        COLL: OPTIONAL // Part collider. If not provided, part geometry will be used.
        PROB: OPTIONAL // Probability distribution for each part
        ADD_GEO: OPTIONAL // Additional geometry to import in DisCo (e.g., environment geometry)
        PATH: Path where to save the DisCo .json file
        NAME: Export file name
        SAVE: True to export
    Returns:
        TXT: ...
        FILE: ...
"""

ghenv.Component.Name = "Wasp_DisCo Rule Group"
ghenv.Component.NickName = 'RuleG'
ghenv.Component.Message = 'VER 0.2.07'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "5 | DisCo VR"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import sys
import json
import Rhino.Geometry as rg
import Grasshopper as gh

## add Wasp install directory to system path
ghcompfolder = gh.Folders.DefaultAssemblyFolder
wasp_path = ghcompfolder + "Wasp"
if wasp_path not in sys.path:
    sys.path.append(wasp_path)
try:
    import wasp
except:
    msg = "Cannot import Wasp. Is the wasp.py module installed in " + wasp_path + "?"
    ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)


def main(group_name, rule_grammar):
    
    check_data = True
    
    ## check inputs
    if group_name is None:
        check_data = False
        msg = "No group name provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if len(rule_grammar) == 0:
        check_data = False
        msg = "No rules grammar provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    
    if check_data:
        group_dict = {}
        group_dict['RuleGroupName'] = group_name
        group_dict["RuleGrammar"] = rule_grammar
        
        return json.dumps(group_dict)
    else:
        return -1


result = main(NAME, GR)

if result != -1:
    RULE_G = result