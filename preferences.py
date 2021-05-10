# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Hell is other people's code

import bpy
import os
from . import addon_updater_ops

def get_path():
	return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def get_name():
	return os.path.basename(get_path())

def get_prefs():
	# return bpy.context.preferences.addons[get_name()].preferences
	return bpy.context.preferences.addons[__package__].preferences


class wowbjectAddonPrefs(bpy.types.AddonPreferences):
	bl_idname = __package__

	# Stuff from the CGCookie Add-on Updater.
	auto_check_update: bpy.props.BoolProperty(
		name="Auto-check for Update",
		description="If enabled, auto-check for updates using an interval",
		default=False,
		)
	updater_intrval_months: bpy.props.IntProperty(
		name='Months',
		description="Number of months between checking for updates",
		default=0,
		min=0
		)
	updater_intrval_days: bpy.props.IntProperty(
		name='Days',
		description="Number of days between checking for updates",
		default=7,
		min=0,
		max=31
		)
	updater_intrval_hours: bpy.props.IntProperty(
		name='Hours',
		description="Number of hours between checking for updates",
		default=0,
		min=0,
		max=23
		)
	updater_intrval_minutes: bpy.props.IntProperty(
		name='Minutes',
		description="Number of minutes between checking for updates",
		default=0,
		min=0,
		max=59
		)

	# TODO: Create some sort of per-project system for this.
	default_dir: bpy.props.StringProperty(
		name="Default Directory",
		description="",
		default="",
		subtype='DIR_PATH'
	)

	# A fallback option for when the import operator
	# is called without a specified base shader type.
	base_shader_items = [
						("EMIT", "Emission Shader", ""),
						("DIFF", "Diffuse Shader", ""),
						("SPEC", "Specular Shader", ""),
						("PRIN", "Principled Shader", ""),
						("EXPE", "Experimental", ""),
					  ]

	base_shader: bpy.props.EnumProperty(
								name="Base Shader",
								items=base_shader_items,
								default="EMIT",
								)

	report_items = [
		('WARNING', "Warnings", "Show warnings", 'ERROR', 1),
		('ERROR', "Errors", "Show error reports", 'CANCEL', 2),
		('INFO', "Info", "Show general reports", 'INFO', 4),
		('PROPERTY', "Sub-Steps", "Show step-by-step info (annoyingly verbose)", 'TEXT', 8)
		]

	reporting: bpy.props.EnumProperty(
								name="Report Level",
								description='',
								items=report_items,
								options={'ENUM_FLAG'},
								default={'WARNING', 'ERROR'},
								)

	def draw(self, context):
		layout = self.layout

		# works best if a column, or even just self.layout
		mainrow = layout.row()
		col = mainrow.column()
		col.label(text="Importer Defaults:")
		col.prop(self, 'default_dir', text='Directory')
		col.label(text="Report Verbosity:")
		row = col.grid_flow(columns=2, align=True, even_rows=False)
		row.prop(self, 'reporting', expand=True)

		# updater draw function
		# could also pass in col as third arg
		addon_updater_ops.update_settings_ui(self, context)


	def get_base_shader(self, base):
		if base == None:
			base = self.base_shader

		if base == 'EMIT':
			return "ShaderNodeEmission"
		elif base == 'DIFF':
			return "ShaderNodeBsdfDiffuse"
		elif base == 'SPEC':
			return "ShaderNodeEeveeSpecular"
		elif base == 'PRIN':
			return "ShaderNodeBsdfPrincipled"
		elif base == 'EXPE':
			return "Experimental"
		else:
			return "ShaderNodeEmission"


class WoWbject_texture(bpy.types.PropertyGroup):
	datablock: bpy.props.PointerProperty(
		type=bpy.types.Image,
		name="Texture"
		)
	path: bpy.props.StringProperty(name="Texture Path", default="")


class WoWbject_ObjectProperties(bpy.types.PropertyGroup):
	"""
	Mostly Summary Information
	"""
	initialized: bpy.props.BoolProperty(
		default=False,
		options={'HIDDEN'}
	)

	speed_factor: bpy.props.FloatProperty(
		name="UV Animation Speed",
		default=1.0
	)

	source_asset: bpy.props.StringProperty(
		name="Source File",
		description="Where it come from",
		default="",
		subtype='FILE_NAME',
		# get=lambda self : self["source_asset"] 
		# options={''}
	)

	source_directory: bpy.props.StringProperty(
		name="Source Directory",
		description="Where it come from",
		default="",
		subtype='DIR_PATH',
		# get=lambda self : self["source_directory"] 
	)

	textures: bpy.props.CollectionProperty(
		type=WoWbject_texture,
		name="Textures"
	)


class WoWbject_MaterialProperties(bpy.types.PropertyGroup):
	"""
	Mostly Summary Information
	"""

	initialized: bpy.props.BoolProperty(
		default=False,
		options={'HIDDEN'}
	)

	linked_asset: bpy.props.StringProperty(
		name="Source File",
		description="Where it come from",
		default="",
		# options={''}
	)

	textures: bpy.props.CollectionProperty(
		type=WoWbject_texture,
		name="Textures"
	)


def get_rate(self):
	return bpy.context.scene.render.fps


class WoWbject_NodeGroupProperties(bpy.types.PropertyGroup):
	"""
	Mostly Summary Information
	"""
	rate: bpy.props.FloatProperty(
		name="Rate",
		description="",
		default=24,
		get=get_rate
	)