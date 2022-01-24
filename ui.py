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
from .lookup_funcs import wmo_read_root_flags, wmo_read_group_flags, wmo_read_mat_flags
from typing import cast
from .properties import WoWbject_MaterialProperties, WoWbject_ObjectProperties


class VIEW3D_PT_wowbject_scene_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "WBJ"
    bl_label = "WMO Exterior Lighting"

    @classmethod
    def poll(cls, context):
        return True
        if context.scene.WBJ.initialized:
            return True

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        scene_props = scene.WBJ

        # row = layout.row()
        layout.label(text="WMO Exterior Lighting")

        row = layout.row()
        # row.enabled = False
        row.prop(scene_props, "wmo_exterior_ambient_color")

        row = layout.row()
        # row.label(text="meow")
        row.prop(scene_props, "wmo_exterior_horizon_ambient_color")

        row = layout.row()
        row.prop(scene_props, "wmo_exterior_ground_ambient_color")

        row = layout.row()
        row.prop(scene_props, "wmo_exterior_direct_color")


class VIEW3D_PT_wowbject_object_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "WBJ"
    bl_label = "WoWbject Source Info"

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if context.view_layer.objects.active:
            if context.view_layer.objects.active.WBJ.initialized:  # type: ignore
                return True

        return False

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout

        obj = context.view_layer.objects.active
        WBJ = cast('WoWbject_ObjectProperties', obj.WBJ)  # type: ignore

        # row = layout.row()
        # row.enabled = False
        # row.prop(WBJ, "wow_model_type")

        # row = layout.row()
        # row.prop(WBJ, "wmo_lighting_type")

        block = layout.column(align=True)
        block.label(text=f"Type: {WBJ.wow_model_type}")
        if WBJ.source_fdid > 0:
            block.label(text=f"FDID: {WBJ.source_fdid}")

        if WBJ.wow_model_type == 'WMO':
            if WBJ.wmo_root_fdid > 0:
                block.label(text=f"Root FDID: {WBJ.wmo_root_fdid}")
            # block.label(text=f"Lighting: {WBJ.wmo_lighting_type}")
            block.label(text=f"Flags: {WBJ.wmo_group_flags}")
            # block.label(text="")
            # block.label(text=f"Trans batches: {WBJ.wmo_group_batches_a}")
            # block.label(text=f"Int batches: {WBJ.wmo_group_batches_b}")
            # block.label(text=f"Ext batches: {WBJ.wmo_group_batches_c}")

            block = layout.column(align=True)

            if WBJ.wmo_group_flags > 0:
                block = layout.column(align=True)
                block.label(text="Group flags:")
                flag_list = wmo_read_group_flags(WBJ.wmo_group_flags)
                for flag in flag_list:
                    block.label(text=f"    {flag}")

            if WBJ.wmo_root_flags > 0:
                block = layout.column(align=True)
                block.label(text="Root flags:")
                flag_list = wmo_read_root_flags(WBJ.wmo_root_flags)
                for flag in flag_list:
                    block.label(text=f"    {flag}")

        # row = layout.row()
        # row.prop(WBJ, "use_scene_wmo_lighting")

        # if not WBJ.use_scene_wmo_lighting:
        #     row = layout.row()
        #     # row.enabled = False
        #     row.prop(WBJ, "wmo_exterior_ambient_color")

        #     row = layout.row()
        #     # row.label(text="meow")
        #     row.prop(WBJ, "wmo_exterior_horizon_ambient_color")

        #     row = layout.row()
        #     row.prop(WBJ, "wmo_exterior_ground_ambient_color")

        #     row = layout.row()
        #     row.prop(WBJ, "wmo_exterior_direct_color")

# class VIEW3D_PT_wowbject_combiner_panel(bpy.types.Panel):
#     bl_space_type = 'NODE_EDITOR'
#     bl_region_type = 'UI'
#     bl_category = "WoWbject"
#     bl_label = "WoWbject Combiners"

#     def draw(self, context):
#         layout = self.layout
#         root = layout.column(align=True)

#         op = root.operator_menu_enum(
#             "wowbj.get_combiner",
#             "combiner"
#         )

#         if context.active_node:
#             root.prop(context.active_node, "location")


class VIEW3D_PT_wowbject_material_panel(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "WBJ"
    bl_label = "WoWbject"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout

        if context.material:
            WBJ = cast('WoWbject_MaterialProperties', context.material.WBJ)  # type: ignore
            block = layout.column(align=True)
            block.label(text="Raw:")

            block = layout.column(align=True)
            # block.enabled = False
            # block.prop(context.material.WBJ, "wmo_shader_id")
            # block.prop(context.material.WBJ, "wmo_blend_mode")
            # block.prop(context.material.WBJ, "wmo_mat_flags")

            # FIXME: Is there a better way?
            block.label(text=f"    Shader ID: {WBJ.wmo_shader_id:-5d}")
            block.label(text=f"    Blend Mode: {WBJ.wmo_blend_mode:-5d}")
            block.label(text=f"    Flags: {WBJ.wmo_mat_flags:-5d}")

            if WBJ.wmo_mat_flags > 0:
                block = layout.column(align=True, heading="xxx")
                block.label(text="Flags:")
                flag_list = wmo_read_mat_flags(WBJ.wmo_mat_flags)
                for flag in flag_list:
                    block.label(text=f"    {flag}")


        # op = root.operator_menu_enum(
        #     "wowbj.get_combiner",
        #     "combiner"
        # )

        # if context.active_node:
        #     root.prop(context.active_node, "location")
