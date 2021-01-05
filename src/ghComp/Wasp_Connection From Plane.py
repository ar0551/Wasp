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
Create a connection from a given plane.
It can create connections which cause collisions and overlapping of components
-
Provided by Wasp 0.4
    Args:
        PLN: Connection plane
        T: OPTIONAL // Connection type (to be used with Rule Generator component)
    Returns:
        CONN: Connection object
        PLN_OUT: Connection plane (for debugging)
"""

ghenv.Component.Name = "Wasp_Connection From Plane"
ghenv.Component.NickName = 'ConnPln'
ghenv.Component.Message = 'VER 0.4.012'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "1 | Elements"
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
    from wasp.core import Connection


def main(conn_planes, conn_type):
        
    check_data = True
    
    ##check inputs
    if len(conn_planes) == 0:
        check_data = False
        msg = "No plane provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    types = []
    if len(conn_type) == 0:
        for i in range(len(conn_planes)):
            types.append("")
    elif len(conn_type) == 1:
        for i in range(len(conn_planes)):
            types.append(conn_type[0])
    elif len(conn_planes) != len(conn_type):
        check_data = False
        msg = "Different amount of planes and types provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)
    else:
        for i in range(len(conn_planes)):
            types.append(conn_type[i])
    
    
    if check_data:
        connections = []
        out_planes = []
        for i in range(len(conn_planes)):
            plane = conn_planes[i]
            if plane is None:
                msg = "No valid plane provided for connection %d"%(i)
                ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)
            else:
                conn = Connection(plane, types[i], "", -1)
                connections.append(conn)
                out_planes.append(plane)
        
        return connections, out_planes
    
    else:
        return -1

result = main(PLN, T)

if result != -1:
    CONN = result[0]
    PLN_OUT = result[1]