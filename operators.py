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
from .node_groups import serialize_nodegroups
from .node_groups import generate_nodegroups
from .node_groups import get_utility_group
from .utilties import do_import
from . import preferences


class WOWBJ_OT_ToolTip(bpy.types.Operator):
    """Use this operator to display inline tooltips."""
    bl_idname = "wowbj.tool_tip"
    bl_label = "WoWbject Tool Tip"
    bl_description = "If you can read this, something is broken."

    tooltip: bpy.props.StringProperty(default="")

    @classmethod
    def description(cls, context, properties):
        return properties.tooltip

    def execute(self, context):
        return {'CANCELLED'}


class WOWBJ_OT_Import(bpy.types.Operator):
    """Load a WoW .OBJ, with associated JSON and .m2 data"""
    bl_idname = 'wowbj.import'
    bl_label = 'WoWbject Import'
    bl_options = {'PRESET', 'UNDO'}

    # The importer can handle multi-file, multi-type selections
    # So these are technically optional
    filename_ext   = '.obj'
    filter_glob: bpy.props.StringProperty(default='*.obj')

    files: bpy.props.CollectionProperty(name = 'Files', type= bpy.types.OperatorFileListElement)
    directory: bpy.props.StringProperty(subtype = 'DIR_PATH')
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for importing the file",
        maxlen=1024,
        subtype='FILE_PATH',
    )

    name_override: bpy.props.StringProperty(
        name="Name",
        description="Defaults to asset name when left blank",
        default=''
    )

    reuse_materials: bpy.props.BoolProperty(
        name='Reuse Materials',
        description='Re-use the existing materials in the scene if they match',
        default=False)

    create_aovs: bpy.props.BoolProperty(
        name='Create AOVs',
        description='[NOT IMPLEMENTED] Create AOVs for materials that use special blending modes',
        default=False)

    base_shader_items = [
                        ("EMIT", "Emission Shader", "Standard unlit look"),
                        ("DIFF", "Diffuse Shader", "Lit look without additional specularity"),
                        ("SPEC", "Specular Shader", "Lit look with extra downmixing for spec maps"),
                        ("PRIN", "Principled Shader", "All the sliders"),
                        ("EXPE", "Experimental", "You probably won't want to use this one"),
                      ]

    base_shader: bpy.props.EnumProperty(
                                name="Shader Base",
                                items=base_shader_items,
                                default="EMIT",
                                )


    def invoke(self, context, _event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


    def execute(self, context):
        prefs = preferences.get_prefs()
        verbosity = prefs.reporting
        args = self.as_keywords(ignore=("filter_glob",))
        reports = do_import(self.files, self.directory, self.reuse_materials, self.base_shader, args)

        if (len(reports.warnings) > 0) and 'WARNING' in verbosity:
            self.report({'WARNING'}, "Warnings encountered. Check the console for details")

            for report in reports.warnings:
                print(report)

        if (len(reports.errors) > 0) and 'ERROR' in verbosity:
            self.report({'ERROR'}, "Errors ecountered. Check the console for details")

            for report in reports.errors:
                print(report)

        if (len(reports.info) > 0) and 'INFO' in verbosity:
            self.report({'INFO'}, "Info messages generated. Check the console for details")

            for report in reports.info:
                print(report)

        if (len(reports.sub_steps) > 0) and 'PROPERTY' in verbosity:
            self.report({'PROPERTY'}, "Sub-step report generated. Check the console for details")

            for report in reports.sub_steps:
                print(report)

        return {'FINISHED'}


    def draw(self, context):
        layout = self.layout
        root = layout.column(align=True)
        root.use_property_split = True

        root.label(text="Basic Settings:")
        root.prop (self, 'name_override', text="Rename to:")

        row = root.row(align=True)
        row.prop(self, 'reuse_materials')
 
        col = root.column(align=True)
        col.use_property_split = True
        col.label(text="Shading:")
        col.prop(self, 'base_shader', expand=False)


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

class WOWBJ_OT_LoadCombiner(bpy.types.Operator):
    """
    Creates node groups based on the JSON schema.
    """
    bl_idname = 'wowbj.get_combiner'
    bl_label = 'WoWbject Get Combiner'
    bl_options = {'REGISTER', 'UNDO'}

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