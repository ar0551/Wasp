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
Provided by Wasp 0.3
    Args:
        NAME: Part name
        GEO: Part geometry. It will be converted to mesh - to improve performance, perform the conversion before adding to the part and user a low-poly count
        CONN: Connections list
        COLL: OPTIONAL // Collider geometry (for collision detection). A collider will be automatically generated. For complex parts, automatic generation might not work, and you can add a custom collider geometry here.
        FIELD: OPTIONAL // Field to associate with the part for Field-Driven Aggegation (Needed only when using multiple fields within one aggregation)
        HI: OPTIONAL // Hierarchy: List of parts composing the part at a lower heriarchical level in the aggregation
        ATTR: OPTIONAL // Part attributes
        E_COLL: OPTIONAL // Additional collider geometry (e.g. assembly tool), to be checked in Constrained mode
        SUP: OPTIONAL // Required supports for part placement, to be checked in Constrained mode
    Returns:
        PART: Part instance
"""

ghenv.Component.Name = "Wasp_Advanced Part"
ghenv.Component.NickName = 'AdvPart'
ghenv.Component.Message = 'VER 0.3.001'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "2 | Parts"
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
    msg = "Cannot import Wasp. Is the wasp.py module installed in " + wasp_path + "?"
    ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)

## if Wasp is installed correctly, load the classes required by the component
if wasp_loaded:
    from wasp import AdvancedPart
    from wasp import Collider
    from wasp import global_tolerance


def main(part_name, part_geo, connections, collider, field_name, sub_parts, attributes, add_collider, supports):
    
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
    if collider is None:
        if part_geo is not None:
            collider_geo = part_geo.Duplicate().Offset(global_tolerance)
            collider_intersection = rg.Intersect.Intersection.MeshMeshFast(collider_geo, part_geo)
            if len(collider_intersection) > 0:
                collider_geo = None
                collider_geo = part_geo.Duplicate()
                center = part_geo.GetBoundingBox(True).Center
                scale_plane = rg.Plane(center, rg.Vector3d(1,0,0), rg.Vector3d(0,1,0))
                scale_transform = rg.Transform.Scale(scale_plane, 1-global_tolerance, 1-global_tolerance, 1-global_tolerance)
                collider_geo.Transform(scale_transform)
                collider_intersection = rg.Intersect.Intersection.MeshMeshFast(collider_geo, part_geo)
                if len(collider_intersection) > 0:
                    collider_geo = None
                    msg = "Could not compute a valid collider geometry. Please provide a valid collider in the COLL input."
                    ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)
                    check_data = False
            
            if collider_geo is not None:
                collider = Collider([collider_geo])
    
    else:
        if type(collider) != Collider:
            if type(collider) == rg.Mesh:
                collider = Collider([collider])
            else:
                msg = "Collider geometry must be of type Mesh or WaspCollider."
                ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)
                check_data = False
        
    if collider is not None and collider.faces_count > 1000:
        msg = "The collider has a high faces count. Consider providing a low poly collider to improve performance"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    
    if check_data:
        if add_collider is not None and type(add_collider) != Collider:
            add_collider = Collider([add_collider])
        
        ## create part instance
        new_part = AdvancedPart(part_name, part_geo, connections, collider, attributes, add_collider, supports, field=field_name, sub_parts=sub_parts)
        new_part.is_constrained = True
        
        if new_part.dim < global_tolerance*10:
            msg = "The parts you created are very small. You might consider scaling them or decreasing the tolerance of your Rhino file."
            ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
        
        return new_part
    else:
        return -1


result = main(NAME, GEO, CONN, COLL, FIELD, HI, ATTR, E_COLL, SUP)

if result != -1:
    PART = result