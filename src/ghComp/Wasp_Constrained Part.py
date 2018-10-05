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
Create a Wasp Part with additional constraints (supports, additional colliders)
-
Provided by Wasp 0.1.0
    Args:
        NAME: Part name
        GEO: Part geometry. It will be converted to mesh - to improve performance, perform the conversion before adding to the part and user a low-poly count
        CONN: Connections list
        COLL: OPTIONAL // Collider geometry (for collision detection). A collider will be automatically generated. For complex parts, automatic generation might not work, and you can add a custom collider geometry here.
        ATTR: OPTIONAL // Part attributes
        E_COLL: OPTIONAL // Additional collider geometry (e.g. assembly tool), to be checked in Constrained mode
        SUP: OPTIONAL // Required supports for part placement, to be checked in Constrained mode
    Returns:
        PART: Part instance
"""

ghenv.Component.Name = "Wasp_Constrained Part"
ghenv.Component.NickName = 'ConstrPart'
ghenv.Component.Message = 'VER 0.2.1'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "2 | Parts"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import sys
import scriptcontext as sc
import Rhino.Geometry as rg
import Grasshopper as gh

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


def main(part_name, part_geo, connections, collider_geo, field_name, sub_parts, attributes, add_collider, supports):
    
    check_data = True
    
    ## check inputs
    if part_name is None:
        check_data = False
        msg = "No part name provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if part_geo is None:
        check_data = False
        msg = "No part geometry provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
        check_data = False
    
    ## compute collider, if no custom collider is provided
    if collider_geo is None and part_geo is not None:
        collider_geo = part_geo.Duplicate().Offset(wasp.global_tolerance)
        collider_intersection = rg.Intersect.Intersection.MeshMeshFast(collider_geo, part_geo)
        if len(collider_intersection) > 0:
            collider_geo = None
            collider_geo = part_geo.Duplicate()
            center = part_geo.GetBoundingBox(True).Center
            scale_plane = rg.Plane(center, rg.Vector3d(1,0,0), rg.Vector3d(0,1,0))
            scale_transform = rg.Transform.Scale(scale_plane, 1-wasp.global_tolerance, 1-wasp.global_tolerance, 1-wasp.global_tolerance)
            collider_geo.Transform(scale_transform)
            collider_intersection = rg.Intersect.Intersection.MeshMeshFast(collider_geo, part_geo)
            if len(collider_intersection) > 0:
                collider_geo = None
                msg = "Could not compute a valid collider geometry. Please provide a valid collider in the COLL input."
                ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)
                check_data = False
    
    if collider_geo is not None and collider_geo.Faces.Count > 1000:
        msg = "The computed collider has a high faces count. Consider providing a low poly collider to improve performance"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if add_collider is None and len(supports) == 0:
        msg = "No information provided for Constrained mode. You might want to use the Basic Part component for better performance"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Remark, msg)
    
    
    if check_data:
        ## create collider
        collider = wasp.Collider([collider_geo])
        
        if add_collider is not None and type(add_collider) != wasp.Collider:
            add_collider = wasp.Collider([add_collider])
        
        ## create part instance
        new_part = wasp.Constrained_Part(part_name, part_geo, connections, collider, attributes, add_collider, supports, field=field_name, sub_parts=sub_parts)
        new_part.is_constrained = True
        return new_part
    else:
        return -1


result = main(NAME, GEO, CONN, COLL, FIELD, HI, ATTR, E_COLL, SUP)

if result != -1:
    PART = result