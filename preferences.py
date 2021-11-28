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

    # This feels dirty
    layout: bpy.types.UILayout

    report_items = [
        ('WARNING', "Warnings", "Show warnings", 'ERROR', 1),
        ('ERROR', "Errors", "Show error reports", 'CANCEL', 2),
        ('INFO', "Info", "Show general reports", 'INFO', 4),
        ('PROPERTY', "Sub-Steps", "Show step-by-step info (verbose)", 'TEXT', 8),
    ]

    if TYPE_CHECKING:
        reporting: bpy.types.EnumProperty
    else:
        reporting: bpy.props.EnumProperty(
            name="Report Level",
            description='',
            items=report_items,
            options={'ENUM_FLAG'},
            default={'WARNING', 'ERROR'},
        )

    def draw(self, context: bpy.types.Context):
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
        update_settings_ui(self, context)


    def get_base_shader(self, base: str) -> str:
        if base is None:
            # FIXME: why isn't enumproperty assignable to str in pylance? Have
            # to do the str() thing instead, which shouldn't be needed?
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


class WoWbject_SceneProperties(bpy.types.PropertyGroup):
    """
    Mostly WMO lighting info (possibly temporary here)
    """
    if TYPE_CHECKING:
        initialized: bpy.types.BoolProperty
    else:
        initialized: bpy.props.BoolProperty(
            default=False,
            options={'HIDDEN'}
        )

    if TYPE_CHECKING:
        wmo_exterior_ambient_color: bpy.types.FloatVectorAttribute
    else:
        wmo_exterior_ambient_color: bpy.props.FloatVectorProperty(
            name="WMO Exterior Ambient Color",
            description="External ambient lighting color used for WMO objects",
            default=(1.0, 0.1, 0.1),  # FIXME: figure out if this should have alpha
            soft_min=0.0, soft_max=1.0,
            subtype='COLOR',
            size=3,
        )

    if TYPE_CHECKING:
        wmo_exterior_horizon_ambient_color: bpy.types.FloatVectorAttribute
    else:
        wmo_exterior_horizon_ambient_color: bpy.props.FloatVectorProperty(
            name="WMO Exterior Horizon Ambient Color",
            description="External horizon ambient lighting color used for WMO objects",
            default=(1.0, 1.0, 1.0),  # FIXME: figure out if this should have alpha
            soft_min=0.0, soft_max=1.0,
            subtype='COLOR',
            size=3,
        )

    if TYPE_CHECKING:
        wmo_exterior_ground_ambient_color: bpy.types.FloatVectorAttribute
    else:
        wmo_exterior_ground_ambient_color: bpy.props.FloatVectorProperty(
            name="WMO Exterior Ground Ambient Color",
            description="External ground ambient lighting color used for WMO objects",
            default=(1.0, 1.0, 1.0),  # FIXME: figure out if this should have alpha
            soft_min=0.0, soft_max=1.0,
            subtype='COLOR',
            size=3,
        )

    if TYPE_CHECKING:
        wmo_exterior_direct_color: bpy.types.FloatVectorAttribute
    else:
        wmo_exterior_direct_color: bpy.props.FloatVectorProperty(
            name="WMO Exterior Direct Lighting Color",
            description="External direct lighting color used for WMO objects",
            # FIXME: my notes say the default for this should be something like
            # (0.3, 0.3, 0.3, 1.3), which implies an alpha channel that's used
            # for... intensity, maybe? Revisit this and find out for sure.
            default=(0.3, 0.3, 0.3),
            soft_min=0.0, soft_max=1.0,
            subtype='COLOR',
            size=3,
        )

    if TYPE_CHECKING:
        wmo_exterior_direct_color_direction: bpy.types.FloatVectorAttribute
    else:
        wmo_exterior_direct_color_direction: bpy.props.FloatVectorProperty(
            name="WMO Exterior Direct Lighting Direction",
            description="External direct lighting direction used for WMO objects",
            default=(0.0, 0.0, 0.0),
            soft_min=0.0, soft_max=1.0,
            subtype='DIRECTION',
            size=3,
        )


class WoWbject_texture(bpy.types.PropertyGroup):
    if TYPE_CHECKING:
        datablock: bpy.types.PointerProperty  # FIXME: is this the right type?
    else:
        datablock: bpy.props.PointerProperty(
            type=bpy.types.Image,
            name="Texture",
        )

    if TYPE_CHECKING:
        path: bpy.types.StringProperty
    else:
        path: bpy.props.StringProperty(
            name="Texture Path",
            default="",
        )


# FIXME: Consider generating these somehow? Or is there a way to have a
# single generic one that knows what field it's being called for?
def get_wmo_exterior_ambient(self: "WoWbject_ObjectProperties") -> bpy.types.FloatVectorAttribute:
    if self.use_scene_wmo_lighting or "wmo_exterior_ambient_color" not in self:
        return cast(WoWbject_SceneProperties, bpy.context.scene.WBJ).wmo_exterior_ambient_color
    else:
        return self["wmo_exterior_ambient_color"]

def get_wmo_exterior_horizon_ambient(self: "WoWbject_ObjectProperties") -> bpy.types.FloatVectorAttribute:
    if self.use_scene_wmo_lighting or "wmo_exterior_horizon_ambient_color" not in self:
        return cast(WoWbject_SceneProperties, bpy.context.scene.WBJ).wmo_exterior_horizon_ambient_color
    else:
        return self["wmo_exterior_horizon_ambient_color"]

def get_wmo_exterior_ground_ambient(self: "WoWbject_ObjectProperties") -> bpy.types.FloatVectorAttribute:
    if self.use_scene_wmo_lighting or "wmo_exterior_ground_ambient_color" not in self:
        return cast(WoWbject_SceneProperties, bpy.context.scene.WBJ).wmo_exterior_ground_ambient_color
    else:
        return self["wmo_exterior_ground_ambient_color"]

def get_wmo_exterior_direct(self: "WoWbject_ObjectProperties") -> bpy.types.FloatVectorAttribute:
    if self.use_scene_wmo_lighting or "wmo_exterior_direct_color" not in self:
        return cast(WoWbject_SceneProperties, bpy.context.scene.WBJ).wmo_exterior_direct_color
    else:
        return self["wmo_exterior_direct_color"]

def get_wmo_exterior_direct_direction(self: "WoWbject_ObjectProperties") -> bpy.types.FloatVectorAttribute:
    if self.use_scene_wmo_lighting or "wmo_exterior_direct_color_direction" not in self:
        return cast(WoWbject_SceneProperties, bpy.context.scene.WBJ).wmo_exterior_direct_color_direction
    else:
        return self["wmo_exterior_direct_color_direction"]

# and some setters
def set_wmo_exterior_ambient(self: 'WoWbject_ObjectProperties', val: bpy.types.FloatVectorAttribute) -> None:
    self["wmo_exterior_ambient_color"] = val

def set_wmo_exterior_horizon_ambient(self: 'WoWbject_ObjectProperties', val: bpy.types.FloatVectorAttribute) -> None:
    self["wmo_exterior_horizon_ambient_color"] = val

def set_wmo_exterior_ground_ambient(self: 'WoWbject_ObjectProperties', val: bpy.types.FloatVectorAttribute) -> None:
    self["wmo_exterior_ground_ambient_color"] = val

def set_wmo_exterior_direct(self: 'WoWbject_ObjectProperties', val: bpy.types.FloatVectorAttribute) -> None:
    self["wmo_exterior_direct_color"] = val

def set_wmo_exterior_direct_direction(self: 'WoWbject_ObjectProperties', val: bpy.types.FloatVectorAttribute) -> None:
    self["wmo_exterior_direct_color_direction"] = val


class WoWbject_ObjectProperties(bpy.types.PropertyGroup):
    """
    Mostly Summary Information
    """
    if TYPE_CHECKING:
        # initialized: bpy.types.BoolProperty
        initialized: bool
    else:
        initialized: bpy.props.BoolProperty(
            default=False,
            options={'HIDDEN'},
        )

    wow_model_types = [
        ('M2', "M2", "M2 Model (character/object/mob)"),
        ('WMO', "WMO", "WMO Model (buildings/caves)"),
        ('ADT', "ADT", "ADT 'model' (terrain)"),
    ]

    if TYPE_CHECKING:
        # wow_model_type: bpy.types.EnumProperty
        wow_model_type: str
    else:
        wow_model_type: bpy.props.EnumProperty(
            name="Model Type",
            items=wow_model_types,
            default='M2',
        )

    wmo_lighting_types = [
        ('UNLIT', "Unlit", "Model is Unlit", 0),
        ('EXTERIOR', "Exterior", "Model is Exterior Surfaces", 1),
        ('TRANSITION', "Transition", "Model is Transition Surfaces", 2),
        ('INTERIOR', "Interior", "Model is Interior Surfaces", 3),
    ]

    # FIXME: Is this better as an enum, or something broken down?
    if TYPE_CHECKING:
        # wmo_lighting_type: bpy.types.EnumProperty
        wmo_lighting_type: str
    else:
        wmo_lighting_type: bpy.props.EnumProperty(
            name="Lighting",
            description='Lighting calculation to be used for WMO object',
            items=wmo_lighting_types,
            default='UNLIT',
        )

    if TYPE_CHECKING:
        # use_scene_wmo_lighting: bpy.types.BoolProperty
        use_scene_wmo_lighting: bool
    else:
        use_scene_wmo_lighting: bpy.props.BoolProperty(
            name="Use Scene WMO Lighting",
            default=True,
        )

    if TYPE_CHECKING:
        # speed_factor: bpy.types.FloatProperty
        speed_factor: float
    else:
        speed_factor: bpy.props.FloatProperty(
            name="UV Animation Speed",
            default=1.0,
        )

    if TYPE_CHECKING:
        # source_asset: bpy.types.StringProperty
        source_file: str
    else:
        source_file: bpy.props.StringProperty(
            name="Source File",
            description="Where it come from",
            default="",
            subtype='FILE_NAME',
            # get=lambda self : self["source_asset"],
            # options={''},
        )

    if TYPE_CHECKING:
        source_fdid: int
    else:
        source_fdid: bpy.props.IntProperty(
            name="Source FDID",
            description="File Data ID of source asset",
            default=0,
            # get=lambda self : self["source_asset"],
            # options={''},
        )

    if TYPE_CHECKING:
        # source_directory: bpy.types.StringProperty
        source_directory: str
    else:
        source_directory: bpy.props.StringProperty(
            name="Source Directory",
            description="Where it come from",
            default="",
            subtype='DIR_PATH',
            # get=lambda self : self["source_directory"],
        )

    if TYPE_CHECKING:
        textures: bpy.types.CollectionProperty
    else:
        textures: bpy.props.CollectionProperty(
            type=WoWbject_texture,
            name="Textures",
        )

    # WMO bits, mostly an exact duplicate of what's in the scene
    # FIXME: Can we deduplicate anything at all?
    if TYPE_CHECKING:
        # wmo_exterior_ambient_color: bpy.types.FloatVectorAttribute
        wmo_exterior_ambient_color: Tuple[float, float, float]   # or just List?
    else:
        wmo_exterior_ambient_color: bpy.props.FloatVectorProperty(
            name="WMO Exterior Ambient Color",
            description="External ambient lighting color used for WMO objects",
            default=(0.8, 0.8, 0.8),  # FIXME: figure out if this should have alpha
            soft_min=0.0, soft_max=1.0,
            subtype='COLOR',
            size=3,
            get=get_wmo_exterior_ambient,
            set=set_wmo_exterior_ambient
        )
    if TYPE_CHECKING:
        # wmo_exterior_horizon_ambient_color: bpy.types.FloatVectorAttribute
        wmo_exterior_horizon_ambient_color: Tuple[float, float, float]
    else:
        wmo_exterior_horizon_ambient_color: bpy.props.FloatVectorProperty(
            name="WMO Exterior Horizon Ambient Color",
            description="External horizon ambient lighting color used for WMO objects",
            default=(1.0, 1.0, 1.0),  # FIXME: figure out if this should have alpha
            soft_min=0.0, soft_max=1.0,
            subtype='COLOR',
            size=3,
            get=get_wmo_exterior_horizon_ambient,
            set=set_wmo_exterior_horizon_ambient,
        )
    if TYPE_CHECKING:
        # wmo_exterior_ground_ambient_color: bpy.types.FloatVectorAttribute
        wmo_exterior_ground_ambient_color: Tuple[float, float, float]
    else:
        wmo_exterior_ground_ambient_color: bpy.props.FloatVectorProperty(
            name="WMO Exterior Ground Ambient Color",
            description="External ground ambient lighting color used for WMO objects",
            default=(1.0, 1.0, 1.0),  # FIXME: figure out if this should have alpha
            soft_min=0.0, soft_max=1.0,
            subtype='COLOR',
            size=3,
            get=get_wmo_exterior_ground_ambient,
            set=set_wmo_exterior_ground_ambient,
        )

    if TYPE_CHECKING:
        # wmo_exterior_direct_color: bpy.types.FloatVectorAttribute
        wmo_exterior_direct_color: Tuple[float, float, float]
    else:
        wmo_exterior_direct_color: bpy.props.FloatVectorProperty(
            name="WMO Exterior Direct Lighting Color",
            description="External direct lighting color used for WMO objects",
            # FIXME: my notes say the default for this should be something like
            # (0.3, 0.3, 0.3, 1.3), which implies an alpha channel that's used
            # for... intensity, maybe? Revisit this and find out for sure.
            default=(0.3, 0.3, 0.3),
            soft_min=0.0, soft_max=1.0,
            subtype='COLOR',
            size=3,
            get=get_wmo_exterior_direct,
            set=set_wmo_exterior_direct,
        )
    if TYPE_CHECKING:
        # wmo_exterior_direct_color_direction: bpy.types.FloatVectorAttribute
        wmo_exterior_direct_color_direction: Tuple[float, float, float]
    else:
        wmo_exterior_direct_color_direction: bpy.props.FloatVectorProperty(
            name="WMO Exterior Direct Lighting Direction",
            description="External direct lighting direction used for WMO objects",
            default=(0.0, 0.0, 0.0),
            soft_min=0.0, soft_max=1.0,
            subtype='DIRECTION',
            size=3,
            get=get_wmo_exterior_direct_direction,
            set=set_wmo_exterior_direct_direction,
        )


class WoWbject_MaterialProperties(bpy.types.PropertyGroup):
    """
    Mostly Summary Information
    """
    if TYPE_CHECKING:
        initialized: bpy.types.BoolProperty
    else:
        initialized: bpy.props.BoolProperty(
            default=False,
            options={'HIDDEN'},
        )

    if TYPE_CHECKING:
        linked_asset: bpy.types.StringProperty
    else:
        linked_asset: bpy.props.StringProperty(
            name="Source File",
            description="Where it come from",
            default="",
            # options={''},
        )

    if TYPE_CHECKING:
        textures: bpy.types.CollectionProperty
    else:
        textures: bpy.props.CollectionProperty(
            type=WoWbject_texture,
            name="Textures",
        )


def get_rate(self: 'WoWbject_NodeGroupProperties'):
    return bpy.context.scene.render.fps


class WoWbject_NodeGroupProperties(bpy.types.PropertyGroup):
    """
    Mostly Summary Information
    """
    if TYPE_CHECKING:
        rate: bpy.types.FloatProperty
    else:
        rate: bpy.props.FloatProperty(
            name="Rate",
            description="",
            default=24,
            get=get_rate,
        )


class WoWbject_BoneProperties(bpy.types.PropertyGroup):
    """
    Where billboard info goes
    """
    if TYPE_CHECKING:
        billboard_type: bpy.types.IntProperty
    else:
        billboard_type: bpy.props.IntProperty(
            name="Billboard Type",
            default=-1,
        )


def get_path() -> str:
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def get_name() -> str:
    return os.path.basename(get_path())


def get_prefs() -> wowbjectAddonPrefs:
    return cast(wowbjectAddonPrefs, bpy.context.preferences.addons[__package__].preferences)
