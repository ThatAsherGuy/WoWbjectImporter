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
from .lookup_funcs import get_vertex_shader, get_shadereffects
from .obj_import import import_obj
from .kaitai.m2_handler import load_kaitai, read_m2
from bpy_extras.wm_utils.progress_report import ProgressReport


# Rather than pass everything individually or assign things to globals, I made this.
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
        self.base_shader

    def unpack_m2(self):
        if self.m2 == None:
            return False

        load_kaitai()
        self.use_m2, self.anim_combos = read_m2(self.source_directory, self.m2)

    def setup_json_data(self, config):
        self.json_config = config

        self.json_textures = self.json_config.get("textures")
        self.json_tex_combos = self.json_config.get("textureCombos")
        self.json_tex_units = self.json_config.get("skin", {}).get("textureUnits")
        self.json_mats = self.json_config.get("materials")
        self.json_submeshes = self.json_config.get("skin", {}).get("subMeshes")

        self.setup_textures()

        return (self.json_textures, self.json_tex_combos, self.json_tex_units)

    def setup_textures(self):
        directory = self.source_directory
        source_textures = self.source_files.get('textures')
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
        


class meshComponent:
    def __init__(self):
        self.usemtl = ''
        self.name = ''
        self.verts = set()
        self.faces = []
        self.uv = []

class meshObject:
    def __init__(self):
        self.usemtl = ''
        self.mtlfile = ''
        self.name = ''
        self.verts = []
        self.faces = []
        self.normals = []
        self.uv = []
        self.uv2 = []
        self.components = []

def debug_print(string):
    do_debug = False

    if do_debug:
        print(string)


def do_import(files, directory, reuse_mats, base_shader, *args):
    with ProgressReport(bpy.context.window_manager) as progress:
        progress.enter_substeps(1, "Importing Files From %r..." % directory)

        box_of_trash = import_container()
        
        source_mesh = None
        source_config = None

        # Stubs for handling multi-import
        source_meshes = []
        source_textures = []
        souce_shaders = []

        # Raw files for debugging
        blp_files = []
        skin_files = []
        raw_file = None

        # Index what we've been handed so we can sanity-check
        for file in files:
            name = file.name.split('.')
            if name[1] == 'png':
                source_textures.append(file.name)
                box_of_trash.source_files['texture'].append(file.name)
            elif name[1] == 'obj':
                source_mesh = file.name
                source_meshes.append(file.name)
                box_of_trash.source_files['OBJ'].append(file.name)
            elif name[1] == 'mtl':
                souce_shaders.append(file.name)
                box_of_trash.source_files['MTL'].append(file.name)
            elif name[1] == 'json':
                source_config = file.name
                box_of_trash.source_files['config'].append(file.name)
            elif name[1] == 'm2':
                raw_file = file.name
                box_of_trash.source_files['M2'].append(file.name)
            elif name[1] == 'blp':
                blp_files.append(file.name)
                box_of_trash.source_files['BLP'].append(file.name)
            elif name[1] == 'skin':
                skin_files.append(file.name)
                box_of_trash.source_files['skin'].append(file.name)
            else:
                print("Unhandled File Type")
                box_of_trash.source_files['unhandled'].append(file.name)

        use_m2_data = False
        if raw_file:
            box_of_trash.m2 = raw_file
            progress.enter_substeps(2, "Reading %r..." % raw_file)
            load_kaitai()
            use_m2_data, anim_chunk_combos = read_m2(directory, raw_file)
            

        # Flatten the JSON data.
        # Makes it easier to pull out sub-dicts later on
        if source_config:
            config_path = os.path.join(directory, source_config)

            if not os.path.isfile(config_path):
                print("CONFIG NOT FOUND")
                return False

            with open(config_path) as p:
                asset_data = json.load(p)
                box_of_trash.json_config = asset_data

                asset_textures = asset_data.get("textures")
                asset_tex_combos = asset_data.get("textureCombos")
                asset_tex_units = asset_data.get("skin", {}).get("textureUnits")

                asset_mats = asset_data.get("materials")
                asset_submeshes = asset_data.get("skin", {}).get("subMeshes")

        newObj = import_obj(source_mesh, directory)
        box_of_trash.bl_obj = newObj

        # Some textures have ID-matchable names, but not all of them.
        # Match where possible, list the ones we have to make guesses about.
        orphaned_textures = []
        used_texture_files = []

        for tex in asset_textures:
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

        progress.enter_substeps(2, "Setting Up Materials...")
        for unit in asset_tex_units:
            texAnim = unit.get("textureTransformComboIndex")
            material = newObj.material_slots[unit.get("skinSectionIndex")].material
            tree = material.node_tree

            # Lazy check to avoid re-building existing materials
            if len(tree.nodes.items()) == 2:
                if use_m2_data:        
                    build_shader(unit, material, asset_mats, asset_textures, asset_tex_combos, base_shader, anim_combos=anim_chunk_combos)
                else:
                    build_shader(unit, material, asset_mats, asset_textures, asset_tex_combos, base_shader)

