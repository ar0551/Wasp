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
Support definition for constrained parts.
Each set of lines defining support locations can be set
-
Provided by Wasp 0.4
    Args:
        DIR: Directions of the support locations as lines
        GEO: OPTIONAL // Geometry of the part the support belongs to (useful for checking if the supports are correctly placed)
    Returns:
        SUP: Support instance
"""

ghenv.Component.Name = "Wasp_Support"
ghenv.Component.NickName = 'Support'
ghenv.Component.Message = 'VER 0.4.007'
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
    from wasp.core import Support


def main(sup_dir, part_geo):
    
    check_data = True
    
    ##check inputs
    support_lines = []
    if len(sup_dir) == 0:
        check_data = False
        msg = "Please provide a valid list of lines as support directions"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    else:
        for sup in sup_dir:
            start = sup.PointAtStart
            end = sup.PointAtEnd
            sup_ln = rg.Line(start, end)
            support_lines.append(sup_ln)
    
    if part_geo is not None:
        for i in range(len(support_lines)):
            intersection = rg.Intersect.Intersection.MeshLine(part_geo, support_lines[i])
            if len(intersection[0]) == 0:
                msg = "Support direction " + str(i) + " does not intersect with the part geometry. Please verify this is intended."
                ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if check_data:
        support = Support(DIR)
        return support
    else:
        return -1


result = main(DIR, GEO)

if result != -1:
    SUP = result