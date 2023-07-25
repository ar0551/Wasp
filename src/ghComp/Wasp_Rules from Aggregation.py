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
Extract aggregation rules from an aggregation. These can be used to recreate the aggregation using the Graph-Grammar Aggregation component, as well as to replace parts in an aggregation.
-
Provided by Wasp 0.5
    Args:
        AGGR: Aggregation from which to extract the rules
        ON: OPTIONAL // If replacing parts, old names of the existing parts in the aggregation
        NN: OPTIONAL // If replacing parts, new names of the parts to replace with. Order should match the order provided in ON
    Returns:
        GR: Graph rules to recreate the aggregation
        PREV: If the provided aggregation contained parts assigned before the aggregation algorithm (in the PREV input), those parts are returned here. WARNING: when using a Graph Grammar Aggregation to replace parts, these parts will not be replaced.
"""

ghenv.Component.Name = "Wasp_Rules from Aggregation"
ghenv.Component.NickName = 'GraphRules'
ghenv.Component.Message = 'v0.5.008'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "3 | Rules"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import sys
import Rhino.Geometry as rg
import Grasshopper as gh
import ghpythonlib.treehelpers as th


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
    from wasp.core import Aggregation, Graph


def main(aggregation, old_names, new_names):
    
    check_data = True
    
    ##check inputs
    if aggregation is None:
        check_data = False
        msg = "No aggregation provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if len(old_names) > 0:
        if len(old_names) != len(new_names):
            check_data = False
            msg = "Different number of old and new names provided"
            ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, msg)
    
    if check_data:
        graph_rules = []
        
        replace_names = False
        n_dict = {}
        if len(old_names) > 0 and len(old_names) == len(new_names):
            replace_names = True
            for i in range(len(old_names)):
                n_dict[old_names[i]] = new_names[i]
        
        ################################### if replacing parts, PREV input is currently not working
        prev_parts = []
        if aggregation.prev_num > 0:
            prev_parts = aggregation.aggregated_parts[:aggregation.prev_num]
        
        graph_edges = aggregation.graph.get_edges_attributes()
        
        for edge in graph_edges:
            start_p = aggregation.aggregated_parts[int(edge['start'])].name
            end_p = aggregation.aggregated_parts[int(edge['end'])].name
            start_conn = edge['conn_start']
            end_conn = edge['conn_end']
            
            if replace_names:
                start_p = n_dict[start_p]
                end_p = n_dict[end_p]
            
            if len(graph_rules) == 0 and aggregation.prev_num == 0:
                rule = "{}|{}_{}|{}>{}_{}".format(start_p, start_conn, end_p, end_conn, edge['start'], edge['end'])
            else:
                rule = "{}|{}_{}|{}>{}_{}".format(edge['start'], start_conn, end_p, end_conn, edge['start'], edge['end'])
            
            graph_rules.append(rule)
            
        return graph_rules, prev_parts
        
    else:
        return -1


result = main(AGGR, ON, NN)

if result != -1:
    GR = result[0]
    PREV = result[1]
