# Wasp: Discrete Design with Grasshopper plug-in (LGPL) initiated by Andrea Rossi
# 
# This file is part of Wasp.
# 
# Copyright (c) 2017, Andrea Rossi <a.rossi.andrea@gmail.com>
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
# Significant parts of Wasp have been developed by Andrea Rossi
# as part of research on digital materials and discrete design at:
# DDU Digital Design Unit - Prof. Oliver Tessmann
# Technische Universitt Darmstadt


#########################################################################
##                            COMPONENT INFO                           ##
#########################################################################

"""
DisCo placement settings.
DisCo (Discrete Choreography) is developed by Jan Philipp Drude at dMA Hannover - Prof. Mirco Becker.
Project DisCo is available at: http://www.project-disco.com/
-
Provided by Wasp 0.5
    Args:
        PLACE: OPTIONAL // Allow use of the Place tool (True by default)
        CHOREO: OPTIONAL // Allow use of the Choreograph tool (True by default)
        SHOOT: OPTIONAL // Allow use of the Shoot tool (True by default)
        GROW: OPTIONAL // Allow use of the Grow tool (True by default)
        PICK: OPTIONAL // Allow use of the Pick-and-Place tool (True by default)
        DEL: OPTIONAL // Allow use of the Delete tool (True by default)
        DEL_REC: OPTIONAL // Allow use of the Recursive Delete tool (True by default)
        DEL_SP: OPTIONAL // Allow use of the Sphere Delete tool (True by default)
        DIS: OPTIONAL // Allow use of the Disable-Enable tool (True by default)
    Returns:
        PS: DisCo placement settings (to use with the DisCoPlayer component)
"""

ghenv.Component.Name = "Wasp_DisCo Placement Settings"
ghenv.Component.NickName = 'DisCoPlace'
ghenv.Component.Message = 'v0.5.007'
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
    from wasp.disco import DisCoPlacementSettings


def main(place, choreo, shoot, grow, pick, delete, delete_recursive, delete_sphere, disable):
    
    check_data = True
    
    if check_data:
        
        placement_settings = DisCoPlacementSettings()
        
        if place is not None:
            placement_settings.place = place
        
        if choreo is not None:
            placement_settings.choreo = choreo
        
        if shoot is not None:
            placement_settings.shoot = shoot
        
        if grow is not None:
            placement_settings.grow = grow
        
        if pick is not None:
            placement_settings.pick = pick
        
        if delete is not None:
            placement_settings.delete = delete
        
        if delete_recursive is not None:
            placement_settings.delete_recursive = delete_recursive
        
        if delete_sphere is not None:
            placement_settings.delete_sphere = delete_sphere
        
        if disable is not None:
            placement_settings.disable = disable
        
        return placement_settings
    else:
        return -1


result = main(PLACE, CHOREO, SHOOT, GROW, PICK, DEL, DEL_R, DEL_SP, DIS)

if result != -1:
    PS = result