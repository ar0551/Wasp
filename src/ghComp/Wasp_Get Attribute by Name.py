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
Extract values stored in an atrribute with the given name.
-
Provided by Wasp 0.1.0
    Args:
        ATTR: Attributes list to search
        ID: Name of the attribute to extract
    Returns:
        VAL: Value stored in the requested attribute
"""

ghenv.Component.Name = "Wasp_Get Attribute by Name"
ghenv.Component.NickName = 'GetAttr'
ghenv.Component.Message = 'VER 0.2.1'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "1 | Elements"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import sys
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


def main(attributes, id):
        
    check_data = True
    
    ## check inputs
    if len(attributes) == 0:
        check_data = False
        msg = "No attribute provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if id is None:
        check_data = False
        msg = "No attribute id provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    ## execute main code if all needed inputs are available
    if check_data:
        values = []
        for attr in attributes:
            if attr.name == id:
                values = attr.values
        return values
    else:
        return -1

result = main(ATTR, ID)

if result != -1:
    VAL = result




elif ID is None:
    msg = "No id provided"
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
else:
    VAL = []
    for attr in ATTR:
        if attr.name == ID:
            VAL = attr.values