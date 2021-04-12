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

def get_path():
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def get_name():
    return os.path.basename(get_path())

def get_prefs():
    # return bpy.context.preferences.addons[get_name()].preferences
    return bpy.context.preferences.addons[__package__].preferences

class wowbjectAddonPrefs(bpy.types.AddonPreferences):
    bl_idname = __package__

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


