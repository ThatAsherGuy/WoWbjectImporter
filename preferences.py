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
    auto_check_update: bpy.props.BoolProperty(  # type: ignore
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=False,
    )

    updater_intrval_months: bpy.props.IntProperty(  # type: ignore
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0,
    )

    updater_intrval_days: bpy.props.IntProperty(  # type: ignore
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0,
        max=31,
    )

    updater_intrval_hours: bpy.props.IntProperty(  # type: ignore
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23,
    )

    updater_intrval_minutes: bpy.props.IntProperty(  # type: ignore
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59,
    )

    # TODO: Create some sort of per-project system for this.
    default_dir: bpy.props.StringProperty(  # type: ignore
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

    base_shader: bpy.props.EnumProperty(  # type: ignore
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

    reporting: bpy.props.EnumProperty(  # type: ignore
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


class WoWbject_SceneProperties(bpy.types.PropertyGroup):
    """
    Mostly WMO lighting info (possibly temporary here)
    """
    initialized: bpy.props.BoolProperty(  # type: ignore
        default=False,
        options={'HIDDEN'}
    )

    wmo_exterior_ambient_color: bpy.props.FloatVectorProperty(  # type: ignore
        name="WMO Exterior Ambient Color",
        description="External ambient lighting color used for WMO objects",
        default=(1.0, 0.1, 0.1),  # FIXME: figure out if this should have alpha
        soft_min=0.0, soft_max=1.0,
        subtype='COLOR',
        size=3,
    )

    wmo_exterior_horizon_ambient_color: bpy.props.FloatVectorProperty(  # type: ignore
        name="WMO Exterior Horizon Ambient Color",
        description="External horizon ambient lighting color used for WMO objects",
        default=(1.0, 1.0, 1.0),  # FIXME: figure out if this should have alpha
        soft_min=0.0, soft_max=1.0,
        subtype='COLOR',
        size=3,
    )

    wmo_exterior_ground_ambient_color: bpy.props.FloatVectorProperty(  # type: ignore
        name="WMO Exterior Ground Ambient Color",
        description="External ground ambient lighting color used for WMO objects",
        default=(1.0, 1.0, 1.0),  # FIXME: figure out if this should have alpha
        soft_min=0.0, soft_max=1.0,
        subtype='COLOR',
        size=3,
    )

    wmo_exterior_direct_color: bpy.props.FloatVectorProperty(  # type: ignore
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

    wmo_exterior_direct_color_direction: bpy.props.FloatVectorProperty(  # type: ignore
        name="WMO Exterior Direct Lighting Direction",
        description="External direct lighting direction used for WMO objects",
        default=(0.0, 0.0, 0.0),
        soft_min=0.0, soft_max=1.0,
        subtype='DIRECTION',
        size=3,
    )


class WoWbject_texture(bpy.types.PropertyGroup):
    datablock: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Image,
        name="Texture",
    )

    path: bpy.props.StringProperty(  # type: ignore
        name="Texture Path",
        default="",
    )


# FIXME: Consider generating these somehow? Or is there a way to have a
# single generic one that knows what field it's being called for?
def get_wmo_exterior_ambient(self):
    if self.use_scene_wmo_lighting or "wmo_exterior_ambient_color" not in self:
        return bpy.context.scene.WBJ.wmo_exterior_ambient_color
    else:
        return self["wmo_exterior_ambient_color"]

def get_wmo_exterior_horizon_ambient(self):
    if self.use_scene_wmo_lighting or "wmo_exterior_horizon_ambient_color" not in self:
        return bpy.context.scene.WBJ.wmo_exterior_horizon_ambient_color
    else:
        return self["wmo_exterior_horizon_ambient_color"]

def get_wmo_exterior_ground_ambient(self):
    if self.use_scene_wmo_lighting or "wmo_exterior_ground_ambient_color" not in self:
        return bpy.context.scene.WBJ.wmo_exterior_ground_ambient_color
    else:
        return self["wmo_exterior_ground_ambient_color"]

def get_wmo_exterior_direct(self):
    if self.use_scene_wmo_lighting or "wmo_exterior_direct_color" not in self:
        return bpy.context.scene.WBJ.wmo_exterior_direct_color
    else:
        return self["wmo_exterior_direct_color"]

def get_wmo_exterior_direct_direction(self):
    if self.use_scene_wmo_lighting or "wmo_exterior_direct_color_direction" not in self:
        return bpy.context.scene.WBJ.wmo_exterior_direct_color_direction
    else:
        return self["wmo_exterior_direct_color_direction"]

# and some setters
def set_wmo_exterior_ambient(self, val):
    self["wmo_exterior_ambient_color"] = val

def set_wmo_exterior_horizon_ambient(self, val):
    self["wmo_exterior_horizon_ambient_color"] = val

def set_wmo_exterior_ground_ambient(self, val):
    self["wmo_exterior_ground_ambient_color"] = val

def set_wmo_exterior_direct(self, val):
    self["wmo_exterior_direct_color"] = val

def set_wmo_exterior_direct_direction(self, val):
    self["wmo_exterior_direct_color_direction"] = val


class WoWbject_ObjectProperties(bpy.types.PropertyGroup):
    """
    Mostly Summary Information
    """
    initialized: bpy.props.BoolProperty(  # type: ignore
        default=False,
        options={'HIDDEN'},
    )

    wow_model_types = [
        ('M2', "M2", "M2 Model (character/object/mob)"),
        ('WMO', "WMO", "WMO Model (buildings/caves)"),
        ('ADT', "ADT", "ADT 'model' (terrain)"),
    ]

    wow_model_type: bpy.props.EnumProperty(  # type: ignore
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
    wmo_lighting_type: bpy.props.EnumProperty(  # type: ignore
        name="Lighting",
        description='Lighting calculation to be used for WMO object',
        items=wmo_lighting_types,
        default='UNLIT',
    )

    use_scene_wmo_lighting: bpy.props.BoolProperty(  # type: ignore
        name="Use Scene WMO Lighting",
        default=True,
    )

    speed_factor: bpy.props.FloatProperty(  # type: ignore
        name="UV Animation Speed",
        default=1.0,
    )

    source_asset: bpy.props.StringProperty(  # type: ignore
        name="Source File",
        description="Where it come from",
        default="",
        subtype='FILE_NAME',
        # get=lambda self : self["source_asset"],
        # options={''},
    )

    source_directory: bpy.props.StringProperty(  # type: ignore
        name="Source Directory",
        description="Where it come from",
        default="",
        subtype='DIR_PATH',
        # get=lambda self : self["source_directory"],
    )

    textures: bpy.props.CollectionProperty(  # type: ignore
        type=WoWbject_texture,
        name="Textures",
    )

    # WMO bits, mostly an exact duplicate of what's in the scene
    # FIXME: Can we deduplicate anything at all?
    wmo_exterior_ambient_color: bpy.props.FloatVectorProperty(  # type: ignore
        name="WMO Exterior Ambient Color",
        description="External ambient lighting color used for WMO objects",
        default=(0.8, 0.8, 0.8),  # FIXME: figure out if this should have alpha
        soft_min=0.0, soft_max=1.0,
        subtype='COLOR',
        size=3,
        get=get_wmo_exterior_ambient,
        set=set_wmo_exterior_ambient
    )

    wmo_exterior_horizon_ambient_color: bpy.props.FloatVectorProperty(  # type: ignore
        name="WMO Exterior Horizon Ambient Color",
        description="External horizon ambient lighting color used for WMO objects",
        default=(1.0, 1.0, 1.0),  # FIXME: figure out if this should have alpha
        soft_min=0.0, soft_max=1.0,
        subtype='COLOR',
        size=3,
        get=get_wmo_exterior_horizon_ambient,
        set=set_wmo_exterior_horizon_ambient,
    )

    wmo_exterior_ground_ambient_color: bpy.props.FloatVectorProperty(  # type: ignore
        name="WMO Exterior Ground Ambient Color",
        description="External ground ambient lighting color used for WMO objects",
        default=(1.0, 1.0, 1.0),  # FIXME: figure out if this should have alpha
        soft_min=0.0, soft_max=1.0,
        subtype='COLOR',
        size=3,
        get=get_wmo_exterior_ground_ambient,
        set=set_wmo_exterior_ground_ambient,
    )

    wmo_exterior_direct_color: bpy.props.FloatVectorProperty(  # type: ignore
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

    wmo_exterior_direct_color_direction: bpy.props.FloatVectorProperty(  # type: ignore
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

    initialized: bpy.props.BoolProperty(  # type: ignore
        default=False,
        options={'HIDDEN'},
    )

    linked_asset: bpy.props.StringProperty(  # type: ignore
        name="Source File",
        description="Where it come from",
        default="",
        # options={''},
    )

    textures: bpy.props.CollectionProperty(  # type: ignore
        type=WoWbject_texture,
        name="Textures",
    )


def get_rate(self):
    return bpy.context.scene.render.fps


class WoWbject_NodeGroupProperties(bpy.types.PropertyGroup):
    """
    Mostly Summary Information
    """
    rate: bpy.props.FloatProperty(  # type: ignore
        name="Rate",
        description="",
        default=24,
        get=get_rate,
    )


class WoWbject_BoneProperties(bpy.types.PropertyGroup):
    """
    Where billboard info goes
    """
    billboard_type: bpy.props.IntProperty(  # type: ignore
        name="Billboard Type",
        default=-1,
    )
