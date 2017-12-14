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
Saves an aggregation to a .txt file to be loaded for further work
--> WIP Component: might be incomplete or contain bugs! <--
-
Provided by Wasp 0.0.04
    Args:
        AGGR: Aggregation to save
        PATH: Path where to save the aggregation
        NAME: Name of the exported file
        SAVE: True to export
    Returns:
        TXT: Text representation of the aggregation
"""

ghenv.Component.Name = "Wasp_Save to File"
ghenv.Component.NickName = 'WaspSave'
ghenv.Component.Message = 'VER 0.0.04\nDEC_13_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "X | Experimental"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import Rhino.Geometry as rg
import Grasshopper.Kernel as gh


TXT = ""

for part in AGGR:
    
    str_data = ""
    
    str_data += part.name + "\n"
    
    str_a_conn = ""
    for a_conn in part.active_connections:
        str_a_conn += str(a_conn) + ";"
    str_data += str_a_conn + "\n" 
    
    str_transform = ""
    str_transform += str(part.transformation.M00) + ";"
    str_transform += str(part.transformation.M01) + ";"
    str_transform += str(part.transformation.M02) + ";"
    str_transform += str(part.transformation.M03) + ";"
    str_transform += str(part.transformation.M10) + ";"
    str_transform += str(part.transformation.M11) + ";"
    str_transform += str(part.transformation.M12) + ";"
    str_transform += str(part.transformation.M13) + ";"
    str_transform += str(part.transformation.M20) + ";"
    str_transform += str(part.transformation.M21) + ";"
    str_transform += str(part.transformation.M22) + ";"
    str_transform += str(part.transformation.M23) + ";"
    str_transform += str(part.transformation.M30) + ";"
    str_transform += str(part.transformation.M31) + ";"
    str_transform += str(part.transformation.M32) + ";"
    str_transform += str(part.transformation.M33) + ";"
    str_data += str_transform + "\n"
    
    str_data += str(part.is_constrained) + "\n"
    
    TXT += str_data + "---\n"

if SAVE:
    file_name = PATH + "\\" + NAME + ".txt"
    with open(file_name, "w") as outF:
        outF.write(TXT)