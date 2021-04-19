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
import json
import bmesh
from math import radians
from .node_groups import build_shader
from .lookup_funcs import get_vertex_shader, get_shadereffects, get_bone_flags
from .obj_import import import_obj
from .kaitai.m2_handler import load_kaitai, read_m2
from bpy_extras.wm_utils.progress_report import ProgressReport


# Rather than pass everything individually or assign stuff to globals, I made this... Thing.
# The idea here is that I can then pass this object to the external functions it calls, in order to pull extra data from it.
class import_container():
    def __init__(self):
        self.m2 = None
        self.json_config = None
        self.bl_obj = None
        self.anim_combos = None
        self.extracted_config_data = {}
        self.source_files = {
            "OBJ": [],
            "texture": [],
            "MTL": [],
            "BLP": [],
            "skin": [],
            "config": [],
            "unhandled": [],
            "M2": []
        }
        self.source_directory = ''
        self.use_m2 = False
        self.base_shader = None
        self.do_bones = False


    def do_setup(self, files, directory, **kwargs):
        with ProgressReport(bpy.context.window_manager) as progress:
            progress.enter_substeps(5, "Importing Files From %r..." % directory)

            self.source_directory = directory
            for arg, val in kwargs.items():
                if arg == 'base_shader':
                    self.base_shader = val
                elif arg == 'reuse_mats':
                    self.reuse_mats = val

            for file in files:
                name, ext = file.split('.')
                if ext == 'png':
                    self.source_files['texture'].append(file)
                elif ext == 'obj':
                    self.source_files['OBJ'].append(file)
                elif ext == 'mtl':
                    self.source_files['MTL'].append(file)
                elif ext == 'json':
                    self.source_files['config'].append(file)
                elif ext == 'm2':
                    self.source_files['M2'].append(file)
                elif ext == 'blp':
                    self.source_files['BLP'].append(file)
                elif ext == 'skin':
                    self.source_files['skin'].append(file)
                else:
                    print("Unhandled File Type")
                    self.source_files['unhandled'].append(file)

            progress.step("Setting up JSON Data")
            self.setup_json_data()
            progress.step("Unpacking Textures")
            self.setup_textures()
            progress.step("Initializing Object")
            self.setup_bl_object()

            raw = self.source_files.get('M2')
            if len(raw) > 0:
                progress.step("Reading M2")
                self.m2 = raw[0]
                self.unpack_m2()
            progress.step("Generating Materials")
            self.setup_materials()


    def unpack_m2(self):
        if self.m2 == None:
            return False

        load_kaitai()
        self.use_m2, self.m2_dict, self.anim_combos, self.anim_transforms, self.bones = read_m2(self.source_directory, self.m2)

        if self.do_bones:
            bone_markers = []
            for bone in self.bones:
                marker = bpy.data.objects.new("Jimbo", None)
                bone_markers.append(marker)
                bpy.context.view_layer.active_layer_collection.collection.objects.link(marker)
                marker.location = (bone.pivot.x, bone.pivot.y, bone.pivot.z)
                marker.empty_display_size = 0.05
                marker.show_in_front = True
                bpy.context.evaluated_depsgraph_get().update()

                if bone.parent_bone > -1:                    
                    marker.parent = bone_markers[bone.parent_bone]
                    marker.matrix_parent_inverse = bone_markers[bone.parent_bone].matrix_world.inverted()

                bone_flags = get_bone_flags(bone.flags)
                for flag in bone_flags:
                    if flag in {'spherical_billboard', 'cylindrical_billboard_lock_x', 'cylindrical_billboard_lock_y', 'cylindrical_billboard_lock_z'}:
                        marker.empty_display_type = 'CUBE'


    def setup_json_data(self, **kwargs):
        if not kwargs.get('config') == None:
            self.json_config = kwargs.get('config')
        else:
            source = self.source_files['config']

            if len(source) > 1:
                return False

            if len(source) == 0:
                return False

            config_path = os.path.join(self.source_directory, source[0])
            with open(config_path) as p:
                self.json_config = json.load(p)

        self.json_textures = self.json_config.get("textures")
        self.json_tex_combos = self.json_config.get("textureCombos")
        self.json_tex_units = self.json_config.get("skin", {}).get("textureUnits")
        self.json_mats = self.json_config.get("materials")
        self.json_submeshes = self.json_config.get("skin", {}).get("subMeshes")


    def setup_bl_object(self):
        source = self.source_files['OBJ']

        # Nothing to setup. TODO: Setup a report logging system here.
        if len(source) == 0:
            return False

        # Haven't set up multi-object importing
        if len(source) > 1:
            return False

        self.bl_obj = import_obj(source[0], self.source_directory)


    def setup_textures(self):
        directory = self.source_directory
        source_textures = self.source_files.get('texture')
        orphaned_textures = []
        used_texture_files = []

        for tex in self.json_textures:
            texID = tex.get("fileDataID")
            match = False

            if not texID:
                print("Texture ID Not Found")

            for tex_file in source_textures:
                if str(texID) in tex_file:
                    tex["name"] = tex_file
                    tex["path"] = os.path.join(directory, tex_file)
                    used_texture_files.append(tex_file)
                    match = True
                    break
            
            if not match:
                orphaned_textures.append(tex)
            
        if len(orphaned_textures) > 0:
            print("Unable to Match Textures")
            if len(orphaned_textures) == 1:
                orphan = orphaned_textures[0]
                temp_set = set(source_textures).difference(set(used_texture_files))
                if len(temp_set) > 0:
                    orphaned_file = list(temp_set)[0]
                    orphan["name"] = orphaned_file
                    orphan["path"] = os.path.join(directory, orphaned_file)
                else:
                    pass # TODO: Discard the texture so we don't try to use it down the road.
            else:
                print("Too many orphaned textures to finesse")


    def setup_materials(self):

        for unit in self.json_tex_units:
            bl_mat = self.bl_obj.material_slots[unit.get("skinSectionIndex")].material
            tree = bl_mat.node_tree

            # Lazy check to avoid re-building existing materials
            if len(tree.nodes.items()) == 2:
                if self.use_m2:        
                    build_shader(
                        unit,
                        bl_mat,
                        self.json_mats,
                        self.json_textures,
                        self.json_tex_combos,
                        self.base_shader,
                        import_container = self,
                        anim_combos=self.anim_combos,
                        )
                else:
                    build_shader(
                        unit,
                        bl_mat,
                        self.json_mats,
                        self.json_textures,
                        self.json_tex_combos,
                        self.base_shader,
                        import_container = self
                        )


class mat_def():
    def __init__(self):
        self.tex_unit = None
        self.bl_mat = None
        self.blend_mode = None
        self.textures = None
        self.tex_combos = None
        self.base_shader = None
        self.parent = None


def debug_print(string):
    do_debug = False

    if do_debug:
        print(string)


def do_import(files, directory, reuse_mats, base_shader, *args):

    textures = []
    objects = []
    mtl = []
    configs = []
    m2 = []

    for file in files:
        name, ext = file.name.split('.')
        if ext == 'png':
            textures.append(file.name)
        elif ext == 'obj':
            objects.append(file.name)
        elif ext == 'mtl':
            mtl.append(file.name)
        elif ext == 'json':
            configs.append(file.name)
        elif ext == 'm2':
            m2.append(file.name)

    file_lists = (textures, objects, configs, m2)

    do_search = False

    for L in file_lists:
        if len(L) < 1:
            do_search = True
            break


    if do_search:
        ref_name = ''
        if len(objects) == 1:
            ref_name = objects[0].split('.')[0]

        dir_files = [file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))]

        config_found = False
        m2_found = False
        mtl_found = False

        print(ref_name)

        for file in dir_files:
            name, ext = file.split('.')

            if len(configs) < 1:
                if (name == ref_name) and (ext == 'json'):
                    configs.append(file)
                    config_found = True
                    continue

            if len(m2) < 1:
                if (name == ref_name) and (ext == 'm2'):
                    m2.append(file)
                    m2_found = True
                    continue

            if len(mtl) < 1:
                if (name == ref_name) and (ext == 'mtl'):
                    mtl.append(file)
                    mtl_found = True
                    continue

        find_textures = False
        if len(textures) < 1:
            find_textures = True

        if find_textures:
            if len(mtl) == 1:
                textures = read_mtl(directory, mtl[0])

    files = textures + objects + mtl + configs + m2

    box_of_trash = import_container()
    box_of_trash.do_setup(
        files,
        directory,
        reuse_mats=reuse_mats,
        base_shader=base_shader
        )

def read_mtl(directory, mtl):
    textures = []
    with open(os.path.join(directory, mtl), 'r') as f:
        for line in f:
            line_split = line.split()
            if not line_split:
                continue
            line_start = line_split[0]

            if line_start == 'map_Kd':
                textures.append(line_split[1])

    return textures