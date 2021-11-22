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

import os

import bpy
import bpy.props
from bpy_extras.io_utils import ImportHelper

from typing import TYPE_CHECKING, Union, Set
from .node_groups import serialize_nodegroups
from .node_groups import generate_nodegroups
from .node_groups import get_utility_group
from .utilties import do_import
# from . import preferences
from .preferences import get_prefs

class WOWBJ_OT_ToolTip(bpy.types.Operator):
    """Use this operator to display inline tooltips."""
    bl_idname = "wowbj.tool_tip"
    bl_label = "WoWbject Tool Tip"
    bl_description = "If you can read this, something is broken."
    bl_options = {'INTERNAL'}

    if TYPE_CHECKING:
        tooltip: str
    else:
        tooltip: bpy.props.StringProperty(default="")

    @classmethod
    def description(cls, context: bpy.types.Context, properties: bpy.types.OperatorProperties) -> str:
        return properties.tooltip  # type: ignore

    def execute(self, context: bpy.types.Context) -> Union[Set[str], Set[int]]:
        return {'CANCELLED'}


class WOWBJ_OT_SetDefaultDir(bpy.types.Operator):
    """Use the current directory as the default directory for importing"""
    bl_idname = 'wowbj.set_default_dir'
    bl_label = 'WoWbject Set Default Directory'
    bl_options = {'INTERNAL', 'UNDO'}

    if TYPE_CHECKING:
        new_dir: str
    else:
        new_dir: bpy.props.StringProperty(
            default="",
            subtype='DIR_PATH'
        )

    def execute(self, context: bpy.types.Context) -> Union[Set[str], Set[int]]:
        prefs = get_prefs()
        prefs.default_dir = self.new_dir
        return {'FINISHED'}


class WOWBJ_OT_Import_Old(bpy.types.Operator, ImportHelper):
    """Load a WoW .OBJ, with associated JSON and .m2 data"""
    bl_idname = 'import_scene.wowbject_old'
    bl_label = 'WoWbject Import'
    bl_options = {'PRESET', 'UNDO'}

    if TYPE_CHECKING:
        directory: str
    else:
        directory: bpy.props.StringProperty(subtype='DIR_PATH')


    filename_ext = '.obj'
    if TYPE_CHECKING:
        filter_glob: bpy.types.StringProperty
    else:
        filter_glob: bpy.props.StringProperty(default='*.obj')


    if TYPE_CHECKING:
        files: bpy.types.Collection
    else:
        files: bpy.props.CollectionProperty(
            name='File Path',
            type=bpy.types.OperatorFileListElement,
        )


    # filepath: bpy.props.StringProperty(
    #     name="File Path",
    #     description="Filepath used for importing the file",
    #     maxlen=1024,
    #     subtype='FILE_PATH',
    # )
    if TYPE_CHECKING:
        name_override: str
    else:
        name_override: bpy.props.StringProperty(
            name="Name",
            description="Defaults to asset name when left blank",
            default=''
        )

    if TYPE_CHECKING:
        merge_verts: bool
    else:
        merge_verts: bpy.props.BoolProperty(
            name='Dedupe Vertices',
            description='Deduplicate and merge vertices',
            default=True
        )

    if TYPE_CHECKING:
        make_quads: bool
    else:
        make_quads: bpy.props.BoolProperty(
            name='Tris to Quads',
            description='Automatically convert to quad-based geometry where possible',
            default=False
        )

    if TYPE_CHECKING:
        use_collections: bool
    else:
        use_collections: bpy.props.BoolProperty(
            name='Use Collections',
            description='Create objects inside collections when possible (WMO only)',
            default=True
        )

    if TYPE_CHECKING:
        reuse_materials: bool
    else:
        reuse_materials: bpy.props.BoolProperty(
            name='Reuse Materials',
            description='Re-use the existing materials in the scene if they match',
            default=False
        )

    if TYPE_CHECKING:
        create_aovs: bool
    else:
        create_aovs: bpy.props.BoolProperty(
            name='Create AOVs',
            description='[NOT IMPLEMENTED] Create AOVs for materials that use special blending modes',
            default=False
        )

    if TYPE_CHECKING:
        use_vertex_lighting: bool
    else:
        use_vertex_lighting: bpy.props.BoolProperty(
            name="Experimental Vertex Lighting",
            description="Use the experimental vertex lighting node in WMO shaders",
            default=False
        )

    base_shader_items = [
        ("EMIT", "Emission Shader", "Standard unlit look"),
        ("DIFF", "Diffuse Shader", "Lit look without additional specularity"),
        ("SPEC", "Specular Shader", "Lit look with extra downmixing for spec maps"),
        ("PRIN", "Principled Shader", "All the sliders"),
        ("EXPE", "Experimental", "You probably won't want to use this one"),
    ]

    if TYPE_CHECKING:
        base_shader: bool
    else:
        base_shader: bpy.props.EnumProperty(
            name="Shader Base",
            items=base_shader_items,
            default='EMIT',
        )


    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> Union[Set[str], Set[int]]:
        prefs = get_prefs()
        default_dir = prefs.default_dir
        if not default_dir == "":
            self.directory = default_dir
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


    def execute(self, context: bpy.types.Context) -> Union[Set[str], Set[int]]:
        prefs = get_prefs()
        verbosity = prefs.reporting
        default_dir = prefs.default_dir

        # FIXME: not sure how to type this
        args = self.as_keywords(ignore=("filter_glob", "directory", "filepath", "files"))

        # FIXME: Fix up our calls so this works right
        # if self.files:
        #     ret = {'CANCELLED'}
        #     dirname = os.path.dirname(self.filepath)
        #     for file in self.files:
        #         path = os.path.join(dirname, file.name)
        #         if do_import(self.files, self.directory, self.reuse_materials, self.base_shader, args) == {'FINISHED'}:
        #             ret = {'FINISHED'}
        #         return ret
        # else:

        # original:
        #   reports = do_import(self.files, self.directory, self.reuse_materials, self.base_shader, args)
        reports = do_import(self, context, self.filepath,
                            self.reuse_materials, self.base_shader, args)

        if (len(reports.warnings) > 0):
            if 'WARNING' in verbosity:
                self.report({'WARNING'}, "Warnings encountered. Check the console for details")

            for report in reports.warnings:
                print(report)

        if (len(reports.errors) > 0):
            if 'ERROR' in verbosity:
                self.report({'ERROR'}, "Errors ecountered. Check the console for details")

            for report in reports.errors:
                print(report)

        if (len(reports.info) > 0):
            if 'INFO' in verbosity:
                self.report({'INFO'}, "Info messages generated. Check the console for details")

            for report in reports.info:
                print(report)

        if (len(reports.sub_steps) > 0):
            if 'PROPERTY' in verbosity:
                self.report(
                    {'PROPERTY'}, "Sub-step report generated. Check the console for details")

            for report in reports.sub_steps:
                print(report)

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        root = layout.column(align=True)
        root.use_property_split = True

        root.label(text="Basic Settings:")
        root.prop(self, 'name_override', text="Rename to:")

        row = root.row(align=True)
        row.prop(self, 'reuse_materials')

        row = root.row(align=True)
        row.prop(self, 'merge_verts')

        row = root.row(align=True)
        row.prop(self, 'make_quads')

        row = root.row(align=True)
        row.prop(self, 'use_collections')

        col = root.column(align=True)
        col.use_property_split = True
        col.label(text="Shading:")
        col.prop(self, 'base_shader', expand=False)

        selector_params = context.space_data.params

        col = root.column(align=True)
        col.use_property_split = True
        col.label(text="WMO Settings:")
        col.prop(self, 'use_vertex_lighting', expand=False)

        col.label(text="Misc:")
        op = col.operator('wowbj.set_default_dir', text="Use as Default Directory")
        op.new_dir = selector_params.directory


# TODO: Add confirm button to preven data loss. Maybe an export browser?
class WOWBJ_OT_SerializeNodeGroups(bpy.types.Operator):
    """
    Serializes the node groups in the open file.
    Doesn't have any path-setting features, so be careful.
    """
    bl_idname = 'wowbj.serialize_nodegroups'
    bl_label = 'WoWbject Serialize Nodegroups'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        file_paths = os.path.join(os.path.dirname(__file__), "BlendFunctions.blend")
        serialize_nodegroups(os.path.join(os.path.dirname(__file__), "BlendFunctions.blend"))
        return {'FINISHED'}


# TODO: Add confirm buttons to prevent data loss
class WOWBJ_OT_GenerateNodeGroups(bpy.types.Operator):
    """
    Creates node groups based on the JSON schema.
    """
    bl_idname = 'wowbj.generate_nodegroups'
    bl_label = 'WoWbject Generate Nodegroups'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        generate_nodegroups(os.path.join(os.path.dirname(__file__), "BlendFunctions.blend"))
        return {'FINISHED'}


# Lazy way of respecting Blender's Enum capitalization requirement. Also allows substitutions
# TODO: Move to lookup_funcs.py
# autopep8: off
combiner_enum_map = {
    "COMBINERS_OPAQUE_MOD2XNA_ALPHA":           "Combiners_Opaque_Mod2xNA_Alpha",
    "COMBINERS_OPAQUE_ADDALPHA":                "Combiners_Opaque_AddAlpha",
    "COMBINERS_OPAQUE_ADDALPHA_ALPHA":          "Combiners_Opaque_AddAlpha_Alpha",
    "COMBINERS_OPAQUE_MOD2XNA_ALPHA_ADD":       "Combiners_Opaque_Mod2xNA_Alpha_Add",
    "COMBINERS_MOD_ADDALPHA":                   "Combiners_Mod_AddAlpha",
    "COMBINERS_OPAQUE_ADDALPHA":                "Combiners_Opaque_AddAlpha",
    "COMBINERS_MOD_ADDALPHA":                   "Combiners_Mod_AddAlpha",
    "COMBINERS_MOD_ADDALPHA_ALPHA":             "Combiners_Mod_AddAlpha_Alpha",
    "COMBINERS_OPAQUE_ALPHA_ALPHA":             "Combiners_Opaque_Alpha_Alpha",
    "COMBINERS_OPAQUE_MOD2XNA_ALPHA_3S":        "Combiners_Opaque_Mod2xNA_Alpha_3s",
    "COMBINERS_OPAQUE_ADDALPHA_WGT":            "Combiners_Opaque_AddAlpha_Wgt",
    "COMBINERS_MOD_ADD_ALPHA":                  "Combiners_Mod_Add_Alpha",
    "COMBINERS_OPAQUE_MODNA_ALPHA":             "Combiners_Opaque_ModNA_Alpha",
    "COMBINERS_MOD_ADDALPHA_WGT":               "Combiners_Mod_AddAlpha_Wgt",
    "COMBINERS_MOD_ADDALPHA_WGT":               "Combiners_Mod_AddAlpha_Wgt",
    "COMBINERS_OPAQUE_ADDALPHA_WGT":            "Combiners_Opaque_AddAlpha_Wgt",
    "COMBINERS_OPAQUE_MOD_ADD_WGT":             "Combiners_Opaque_Mod_Add_Wgt",
    "COMBINERS_OPAQUE_MOD2XNA_ALPHA_UNSHALPHA": "Combiners_Opaque_Mod2xNA_Alpha_UnshAlpha",
    "COMBINERS_MOD_DUAL_CROSSFADE":             "Combiners_Mod_Dual_Crossfade",
    "COMBINERS_MOD_DEPTH":                      "Combiners_Mod_Depth",
    "COMBINERS_OPAQUE_MOD2XNA_ALPHA_ALPHA":     "Combiners_Opaque_Mod2xNA_Alpha_Alpha",
    "COMBINERS_MOD_MOD":                        "Combiners_Mod_Mod",
    "COMBINERS_MOD_MASKED_DUAL_CROSSFADE":      "Combiners_Mod_Masked_Dual_Crossfade",
    "COMBINERS_OPAQUE_ALPHA":                   "Combiners_Opaque_Alpha",
    "COMBINERS_OPAQUE_MOD2XNA_ALPHA_UNSHALPHA": "Combiners_Opaque_Mod2xNA_Alpha_UnshAlpha",
    "COMBINERS_MOD_DEPTH":                      "Combiners_Mod_Depth",
    "GUILD":                                    "Guild",
    "GUILD_NOBORDER":                           "Guild_NoBorder",
    "GUILD_OPAQUE":                             "Guild_Opaque",
    "ILLUM":                                    "Illum",
    "COMBINERS_MOD_MOD_MOD_CONST":              "Combiners_Mod_Mod_Mod_Const",
    "COMBINERS_MOD_MOD_MOD_CONST":              "Combiners_Mod_Mod_Mod_Const",
    "COMBINERS_OPAQUE":                         "Combiners_Opaque",
    "COMBINERS_MOD_MOD2X":                      "Combiners_Mod_Mod2x",
}

combiner_items = [
    ("COMBINERS_OPAQUE_MOD2XNA_ALPHA",           "Combiners_Opaque_Mod2xNA_Alpha",             ""),
    ("COMBINERS_OPAQUE_ADDALPHA",                "Combiners_Opaque_AddAlpha",                  ""),
    ("COMBINERS_OPAQUE_ADDALPHA_ALPHA",          "Combiners_Opaque_AddAlpha_Alpha",            ""),
    ("COMBINERS_OPAQUE_MOD2XNA_ALPHA_ADD",       "Combiners_Opaque_Mod2xNA_Alpha_Add",         ""),
    ("COMBINERS_MOD_ADDALPHA",                   "Combiners_Mod_AddAlpha",                     ""),
    ("COMBINERS_OPAQUE_ADDALPHA",                "Combiners_Opaque_AddAlpha",                  ""),
    ("COMBINERS_MOD_ADDALPHA",                   "Combiners_Mod_AddAlpha",                     ""),
    ("COMBINERS_MOD_ADDALPHA_ALPHA",             "Combiners_Mod_AddAlpha_Alpha",               ""),
    ("COMBINERS_OPAQUE_ALPHA_ALPHA",             "Combiners_Opaque_Alpha_Alpha",               ""),
    ("COMBINERS_OPAQUE_MOD2XNA_ALPHA_3S",        "Combiners_Opaque_Mod2xNA_Alpha_3s",          ""),
    ("COMBINERS_OPAQUE_ADDALPHA_WGT",            "Combiners_Opaque_AddAlpha_Wgt",              ""),
    ("COMBINERS_MOD_ADD_ALPHA",                  "Combiners_Mod_Add_Alpha",                    ""),
    ("COMBINERS_OPAQUE_MODNA_ALPHA",             "Combiners_Opaque_ModNA_Alpha",               ""),
    ("COMBINERS_MOD_ADDALPHA_WGT",               "Combiners_Mod_AddAlpha_Wgt",                 ""),
    ("COMBINERS_MOD_ADDALPHA_WGT",               "Combiners_Mod_AddAlpha_Wgt",                 ""),
    ("COMBINERS_OPAQUE_ADDALPHA_WGT",            "Combiners_Opaque_AddAlpha_Wgt",              ""),
    ("COMBINERS_OPAQUE_MOD_ADD_WGT",             "Combiners_Opaque_Mod_Add_Wgt",               ""),
    ("COMBINERS_OPAQUE_MOD2XNA_ALPHA_UNSHALPHA", "Combiners_Opaque_Mod2xNA_Alpha_UnshAlpha",   ""),
    ("COMBINERS_MOD_DUAL_CROSSFADE",             "Combiners_Mod_Dual_Crossfade",               ""),
    ("COMBINERS_MOD_DEPTH",                      "Combiners_Mod_Depth",                        ""),
    ("COMBINERS_OPAQUE_MOD2XNA_ALPHA_ALPHA",     "Combiners_Opaque_Mod2xNA_Alpha_Alpha",       ""),
    ("COMBINERS_MOD_MOD",                        "Combiners_Mod_Mod",                          ""),
    ("COMBINERS_MOD_MASKED_DUAL_CROSSFADE",      "Combiners_Mod_Masked_Dual_Crossfade",        ""),
    ("COMBINERS_OPAQUE_ALPHA",                   "Combiners_Opaque_Alpha",                     ""),
    ("COMBINERS_OPAQUE_MOD2XNA_ALPHA_UNSHALPHA", "Combiners_Opaque_Mod2xNA_Alpha_UnshAlpha",   ""),
    ("COMBINERS_MOD_DEPTH",                      "Combiners_Mod_Depth",                        ""),
    ("GUILD",                                    "Guild",                                      ""),
    ("GUILD_NOBORDER",                           "Guild_NoBorder",                             ""),
    ("GUILD_OPAQUE",                             "Guild_Opaque",                               ""),
    ("ILLUM",                                    "Illum",                                      ""),
    ("COMBINERS_MOD_MOD_MOD_CONST",              "Combiners_Mod_Mod_Mod_Const",                ""),
    ("COMBINERS_MOD_MOD_MOD_CONST",              "Combiners_Mod_Mod_Mod_Const",                ""),
    ("COMBINERS_OPAQUE",                         "Combiners_Opaque",                           ""),
    ("COMBINERS_MOD_MOD2X",                      "Combiners_Mod_Mod2x",                        ""),
]
# autopep8: on


class WOWBJ_OT_LoadCombiner(bpy.types.Operator):
    """
    Creates node groups based on the JSON schema.
    """
    bl_idname = 'wowbj.get_combiner'
    bl_label = 'WoWbject Get Combiner'
    bl_options = {'REGISTER', 'UNDO'}

    if TYPE_CHECKING:
        combiner: str
    else:
        combiner: bpy.props.EnumProperty(
            name="Shader Base",
            items=combiner_items,
            default="COMBINERS_OPAQUE_MOD2XNA_ALPHA",
        )

    def execute(self, context):
        obj = context.active_object
        material = obj.active_material
        nodes = material.node_tree.nodes

        group_node = nodes.new('ShaderNodeGroup')
        group_node.node_tree = get_utility_group(combiner_enum_map.get(self.combiner))

        return {'FINISHED'}
