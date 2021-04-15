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

def initialize_mesh(mesh_path):
    '''Reads the actual OBJ file, shoves it into a meshObject()'''
    obj = meshObject()
    meshIndex = -1

    with open(mesh_path, 'rb') as f:
        for line in f:
            line_split = line.split()
            if not line_split:
                continue
            line_start = line_split[0]
            if line_start == b'mtllib':
                obj.mtlfile = line_split[1]
            elif line_start == b'v':
                obj.verts.append([float(v) for v in line_split[1:]])
            elif line_start == b'vn':
                obj.normals.append([float(v) for v in line_split[1:]])
            elif line_start == b'vt2':
                obj.uv2.append([float(v) for v in line_split[1:]])
            elif line_start == b'vt':
                obj.uv.append([float(v) for v in line_split[1:]])
            elif line_start == b'f':
                line_split = line_split[1:]
                fv = [int(v.split(b'/')[0]) for v in line_split]
                obj.components[meshIndex].faces.append((fv[0], fv[1], fv[2]))
                obj.components[meshIndex].verts.update([i - 1 for i in fv])
            elif line_start == b'g':
                meshIndex += 1
                obj.components.append(meshComponent())
                obj.components[meshIndex].name = line_split[1].decode('utf-8')
            elif line_start == b'usemtl':
                obj.components[meshIndex].usemtl = line_split[1].decode('utf-8')

    return obj


def debug_print(string):
    do_debug = False

    if do_debug:
        print(string)


def do_import(files, directory, reuse_mats, base_shader, *args):
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
        elif name[1] == 'obj':
            source_mesh = file.name
            source_meshes.append(file.name)
        elif name[1] == 'mtl':
            souce_shaders.append(file.name)
        elif name[1] == 'json':
            source_config = file.name
        elif name[1] == 'm2':
            raw_file = file.name
        elif name[1] == 'blp':
            blp_files.append(file.name)
        elif name[1] == 'skin':
            skin_files.append(file.name)
        else:
            print("Unhandled File Type")

    use_m2_data = False
    if raw_file:
        from .kaitai import m2_handler
        from .kaitai.m2 import M2
        m2_struct = M2.from_file(os.path.join(directory, raw_file))
        m2_globals = m2_struct.Md20GlobalFlags
        m2_dict = m2_struct.__dict__

        md21_chunk = None
        uv_anim_chunk = None
        texTransform_chunk = None

        for entry, item in m2_dict.items():
            if entry == "chunks":
                for chunk in item:
                    if chunk.chunk_type == "MD21":
                        md21_chunk = chunk.data.data
                        break

        if md21_chunk:
            tex_iterable = md21_chunk.textures.__dict__
            uv_anim_chunk = md21_chunk.texture_transform_combos
            texTransform_chunk = md21_chunk.texture_transforms
            # print(tex_iterable)

            anim_chunk_combos = uv_anim_chunk.items
            print(anim_chunk_combos)
            use_m2_data = True

    # Flatten the JSON data.
    # Makes it easier to pull out sub-dicts later on
    if source_config:
        config_path = os.path.join(directory, source_config)

        if not os.path.isfile(config_path):
            print("CONFIG NOT FOUND")
            return False

        with open(config_path) as p:
            asset_data = json.load(p)

            asset_textures = asset_data.get("textures")
            asset_tex_combos = asset_data.get("textureCombos")
            asset_tex_units = asset_data.get("skin", {}).get("textureUnits")

            asset_mats = asset_data.get("materials")
            asset_submeshes = asset_data.get("skin", {}).get("subMeshes")


    # A lot of this code is from WoW Export
    mesh_name, mesh_type = source_mesh.split('.')
    base_name = mesh_name

    if mesh_name in bpy.data.objects:
        objIndex = 1
        newName = mesh_name
        while(newName in bpy.data.objects):
            newName = mesh_name + '.' + str(objIndex).rjust(3, '0')
            objIndex += 1
        mesh_name = newName

    if bpy.ops.object.select_all.poll():
        bpy.ops.object.select_all(action='DESELECT')

    mesh_data = initialize_mesh(os.path.join(directory, source_mesh))
    newMesh = bpy.data.meshes.new(mesh_name)
    newObj = bpy.data.objects.new(mesh_name, newMesh)

    bm = bmesh.new()

    for i, v in enumerate(mesh_data.verts):
        vert = bm.verts.new(v)
        vert.normal = mesh_data.normals[i]

    bm.verts.ensure_lookup_table()
    bm.verts.index_update()

    for i, component in enumerate(mesh_data.components):
        exampleFaceSet = False

        mat_name_base = base_name + "_" + component.name

        if (mat_name_base in bpy.data.materials) and reuse_mats:
            mat = bpy.data.materials[mat_name_base]
        else:
            mat = bpy.data.materials.new(name=mat_name_base)
            mat.use_nodes = True

        newObj.data.materials.append(mat)

        #Silly as it is, this gives us the name with the trailing .00X
        mat_name = mat.name


        for face in component.faces:
            if exampleFaceSet == False:
                bm.faces.new((
                    bm.verts[face[0] - 1],
                    bm.verts[face[1] - 1],
                    bm.verts[face[2] - 1]
                ))
                bm.faces.ensure_lookup_table()

                # Damn it, why does this work?
                bm.faces[-1].material_index = max(newObj.data.materials.find(mat_name), 0)

                bm.faces[-1].smooth = True
                exampleFace = bm.faces[-1]
                exampleFaceSet = True
            else:
                ## Use example face if set to speed up material copy!
                bm.faces.new((
                    bm.verts[face[0] - 1],
                    bm.verts[face[1] - 1],
                    bm.verts[face[2] - 1]
                ), exampleFace)

    uv_layer = bm.loops.layers.uv.new()
    for face in bm.faces:
        for loop in face.loops:
            loop[uv_layer].uv = mesh_data.uv[loop.vert.index]

    if len(mesh_data.uv2) > 0:
        uv2_layer = bm.loops.layers.uv.new('UV2Map')
        for face in bm.faces:
            for loop in face.loops:
                loop[uv2_layer].uv = mesh_data.uv2[loop.vert.index]

    bm.to_mesh(newMesh)
    bm.free()


    for i, component in enumerate(sorted(mesh_data.components, key=lambda m: m.name.lower())):
        vg = newObj.vertex_groups.new(name=f"{component.name}")
        vg.add(list(component.verts), 1.0, "REPLACE")

    ## Rotate object the right way
    newObj.rotation_euler = [0, 0, 0]
    newObj.rotation_euler.x = radians(90)

    # Defaults to master collection if no collection exists.
    bpy.context.view_layer.active_layer_collection.collection.objects.link(newObj)
    newObj.select_set(True)

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

        # This bit doesn't work yet. 
        # Tried to do some glorifies spear fishing
        # but it looks like I'll need to look into
        # the m2 file directly.
        do_animate = False
        if (texAnim == 0) and do_animate:
            mod = newObj.modifiers.new('Texture Animation', 'UV_WARP')
            mod.uv_layer = 'UV2Map'
            temp = material.name.split('_')
            target = temp[-1]
            mod.vertex_group = target
