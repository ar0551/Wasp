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
Loads an aggregation from a previously saved .txt file
-
Provided by Wasp 0.5
    Args:
        FILE: File where the field is saved (.json)
        UPDATE: True to load the saved file
    Returns:
        FIELD: Imported field
"""

ghenv.Component.Name = "Wasp_Load Field from File"
ghenv.Component.NickName = 'LoadField'
ghenv.Component.Message = 'v0.5.003'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "5 | Fields"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import sys
import Grasshopper as gh
import json


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
    from wasp.field import Field


def main(file_path, load_file):
        
    check_data = True
    
    ## check inputs
    if file_path is None:
        check_data = False
        msg = "No path provided for the file to load"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if load_file is None:
        lad_file = False
    
    ## execute main code if all needed inputs are available
    if check_data:
        
        if load_file:
            field_dict = {}
            
            ## load json data
            with open(file_path, "r") as inF:
                txt_data = inF.read()
                field_dict = json.loads(txt_data)
            
            field = Field.from_data(field_dict)
            return field
        else:
            return -1
        
    else:
        return -1


result = main(FILE, LOAD)

if result != -1:
    FIELD = result