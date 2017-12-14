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
Create a basic Wasp Part to be used for aggregation
-
Provided by Wasp 0.0.04
    Args:
        NAME: Part name
        GEO: Part geometry. It will be converted to mesh - to improve performance, perform the conversion before adding to the part and user a low-poly count
        CONN: Connections list
        COLL: OPTIONAL // Collider geometry (for collision detection). A collider will be automatically generated. For complex parts, automatic generation might not work, and you can add a custom collider geometry here.
        ATTR: OPTIONAL // Part attributes
    Returns:
        PART: Part instance
"""

ghenv.Component.Name = "Wasp_Basic Part"
ghenv.Component.NickName = 'Part'
ghenv.Component.Message = 'VER 0.0.04\nDEC_13_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "2 | Parts"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import scriptcontext as sc
import Rhino.Geometry as rg
import Grasshopper.Kernel as gh


def main(part_name, part_geo, connections, collider, attributes):
    
    ## check if Wasp is setup
    if sc.sticky.has_key('WaspSetup'):
        
        check_data = True
        
        ## check inputs
        if part_name is None:
            part_name = 'P1'
            msg = "Default name 'P1' assigned to part"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, msg)
        
        if part_geo is None:
            check_data = False
            msg = "No part geometry provided"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            check_data = False
        
        if collider is None and part_geo is not None:
            collider = part_geo.Duplicate().Offset(sc.sticky['model_tolerance'])
            collider_intersection = rg.Intersect.Intersection.MeshMeshFast(collider, part_geo)
            if len(collider_intersection) > 0:
                collider = None
                collider = part_geo.Duplicate()
                center = part_geo.GetBoundingBox(True).Center
                scale_plane = rg.Plane(center, rg.Vector3d(1,0,0), rg.Vector3d(0,1,0))
                scale_transform = rg.Transform.Scale(scale_plane, 1-sc.sticky['model_tolerance'], 1-sc.sticky['model_tolerance'], 1-sc.sticky['model_tolerance'])
                collider.Transform(scale_transform)
                collider_intersection = rg.Intersect.Intersection.MeshMeshFast(collider, part_geo)
                if len(collider_intersection) > 0:
                    collider = None
                    msg = "Could not compute a valid collider geometry. Please provide a valid collider in the COLL input."
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, msg)
                    check_data = False
        
        if collider is not None and collider.Faces.Count > 1000:
            msg = "The computed collider has a high faces count. Consider providing a low poly collider to improve performance"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
        
        if check_data:
            new_part = sc.sticky['Part'](part_name, part_geo, connections, collider, attributes)
            return new_part
        else:
            return -1
    
    else:
        ## throw warining
        msg = "You must run the SetupWasp component before starting to build!"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1


result = main(NAME, GEO, CONN, COLL, ATTR)

if result != -1:
    PART = result