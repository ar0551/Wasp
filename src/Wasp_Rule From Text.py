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
Generate an aggregation rule from a text string description
-
Provided by Wasp 0.0.03
    Args:
        TXT: Text description of the rule with format "Part1|Conn1_Part2|Conn2"
    Returns:
        R: Rule
"""

ghenv.Component.Name = "Wasp_Rule From Text"
ghenv.Component.NickName = 'RuleTxt'
ghenv.Component.Message = 'VER 0.0.03\nSEP_17_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "0 | Wasp"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh

def main(text):
    
    ## check if Wasp is setup
    if sc.sticky.has_key('WaspSetup'):
        
        check_data = True
        
        ##check inputs
        if text is None:
            check_data = False
            msg = "No text provided"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
        if check_data:
            
            try:
                rule_parts = text.split("_")
                part1 = str(rule_parts[0].split("|")[0])
                conn1 = int(rule_parts[0].split("|")[1])
                part2 = str(rule_parts[1].split("|")[0])
                conn2 = int(rule_parts[1].split("|")[1])
                
                rule = sc.sticky['Rule'](part1, conn1, part2, conn2)
                return rule
            except:
                msg = "Text string %s is not formatted correctly"%(text)
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, msg)
                return -1
        else:
            return -1
    
    else:
        ## throw warining
        msg = "You must run the SetupWasp component before starting to build!"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1


result = main(TXT)

if result != -1:
    R = result