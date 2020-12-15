"""
(C) 2017-2020 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.4.011

Rule class and (WIP) rules generation utilities
"""

class Rule(object):
	
	## constructor
	def __init__(self, _part1, _conn1, _part2, _conn2, _active = True):
		self.part1 = _part1
		self.conn1 = _conn1
		self.part2 = _part2
		self.conn2 = _conn2
		self.active = _active
	

	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "WaspRule [%s|%s_%s|%s]" % (self.part1, self.conn1, self.part2, self.conn2)
	

	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		return cls(data['part1'], int(data['conn1']), data['part1'], int(data['conn1']), _active = data['active'])

		
	## return the data dictionary representing the rule
	def to_data(self):
		data = {}
		data['part1'] = self.part1
		data['conn1'] = self.conn1
		data['part2'] = self.part2
		data['conn2'] = self.conn2
		data['active'] = self.active
		return data	