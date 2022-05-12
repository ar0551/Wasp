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
Provided by Wasp 0.5
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
ghenv.Component.Message = 'v0.5.006'
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
    from wasp import global_tolerance


def main(part_geo, conn_centers, conn_ups, conn_type):
        
    check_data = True
    
    ## check inputs
    if part_geo is None:
        check_data = False
        msg = "No part geometry provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if len(conn_centers) != len(conn_ups):
        check_data = False
        msg = "Different amount of centers and up vectors provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)
    
    types = []
    if len(conn_type) == 0:
        for i in range(len(conn_centers)):
            types.append("0")
    elif len(conn_type) == 1:
        for i in range(len(conn_centers)):
            types.append(conn_type[0])
    elif len(conn_centers) != len(conn_type):
        check_data = False
        msg = "Different amount of centers and types provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)
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
            
            if type(part_geo) == rg.Brep:
                for face in part_geo.Faces:
                    pt_uv = face.ClosestPoint(center)
                    pt = face.PointAt(pt_uv[1], pt_uv[2])
                    dist = rg.Point3d.DistanceTo(center, pt)
                    if(dist < global_tolerance):
                        normal = face.NormalAt(pt_uv[1], pt_uv[2])
                        plane = rg.Plane(center, normal)
                        x_axis = plane.XAxis
                        angle = rg.Vector3d.VectorAngle(x_axis, up_vec, plane)
                        plane.Rotate(angle, normal)
                        break
            
            elif type(part_geo) == rg.Mesh:
                part_geo.Normals.ComputeNormals()
                mesh_pt = part_geo.ClosestMeshPoint(center, global_tolerance)
                if mesh_pt is not None:
                    normal = part_geo.NormalAt(mesh_pt)
                    plane = rg.Plane(center, normal)
                    x_axis = plane.XAxis
                    angle = rg.Vector3d.VectorAngle(x_axis, up_vec, plane)
                    plane.Rotate(angle, normal)
            
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

result = main(GEO, CEN, UP, T)

if result != -1:
    CONN = result[0]
    PLN_OUT = result[1]