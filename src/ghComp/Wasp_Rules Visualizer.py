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
Visualize the provided rules.
-
Provided by Wasp 0.5
    Args:
        PART: Parts from which to visualize the rules
        R: Rules to visualize
        SF: OPTIONAL // Spacing factor between rules visualizations (2.0 by default)
        PLN: OPTIONAL // If the rules should be visualized in a different location than the worldXY, base plane of the desired coordinate system
        SI: OPTIONAL // True to show rule index in the list, False to hide it (True by default)
        ST: OPTIONAL // True to show connection types, False to hide them (True by default)
    Returns:
        BP: Base part for the rule
        NP: Added part for the rule
        RTL: Rule text location
        RT: Rule text
"""

ghenv.Component.Name = "Wasp_Rules Visualizer"
ghenv.Component.NickName = 'RuleViz'
ghenv.Component.Message = 'v0.5.006'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "3 | Rules"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import sys
import Grasshopper as gh
import Rhino.Geometry as rg
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
    pass


def main(parts, rules, spacing_factor, base_plane, show_index, show_types):
    
    check_data = True
    
    ##check inputs
    if len(parts) == 0 or parts is None:
        check_data = False
        msg = "No part provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if len(rules) == 0 or rules is None:
        check_data = False
        msg = "No rules provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if spacing_factor == None:
        spacing_factor = 2.0
    
    if show_index is None:
        show_index = True
    
    if show_types is None:
        show_types = True
    
    if check_data:
        
        spacing = 0
        for part in parts:
            if part.dim > spacing:
                spacing = part.dim
        spacing *= 2.0
        spacing *= spacing_factor
        
        rows_count = int(math.ceil(math.sqrt(len(rules))))
        
        base_parts = []
        next_parts = []
        rule_texts = []
        rule_text_locs = []
        
        if base_plane != None:
            global_transform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, base_plane)
        
        for x in range(rows_count):
            for y in range(rows_count):
                
                rule_id = y + (x*rows_count)
                if rule_id >= len(rules):
                    break
                
                rule = rules[rule_id]
                
                first_part = None
                for part in parts:
                    if part.name == rule.part1:
                        first_part = part
                        break
                
                next_part = None
                for part in parts:
                    if part.name == rule.part2:
                        next_part = part
                        break
                
                grid_point = rg.Vector3d(x*spacing, y*spacing, 0)
                move_vec = rg.Vector3d.Subtract(grid_point, rg.Vector3d(first_part.center))
                move_trans = rg.Transform.Translation(move_vec)
                first_part = first_part.transform(move_trans)
                
                if base_plane != None:
                    first_part = first_part.transform(global_transform)
                
                orientTransform = rg.Transform.PlaneToPlane(next_part.connections[rule.conn2].flip_pln, first_part.connections[rule.conn1].pln)
                next_part = next_part.transform(orientTransform)
                
                base_parts.append(first_part)
                next_parts.append(next_part)
                
                text_loc = rg.Point3d(grid_point)
                text_loc.X -= spacing*0.5
                text_loc.Y -= spacing*0.5
                
                text_pln = rg.Plane(text_loc, rg.Vector3d.XAxis, rg.Vector3d.YAxis)
                
                if base_plane != None:
                    text_pln.Transform(global_transform)
                
                text = rule.ToString()
                text = text.replace("WaspRule [", "")
                text = text.replace("]", "")
                
                if show_index:
                    text = str(rule_id) + ": " + text
                
                if show_types:
                    text +="\n"
                    text += "%s>%s"%(first_part.connections[rule.conn1].type, next_part.connections[rule.conn2].type)
                
                rule_texts.append(text)
                rule_text_locs.append(text_pln)
                
            if rule_id >= len(rules):
                break
        return base_parts, next_parts, rule_texts, rule_text_locs
    else:
        return -1

result = main(PART, R, SF, PLN, SI, ST)

if result != -1:
    BP = result[0]
    NP = result[1]
    RT = result[2]
    RTL = result[3]

