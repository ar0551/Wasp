"""
(C) 2017-2021 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.6.001

DisCo player settings classes
"""

from wasp.disco.constraints import *


#################################################################### Player ####################################################################
class DisCoPlayer(object):

	## constructor
	def __init__(self, _name, _vr_fps, _scale, _tool, _place, _IO, _pt_const, _box_const, _crv_const):
		self.name = _name
		self.vr_fps = _vr_fps
		self.scale = _scale
		self.tool_settings = _tool
		self.placement_settings = _place
		self.IO_settings = _IO
		self.point_constraints = _pt_const
		self.box_constraints = _box_const
		self.curve_constraints = _crv_const

	
	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "DisCoPlayer [name: %s]" % (self.name)
	

	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		name = data['playerName']
		vr_fps = data['VrFps']
		scale = data['Scale']
		tool_settings = DisCoToolSettings.from_data(data['toolsetSettings'])
		placement_settings = DisCoPlacementSettings.from_data(data['placementSettings'])
		IO_settings = DisCoIOSettings.from_data(data['saveLoadSettings'])
		point_constraints = [DisCoPointConstraint.from_data(pt_data) for pt_data in data['constraintPoints']]
		box_constraints = [DisCoBoxConstraint.from_data(box_data) for box_data in data['constraintBoxes']]
		curve_constraints = [DisCoCurveConstraint.from_data(crv_data) for crv_data in data['constraintCurves']]
		return cls(name, vr_fps, scale, tool_settings, placement_settings, IO_settings, point_constraints, box_constraints, curve_constraints)
	

	## return the data dictionary representing the class
	def to_data(self):
		data = {}
		data['playerName'] = self.name
		data['VrFps'] = self.vr_fps
		data['Scale'] = self.scale
		data['toolsetSettings'] = self.tool_settings.to_data()
		data['placementSettings'] = self.placement_settings.to_data()
		data['saveLoadSettings'] = self.IO_settings.to_data()
		data['constraintPoints'] = [pc.to_data() for pc in self.point_constraints]
		data['constraintBoxes'] = [bc.to_data() for bc in self.box_constraints]
		data['constraintCurves'] = [cc.to_data() for cc in self.curve_constraints]
		return data


#################################################################### Tool Settings ####################################################################
class DisCoToolSettings(object):

	## constructor
	def __init__(self):
		self.num_parts = True
		self.part_filter = True
		self.rule_filter = True
		self.placement = True
		self.field = True
		self.save_load = True
		self.simulate = True
		self.character = True
		self.scale = True


	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "DisCoToolSettings"
	

	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		tool_settings = cls()
		tool_settings.num_parts = data['NumParts']
		tool_settings.part_filter = data['PartFilter']
		tool_settings.rule_filter = data['RuleFilter']
		tool_settings.placement = data['PlacementType']
		tool_settings.field = data['Field']
		tool_settings.save_load = data['SaveLoad']
		tool_settings.simulate = data['Simulation']
		tool_settings.character = data['CharacterSettings']
		tool_settings.scale = data['Scale']
		return tool_settings
	

	## return the data dictionary representing the class
	def to_data(self):
		data = {}
		data['NumParts'] = self.num_parts
		data['PartFilter'] = self.part_filter
		data['RuleFilter'] = self.rule_filter
		data['PlacementType'] = self.placement
		data['Field'] = self.field
		data['SaveLoad'] = self.save_load
		data['Simulation'] = self.simulate
		data['CharacterSettings'] = self.character
		data['Scale'] = self.scale
		return data


#################################################################### Tool Settings ####################################################################
class DisCoPlacementSettings(object):

	## constructor
	def __init__(self):
		self.place = True
		self.choreo = True
		self.shoot = True
		self.grow = True
		self.pick = True
		self.delete = True
		self.delete_recursive = True
		self.delete_sphere = True
		self.disable = True


	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "DisCoPlacementSettings"
	

	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		placement_settings = cls()
		placement_settings.place = data['Place']
		placement_settings.choreo = data['Choreograph']
		placement_settings.shoot = data['Shoot']
		placement_settings.grow = data['Grow']
		placement_settings.pick = data['PickNChose']
		placement_settings.delete = data['Delete']
		placement_settings.delete_recursive = data['DeleteRec']
		placement_settings.delete_sphere = data['DeleteSphere']
		placement_settings.disable = data['EnableDisable']
		return placement_settings
	

	## return the data dictionary representing the class
	def to_data(self):
		data = {}
		data['Place'] =	 self.place
		data['Choreograph'] = self.choreo
		data['Shoot'] = self.shoot
		data['Grow'] = self.grow
		data['PickNChose'] = self.pick
		data['Delete'] = self.delete
		data['DeleteRec'] = self.delete_recursive
		data['DeleteSphere'] = self.delete_sphere
		data['EnableDisable'] = self.disable
		return data


#################################################################### Tool Settings ####################################################################
class DisCoIOSettings(object):

	## constructor
	def __init__(self):
		self.save_game = True
		self.load_game = True
		self.new_game = True
		self.export_field = True


	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "DisCoIOSettings"
	

	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		IO_settings = cls()
		IO_settings.save_game = data['SaveGame']
		IO_settings.load_game = data['LoadGame']
		IO_settings.new_game = data['NewGame']
		IO_settings.export_field = data['ExportField']
		return IO_settings
	

	## return the data dictionary representing the class
	def to_data(self):
		data = {}
		data['SaveGame'] = self.save_game
		data['LoadGame'] = self.load_game
		data['NewGame'] = self.new_game
		data['ExportField'] = self.export_field
		return data