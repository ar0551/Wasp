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
Saves current status of an aggregation to a .json file.
-
Provided by Wasp 0.4
    Args:
        OBJ: Object to serialize and save to file
        FILTER: OPTIONAL // keys of the elements to serialize (by default, all object's parameters will be serialized)
        PATH: Path where to save the object
        NAME: Name of the exported file
        SAVE: True to export
    Returns:
        KEY: list of the keys available in the object's dictionary (for filtering)
        TXT: Text representation of the object. NB!!! files can become very large, and attempting to visualize them in a panel might cause Grasshopper to crash!!!
        FILE: Path to the saved file
"""

ghenv.Component.Name = "Wasp_Serialize Object to File"
ghenv.Component.NickName = 'Serializer'
ghenv.Component.Message = 'VER 0.4.007'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "X | Experimental"
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass


import sys
import os
import Rhino.Geometry as rg
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
    pass


def main(object, filter, path, filename, save):
        
    check_data = True
    check_save_data = True
    
    ## check inputs
    if object is None:
        check_data = False
        msg = "No object provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if path is None:
        check_save_data = False
    
    if filename is None:
        check_save_data = True
    
    if save is None:
        save = False
    
    ## execute main code if all needed inputs are available
    if check_data:
        data = object.to_data()
        keys = data.keys()
        
        filtered_data = {}
        if len(filter) > 0:
            for f_key in filter:
                if data.has_key(f_key):
                    filtered_data[f_key] = data[f_key]
        else:
            filtered_data = data
        
        full_path = None
        if check_save_data:
            full_path = os.path.join(path, filename + ".json")
        
        if save:
            if full_path is not None:
                with open(full_path, "w") as outF:
                    json.dump(filtered_data, outF)
            else:
                msg = "Cannot save the file. Either the path or the filename are missing."
                ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)
        
        return keys, json.dumps(filtered_data, indent = 2), full_path
    else:
        return -1

result = main(OBJ, FILTER, PATH, NAME, SAVE)

if result != -1:
    KEY = result[0]
    TXT = result[1]
    FILE = result[2]

