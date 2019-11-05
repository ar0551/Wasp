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
Generate an aggregation rule from part names and connections ids
-
Provided by Wasp 0.3
    Args:
        P1: Name of base part
        C1: Id of base connection
        P2: Name of new part to be aggregated
        C2: Id of new connection
    Returns:
        R: Rule
"""

ghenv.Component.Name = "Wasp_Rule"
ghenv.Component.NickName = 'Rule'
ghenv.Component.Message = 'VER 0.3.001'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "3 | Rules"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import sys
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
    msg = "Cannot import Wasp. Is the wasp.py module installed in " + wasp_path + "?"
    ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)

## if Wasp is installed correctly, load the classes required by the component
if wasp_loaded:
    from wasp import Rule


def main(part1, conn1, part2, conn2):
    
    check_data = True
    
    ##check inputs
    if part1 is None or conn1 is None or part2 is None or conn2 is None:
        check_data = False
        msg = "Missing data. Please provide data for all inputs."
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if check_data:
        rule = Rule(part1, conn1, part2, conn2)
        return rule
    else:
        return -1


result = main(P1, C1, P2, C2)

if result != -1:
    R = result