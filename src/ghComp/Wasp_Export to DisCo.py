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
-
Provided by Wasp 0.5
    Args:
        SETUP: OPTIONAL // DisCo setup data
        ENV: OPTIONAL // DisCo environment data
        PLAY: OPTIONAL // DisCo player settings for multi-player mode
        PATH: Path where to save the DisCo .json file
        NAME: Export file name
        SAVE: True to export
    Returns:
        FILES: .Path to the setup and players files
        SF: Setup file data as string
        PF: Players file data as string
"""

ghenv.Component.Name = "Wasp_Export to DisCo"
ghenv.Component.NickName = 'Wasp2DisCo'
ghenv.Component.Message = 'VER 0.5.001'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "7 | DisCo VR"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
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
    from wasp.core import Collider


def main(setup, environment, players, filepath, filename, save):
    
    check_data = True
    
    if setup is None and environment is not None:
        check_data = False
        msg = "No setup provided. If you want to export environment data, SETUP cannot be left empty."
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)
    
    if filepath is None:
        check_data = False
        msg = "No path provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if filename is None:
        check_data = False
        msg = "No filename provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if save is None:
        save = False
    
    if check_data:
        
        setup_path = filepath + "\\" + filename + "_setup.json"
        player_path = filepath + "\\" + filename + "_player.json"
        
        setup_data = None
        if setup is not None:
            setup_data = setup.to_data()
        if environment is not None:
            setup_data['environment'] = environment.to_data()
        
        players_data = None
        if len(players) != 0:
            players_data = {}
            players_data['players'] = [p.to_data() for p in players]
        
        if save:
            if setup_data is not None:
                with open(setup_path, "w") as outF:
                    json.dump(setup_data, outF)
            
            if players_data is not None:
                with open(player_path, "w") as outF:
                    json.dump(players_data, outF) 
            
        return [setup_path, player_path], json.dumps(setup_data, indent=2), json.dumps(players_data, indent=2)
    else:
        return -1


result = main(SETUP, ENV, PLAY, PATH, NAME, SAVE)

if result != -1:
    FILES = result[0]
    SF = result[1]
    PF = result[2]