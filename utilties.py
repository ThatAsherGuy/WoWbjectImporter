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
        self.op_args = {}
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
        self.tex_dir = ''
        self.use_m2 = False
        self.base_shader = None
        self.do_bones = False
        self.reuse_mats = False
        self.fallback_texture = None
        self.fallback_type = ''
        self.fallback_generated = False
        self.err = set()
        self.reports = []
        self.damage_control = False


    def do_setup(self, files, directory, op_args, **kwargs):
        # ProgressReport is the thing that does the fancy print messages and changes the cursor.
        # I'm 50/50 on it. There's also no documentation for it, outside of comments in the source code.
        with ProgressReport(bpy.context.window_manager) as progress:
            progress.enter_substeps(5, "Importing Files From %r..." % directory)

            self.op_args = op_args
            self.source_directory = directory
            for arg, val in kwargs.items():
                if arg == 'base_shader':
                    self.base_shader = val
                elif arg == 'reuse_mats':
                    self.reuse_mats = val

            for file in files:
                name, ext = os.path.splitext(file)
                if ext == '.png':
                    self.source_files['texture'].append(file)
                elif ext == '.obj':
                    self.source_files['OBJ'].append(file)
                elif ext == '.mtl':
                    self.source_files['MTL'].append(file)
                elif ext == '.json':
                    self.source_files['config'].append(file)
                elif ext == '.m2':
                    self.source_files['M2'].append(file)
                elif ext == '.blp':
                    self.source_files['BLP'].append(file)
                elif ext == '.skin':
                    self.source_files['skin'].append(file)
                else:
                    print("Unhandled File Type: " + str(file))
                    self.source_files['unhandled'].append(file)

            progress.step("Setting up JSON Data")
            load_step = self.setup_json_data()
            if not load_step:
                self.err.add('ERROR')
                self.reports.append('Failed to load JSON Data')
                self.damage_control = True

            progress.step("Unpacking Textures")
            load_step = self.setup_textures()
            # if not load_step:
            #     self.reports.append('Failed to load textures')

            progress.step("Initializing Object")
            load_step = self.setup_bl_object()
            if not load_step:
                self.err.add('ERROR')
                self.reports.append('Failed to initialize blender object')

            raw = self.source_files.get('M2')
            if len(raw) > 0:
                progress.step("Reading M2")
                self.m2 = raw[0]
                load_step = self.unpack_m2()

            load_step = self.unpack_m2()

            progress.step("Generating Materials")
            load_step = self.setup_materials()
            if not load_step:
                self.reports.append('Failed to setup materials')

            return (self.err, self.reports)

    def unpack_m2(self):
        if self.m2 == None:
            self.err.add('INFO')
            self.reports.append("M2 File not found")
            return False

        # Kaitai is now bundled, no need to import
        # load_kaitai()
        self.use_m2, self.m2_dict, self.anim_combos, self.anim_transforms, self.bones = read_m2(self.source_directory, self.m2)

        # Bone/billboard debugging
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

        # Won't make up for missing JSON data (will need to kaitai .skin files for texUnit data)
        if self.damage_control:
            main_chunk = None
            for entry, item in self.m2_dict.items():
                if entry == "chunks":
                    for chunk in item:
                        if chunk.chunk_type == "MD21":
                            main_chunk = chunk.data.data
                            break

            if main_chunk:
                textures = main_chunk.textures
                combos = main_chunk.texture_combos
                mats = main_chunk.materials

                json_textures = {}

                for i, tex in enumerate(textures.values):
                    json_textures[i] = {tex.flags, tex.filename}

        return True


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

        self.json_textures = self.json_config.get("textures", [])
        self.json_tex_combos = self.json_config.get("textureCombos", [])
        self.json_tex_units = self.json_config.get("skin", {}).get("textureUnits", [])
        self.json_mats = self.json_config.get("materials", [])
        self.json_submeshes = self.json_config.get("skin", {}).get("subMeshes", [])

        return True


    def setup_bl_object(self):
        '''
        Calls the actual OBJ importer and sets up an object in Blender.
        Materials are assigned to face during this process, but the material setup happens later.
        '''
        source = self.source_files['OBJ']

        # TODO: Setup a report logging system here.
        if len(source) == 0:
            return False

        # TODO: set up multi-object importing
        if len(source) > 1:
            return False

        self.bl_obj = import_obj(
            source[0],
            self.source_directory,
            self.reuse_mats,
            self.op_args.get("name_override")
            )

        return True


    def setup_textures(self):
        '''
        Matches the fileIDs in the json_texutres dict to the actual image files.
        Packs the related info back into that dict for later use.
        '''

        # sub-directory handling
        if self.tex_dir == '':
            directory = self.source_directory
        else:
            directory = os.path.join(self.source_directory, self.tex_dir)

        source_textures = self.source_files.get('texture')

        if self.damage_control:
            self.json_textures = {}
            self.json_tex_combos = []
            self.json_tex_units = {}
            self.json_mats = {}
            self.json_submeshes = {}
            self.reports.append("Textures must be setup manually")
            return False

        for tex in self.json_textures:
            texID = tex.get("fileDataID")

            if not texID:
                print("Texture ID Not Found")

            match = False
            for tex_file in source_textures:
                if str(texID) in tex_file:
                    tex["name"] = tex_file
                    tex["path"] = os.path.join(directory, tex_file)
                    match = True
                    break

            if not match:
                print("TEXTURE NOT FOUND")

        return True


    def get_fallback_tex(self):
        if self.fallback_generated:
            return self.fallback_texture
        else:
            if "WoWbject_Fallback_Texture" in bpy.data.images:
                img = bpy.data.images["WoWbject_Fallback_Texture"]
                self.fallback_texture = img
                self.fallback_generated = True
                return img

            img = bpy.data.images.new("WoWbject_Fallback_Texture", 512, 512, alpha=True)
            if self.fallback_type == '':
                img.generated_type = 'COLOR_GRID'
            else:
                img.generated_type = self.fallback_type

            img.alpha_mode = 'CHANNEL_PACKED'

            self.fallback_generated = True
            self.fallback_texture = img
            return img


    def setup_materials(self):
        '''
        Generates a material for each texture unit in the JSON config.
        Most of the work here happens in build_shader from node_groups.py
        '''

        # if self.damage_control == True, self.json_tex_units wil be empty.
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

        return True


# Currently unused
class mat_def():
    def __init__(self):
        self.tex_unit = None
        self.bl_mat = None
        self.blend_mode = None
        self.textures = None
        self.tex_combos = None
        self.base_shader = None
        self.parent = None


# Currently unused
def debug_print(string):
    do_debug = False

    if do_debug:
        print(string)


def do_import(files, directory, reuse_mats, base_shader, op_args, **kwargs):
    '''
    The pre-sorting and initializing function called by the import operator.
    Most of the actual data-handling is handled by an import_container object.
    '''

    files = op_args.get("files")
    directory = op_args.get("directory")
    reuse_mats = op_args.get("reuse_materials")
    base_shader = op_args.get("base_shader")
    name_override = op_args.get("name_override")

    textures = []
    objects = []
    mtl = []
    configs = []
    m2 = []

    for file in files:
        name, ext = os.path.splitext(file.name)

        if ext == '.png':
            textures.append(file.name)
        elif ext == '.obj':
            objects.append(file.name)
        elif ext == '.mtl':
            mtl.append(file.name)
        elif ext == '.json':
            configs.append(file.name)
        elif ext == '.m2':
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

        dir_files = []
        subdirs = []
        tex_dir = ''

        for thing in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, thing)):
                dir_files.append(thing)
            elif os.path.isdir(os.path.join(directory, thing)):
                subdirs.append(thing)
                if thing == 'textures':
                    tex_dir = thing

        config_found = False
        m2_found = False
        mtl_found = False

        # Search source directory for missing files
        for file in dir_files:
            name, ext = os.path.splitext(file)

            if len(configs) < 1:
                if (name == ref_name) and (ext == '.json'):
                    configs.append(file)
                    config_found = True
                    continue

            if len(m2) < 1:
                if (name == ref_name) and (ext == '.m2'):
                    m2.append(file)
                    m2_found = True
                    continue

            if len(mtl) < 1:
                if (name == ref_name) and (ext == '.mtl'):
                    mtl.append(file)
                    mtl_found = True
                    continue

        # Find missing textures by checking configs
        # Doesn't handle situations where only some are missing
        if len(textures) < 1:
            if mtl_found == 1:
                textures = read_mtl(directory, mtl[0])
            elif config_found:
                with open(os.path.join(directory, configs[0])) as p:
                    json_config = json.load(p)
                    tex_defs = json_config.get("textures")
                    for tdef in tex_defs:
                        tID = tdef.get("fileDataID")
                        textures.append(tID + ".png")

    files = textures + objects + mtl + configs + m2

    import_obj = import_container()
    import_obj.tex_dir = tex_dir
    reports = import_obj.do_setup(
        files,
        directory,
        op_args,
        reuse_mats=reuse_mats,
        base_shader=base_shader
        )
    return reports

# TODO: Logging
def read_mtl(directory, mtl):
    textures = []
    if os.path.isfile(os.path.join(directory, mtl)):
        with open(os.path.join(directory, mtl), 'r') as f:
            for line in f:
                line_split = line.split()
                if not line_split:
                    continue
                line_start = line_split[0]

                if line_start == 'map_Kd':
                    textures.append(line_split[1])
        return textures
    else:
        print("Invalid MTL!")
        return False
