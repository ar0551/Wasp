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
Plane global constraint
-
Provided by Wasp 0.2
    Args:
        PLN: Plane to use as constraints
        POS: OPTIONAL // True to place parts on the positive direction of the Z axis, False for the negative direction (True by default)
        SOFT: OPTIONAL // True to check only the part center point, False to check also for geometry intersection (True by default)
    Returns:
        PC: Plane constraint
"""

ghenv.Component.Name = "Wasp_Plane Constraint"
ghenv.Component.NickName = 'PlaneConst'
ghenv.Component.Message = "VER 0.2.07"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "4 | Aggregation"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import sys
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


## Main code execution
def main(plane, positive, soft_constraint):
    
    check_data = True
    ##check inputs
    if plane is None:
        check_data = False
        msg = "Provide a valid plane"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if positive is None:
        positive = True
    
    if soft_constraint is None:
        soft_constraint = True
    
    if check_data:
        plane_constraint = wasp.Plane_Constraint(plane, _positive = positive, _soft = soft_constraint)
        return plane_constraint
        
    else:
        return -1


result = main(PLN, POS, SOFT)

if result != -1:
    PC = result