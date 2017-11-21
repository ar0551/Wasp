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
Generate a 3d point grid to be fed to the field component
-
Provided by Wasp 0.0.04
    Args:
        BOU: List of geometries defining the boundaries of the field. Geometries must be closed breps or meshes.
        RES: Resolution (Dimension of each cell)
    Returns:
        PTS: Points for field
        COUNT: Cell counts in x, y and z directions
"""

ghenv.Component.Name = "Wasp_Field Points"
ghenv.Component.NickName = 'FieldPts'
ghenv.Component.Message = 'VER 0.0.04\nNOV_21_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "0 | Wasp"
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass

import scriptcontext as sc
import Rhino.Geometry as rg
import Grasshopper.Kernel as gh
import math


def main(boundaries, resolution):
    
    ## check if Wasp is setup
    if sc.sticky.has_key('WaspSetup'):
        
        check_data = True
        
        ##check inputs
        if len(boundaries) == 0:
            check_data = False
            msg = "No boundary geometry provided"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
        if resolution is None and len(boundaries) != 0:
            global_bbox = None
            for geo in boundaries:
                bbox = geo.GetBoundingBox(True)
                
                if global_bbox is None:
                    global_bbox = bbox
                else:
                    global_bbox.Union(bbox)
            
            x_size = global_bbox.Max.X - global_bbox.Min.X
            resolution = int(x_size / 10)
            
            msg = "No resolution provided. Default resolution set to %d"%(resolution)
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            
        if check_data:
            global_bbox = None
            for geo in boundaries:
                bbox = geo.GetBoundingBox(True)
                
                if global_bbox is None:
                    global_bbox = bbox
                else:
                    global_bbox.Union(bbox)
            print global_bbox
            x_size = global_bbox.Max.X - global_bbox.Min.X
            x_count = int(math.ceil(x_size / resolution)) + 1
            y_size = global_bbox.Max.Y - global_bbox.Min.Y
            y_count = int(math.ceil(y_size / resolution)) + 1
            z_size = global_bbox.Max.Z - global_bbox.Min.Z
            z_count = int(math.ceil(z_size / resolution)) + 1
            
            count_vec = rg.Vector3d(x_count, y_count, z_count)
            
            pts = []
            s_pt = global_bbox.Min
            
            for z in range(z_count):
                for y in range(y_count):
                    for x in range(x_count):
                        pt = rg.Point3d(s_pt.X + x*resolution, s_pt.Y + y*resolution, s_pt.Z + z*resolution)
                        pts.append(pt)
            return pts, count_vec
            
        else:
            return -1
    
    else:
        ## throw warining
        msg = "You must run the SetupWasp component before starting to build!"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1


result = main(BOU, RES)

if result != -1:
    PTS = result[0]
    COUNT = result[1]