# Wasp: Discrete Design with Grasshopper plug-in (LGPL) initiated by Andrea Rossi
# 
# This file is part of Wasp.
# 
# Copyright (c) 2017, Andrea Rossi <a.rossi.andrea@gmail.com>
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
# You should have received a copy of the GNU General Public License
# along with Wasp; If not, see <http://www.gnu.org/licenses/>.
# 
# @license LGPL-3.0 https://www.gnu.org/licenses/lgpl-3.0.html
#
# Significant parts of Wasp have been developed by Andrea Rossi
# as part of research on digital materials and discrete design at:
# DDU Digital Design Unit - Prof. Oliver Tessmann
# Technische Universitt Darmstadt


#########################################################################
##                            COMPONENT INFO                           ##
#########################################################################

"""
Automated rules generator given a list of parts. It has two separate modes:
- If no grammar is provided in the GR input, the component generates rules between connections of the same type.
- If a grammar is provided, rules are created between connections of different types, according to the specified grammar rules.
-
Provided by Wasp 0.5
    Args:
        PART: Parts from which to generate aggregation rules
        SELF_P: OPTIONAL // Create rules between connections belonging to the same part (True by default)
        SELF_C: OPTIONAL // Create rules between connection with same id (True by default)
        TYP: OPTIONAL // Create rules only between connections of the same type (False by default). Make sure this component is set to False when using Rule Grammars.
        GR: OPTIONAL // Custom connection grammar with format "ConnType">"ConnType"
    Returns:
        R: Generated aggregation rules
"""

ghenv.Component.Name = "Wasp_Rules Generator"
ghenv.Component.NickName = 'RuleGen'
ghenv.Component.Message = 'v0.5.007'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "3 | Rules"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import sys
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
    from wasp.core import Rule


def main(parts, self_part, self_connection, use_types, grammar):
    
    check_data = True
    
    ##check inputs
    if len(parts) == 0 or parts is None:
        check_data = False
        msg = "No part provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if self_part == None:
        self_part = True
    
    if self_connection == None:
        self_connection = True
    
    if use_types is None:
        use_types = False
    
    if check_data:
        rules = []
        
        if len(grammar) == 0:
            for part in parts:
                for conn in part.connections:
                    for other_part in parts:
                        skip_part = False
                        if self_part == False:
                            if part.name == other_part.name:
                                skip_part = True
                            
                        if skip_part == False:
                            for other_conn in other_part.connections:
                                skip_conn = False
                                if self_connection == False:
                                    if conn.id == other_conn.id:
                                        skip_conn = True
                                
                                if skip_conn == False:
                                    if use_types:
                                        if conn.type == other_conn.type:
                                            r = Rule(part.name, conn.id, other_part.name, other_conn.id)
                                            rules.append(r)
                                    else:
                                        r = Rule(part.name, conn.id, other_part.name, other_conn.id)
                                        rules.append(r)
        else:
            for gr_rule in grammar:
                start_type = gr_rule.split(">")[0]
                end_type = gr_rule.split(">")[1]
                
                for part in parts:
                    for conn in part.connections:
                        if conn.type == start_type:
                            for other_part in parts:
                                skip_part = False
                                if self_part == False:
                                    if part.name == other_part.name:
                                        skip_part = True
                                    
                                if skip_part == False:
                                    for other_conn in other_part.connections:
                                        if other_conn.type == end_type:
                                            skip_conn = False
                                            if self_connection == False:
                                                if conn.id == other_conn.id:
                                                    skip_conn = True
                                            
                                            if skip_conn == False:
                                                r = Rule(part.name, conn.id, other_part.name, other_conn.id)
                                                rules.append(r)
        return [rules]
    else:
        return -1


result = main(PART, SELF_P, SELF_C, TYP, GR)

if result != -1:
    R = result[0]


