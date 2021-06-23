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

# This module doesn't do anything yet.
# Right now, the OBJ reading and sorting is handled
# by the initialize_mesh() function in utilities.py.
# The plan for this module is to build a more robust
# importer, that can handle more complex OBJ data.

# It'd be cool do a direct M2→BMesh conversion, though.

import bpy
import os
import bmesh
from math import radians
from bpy_extras.io_utils import unpack_list
from bpy_extras.image_utils import load_image
from .lookup_funcs import wmo_read_color
from itertools import chain


def setup_blender_object(**kwargs):
    base_name = kwargs.get("name", "wmo_object")
    mesh_data = kwargs.get("mesh_data")
    mat_dict = kwargs.get("mat_dict", {})
    merge_verts = kwargs.get("merge_verts")

    group = kwargs.get("group")
    json_group = group.json_group

    full_name = base_name + "_" + json_group.get("groupName", "section")

    mesh = bpy.data.meshes.new(base_name)
    mesh.use_auto_smooth = True
    mesh.auto_smooth_angle = radians(60)

    blender_object = bpy.data.objects.new(full_name, mesh)

    bm = bmesh.new()
    vcols = bm.loops.layers.color.new("vcols")
    uv_layer = bm.loops.layers.uv.new()

    batches = group.mesh_batches
    json_batches = group.json_batches
    color_list = group.colors

    batch_offset = 0
    colors = {}

    # print("JSON Batches: %i" % len(json_batches))
    # print("Direct Batches: %i" % len(batches))
    v_dict = {}
    uv_dict = {}
    for i, batch in enumerate(batches):
        exampleFaceSet = False

        for face in batch.faces:
            for v in face:
                vert = bm.verts.new(mesh_data.verts[v - 1])
                v_dict[v] = vert

                # The data layer for vertex color is actually in the face loop.
                # We can't set the color until after all of the faces are made,
                # So we throw it all into a dictionary and brute-force it later.
                # v_color = wmo_read_color(color_list[v], 'CImVector')
                # colors[vert.index] = v_color
            try:
                if exampleFaceSet == False:
                    face = bm.faces.new((
                        v_dict[face[0]],
                        v_dict[face[1]],
                        v_dict[face[2]]
                    ))
                    exampleFace = face
                    exampleFaceSet = True

                    if json_batches[i].get("flags") == 2:
                        mat_ID = json_batches[i].get("possibleBox2")[2]
                    else:
                        mat_ID = json_batches[i].get("materialID")

                    local_index = blender_object.data.materials.find(mat_dict[mat_ID].name)

                    if local_index == -1:
                        blender_object.data.materials.append(mat_dict[mat_ID])
                        face.material_index = blender_object.data.materials.find(mat_dict[mat_ID].name)
                    else:
                        face.material_index = local_index

                else:
                    face = bm.faces.new((
                        v_dict[face[0]],
                        v_dict[face[1]],
                        v_dict[face[2]]
                    ), exampleFace)

            except ValueError:
                pass

    if len(mesh_data.uv2) > 0:
        uv2_layer = bm.loops.layers.uv.new('UV2Map')

    bm.faces.ensure_lookup_table()

    face_list = [batch.faces for batch in batches]
    face_list = [face for sublist in face_list for face in sublist]

    for i, face in enumerate(face_list):
        for j, loop in enumerate(bm.faces[i].loops):
            loop[uv_layer].uv = mesh_data.uv[face[j] -1]
            if len(mesh_data.uv2) > 0:
                loop[uv2_layer].uv = mesh_data.uv2[face[j]-1]

    bm.verts.ensure_lookup_table()

    if len(color_list) > 0:
        for vert in bm.verts:
            for loop in vert.link_loops:
                # loop[vcols] = colors[vert.index]
                loop[vcols] = wmo_read_color(color_list[vert.index], 'CImVector')

    if merge_verts:
        before=len(bm.verts)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00001)
        removed = before - len(bm.verts)
        print(f"vertex deduplication cleaned {removed} of {before} verts from {blender_object.name}")

    bm.to_mesh(mesh)
    bm.free()
    bpy.context.view_layer.active_layer_collection.collection.objects.link(blender_object)
    blender_object.rotation_euler = [0, 0, 0]
    blender_object.rotation_euler.x = radians(90)
    return blender_object

# TL;DR:
# Step one: Repack OBJ into meshObject
# Step two: Repack meshObject into wmoGroups
# Step three: Generate blenderObjects from wmoGroups
class wmoGroup:
    def __init__(self):
        self.mesh_data = None

        # Pulled from mesh_batches
        self.face_offset = -1
        self.faces = []
        self.b_faces = []

        # Pulled from mesh_batches
        self.vert_offset = -1
        self.verts = []
        self.b_verts = []

        self.batch_count = -1
        self.group_offset = -1

        # A list of meshComponent objects
        self.mesh_batches = []
        # The renderBatches that map to the meshComponent objects
        self.json_batches = []
        self.json_group = None

        self.colors = []


def repack_wmo(**kwargs):
    container = kwargs.get("import_container")
    json_groups = container.json_config.get("groups")
    mesh_data = kwargs.get("mesh_data")

    groups = []

    offset = 0

    for group in json_groups:
        g_batches = group.get("renderBatches", [])
        g_length = len(g_batches)

        if g_length > 0:
            g_slice = slice(offset, offset + g_length)
            wmo_group = wmoGroup()

            wmo_group.json_group = group
            wmo_group.json_batches = g_batches
            wmo_group.mesh_batches = mesh_data.components[g_slice]
            wmo_group.batch_count = g_length

            wmo_group.mesh_data = mesh_data
            wmo_group.colors = group.get("vertexColours", [])

            groups.append(wmo_group)

            offset += g_length
            wmo_group.group_offset = offset

    return groups

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
    '''Essentially a straight rip from the add-on'''
    obj = meshObject()
    meshIndex = -1

    # when there are faces that end with \
    # it means they are multiline-
    # since we use xreadline we cant skip to the next line
    # so we need to know whether
    context_multi_line = b''

    with open(mesh_path, 'rb') as f:
        for line in f:
            line_split = line.split()

            if not line_split:
                continue

            line_start = line_split[0]

            if len(line_split) == 1 and not context_multi_line and line_start != b'end':
                print("WARNING, skipping malformatted line: %s" % line.decode('UTF-8', 'replace').rstrip())
                continue

    # TODO: Replace with a more robust port of the ImportObj add-on's process
    with open(mesh_path, 'rb') as f:
        f_count = 0
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
                f_count += 1
            elif line_start == b'g':
                meshIndex += 1
                obj.components.append(meshComponent())
                obj.components[meshIndex].name = line_split[1].decode('utf-8')
            elif line_start == b'usemtl':
                obj.components[meshIndex].usemtl = line_split[1].decode('utf-8')
    # print(f_count)
    return obj

def import_obj(file, directory, reuse_mats, name_override, merge_verts, import_container, **kwargs):
    if bpy.ops.object.select_all.poll():
        bpy.ops.object.select_all(action='DESELECT')

    if name_override:
        mesh_name = name_override
    else:
        mesh_name = os.path.splitext(file)[0]

    mesh_data = initialize_mesh(os.path.join(directory, file))

    newMesh = bpy.data.meshes.new(mesh_name)
    newMesh.use_auto_smooth = True
    newMesh.auto_smooth_angle = radians(60)

    newObj = bpy.data.objects.new(mesh_name, newMesh)

    newObj.WBJ.source_asset = file
    newObj.WBJ.source_directory = directory
    newObj.WBJ.initialized = True

    bm = bmesh.new()
    output_meshes = []

    if import_container.wmo:
        config = import_container.json_config
        json_mats = config.get("materials")
        groups = config.get("groups")
        used_mats = set()

        wmo_groups = repack_wmo(import_container=import_container, groups=groups, mesh_data=mesh_data, config=config)

        mat_dict = {}
        for i, mat in enumerate(json_mats):
            mat = bpy.data.materials.new(name=mesh_name + "_mat_" + str(i))
            mat.use_nodes = True
            mat_name = mat.name
            mat_dict[i] = mat

        objects = []

        for group in wmo_groups:
            bl_obj = setup_blender_object(name=mesh_name, group=group, mesh_data=mesh_data, mat_dict=mat_dict, merge_verts=merge_verts)
            objects.append(bl_obj)

        return objects

    for i, v in enumerate(mesh_data.verts):
        vert = bm.verts.new(v)
        vert.normal = mesh_data.normals[i]

    bm.verts.ensure_lookup_table()
    bm.verts.index_update()

    group_faces = []

    for i, component in enumerate(mesh_data.components):
        create_mat = True
        exampleFaceSet = False
        mat_name = mesh_name + "_" + component.name + "_mat"
        fallback_name = os.path.splitext(file)[0] + "_" + component.name + "_mat"

        if reuse_mats:
            for bl_mat in bpy.data.materials:
                if bl_mat.name == mat_name:
                    mat = bl_mat
                    create_mat = False
                    break

                elif bl_mat.name == fallback_name:
                    mat = bl_mat
                    create_mat = False
                    break

        if create_mat:
            if not import_container.wmo:
                mat = bpy.data.materials.new(name=mat_name)
                mat.use_nodes = True
                mat_name = mat.name
                newObj.data.materials.append(mat)

        for face in component.faces:
            try:
                if exampleFaceSet == False:
                    face = bm.faces.new((
                        bm.verts[face[0] - 1],
                        bm.verts[face[1] - 1],
                        bm.verts[face[2] - 1]
                    ))
                    bm.faces.ensure_lookup_table()

                    bm.faces[-1].material_index = newObj.data.materials.find(mat_name)

                    bm.faces[-1].smooth = True
                    exampleFace = bm.faces[-1]
                    exampleFaceSet = True
                else:
                    ## Use example face if set to speed up material copy!
                    face = bm.faces.new((
                        bm.verts[face[0] - 1],
                        bm.verts[face[1] - 1],
                        bm.verts[face[2] - 1]
                    ), exampleFace)

                group_faces.append(face)

            except ValueError:
                # sometimes there are duplicate faces. Spot checking these,
                # the duplicates tend to be the same as a previous, except
                # with a vert order of (2,1,3) instead of (1,2,3), which
                # gives the duplicate face the opposite normal of the one
                # it is duplicating. We're pretty sure these are used for
                # cloaks and other double-sided things, since the WoW engine
                # doesn't believe in double-sided polys. There may be some
                # situations where there's something different going on,
                # and we'd really like to find/investigate those if they
                # exist, but for now, just ignoring duplicate faces will
                # stop the addon from crashing, with no apparent downsides.
                pass

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

    # needed to have a mesh before we can create vertex groups, so do that now
    # FIXME: Can we do this without doing bm.to_mesh first?
    for i, component in enumerate(mesh_data.components):
        vg = newObj.vertex_groups.new(name=f"{component.name}")
        vg.add(list(component.verts), 1.0, "REPLACE")

    ## Rotate object the right way
    newObj.rotation_euler = [0, 0, 0]
    newObj.rotation_euler.x = radians(90)

    # Defaults to main collection if no collection exists.
    bpy.context.view_layer.active_layer_collection.collection.objects.link(newObj)
    # newObj.select_set(True)

    return newObj
