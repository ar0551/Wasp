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
Support definition for constrained parts.
Each set of lines defining support locations can be set
-
Provided by Wasp 0.0.04
    Args:
        DIR: Directions of the support locations as lines
        GEO: OPTIONAL // Geometry of the part the support belongs to
    Returns:
        SUP: Support element
"""

ghenv.Component.Name = "Wasp_Support"
ghenv.Component.NickName = 'Support'
ghenv.Component.Message = 'VER 0.0.04\nDEC_13_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "1 | Elements"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import scriptcontext as sc
import Rhino.Geometry as rg
import Grasshopper.Kernel as gh


def main(sup_dir, part_geo):
    
    ## check if Wasp is setup
    if sc.sticky.has_key('WaspSetup'):
        
        check_data = True
        
        ##check inputs
        if len(sup_dir) == 0:
            check_data = False
            msg = "Please provide a valid list of lines as support directions"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
        if part_geo is not None:
            for i in range(len(sup_dir)):
                intersection = rg.Intersect.Intersection.MeshPolyline(part_geo, sup_dir[i])
                if len(intersection[0]) == 0:
                    msg = "Support direction " + str(i) + " does not intersect with the part geometry. Please verify this is intended."
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        else:
            msg = "No part geometry provided. Correct position of supports cannot be verified."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, msg)
        
        if check_data:
            support = sc.sticky['Support'](DIR)
            return support
        else:
            return -1
    
    else:
        ## throw warining
        msg = "You must run the SetupWasp component before starting to build!"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1


result = main(DIR, GEO)

if result != -1:
    SUP = result