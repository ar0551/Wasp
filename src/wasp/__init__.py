"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.5.001

Wasp: Discrete Design with Grasshopper plug-in (GPL) initiated by Andrea Rossi
 
Copyright (c) 2017, Andrea Rossi <a.rossi.andrea@gmail.com>
Wasp is free software; you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published 
by the Free Software Foundation; either version 3 of the License, 
or (at your option) any later version. 

Wasp is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Wasp; If not, see <http://www.gnu.org/licenses/>.

Initial development of Wasp has been supported as part of research
on digital materials and discrete design at:
DDU Digital Design Unit - Prof. Oliver Tessmann
Technische Universitat Darmstadt.
"""

from __future__ import print_function
from __future__ import division

import os
import sys

from Rhino.RhinoDoc import ActiveDoc


global_tolerance = ActiveDoc.ModelAbsoluteTolerance*2


__author__ = ['ar0551 <a.rossi.andrea@gmail.com>']
__copyright__ = 'Copyright 2017-2021 - Andrea Rossi'
__license__ = 'GPLv3.0'
__email__ = 'ghwasp@gmail.com'
__version__ = '0.5.001'


