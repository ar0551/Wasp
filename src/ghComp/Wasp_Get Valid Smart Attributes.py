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
Get the valid smart attributes from a given aggregation.
-
Provided by Wasp 0.5
    Args:
        AGGR: Aggregation from which to extract the smart attributes
        ID: Name of the smart attribute to extract
    Returns:
        VAL: Value stored in the valid smart attributes
"""

ghenv.Component.Name = "Wasp_Get Valid Smart Attributes"
ghenv.Component.NickName = 'GetSmartAttr'
ghenv.Component.Message = 'v0.5.005'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "1 | Elements"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import sys
import Grasshopper as gh
import ghpythonlib.treehelpers as th


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
    from wasp.core import SmartAttribute


def main(aggregation, ids):
        
    check_data = True
    
    ## check inputs
    if aggregation is None:
        check_data = False
        msg = "No aggregation provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if len(ids) == 0:
        check_data = False
        msg = "No attribute ids provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    ## execute main code if all needed inputs are available
    if check_data:
        
        values = []
        
        for i in range(len(aggregation.aggregated_parts)):
            part = aggregation.aggregated_parts[i]
            p_matrix = aggregation.check_blocked_connections(part)
            values.append([])
            for attr_id in ids:
                for attr in part.attributes:
                    if type(attr) == SmartAttribute:
                        if attr.name == attr_id:
                            is_valid = True
                            for i2 in range(len(attr.conn_mask)):
                                if attr.conn_mask[i2] == 1:
                                    if i2 not in p_matrix:
                                        is_valid = False
                                        break
                                elif attr.conn_mask[i2] == -1:
                                    if i2 in p_matrix:
                                        is_valid = False
                                        break
                            if is_valid:
                                values[i].append(attr.values)
                            break
        
        return th.list_to_tree(values)
    else:
        return -1

result = main(AGGR, ID)

if result != -1:
        VAL = result