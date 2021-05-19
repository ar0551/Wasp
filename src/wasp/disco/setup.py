"""
(C) 2017-2021 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.5.004

DisCo aggregation setup classes
"""


#################################################################### Player ####################################################################
class DisCoSetup(object):

	## constructor
	def __init__(self, _parts, _rules, _rule_groups, _probabilities, _spawn_counts):
		self.parts = _parts
		self.rules = _rules
		self.rule_groups = _rule_groups

		probability_total = 0
		for prob in _probabilities:
			probability_total += prob
		
		self.probabilities = []
		if probability_total == 1:
			self.probabilities = _probabilities
		elif probability_total == 0:
			self.probabilities = [1.0/len(self.parts) for part in self.parts]
		else:
			self.probabilities = [p/probability_total for p in _probabilities]
		
		self.spawn_counts = _spawn_counts

	
	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "DisCoSetup"
	

	## create class from data dictionary
	## NOT IMPLEMENTED
	@classmethod
	def from_data(cls, data):
		return None
	

	## return the data dictionary representing the class
	def to_data(self):
		data = {}

		data['PartData'] = []
		for i in range(len(self.parts)):
			part_data = self.parts[i].to_data()
			part_data['Probability'] = self.probabilities[i]
			part_data['SpawnNumber'] = self.spawn_counts[i]
			data['PartData'].append(part_data)

		data['RuleData'] = [rule.to_data() for rule in self.rules]
		data['RuleGroupsData'] = [rg.to_data() for rg in self.rule_groups]

		return data


#################################################################### Rule Group ####################################################################
class DisCoRuleGroup(object):

	## constructor
	def __init__(self, _name, _grammar):
		self.name = _name
		self.grammar = _grammar


	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "DisCoRuleGroup [name: %s]" % (self.name)
	

	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		return cls(data['RuleGroupName'], data['RuleGrammar'])
	

	## return the data dictionary representing the class
	def to_data(self):
		data = {}
		data['RuleGroupName'] = self.name
		data['RuleGrammar'] = self.grammar
		return data
