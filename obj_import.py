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


def import_obj(file, directory, reuse_mats, name_override, **kwargs):
    if bpy.ops.object.select_all.poll():
        bpy.ops.object.select_all(action='DESELECT')

    if name_override:
        mesh_name = name_override
    else:
        mesh_name = file.split('.')[0]

    mesh_data = initialize_mesh(os.path.join(directory, file))

    newMesh = bpy.data.meshes.new(mesh_name)
    newMesh.use_auto_smooth = True
    newMesh.auto_smooth_angle = 1.0472

    newObj = bpy.data.objects.new(mesh_name, newMesh)

    newObj.WBJ.source_asset = file
    newObj.WBJ.source_directory = directory
    newObj.WBJ.initialized = True

    bm = bmesh.new()

    for i, v in enumerate(mesh_data.verts):
        vert = bm.verts.new(v)
        vert.normal = mesh_data.normals[i]

    bm.verts.ensure_lookup_table()
    bm.verts.index_update()

    for i, component in enumerate(mesh_data.components):
        create_mat = True
        exampleFaceSet = False
        mat_name = mesh_name + "_" + component.name + "_mat"
        fallback_name = file.split('.')[0] + "_" + component.name + "_mat"

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
            mat = bpy.data.materials.new(name=mat_name)
            mat.use_nodes = True
            mat_name = mat.name

        newObj.data.materials.append(mat)

        try:
            for face in component.faces:
                if exampleFaceSet == False:
                    bm.faces.new((
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
                    bm.faces.new((
                        bm.verts[face[0] - 1],
                        bm.verts[face[1] - 1],
                        bm.verts[face[2] - 1]
                    ), exampleFace)

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
    for i, component in enumerate(sorted(mesh_data.components, key=lambda m: m.name.lower())):
        vg = newObj.vertex_groups.new(name=f"{component.name}")
        vg.add(list(component.verts), 1.0, "REPLACE")

    ## Rotate object the right way
    newObj.rotation_euler = [0, 0, 0]
    newObj.rotation_euler.x = radians(90)

    # Defaults to main collection if no collection exists.
    bpy.context.view_layer.active_layer_collection.collection.objects.link(newObj)
    # newObj.select_set(True)

    return newObj
