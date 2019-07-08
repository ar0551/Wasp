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
Provided by Wasp 0.2
    Args:
        PART: Parts definition for the aggregation
        FILE: File where the aggregation is saved (.txt)
    Returns:
        PART_OUT: Imported aggregation parts
"""

ghenv.Component.Name = "Wasp_Load from File"
ghenv.Component.NickName = 'WaspLoad'
ghenv.Component.Message = 'VER 0.2.08'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "4 | Aggregation"
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass


import sys
import Rhino.Geometry as rg
import Grasshopper as gh
import json


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


def main(parts, file_path):
        
    check_data = True
    
    ## check inputs
    if len(parts) == 0:
        check_data = False
        msg = "No parts provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if file_path is None:
        check_data = False
        msg = "No path provided for the file to load"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    ## execute main code if all needed inputs are available
    if check_data:
        
        loaded_parts = []
        aggr_dict = {}
        
        ## load json data
        with open(FILE, "r") as inF:
            txt_data = inF.read()
            aggr_dict = json.loads(txt_data)
        
        ## sort part ids
        part_ids = [int(id) for id in aggr_dict['parts'].keys()]
        part_ids.sort()
        
        ## load parts
        for id in part_ids:
            part_data = aggr_dict['parts'][str(id)]
                    
            ## part name
            name = part_data['name']
            
            ## part active connections
            active_conn = part_data['active_connections']
            parent = part_data['parent']
            children = part_data['children']
            
            ## part transform
            trans = rg.Transform(0)
            trans.M00 = part_data['transform']['M00']
            trans.M01 = part_data['transform']['M01']
            trans.M02 = part_data['transform']['M02']
            trans.M03 = part_data['transform']['M03']
            
            trans.M10 = part_data['transform']['M10']
            trans.M11 = part_data['transform']['M11']
            trans.M12 = part_data['transform']['M12']
            trans.M13 = part_data['transform']['M13']
            
            trans.M20 = part_data['transform']['M20']
            trans.M21 = part_data['transform']['M21']
            trans.M22 = part_data['transform']['M22']
            trans.M23 = part_data['transform']['M23']
            
            trans.M30 = part_data['transform']['M30']
            trans.M31 = part_data['transform']['M31']
            trans.M32 = part_data['transform']['M32']
            trans.M33 = part_data['transform']['M33']
            
            constrained = part_data['is_constrained']
            
            new_part = None
            for part in PART:
                if part.name == name:
                    new_part = part.transform(trans)
                    
                    ## flip part if negative scaling occurs
                    if trans.M00 * trans.M11 * trans.M22 < 0:
                        ## geometry
                        new_part.geo.Flip(True, True, True)
                        ## connections
                        for conn in new_part.connections:
                            pass
                            conn.pln.Flip()
                            conn.pln.Rotate(math.pi/2, conn.pln.ZAxis)
                        ## collider
                        for geo in new_part.collider.geometry:
                            geo.Flip(True, True, True)
                    
                    break
            
            if new_part is not None:
                new_part.active_connections = active_conn
                new_part.parent = parent
                new_part.children = children
                new_part.is_constrained = constrained
                
                loaded_parts.append(new_part)
            
        return loaded_parts
    else:
        return -1

result = main(PART, FILE)

if result != -1:
    PART_OUT = result