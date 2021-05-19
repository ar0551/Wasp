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
DisCo enviroment data
-
Provided by Wasp 0.5
    Args:
        GA: OPTIONAL // Game Area as a box. Default is (-5.0, 5.0, -5.0, 5.0, 0, 5.0)
        EG: OPTIONAL // Additional environment geometry as mesh
        BPG: OPTIONAL // Blueprint geometry for assembly guidance (does not act as collider)
        GP: OPTIONAL // Activate ground plane (True by default)
        FR: OPTIONAL // Field resolution
    Returns:
        ENV: DisCo environment data
"""

ghenv.Component.Name = "Wasp_DisCo Environment"
ghenv.Component.NickName = 'DisCoEnv'
ghenv.Component.Message = 'v0.5.004'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "7 | DisCo VR"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import sys
import json
import Rhino.Geometry as rg
import Grasshopper as gh
import math


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
    from wasp.disco import DisCoGameArea, DisCoEnvironment


def main(game_box, environment_geometry, blueprint_geometry, ground_plane, field_resolution):
    
    check_data = True
    
    game_area = None
    if game_box is None:
        game_area = DisCoGameArea(-5.0, 5.0, -5.0, 5.0, 0, 5.0)
    else:
        bbox = game_box.GetBoundingBox(rg.Plane.WorldXY)
        game_area = DisCoGameArea.from_bbox(bbox)
    
    if ground_plane is None:
        ground_plane = True
    
    if field_resolution is None:
        x_size = game_area.max_x - game_area.min_x
        y_size = game_area.max_y - game_area.min_y
        z_size = game_area.max_z - game_area.min_z
        
        ga_vol = x_size*y_size*z_size
        ga_vol /= 100000
        field_resolution = math.pow(ga_vol, 1.0/3)
        print field_resolution
        
    else:
        x_size = game_area.max_x - game_area.min_x
        y_size = game_area.max_y - game_area.min_y
        z_size = game_area.max_z - game_area.min_z
        
        x_count = int(x_size/field_resolution)
        y_count = int(y_size/field_resolution)
        z_count = int(z_size/field_resolution)
        
        pts_count = x_count*y_count*z_count
        
        if pts_count > 1000000:
            msg = "Field resolution is very high. You might consider raising the FR value to improve performance"
            ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
        
    
    if check_data:
        
        disco_environment = DisCoEnvironment(game_area, environment_geometry, blueprint_geometry, ground_plane, field_resolution)
        
        return disco_environment
    else:
        return -1


result = main(GA, EG, BPG, GP, FR)

if result != -1:
    ENV = result