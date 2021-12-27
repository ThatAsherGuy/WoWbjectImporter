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
import json
import time

import bpy
import bmesh
import mathutils
from math import radians
from .node_groups import build_shader, do_wmo_mats
from .lookup_funcs import get_vertex_shader, get_shadereffects, get_bone_flags
from .obj_import import import_obj
from .kaitai.m2_handler import load_kaitai, read_m2
from bpy_extras.wm_utils.progress_report import ProgressReport
from collections import namedtuple
from typing import List, Dict, Tuple, cast, Union


# Rather than pass everything individually or assign stuff to globals, I made this... Thing.
# The idea here is that I can then pass this object to the external functions it calls, in order to pull extra data from it.
class import_container():
    def __init__(self):
        self.name = None
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
            "M2": [],
            "WMO": []
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
        self.damage_control = False

        self.reports = namedtuple(
            'log_group', ['warnings', 'errors', 'info', 'sub_steps'])
        self.reports.warnings = []
        self.reports.errors = []
        self.reports.info = []
        self.reports.sub_steps = []

        self.wmo = False

    def do_setup(self, files, directory, op_args, **kwargs):
        # ProgressReport is the thing that does the fancy print messages and changes the cursor.
        # I'm 50/50 on it. There's also no documentation for it, outside of comments in the source code.
        with ProgressReport(bpy.context.window_manager) as progress:
            progress.enter_substeps(
                5, "Importing Files From %r..." % directory)

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
                elif ext == '.wmo':
                    self.source_files['skin'].append(file)
                else:
                    print("Unhandled File Type: " + str(file))
                    self.source_files['unhandled'].append(file)

            progress.step("Setting up JSON Data")
            load_step = self.setup_json_data()
            if not load_step:
                self.reports.errors.append('Failed to load JSON Data')
                self.damage_control = True

            progress.step("Unpacking Textures")
            if not self.wmo:
                load_step = self.setup_textures()
            # if not load_step:
            #     self.reports.append('Failed to load textures')

            progress.step()
            progress.enter_substeps(2, "Initializing Object")
            load_step = self.setup_bl_object(progress)
            if not load_step:
                self.reports.errors.append(
                    'Failed to initialize blender object')

            progress.leave_substeps()

            raw = self.source_files.get('M2')
            if len(raw) > 0:
                progress.step("Reading M2")
                self.m2 = raw[0]
                load_step = self.unpack_m2()

            # Work-in-progress particle system importer
            do_particles = False
            if do_particles:
                self.setup_particles()

            progress.step("Generating Materials")
            load_step = self.setup_materials()
            if not load_step:
                self.reports.errors.append('Failed to setup materials')

            progress.leave_substeps("WMO Loaded")

            return self.reports

    def unpack_m2(self):
        if self.m2 == None:
            self.reports.info.append("M2 File not found")
            return False

        # Kaitai is now bundled, no need to import
        # load_kaitai()
        self.use_m2, self.m2_dict, self.anim_combos, self.anim_transforms, self.bones = read_m2(
            self.source_directory, self.m2)

        main_chunk = self.m2_dict

        # Bone/billboard debugging
        if self.do_bones:
            armature = bpy.data.armatures.new("ARM")
            arm_obj = bpy.data.objects.new("ARM_OBJ", armature)

            bpy.context.view_layer.active_layer_collection.collection.objects.link(
                arm_obj)
            arm_obj.select_set(True)

            bpy.context.view_layer.objects.active = arm_obj
            bpy.ops.object.mode_set(
                'INVOKE_DEFAULT', False, mode='EDIT', toggle=False)

            # EditBones and PoseBones don't hold references to each other.
            # Which means that we have to manuall map M2CompBone:EditBone:PoseBone by name,
            # in order to do all the things we need to do.
            bone_dict = {}

            for i, bone in enumerate(self.bones):

                bone_flags = get_bone_flags(bone.flags)
                for flag in bone_flags:
                    if flag in {'SPHERICAL_BILLBOARD', 'CYL_BILLBOARD_LOCK_X', 'CYL_BILLBOARD_LOCK_Y', 'CYL_BILLBOARD_LOCK_Z'}:
                        bone_tag = "_" + flag

                ebone = armature.edit_bones.new("Bone_" + str(i))
                ebone.head = (bone.pivot.x, bone.pivot.y, bone.pivot.z)
                ebone.tail = (bone.pivot.x, bone.pivot.y, bone.pivot.z + 0.1)

                bone_dict["Bone_" + str(i)] = {
                    "m2_bone": bone
                }

                if 'ignoreParentScale' in bone_flags:
                    ebone.inherit_scale = 'NONE'

                if bone.parent_bone > -1:
                    parent = armature.edit_bones[bone.parent_bone]

                    if not parent.parent:  # Not sure about this
                        parent.tail = ebone.head

                    ebone.parent = parent
                    ebone.use_connect = True

            bpy.ops.object.editmode_toggle()
            bpy.ops.object.mode_set(
                'INVOKE_DEFAULT', False, mode='POSE', toggle=False)

            for pbone in arm_obj.pose.bones:
                do_billboard = False

                bone = bone_dict.get(pbone.name).get("m2_bone")
                bone_flags = get_bone_flags(bone.flags)

                for flag in bone_flags:
                    if flag in {'SPHERICAL_BILLBOARD', 'CYL_BILLBOARD_LOCK_X', 'CYL_BILLBOARD_LOCK_Y', 'CYL_BILLBOARD_LOCK_Z'}:
                        do_billboard = True

                if do_billboard:
                    bb_constraint = pbone.constraints.new('DAMPED_TRACK')
                    if bpy.context.scene.camera:
                        bb_constraint.target = bpy.context.scene.camera

                if 'transformed' in bone_flags:
                    if bone.rotation.values.num > 0:  # There's some janky shit going on here
                        if bone.rotation.values.values[0].num > 0:
                            comp_quat = bone.rotation.values.values[0].values[0]
                            x = (comp_quat.x + 32768) / \
                                32767 if comp_quat.x < 0 else (
                                    comp_quat.x - 32767) / 32767
                            y = (comp_quat.y + 32768) / \
                                32767 if comp_quat.y < 0 else (
                                    comp_quat.y - 32767) / 32767
                            z = (comp_quat.z + 32768) / \
                                32767 if comp_quat.z < 0 else (
                                    comp_quat.z - 32767) / 32767
                            w = (comp_quat.w + 32768) / \
                                32767 if comp_quat.w < 0 else (
                                    comp_quat.w - 32767) / 32767
                            bone_quat = mathutils.Quaternion((w, x, y, z))
                            fquat = mathutils.Quaternion(
                                (1.0, 0.0, 0.0), radians(90))
                            pbone.rotation_quaternion = bone_quat

        # Won't make up for missing JSON data (will need to kaitai .skin files for texUnit data)
        if self.damage_control:
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

        if ".wmo" in self.json_config.get("fileName", ""):
            self.wmo = True

        self.json_textures = self.json_config.get(
            "textures", self.json_config.get("fileDataIDs", []))
        self.json_tex_combos = self.json_config.get("textureCombos", [])
        self.json_tex_units = self.json_config.get(
            "skin", {}).get("textureUnits", [])
        self.json_mats = self.json_config.get("materials", [])
        self.json_submeshes = self.json_config.get(
            "skin", {}).get("subMeshes", [])

        return True

    def setup_bl_object(self, progress):
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
            self.op_args.get("name_override"),
            self.op_args.get("merge_verts"),
            self.op_args.get("make_quads"),
            self.op_args.get("use_collections"),
            self,
            progress
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
            self.reports.info.append("Textures must be setup manually")
            return False

        for tex in self.json_textures:
            texID = tex.get("fileDataID")

            if not texID:
                print("Texture ID Not Found")

            match = False
            for tex_file in source_textures:
                if str(texID) in tex_file:
                    tex["name"] = self.name + "_" + tex_file
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

            img = bpy.data.images.new(
                "WoWbject_Fallback_Texture", 512, 512, alpha=True)
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
        if self.wmo:
            do_wmo_mats(container=self, json=self.json_config)
        else:
            limit = len(self.bl_obj.material_slots) - 1
            # if self.damage_control == True, self.json_tex_units wil be empty.
            for unit in self.json_tex_units:
                bl_mat = self.bl_obj.material_slots[
                    min(unit.get("skinSectionIndex"), limit)].material
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
                            import_container=self,
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
                            import_container=self
                        )

        return True

    def setup_particles(self):
        if not hasattr(self, "m2_dict"):
            return
        if len(self.m2_dict.particle_emitters.values) == 0:
            return

        emitter_geom = bpy.data.meshes.new("Particle_Thingy_Geom")
        emmitter_obj = bpy.data.objects.new(
            "Particle_Thingy_Obj", emitter_geom)

        bpy.context.view_layer.active_layer_collection.collection.objects.link(
            emmitter_obj)
        bpy.context.view_layer.objects.active = emmitter_obj

        # Initialize groups before entering edit mode.
        # Means we have to manipulate vertex groups via the deform data layer
        # But that's somehow less fucky than the alternative
        for i, emitter in enumerate(self.m2_dict.particle_emitters.values):
            vg = emmitter_obj.vertex_groups.new(name="Franklin_" + str(i))
            vg.add([], 1.0, "REPLACE")

        bpy.ops.object.editmode_toggle()
        bm = bmesh.from_edit_mesh(emmitter_obj.data)

        self.particle_emitters = self.m2_dict.particle_emitters.values

        for i, emitter in enumerate(self.m2_dict.particle_emitters.values):
            particle = emitter.old
            p_tex = [emitter.multi_texture_param0,
                     emitter.multi_texture_param1]

            mat = mathutils.Matrix.Translation(
                (particle.position.x, particle.position.y, particle.position.z))

            if particle.emitter_type.value == 1:
                verts = bmesh.ops.create_grid(
                    bm, x_segments=1, y_segments=1, size=0.1, matrix=mat)
                nverts = 4
            elif particle.emitter_type.value == 2:
                verts = bmesh.ops.create_icosphere(
                    bm, subdivisions=1, diameter=0.1, matrix=mat)
                nverts = 12
            else:
                verts = bmesh.ops.create_icosphere(
                    bm, subdivisions=1, diameter=0.05, matrix=mat)
                nverts = 12

            bmesh.update_edit_mesh(emmitter_obj.data)
            bm.verts.ensure_lookup_table()
            bm.verts.layers.deform.verify()

            deform = bm.verts.layers.deform.active

            verts = verts.get('verts')
            verts = [bm.verts[i] for i in range(-nverts, 0)]
            for vert in verts:
                g = vert[deform]
                g[i] = 1

            emit_rate = particle.emission_rate.values.values[0].values[0]
            # print(emit_rate)
            emit_speed = particle.emission_speed.values.values[0].values[0]
            lifespan = particle.lifespan.values.values[0].values[0]

            count = (emit_rate * 24) / (100)
            # print(count)

            bpy.ops.object.particle_system_add()

            sys = emmitter_obj.particle_systems[-1]
            sys.vertex_group_density = "Franklin_" + str(i)

            sys_settings = sys.settings
            sys_settings.effector_weights.gravity = 0
            sys_settings.display_size = 0.01
            sys_settings.count = max(count, 1)
            sys_settings.normal_factor = emit_speed
            sys_settings.lifetime = lifespan * 24

            # Blender uses particle count/emission time to get particles per time step
            # Wow uses emission rate * emission time to get particle count
            # Still need to figure out the actual total particles per minute, though.

            # TODO: Standardize M2Track reading to speed up access for single-item tracks.

        bpy.ops.object.editmode_toggle()

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

# old call:
#   reports = do_import(self.files, self.directory, self.reuse_materials, self.base_shader, args)
# new call:
#   reports = do_import(self, context, filepath=self.filepath, self.reuse_materials, self.base_shader, args)

# orig def:
#   def do_import(files, directory, reuse_mats, base_shader, op_args, **kwargs):
def do_import(operator, context, filepath, reuse_mats, base_shader, op_args, **kwargs):
    '''
    The pre-sorting and initializing function called by the import operator.
    Most of the actual data-handling is handled by an import_container object.
    '''

    # files = op_args.get("files")
    # directory = op_args.get("directory")
    file = os.path.basename(filepath)
    directory = os.path.dirname(filepath)

    # FIXME: these first two aren't needed?
    reuse_mats = op_args.get("reuse_materials")
    base_shader = op_args.get("base_shader")
    name_override = op_args.get("name_override")

    textures = []
    objects = []
    mtl = []
    configs = []
    m2 = []

    # for file in files:
    name, ext = os.path.splitext(file)

    # FIXME: Do we actually need this? We're not multi-selecting non-obj files now
    if ext == '.png':
        textures.append(file)
    elif ext == '.obj':
        objects.append(file)
    elif ext == '.mtl':
        mtl.append(file)
    elif ext == '.json':
        configs.append(file)
    elif ext == '.m2':
        m2.append(file)

    file_lists = (textures, objects, configs, m2)

    do_search = False

    for L in file_lists:
        if len(L) < 1:
            do_search = True
            break

    if do_search:
        ref_name = ''
        if len(objects) == 1:
            ref_name = os.path.splitext(objects[0])[0]

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
                        textures.append(str(tID) + ".png")

        if len(objects) == 1:
            if name_override == '':
                name = os.path.splitext(objects[0])[0]
            else:
                name = name_override

            print(name)

    files = textures + objects + mtl + configs + m2

    import_obj = import_container()
    import_obj.tex_dir = tex_dir
    import_obj.name = name
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


def recursive_remove_doubles(bm: bmesh.types.BMesh, verts: bmesh.types.BMVertSeq, dist: float = 0.00001) -> Dict[str, Union[int, float]]:
    start_time = time.time()
    start_verts = len(bm.verts)

    merge_passes = 0
    while True:
        merge_passes += 1
        before_verts = len(bm.verts)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00001)
        after_verts = len(bm.verts)
        if after_verts == before_verts:
            total_time = time.time() - start_time
            stats = {
                "start_verts": start_verts,
                "end_verts": after_verts,
                "removed_verts": start_verts - after_verts,
                "merge_passes": merge_passes,
                "total_time": total_time,
            }

            return stats


# No bmesh version of tris-to-quads, so we need to use an operator. Make sure
# object is linked into the current scene before calling.
def tris_to_quads(obj: bpy.types.Object, face_thresholdz: float = 5.0):
    start_time = time.time()
    old_active = bpy.context.view_layer.objects.active

    before_faces = len(obj.data.polygons)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.tris_convert_to_quads(
        face_threshold=radians(face_threshold), uvs=True, vcols=True, seam=True,
        sharp=True, materials=True)
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    after_faces = before_faces - len(obj.data.polygons)

    bpy.context.view_layer.objects.active = old_active

    total_time = time.time() - start_time
    stats = {
        "start_faces": before_faces,
        "end_faces": after_faces,
        "removed_faces": before_faces - after_faces,
        "total_time": total_time,
    }
    return stats
