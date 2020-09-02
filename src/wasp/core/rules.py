"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.4.001

Rule class and (WIP) rules generation utilities
"""

class Rule(object):
	
	def __init__(self, _part1, _conn1, _part2, _conn2, _active = True):
		self.part1 = _part1
		self.conn1 = _conn1
		self.part2 = _part2
		self.conn2 = _conn2
		self.active = _active
	
	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspRule [%s|%s_%s|%s]" % (self.part1, self.conn1, self.part2, self.conn2)