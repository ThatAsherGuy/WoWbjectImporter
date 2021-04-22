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

class VIEW3D_PT_wowbject_object_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"
    bl_label = "WoWbject Properties"

    @classmethod
    def poll(cls, context):
        if context.view_layer.objects.active:
            if context.view_layer.objects.active.WBJ.initialized:
                return True

    def draw(self, context):
        layout = self.layout
        root = layout.column(align=True)

        obj = context.view_layer.objects.active
        obj_props = obj.WBJ

        op = root.operator('wm.path_open', icon='IMAGE_BACKGROUND', text="Open Source Folder")
        op.filepath = obj_props.source_directory


class VIEW3D_PT_wowbject_combiner_panel(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "WoWbject"
    bl_label = "WoWbject Combiners"

    def draw(self, context):
        layout = self.layout
        root = layout.column(align=True)

        op = root.operator_menu_enum(
            "wowbj.get_combiner",
            "combiner"
        )