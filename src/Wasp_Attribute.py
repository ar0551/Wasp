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
Attribute to be attached to a part.
Could be geometry or any other kind of data (eg. text, numeric variables, color).
If Geometry, Transformable must be set to True to mantain the geometry attached to the part during aggregation.
-
Provided by Wasp 0.1.0
    Args:
        ID: Name of the attribute
        VAL: Value of the attribute (any type of Gh-compatible data possible)
        TR: Transformable. Set it to True for Geometry, False for other types of data
    Returns:
        ATTR: Attribute instance to attach to a component
"""

ghenv.Component.Name = "Wasp_Attribute"
ghenv.Component.NickName = 'Attribute'
ghenv.Component.Message = 'VER 0.1.0\nDEC_22_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "1 | Elements"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Rhino.Geometry as rg
import Grasshopper.Kernel as gh

def main(id, values, transformable = False):
    
    ## check if Wasp is setup
    if sc.sticky.has_key('WaspSetup'):
        
        check_data = True
        
        ##check inputs
        if id is None:
            id = 'ATTR_01'
            msg = "Default name 'ATTR_01' assigned to attribute"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, msg)
        
        if len(values) == 0:
            check_data = False
            msg = "Please provide values for the attribute"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
        if transformable is None:
            msg = "Transformable set to False by default"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, msg)
        
        if transformable == True:
            val_count = 0
            for i in range(len(values)):
                try:
                    values[i].Transform(rg.Transform.Identity)
                except:
                    check_data = False
                    msg = "Value %d is not transformable"%(i)
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, msg)
        
        if check_data:
            attribute = sc.sticky['Attribute'](id, values, transformable)
            return attribute
        else:
            return -1
    
    else:
        ## throw warining
        msg = "You must run the SetupWasp component before starting to build!"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1


result = main(ID, VAL, TR)

if result != -1:
    ATTR = result