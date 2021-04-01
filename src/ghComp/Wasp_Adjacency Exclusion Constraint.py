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
Part Adjacencies and Exclusions Constraint.
It allows to control if certain connection should be allowed to be in contact with other parts or not.
-
Provided by Wasp 0.5
    Args:
        DIR: Directions of the support locations as lines
        PN: OPTIONAL // If the adjacency/exclusion direction has to be associated to a specific part
        AE: OPTIONAL // Constraint type: True for adjacency, False for exclusion (True by default)
    Returns:
        AEC: Adjacency/Exclusion Constraint instance
"""

ghenv.Component.Name = "Wasp_Adjacency Exclusion Constraint"
ghenv.Component.NickName = 'AdjExcConst'
ghenv.Component.Message = 'v0.5.001'
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
    from wasp.core import Adjacency_Constraint


def main(directions, part_names, adjacency_type):
    
    check_data = True
    
    ##check inputs
    direction_lines = []
    if len(directions) == 0:
        check_data = False
        msg = "Please provide a valid list of lines as directions"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    else:
        for d in directions:
            start = d.PointAtStart
            end = d.PointAtEnd
            d_ln = rg.Line(start, end)
            direction_lines.append(d_ln)
    
    if len(part_names) == 0:
        pass
    elif len(directions) != len(part_names):
        check_data = False
        msg = "Please provide an equal number of directions and part names"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)
    
    if adjacency_type is None:
        adjacency_type = True
    
    if check_data:
        adj_constraint = Adjacency_Constraint(direction_lines, adjacency_type, part_names)
        return adj_constraint
    else:
        return -1


result = main(DIR, PN, AE)

if result != -1:
    AEC = result