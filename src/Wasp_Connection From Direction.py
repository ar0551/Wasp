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
Create a connection on a given part geometry from center and X-asix direction
(Z direction is determined based on the normals of the component geometry)
-
Provided by Wasp 0.0.04
    Args:
        GEO: Geometry of the part to which the connection belongs
        CEN: Origin of the connection plane
        UP: Line idetifying the X-axis of the connection plane - determines the plane orientation to mantain when transforming
        T: OPTIONAL // Connection type (to be used with Rule Generator component)
    Returns:
        CONN: Connection object
        PLN_OUT: Plane for each connection object (for debugging)
"""

ghenv.Component.Name = "Wasp_Connection From Direction"
ghenv.Component.NickName = 'ConnDir'
ghenv.Component.Message = 'VER 0.0.04\nNOV_14_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "0 | Wasp"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import Rhino.Geometry as rg
import Grasshopper.Kernel as gh

def main(part_geo, conn_centers, conn_ups, conn_type):
    
    ## check if Wasp is setup
    if sc.sticky.has_key('WaspSetup'):
        
        check_data = True
        
        ## check inputs
        if part_geo is None:
            check_data = False
            msg = "No part geometry provided"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
        if len(conn_centers) != len(conn_ups):
            check_data = False
            msg = "Different amount of centers and up vectors provided"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, msg)
        
        types = []
        if len(conn_type) == 0:
            for i in range(len(conn_centers)):
                types.append("00")
        elif len(conn_type) == 1:
            for i in range(len(conn_centers)):
                types.append(conn_type[0])
        elif len(conn_centers) != len(conn_type):
            check_data = False
            msg = "Different amount of centers and types provided"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, msg)
        else:
            for i in range(len(conn_centers)):
                types.append(conn_type[i])
        
        ## execute main code if all needed inputs are available
        if check_data:
            connections = []
            out_planes = []
            for i in range(len(conn_centers)):
                
                center = conn_centers[i]
                up = conn_ups[i]
                plane = None
                
                up_start = rg.Vector3d(up.PointAtStart)
                up_end = rg.Vector3d(up.PointAtEnd)
                up_vec = rg.Vector3d.Subtract(up_end, up_start)
                
                for face in GEO.Faces:
                    pt_uv = face.ClosestPoint(center)
                    pt = face.PointAt(pt_uv[1], pt_uv[2])
                    dist = rg.Point3d.DistanceTo(center, pt)
                    if(dist < 0.001):
                        normal = face.NormalAt(pt_uv[1], pt_uv[2])
                        plane = rg.Plane(center, normal)
                        x_axis = plane.XAxis
                        angle = rg.Vector3d.VectorAngle(x_axis, up_vec, plane)
                        plane.Rotate(angle, normal)
                        break
                        
                if plane is None:
                    msg = "No valid plane provided for connection %d"%(i)
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, msg)
                else:
                    conn = sc.sticky['Connection'](plane, types[i], "", -1)
                    connections.append(conn)
                    out_planes.append(plane)
            
            return connections, out_planes
        
        else:
            return -1
            
    
    else:
        ## throw warining
        msg = "You must run the SetupWasp component before starting to build!"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1


result = main(GEO, CEN, UP, T)

if result != -1:
    CONN = result[0]
    PLN_OUT = result[1]