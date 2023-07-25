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
Part Catalog. It allows to define a fixed number of each type of part to be used in a stochastic aggregation.
-
Provided by Wasp 0.5
    Args:
        PART: Parts from which to generate a parts catalog
        NUM: Amounts of each part in the catalog
        LIM: OPTIONAL // If True, the catalog will be limited, and aggregation will stop after using the given parts numbers. If False, the given numbers will be used as proportional (False by default)
        AD: OPTIONAL // If True, catalog will be adaptive, and change its internal probabilities according to the aggregation state (False by default). Works only if LIM is set to False.
    Returns:
        CAT: Parts catalog
"""

ghenv.Component.Name = "Wasp_Parts Catalog"
ghenv.Component.NickName = 'PartCat'
ghenv.Component.Message = 'v0.5.008'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "2 | Parts"
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass

import sys
import scriptcontext as sc
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
    from wasp.core import PartCatalog

def main(parts, amounts, limited, adaptive):
    
    check_data = True
    
    ##check inputs
    if len(parts) == 0:
        check_data = False
        msg = "No part provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if len(amounts) == 0:
        check_data = False
        msg = "No part amounts provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    elif len(amounts) == 1:
        amount = amounts[0]
        amounts = []
        for part in parts:
            amounts.append(amount)
    
    elif len(amounts) != len(parts):
        check_data = False
        msg = "Different amount of parts and part amounts"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)
    
    if limited is None:
        limited = False
    
    if adaptive is None:
        adaptive = False
    
    if check_data:
        part_names = [part.name for part in parts]
        parts_catalog = PartCatalog(part_names, amounts, _is_limited = limited, _is_adaptive = adaptive)
        return parts_catalog
    else:
        return -1


result = main(PART, NUM, LIM, AD)

if result != -1:
    CAT = result