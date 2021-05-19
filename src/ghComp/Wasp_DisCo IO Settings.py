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
DisCo placement settings
-
Provided by Wasp 0.5
    Args:
        SAVE: OPTIONAL // Allow to save game results to file (True by default)
        LOAD: OPTIONAL // Allow to load previously saved files (True by default)
        NEWG: OPTIONAL // Allow to start a new game (True by default)
        FIELD: OPTIONAL // Allow to save user-drawn fields (True by default)
    Returns:
        IOS: DisCo IO settings (to use with the DisCoPlayer component)
"""

ghenv.Component.Name = "Wasp_DisCo IO Settings"
ghenv.Component.NickName = 'DisCoIO'
ghenv.Component.Message = 'v0.5.004'
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
    from wasp.disco import DisCoIOSettings


def main(save_game, load_game, new_game, export_field):
    
    check_data = True
    
    if check_data:
        
        IO_settings = DisCoIOSettings()
        
        if save_game is not None:
            IO_settings.place = save_game
        
        if load_game is not None:
            IO_settings.load_game = load_game
        
        if new_game is not None:
            IO_settings.new_game = new_game
        
        if export_field is not None:
            IO_settings.export_field = export_field
        
        return IO_settings
    else:
        return -1


result = main(SAVE, LOAD, NEWG, FIELD)

if result != -1:
    IOS = result