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

# A bunch of this code is based on Krunthne's WoW Export add-on.

bl_info = {
    "name": "WoWbject Importer",
    "author": "Asher and Alinsa",
    "description": "Import World of Warcraft objects as correctly as possible",
    "blender": (2, 90, 0),
    "version": (0, 0, 0),   # autoreplace
    "location": "File > Import",
    "wiki_url": "https://github.com/ThatAsherGuy/WoWbjectImporter",
    "category": "Import-Export"
}

import bpy
import os

from .operators import WOWBJ_OT_ToolTip
from .operators import WOWBJ_OT_Import
from .operators import WOWBJ_OT_SerializeNodeGroups
from .operators import WOWBJ_OT_GenerateNodeGroups
from .operators import WOWBJ_OT_LoadCombiner
from .operators import WOWBJ_OT_SetDefaultDir

from .preferences import wowbjectAddonPrefs
from .preferences import WoWbject_ObjectProperties
from .preferences import WoWbject_MaterialProperties
from .preferences import WoWbject_NodeGroupProperties
from .preferences import WoWbject_texture

from .ui import VIEW3D_PT_wowbject_object_panel
from .ui import VIEW3D_PT_wowbject_combiner_panel

from . import addon_updater_ops

classes = (
    # Operators
    WOWBJ_OT_ToolTip,
    WOWBJ_OT_Import,
    WOWBJ_OT_SerializeNodeGroups,
    WOWBJ_OT_GenerateNodeGroups,
    WOWBJ_OT_LoadCombiner,
    WOWBJ_OT_SetDefaultDir,

    # Property Groups
    wowbjectAddonPrefs,
    WoWbject_texture,
    WoWbject_ObjectProperties,
    WoWbject_MaterialProperties,
    WoWbject_NodeGroupProperties,

    # UI stuff
    VIEW3D_PT_wowbject_object_panel,
    VIEW3D_PT_wowbject_combiner_panel
)


def menu_func_import(self, context):
    self.layout.operator(WOWBJ_OT_Import.bl_idname, text='WoWbject (.obj)')


def register():
    addon_updater_ops.register(bl_info)
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

    bpy.types.Object.WBJ = bpy.props.PointerProperty(type=WoWbject_ObjectProperties)
    bpy.types.Material.WBJ = bpy.props.PointerProperty(type=WoWbject_MaterialProperties)
    bpy.types.NodeTree.WBJ = bpy.props.PointerProperty(type=WoWbject_NodeGroupProperties)


def unregister():
    from bpy.utils import unregister_class

    addon_updater_ops.unregister()

    for cls in classes:
        unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

    del bpy.types.Object.WBJ
    del bpy.types.Material.WBJ
    del bpy.types.NodeTree.WBJ
