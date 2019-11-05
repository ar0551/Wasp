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
This component doesn't update the installation. It will only update the file
to your current installation. The components that can't be updated automatically
will be marked and should be replaced manually.
--> WIP Component: might be incomplete or contain bugs <--
-
Provided by Wasp 0.3
Code is adapted from Ladybug file updater (https://github.com/mostaphaRoudsari/ladybug)
    
    Args:
        UP: Set to "True" if you want this component to search through the current Grasshopper file and update Wasp components.
    Returns:
        LOG: List of updated files.
"""

ghenv.Component.Name = "Wasp_Update File"
ghenv.Component.NickName = 'UpdateFile'
ghenv.Component.Message = 'VER 0.3.001'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Wasp"
ghenv.Component.SubCategory = "X | Experimental"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import Grasshopper
import System
import os
from datetime import datetime
import time


def markComponent(doc, comp, note=None):
    """Add a Group to the component with a note."""
    note = note or "There is a change in input or output. Replace manually with the inserted component!"
    grp = Grasshopper.Kernel.Special.GH_Group()
    grp.CreateAttributes()
    grp.Border = Grasshopper.Kernel.Special.GH_GroupBorder.Blob
    grp.AddObject(comp.InstanceGuid)
    grp.Colour = System.Drawing.Color.IndianRed
    grp.NickName = note
    doc.AddObject(grp, False);    
    return True

def isWaspComponent(component):
    """Return True if a component is part of Wasp."""
    if component.Name.split('_')[0] == "Wasp":
        return True
    return False


def collectGHPythonComponents(document=None):
    """Collect all the GHPython components in file.""" 
    components = []
    document = document or ghenv.Component.OnPingDocument()
    for obj in document.Objects:
        if type(obj) == type(ghenv.Component)and isWaspComponent(obj):
            if obj.Locked:
                continue
            components.append(obj)
    # remove the component itself
    components = tuple(comp for comp in components if comp.InstanceGuid != ghenv.Component.InstanceGuid)
    return components


def parseVersion(version):
    version = sum(int(n) * 10 ** i for i, n in enumerate(reversed(version.split("VER ")[1].split("."))))
    return version


def isNewerVersion(uo, component):
    """Check if user object is newer version of the component."""
    # try to get date and time
    warnType = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
    try:
        version = parseVersion(component.Message)
    except Exception:
        warning = 'Failed to parse version from "%s" component.' % component.Name
        ghenv.Component.AddRuntimeMessage(warnType, warning)
        return False    
    
    # get the version from the userobject
    for c, line in enumerate(uo.Code.split('\n')):
        if c > 200:
            warning = 'Failed to parse version from "%s" userobject.' % component.Name
            ghenv.Component.AddRuntimeMessage(warnType, warning)
            return False
        if line.strip().startswith("ghenv.Component.Message"):
            uversion = line.split("=")[1].strip()[:-1]
            try:
                uversion = parseVersion(uversion)
            except Exception:
                warning = 'Failed to parse version from "%s" userobject.' % component.Name
                ghenv.Component.AddRuntimeMessage(warnType, warning)
                return False    
            
            if uversion >= version:
                return True
            else:
                return False


def comparePort(p1, p2):
    """compare two ports and return True if they are equal."""
    if hasattr(p1, 'TypeHint'):
        if p1.Name != p2.Name:
            return False
        elif p1.TypeHint.TypeName != p2.TypeHint.TypeName:
            return False
        elif str(p1.Access) != str(p2.Access):
            return False
        else:
            return True
    else:
        # output
        if p1.Name != p2.Name:
            return False
        else:
            return True        

def comparePorts(c1, c2):
    """Compare ports for two components."""
    for i in xrange(c1.Params.Input.Count):
        if not comparePort(c1.Params.Input[i], c2.Params.Input[i]):
            return True
    
    for i in xrange(c1.Params.Output.Count):
        if not comparePort(c1.Params.Output[i], c2.Params.Output[i]):
            return True
    
    return False

def inputOutputChanged(uo, component):
    """Check if inputs or outputs has changed."""
    if uo.Params.Input.Count != component.Params.Input.Count:
        return True
    elif uo.Params.Output.Count != component.Params.Output.Count:
        return True
    
    return comparePorts(uo, component)


def insertNewUO(uo, component, doc):
    # use component to find the location
    x = component.Attributes.Pivot.X + 30
    y = component.Attributes.Pivot.Y - 20
    
    # insert the new one
    uo.Attributes.Pivot = System.Drawing.PointF(x, y)
    doc.AddObject(uo , False, 0)


def updateComponent(component, uofolder):
    """update component from userobject."""
    fp = os.path.join(uofolder, '%s.ghuser' % component.Name)

    if not os.path.isfile(fp):
        warning = 'Failed to find the userobject for %s' % component.Name
        ghenv.Component.AddRuntimeMessage(Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning, warning)
        return False
    uo = Grasshopper.Kernel.GH_UserObject(fp).InstantiateObject()

    # check the version and the date between component and userobject
    if not isNewerVersion(uo, component):
        return False 

    # it is a newer version
    component.Code = uo.Code
    
    # Define the callback function
    def callBack(document):
        component.ExpireSolution(False)

    # Update the solution
    doc.ScheduleSolution(2,
        Grasshopper.Kernel.GH_Document.GH_ScheduleDelegate(callBack))

    # check if inputs or outputs has changed
    if inputOutputChanged(uo, component):
        insertNewUO(uo, component, doc)
        
        # add a group note to the component
        markComponent(doc, component)
        return 'Cannot update %s. Replace manually.' % component.Name

    return 'Updated %s' % component.Name


if UPDATE:
    # find the component
    uofolder = Grasshopper.Folders.UserObjectFolders[0]
    
    doc = ghenv.Component.OnPingDocument()
    
    # load the initial userobject
    components = collectGHPythonComponents(doc)
    
    report = (updateComponent(comp, uofolder) for comp in components)
    
    LOG = '\n'.join(r for r in report if r)