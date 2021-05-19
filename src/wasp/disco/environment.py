"""
(C) 2017-2021 Andrea Rossi <ghwasp@gmail.com>

This file is part of Wasp. https://github.com/ar0551/Wasp
@license GPL-3.0 <https://www.gnu.org/licenses/gpl.html>

@version 0.5.004

DisCo environment classes
"""

from wasp.utilities import mesh_to_data


#################################################################### Environment Geometry ####################################################################
class DisCoEnvironment(object):

	## constructor
	def __init__(self, _game_area, _environment_geo, _blueprint_geo, _ground_plane, _field_resolution):
		self.game_area = _game_area
		self.environment_geo = _environment_geo
		self.blueprint_geo = _blueprint_geo
		self.ground_plane = _ground_plane
		self.field_resolution = _field_resolution


	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "DisCoEnvironment"
	

	## create class from data dictionary
	## NOT IMPLEMENTED
	@classmethod
	def from_data(cls, data):
		return None
	

	## return the data dictionary representing the class
	def to_data(self):
		data = {}
		data["GameArea"] =self.game_area.to_data()

		env_geo_data = []
		count = 0
		for geo in self.environment_geo:
			geo_data = mesh_to_data(geo)
			geo_data['name'] = "Additional_" + str(count)
			env_geo_data.append(geo_data)
			count += 1
		data["AdditionalGeometry"] = env_geo_data

		bp_geo_data = []
		count = 0
		for geo in self.blueprint_geo:
			geo_data = mesh_to_data(geo)
			geo_data['name'] = "Blueprint_" + str(count)
			bp_geo_data.append(geo_data)
			count += 1
		data["BlueprintGeometry"] = bp_geo_data		

		data['GroundPlane'] = self.ground_plane

		data['FieldResolution'] = self.field_resolution
		
		return data


#################################################################### Game Area ####################################################################
class DisCoGameArea(object):

	## constructor
	def __init__(self, _min_x, _max_x, _min_y, _max_y, _min_z, _max_z):
		self.min_x = _min_x
		self.max_x = _max_x
		self.min_y = _min_y
		self.max_y = _max_y
		self.min_z = _min_z
		self.max_z = _max_z


	## override Rhino .ToString() method (display name of the class in Gh)
	def ToString(self):
		return "DisCoGameArea [min: %.2f, %.2f, %.2f, max: %.2f, %.2f, %.2f]" % (self.min_x, self.min_y, self.min_z, self.max_x, self.max_y, self.max_z)
	

	## create class from data dictionary
	@classmethod
	def from_data(cls, data):
		min_x = data['minX']
		max_x = data['maxX']
		min_y = data['minY']
		max_y = data['maxY']
		min_z = data['minZ']
		max_z = data['maxZ']
		return cls(min_x, max_x, min_y, max_y, min_z, max_z)
	

	## return the data dictionary representing the class
	def to_data(self):
		data = {}
		data['minX'] = self.min_x
		data['maxX'] = self.max_x
		data['minY'] = self.min_y
		data['maxY'] = self.max_y
		data['minZ'] = self.min_z
		data['maxZ'] = self.max_z
		return data
	

	## create class from Rhino box
	@classmethod
	def from_bbox(cls, box):
		return cls(box.Min.X, box.Max.X, box.Min.Y, box.Max.Y, box.Min.Z, box.Max.Z)