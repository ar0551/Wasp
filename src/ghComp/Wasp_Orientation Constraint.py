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
Orientation Constraint.
It allows to control if the part should be placed according to a custom orientation.
-
Provided by Wasp 0.4
    Args:
        DIR: Directions of the part orientation to be tested (as Line or Vector)
        R: Angle range which is allowed for the transformed part
        PLN: OPTIONAL // Plane where to calculate the angle (Default is RhinoXY)
    Returns:
        OC: Orientation Constraint instance
"""

ghenv.Component.Name = "Wasp_Orientation Constraint"
ghenv.Component.NickName = 'AdjExcConst'
ghenv.Component.Message = 'VER 0.4.013'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "4 | Constraints"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import sys
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
    from wasp.core import Orientation_Constraint


def main(direction, range, base_plane):
    
    check_data = True
    
    ##check inputs
    if direction is None:
        check_data = False
        msg = "Please provide a valid direction line"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if range is None:
        check_data = False
        msg = "Please provide a valid angle interval"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if base_plane is None:
        base_plane = rg.Plane.WorldXY
    
    if check_data:
        orient_constraint = Orientation_Constraint(direction, base_plane, range)
        return orient_constraint
    else:
        return -1


result = main(DIR, R, PLN)

if result != -1:
    OC = result