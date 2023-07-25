# Wasp: Discrete Design with Grasshopper plug-in (LGPL) initiated by Andrea Rossi
# 
# This file is part of Wasp.
# 
# Copyright (c) 2017-2023, Andrea Rossi <a.rossi.andrea@gmail.com>
# Wasp is free software; you can redistribute it and/or modify 
# it under the terms of the GNU Lesser General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Wasp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with Wasp; If not, see <http://www.gnu.org/licenses/>.
# 
# @license LGPL-3.0 https://www.gnu.org/licenses/lgpl-3.0.html
#
# Early development of Wasp has been carried out by Andrea Rossi
# as part of research on digital materials and discrete design at:
# DDU Digital Design Unit - Prof. Oliver Tessmann
# Technische Universitt Darmstadt


#########################################################################
##                            COMPONENT INFO                           ##
#########################################################################

"""
Applies a geometric transformation to an existing part, returning a transformed copy.
Can be used with any Transform component from Grasshopper.
Create a Transform component without inputting any geometry and plug the X output to the TR input.
-
Provided by Wasp 0.5
    Args:
        PART: Part to be transformed
        TR: Transformation
    Returns:
        PART_OUT: Transformed part
"""

ghenv.Component.Name = "Wasp_Transform Part"
ghenv.Component.NickName = 'PartTr'
ghenv.Component.Message = 'v0.5.008'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "2 | Parts"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import sys
import Grasshopper as gh
import math


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
    from wasp.core import Part


def main(part, transform):
    
    check_data = True
    
    ##check inputs
    if part is None:
        check_data = False
        msg = "Please provide a valid part to be transformed"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if transform is None:
        check_data = False
        msg = "Please provide a valid transformation"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if check_data:
        ## transform part
        part_trans = part.transform(transform, maintain_parenting=True)
        
        ## flip part if negative scaling occurs
        if transform.M00 * transform.M11 * transform.M22 < 0:
            ## geometry
            part_trans.geo.Flip(True, True, True)
            ## connections
            for conn in part_trans.connections:
                pass
                conn.pln.Flip()
                conn.pln.Rotate(math.pi/2, conn.pln.ZAxis)
            ## collider
            for geo in part_trans.collider.geometry:
                geo.Flip(True, True, True)
        
        return part_trans
    else:
        return -1


result = main(PART, TR)

if result != -1:
    PART_OUT = result
