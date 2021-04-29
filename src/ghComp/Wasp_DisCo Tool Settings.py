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
DisCo tool settings
-
Provided by Wasp 0.5
    Args:
        NP: OPTIONAL // Allow control over the number of affected parts (True by default)
        PF: OPTIONAL // Allow use of the Part Filter (True by default)
        RF: OPTIONAL // Allow use of Rules Filter (True by default)
        PLACE: OPTIONAL // Allow choice between different placement modes. Available modes are defined with the DisCo Placement Settings component (True by default)
        FIELD: OPTIONAL // Allow use of the Field drawing tool (True by default)
        SL: OPTIONAL // Allow to access the Save-Load tool. Available Modes are defined with the DisCo IO Settings component (True by default)
        SIM: OPTIONAL // Allow to simulate rigid-body physics (True by default)
        CHAR: OPTIONAL // Allow access to Fly and NoClip characted modes (True by default)
        SCALE: OPTIONAL // Allow to change the character scale (True by default)
    Returns:
        TS: DisCo tool settings (to use with the DisCoPlayer component)
"""

ghenv.Component.Name = "Wasp_DisCo Tool Settings"
ghenv.Component.NickName = 'DisCoTool'
ghenv.Component.Message = 'v0.5.003'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "7 | DisCo VR"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
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
    from wasp.disco import DisCoToolSettings


def main(num_parts, part_filter, rule_filter, placement, field, save_load, simulate, character, scale):
    
    check_data = True
    
    if check_data:
        
        tool_settings = DisCoToolSettings()
        
        if num_parts is not None:
            tool_settings.num_parts = num_parts
        
        if part_filter is not None:
            tool_settings.part_filter = part_filter
        
        if rule_filter is not None:
            tool_settings.rule_filter = rule_filter
        
        if placement is not None:
            tool_settings.placement = placement
        
        if field is not None:
            tool_settings.field = field
        
        if save_load is not None:
            tool_settings.save_load = save_load
        
        if simulate is not None:
            tool_settings.simulate = simulate
        
        if character is not None:
            tool_settings.character = character
        
        if scale is not None:
            tool_settings.scale = scale
        
        return tool_settings
    else:
        return -1


result = main(NP, PF, RF, PLACE, FIELD, SL, SIM, CHAR, SCALE)

if result != -1:
    TS = result