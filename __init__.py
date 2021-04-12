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
    "name" : "WoWbjectifier",
    "author" : "Asher",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import bpy
import os

from .operators import WOWBJ_OT_Import
from .operators import WOWBJ_OT_SerializeNodeGroups
from .operators import WOWBJ_OT_GenerateNodeGroups
from .preferences import wowbjectAddonPrefs

classes = (
    WOWBJ_OT_Import,
    WOWBJ_OT_SerializeNodeGroups,
    WOWBJ_OT_GenerateNodeGroups,
    wowbjectAddonPrefs,
)

def menu_func_import(self, context):
    self.layout.operator(WOWBJ_OT_Import.bl_idname, text='WoWbject (.obj)')

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(WOWBJ_OT_Import)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
