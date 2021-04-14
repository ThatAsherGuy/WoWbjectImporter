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
from .utilties import do_import


class WOWBJ_OT_Import(bpy.types.Operator):
    """
    So the intent here is that, on import, you select:

    1: An OBJ File
    2: A JSON config file
    3: Whatever textures you need

    It doesn't search sub-directories. Yet.
    """
    bl_idname = 'wowbj.import'
    bl_label = 'WoWbject Import'
    bl_options = {'PRESET', 'UNDO'}

    files: bpy.props.CollectionProperty(name = 'Files', type= bpy.types.OperatorFileListElement)
    directory: bpy.props.StringProperty(subtype = 'DIR_PATH')
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for importing the file",
        maxlen=1024,
        subtype='FILE_PATH',
    )

    reuse_materials: bpy.props.BoolProperty(
        name='Reuse Materials',
        description='Re-use the existing materials in the scene if they match',
        default=True)

    create_aovs: bpy.props.BoolProperty(
        name='Create AOVs',
        description='[NOT IMPLEMENTED] Create AOVs for materials that use special blending modes',
        default=False)

    base_shader_items = [
                        ("EMIT", "Emission Shader", ""),
                        ("DIFF", "Diffuse Shader", ""),
                        ("SPEC", "Specular Shader", ""),
                        ("PRIN", "Principled Shader", ""),
                        ("EXPE", "Experimental", ""),
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
        do_import(self.files, self.directory, self.reuse_materials, self.base_shader)
        return {'FINISHED'}


    def draw(self, context):
        layout = self.layout
        root = layout.column(align=True)
        root.use_property_split = False

        root.prop(self, 'reuse_materials')
        root.label(text="Base Shader Type:")
        root.prop(self, 'base_shader', expand=True)


class WOWBJ_OT_SerializeNodeGroups(bpy.types.Operator):
    """
    Serializes the node groups in the open file.
    Doesn't have any path-setting features, so be careful.
    """
    bl_idname = 'wowbj.serialize_nodegroups'
    bl_label = 'WoWbject Serialize Nodegroups'
    bl_options = {'PRESET', 'UNDO'}

    def execute(self, context):
        file_paths = os.path.join(os.path.dirname(__file__), "BlendFunctions.blend")
        serialize_nodegroups(os.path.join(os.path.dirname(__file__), "BlendFunctions.blend"))
        return {'FINISHED'}

class WOWBJ_OT_GenerateNodeGroups(bpy.types.Operator):
    """
    Creates node groups based on the JSON schema.
    """
    bl_idname = 'wowbj.generate_nodegroups'
    bl_label = 'WoWbject Generate Nodegroups'
    bl_options = {'PRESET', 'UNDO'}

    def execute(self, context):
        generate_nodegroups(os.path.join(os.path.dirname(__file__), "BlendFunctions.blend"))
        return {'FINISHED'}