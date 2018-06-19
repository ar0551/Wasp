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
--> WIP Component: might be incomplete or contain bugs! <--
-
Provided by Wasp 0.0.04
    Args:
        PART: Parts definition for the aggregation
        FILE: File where the aggregation is saved (.txt)
    Returns:
        PART_OUT: Imported aggregation parts
"""

ghenv.Component.Name = "Wasp_Load from File"
ghenv.Component.NickName = 'WaspLoad'
ghenv.Component.Message = 'VER 0.1.0\nDEC_22_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "X | Experimental"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import Rhino.Geometry as rg
import Grasshopper.Kernel as gh


PART_OUT = []

txt_data = []


if FILE is not None:
    with open(FILE, "r") as inF:
        txt_data = inF.read().split("---\n")
else:
    msg = "No file provided"
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)

if len(txt_data) > 0:
    for txt in txt_data:
        try:
            data = txt.split("\n")
            
            ## part name
            name = data[0]
            
            ## part active connections
            active_conn = []
            aconn_data = data[1].split(";")
            for ac in aconn_data:
                try:
                    aconn_id = int(ac)
                    active_conn.append(aconn_id)
                except:
                    pass
            
            ## part transform
            trans = rg.Transform(0)
            tranform_data = data[2].split(";")
            
            trans.M00 = float(tranform_data[0])
            trans.M01 = float(tranform_data[1])
            trans.M02 = float(tranform_data[2])
            trans.M03 = float(tranform_data[3])
            trans.M10 = float(tranform_data[4])
            trans.M11 = float(tranform_data[5])
            trans.M12 = float(tranform_data[6])
            trans.M13 = float(tranform_data[7])
            trans.M20 = float(tranform_data[8])
            trans.M21 = float(tranform_data[9])
            trans.M22 = float(tranform_data[10])
            trans.M23 = float(tranform_data[11])
            trans.M30 = float(tranform_data[12])
            trans.M31 = float(tranform_data[13])
            trans.M32 = float(tranform_data[14])
            trans.M33 = float(tranform_data[15])
            
            constrained = bool(data[3])
            
            new_part = None
            for part in PART:
                if part.name == name:
                    new_part = part.transform(trans)
                    break
            
            if new_part is not None:
                new_part.active_connections = active_conn
                new_part.is_constrained = constrained
                
                PART_OUT.append(new_part)
        except:
            pass