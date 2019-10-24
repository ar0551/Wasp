#################################################################### Rule ####################################################################
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