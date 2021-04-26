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
DisCo Player settings
-
Provided by Wasp 0.5
    Args:
        NAME: Player name
        VRFPS: Player mode: 0 for VR player, 1 for FPS player
        TS: OPTIONAL // Tool settings (all tools availabe by default)
        PS: OPTIONAL // Placement settings (all placement modes availabe by default)
        IOS: OPTIONAL // IO settings (all IO modes availabe by default)
        PC: OPTIONAL // Point constraints for fixing the player position
        BC: OPTIONAL // Box constraints for limiting the player movement area
        CC: OPTIONAL // Curve constraints for limiting the player movement along the curve
        CCS: OPTIONAL // Curve constraint sample resolution (0.1 by default)
    Returns:
        PLAY: DisCo Player settings
"""

ghenv.Component.Name = "Wasp_DisCo Player"
ghenv.Component.NickName = 'DisCoPlayer'
ghenv.Component.Message = 'v0.5.002'
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
    from wasp.disco import *


def main(name, vr_fps, tool, place, IO, points, boxes, curves, crv_sample):
    
    check_data = True
    
    if name is None:
        check_data = False
        msg = "Please provide a player name"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if vr_fps is None:
        check_data = False
        msg = "Please provide a payer mode (0 for VR, 1 for FPS)"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if tool is None:
        tool = DisCoToolSettings()
    
    if place is None:
        place = DisCoPlacementSettings()
    
    if IO is None:
        IO = DisCoIOSettings()
    
    if check_data:
        
        pt_const = []
        if len(points) > 0:
            for pt in points:
                pt_const.append(DisCoPointConstraint.from_point(pt))
        
        box_const = []
        if len(boxes) > 0:
            for box in boxes:
                bbox = box.GetBoundingBox(rg.Plane.WorldXY)
                box_const.append(DisCoBoxConstraint.from_bbox(bbox))
        
        crv_const = []
        if len(curves) > 0:
            for crv in curves:
                crv_const.append(DisCoCurveConstraint.from_curve(crv, crv_sample))
        
        player = DisCoPlayer(name, vr_fps, tool, place, IO, pt_const, box_const, crv_const)
        
        return player
    else:
        return -1


result = main(NAME, VRFPS, TS, PS, IOS, PC, BC, CC, CCS)

if result != -1:
    PLAY = result