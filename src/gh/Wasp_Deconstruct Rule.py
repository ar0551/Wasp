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
Extract information from a rule instance.
-
Provided by Wasp 0.1.0
    Args:
        R: Rule
    Returns:
        P1: Name of base part
        C1: Id of base connection
        P2: Name of new part to be aggregated
        C2: Id of new connection
        TXT: Text representation of rule
"""

ghenv.Component.Name = "Wasp_Deconstruct Rule"
ghenv.Component.NickName = 'DeRule'
ghenv.Component.Message = 'VER 0.1.0\nDEC_22_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "3 | Rules"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh

def main(rule):
    
    ## check if Wasp is setup
    if sc.sticky.has_key('WaspSetup'):
        
        check_data = True
        
        ##check inputs
        if rule is None:
            check_data = False
            msg = "No rule provided"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
        if check_data:
            p1 = rule.part1
            c1 = rule.conn1
            p2 = rule.part2
            c2 = rule.conn2
            rule_txt = "%s|%s_%s|%s"%(p1,c1,p2,c2)
            
            return p1, c1, p2, c2, rule_txt
        else:
            return -1
    
    else:
        ## throw warining
        msg = "You must run the SetupWasp component before starting to build!"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1


result = main(R)

if result != -1:
    P1 = result[0]
    C1 = result[1]
    P2 = result[2]
    C2 = result[3]
    TXT = result[4]


R = sc.sticky['Rule'](P1, C1, P2, C2)