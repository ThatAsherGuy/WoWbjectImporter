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
from .addon_updater_ops import update_settings_ui

from typing import TYPE_CHECKING, cast, Dict, Tuple

class wowbjectAddonPrefs(bpy.types.AddonPreferences):
    bl_idname = __package__

    # FIXME: This feels dirty
    layout: bpy.types.UILayout

    # Stuff from the CGCookie Add-on Updater.
    if TYPE_CHECKING:
        auto_check_update: bool
    else:
        auto_check_update: bpy.props.BoolProperty(
            name="Auto-check for Update",
            description="If enabled, auto-check for updates using an interval",
            default=False,
        )

    if TYPE_CHECKING:
        updater_intrval_months: int
    else:
        updater_intrval_months: bpy.props.IntProperty(
            name='Months',
            description="Number of months between checking for updates",
            default=0,
            min=0,
        )
    if TYPE_CHECKING:
        updater_intrval_days: int
    else:
        updater_intrval_days: bpy.props.IntProperty(
            name='Days',
            description="Number of days between checking for updates",
            default=7,
            min=0,
            max=31,
        )

    if TYPE_CHECKING:
        updater_intrval_hours: int
    else:
        updater_intrval_hours: bpy.props.IntProperty(
            name='Hours',
            description="Number of hours between checking for updates",
            default=0,
            min=0,
            max=23,
        )

    if TYPE_CHECKING:
        updater_intrval_minutes: int
    else:
        updater_intrval_minutes: bpy.props.IntProperty(
            name='Minutes',
            description="Number of minutes between checking for updates",
            default=0,
            min=0,
            max=59,
        )

    # TODO: Create some sort of per-project system for this.
    if TYPE_CHECKING:
        default_dir: str
    else:
        default_dir: bpy.props.StringProperty(
            name="Default Directory",
            description="",
            default="",
            subtype='DIR_PATH',
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

    if TYPE_CHECKING:
        base_shader: bpy.types.EnumProperty
    else:
        base_shader: bpy.props.EnumProperty(
            name="Base Shader",
            items=base_shader_items,
            default="EMIT",
        )

    report_items = [
        ('WARNING', "Warnings", "Show warnings", 'ERROR', 1),
        ('ERROR', "Errors", "Show error reports", 'CANCEL', 2),
        ('INFO', "Info", "Show general reports", 'INFO', 4),
        ('PROPERTY', "Sub-Steps", "Show step-by-step info (verbose)", 'TEXT', 8),
    ]

    if TYPE_CHECKING:
        reporting: str
    else:
        reporting: bpy.props.EnumProperty(
            name="Report Level",
            description='',
            items=report_items,
            options={'ENUM_FLAG'},
            default={'WARNING', 'ERROR'},
        )

    def draw(self, context: bpy.types.Context) -> None:
        # print(type(bpy.context.scene.WBJ))
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
        update_settings_ui(self, context)  # type: ignore


    # FIXME: This seems like entirely the wrong place for this
    def get_base_shader(self, base: str) -> str:
        if base is None:
            base = str(self.base_shader)

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


def get_path() -> str:
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def get_name() -> str:
    return os.path.basename(get_path())


def get_prefs() -> wowbjectAddonPrefs:
    return cast(wowbjectAddonPrefs, bpy.context.preferences.addons[__package__].preferences)
