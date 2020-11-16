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
Extract the aggregation graph.
-
Provided by Wasp 0.4
    Args:
        AGGR: Aggregation from which to extract the graph
        FG: [NOT WORKING] OPTIONAL // True to compute the full graph (including edges on overlapping connections), False to create only the aggregation sequence graph (True by default)
        HE: [NOT WORKING] OPTIONAL // True to calculate an half-edge graph (each connection represented twice), False to create only edges from earlier parts to further ones (True by default)
        F: OPTIONAL // True to flatten the edges list, False to maintain edges grouped by node (True by default).
    Returns:
        G: Aggregation graph
        N: Graph nodes (each placed at a part's center)
        E: Graph edges as lines
        ES_ID: part ID at edge start
        EE_ID: part ID at edge end
        CS_ID: connection ID at edge start
        CE_ID: connection ID at edge end
"""

ghenv.Component.Name = "Wasp_Aggregation Graph"
ghenv.Component.NickName = 'AggregationGraph'
ghenv.Component.Message = 'VER 0.4.008'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "X | Experimental"
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass

import sys
import Rhino.Geometry as rg
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
    from wasp.core import Aggregation, Graph

## from http://www.chenjingcheng.com/grasshopper-python-datatree-list-conversion/
def listToDataTree(list):
    rl = list
    result = gh.DataTree[object]()
    for i in range(len(rl)):
        temp = []
        for j in range(len(rl[i])):
            temp.append(rl[i][j])
        path = gh.Kernel.Data.GH_Path(i)
        result.AddRange(temp, path)
    return result


def main(aggregation, full_graph, half_edge, flatten_edges):
    
    check_data = True
    
    ##check inputs
    if aggregation is None:
        check_data = False
        msg = "No aggregation provided"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, msg)
    
    if full_graph is None:
        full_graph = True
    
    if half_edge is None:
        half_edge = True
    
    if flatten_edges is None:
        flatten_edges = True
    
    if check_data:
        
        ## compute aggregation graph
        g = Graph.from_aggregation(aggregation)
        
        ## extract graph data
        nodes = [int(n) for n in g.get_nodes()]
        edges = g.get_edges(flatten = flatten_edges)
        edges_attributes = g.get_edges_attributes(flatten = flatten_edges)
        
        ## generate geometric representation
        nodes_pts = [aggregation.aggregated_parts[int(i)].center for i in sorted(nodes)]
        
        edges_lines = []
        if flatten_edges:
            for edge in edges:
                start = aggregation.aggregated_parts[int(edge[0])].center
                end = aggregation.aggregated_parts[int(edge[1])].center
                edges_lines.append(rg.Line(start, end))
        else:
            for i in range(len(edges)):
                edges_lines.append([])
                for edge in edges[i]:
                    start = aggregation.aggregated_parts[int(edge[0])].center
                    end = aggregation.aggregated_parts[int(edge[1])].center
                    edges_lines[i].append(rg.Line(start, end))
                
        
        ## format data for GH outputs
        edge_start_ids = []
        edge_end_ids =[]
        conn_start_ids =[]
        conn_end_ids =[]
        
        if flatten_edges:
            for edge_attr in edges_attributes:
                edge_start_ids.append(edge_attr['start'])
                edge_end_ids.append(edge_attr['end'])
                conn_start_ids.append(edge_attr['conn_start'])
                conn_end_ids.append(edge_attr['conn_end'])
        else:
            for i in range(len(edges_attributes)):
                edge_start_ids.append([])
                edge_end_ids.append([])
                conn_start_ids.append([])
                conn_end_ids.append([])
                for edge_attr in edges_attributes[i]:
                    edge_start_ids[i].append(edge_attr['start'])
                    edge_end_ids[i].append(edge_attr['end'])
                    conn_start_ids[i].append(edge_attr['conn_start'])
                    conn_end_ids[i].append(edge_attr['conn_end'])
        
        
        """
        for i in range(len(aggregation.aggregated_parts)):
            p = aggregation.aggregated_parts[i]
            
            nodes.append(aggregation.aggregated_parts[i].center)
            edges.append([])
            
            edge_start_ids.append([])
            edge_end_ids.append([])
            
            conn_start_ids.append([])
            conn_end_ids.append([])
            
            neighbours = []
            for i2 in range(len(aggregation.aggregated_parts)):
                if aggregation.aggregated_parts[i].id != aggregation.aggregated_parts[i2].id:
                    p_dist = aggregation.aggregated_parts[i].center.DistanceTo(aggregation.aggregated_parts[i2].center)
                    if p_dist < (aggregation.aggregated_parts[i].dim + aggregation.aggregated_parts[i2].dim)*1.5:
                        neighbours.append(i2)
            for i2 in range(len(p.connections)):
                for i3 in neighbours:
                    other_p = aggregation.aggregated_parts[i3]
                    if aggregation.aggregated_parts[i3].id != p.id:
                        for i4 in range(len(aggregation.aggregated_parts[i3].connections)):
                            c_dist = p.connections[i2].pln.Origin.DistanceTo(aggregation.aggregated_parts[i3].connections[i4].pln.Origin)
                            if c_dist < 0.01:
                                
                                edge = rg.Line(p.center, aggregation.aggregated_parts[i3].center)
                                edges[i].append(edge)
                                
                                edge_start_ids[i].append(i)
                                edge_end_ids[i].append(i3)
                                
                                conn_start_ids[i].append(i2)
                                conn_end_ids[i].append(i4)
        """
        
        if flatten_edges:
            return g, nodes_pts, edges_lines, edge_start_ids, edge_end_ids, conn_start_ids, conn_end_ids
        else:
            
            edges_lines_dt = listToDataTree(edges_lines)
            
            edge_start_ids_dt = listToDataTree(edge_start_ids)
            edge_end_ids_dt = listToDataTree(edge_end_ids)
            conn_start_ids_dt = listToDataTree(conn_start_ids)
            conn_end_ids_dt = listToDataTree(conn_end_ids)
            
            return g, nodes_pts, edges_lines_dt, edge_start_ids_dt, edge_end_ids_dt, conn_start_ids_dt, conn_end_ids_dt
        
    else:
        return -1


result = main(AGGR, FG, HE, F)

if result != -1:
    G = result[0]
    N = result[1]
    E = result[2]
    
    ES_ID = result[3]
    EE_ID = result[4]
    CS_ID = result[5]
    CE_ID = result[6]

