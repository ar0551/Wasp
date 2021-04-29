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
Filter a list of parts according to part names
-
Provided by Wasp 0.5
    Args:
        PART: Parts to filter
        NAME: Name of the parts to extract
    Returns:
        PART_OUT: Filtered parts
        MASK: Boolean mask for the filtered parts
"""

ghenv.Component.Name = "Wasp_Filter Parts by Name"
ghenv.Component.NickName = 'NameFilter'
ghenv.Component.Message = 'v0.5.003'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "2 | Parts"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
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
    from wasp.core import Part


## from http://www.chenjingcheng.com/grasshopper-python-datatree-list-conversion/
def listToDataTree(list):
    rl = list
    result = gh.DataTree[object]()
    for i in range(len(rl)):
        temp = []
        for j in range(len(rl[i])):
            temp.append(rl[i][j])
        path = gh.Kernel.Data.GH_Path(i)
        result.AddRange(temp, path)
    return result


def main(parts, names):
        
    check_data = True
    
    ## check inputs
    if len(parts) == 0:
        check_data = False
        msg = "No part provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if len(names) == 0:
        check_data = False
        msg = "No part name provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    ## execute main code if all needed inputs are available
    if check_data:
        
        filtered_parts = []
        cull_patterns = []
        for i in xrange(len(names)):
            filtered_parts.append([])
            cull_patterns.append([])
            for part in parts:
                if part.name == names[i]:
                    filtered_parts[i].append(part)
                    cull_patterns[i].append(True)
                else:
                    cull_patterns[i].append(False)
        return filtered_parts, cull_patterns
        
    else:
        return -1

result = main(PART, NAME)

if result != -1:
    for i in range(len(result[0])):
        if len(result[0][i]) == 0:
            msg = "No part found with name %s" % (NAME[i])
            ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    PART_OUT = listToDataTree(result[0])
    MASK = listToDataTree(result[1])