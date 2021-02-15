"""
(C) 2017-2021 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.4.015

DisCo player settings classes
"""


#################################################################### Player ####################################################################
class DisCoPlayer(object):

    ## constructor
    def __init__(self, _name, _vr_fps, _tool, _place, _IO, _pt_const, _crv_const, _box_const):
        self.name = _name
        self.vr_fps = _vr_fps
        self.tool_settings = _tool
        self.placement_settings = _place
        self.IO_settings = _IO
        self.point_constraints = _pt_const
        self.curve_constraints = _crv_const
        self.box_constraints = _box_const

    
    ## override Rhino .ToString() method (display name of the class in Gh)
    def ToString(self):
        return "DisCoPlayer [name; %s]"%(self.name)
    

    ## create class from data dictionary
    @classmethod
    def from_data(cls, data):
        return None
    

    ## return the data dictionary representing the class
	def to_data(self):
        data = {}

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
        self.place = data['Place']
        self.choreo = data['Choreograph']
        self.shoot = data['Shoot']
        self.pick = data['PickNChose']
        self.delete = data['Delete']
        self.delete_recursive = data['DeleteRec']
        self.delete_sphere = data['DeleteSphere']
        self.disable = data['EnableDisable']
        return placement_settings
    

    ## return the data dictionary representing the class
	def to_data(self):
        data = {}
        data['Place'] =  self.place
        data['Choreograph'] = self.choreo
        data['Shoot'] = self.shoot
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
        self.save_game = data['SaveGame']
        self.load_game = data['LoadGame']
        self.new_game = data['NewGame']
        self.export_field = data['ExportField']
        return IO_settings
    

    ## return the data dictionary representing the class
	def to_data(self):
        data = {}
        data['SaveGame'] = self.save_game
        data['LoadGame'] = self.load_game
        data['NewGame'] = self.new_game
        data['ExportField'] = self.export_field
        return data