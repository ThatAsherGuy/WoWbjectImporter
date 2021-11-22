
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

import bmesh
import bpy
import bpy.props
from mathutils import Vector

import json

from math import radians
from pathlib import Path
from typing import (Any, Dict, List, Optional, Set, cast)
import dataclasses


from .lookup_funcs import wmo_read_color, wmo_read_group_flags
from .node_groups import do_wmo_combiner, get_utility_group
from .preferences import WoWbject_ObjectProperties, get_prefs
from .wbjtypes import JsonWmoGroup, JsonWmoMetadata, JsonWmoRenderBatches


# FIXME: Which of these should be general, and which wmo-specific?
@dataclasses.dataclass
class MeshComponent:
    usemtl: str = ""  # FIXME: better default values
    name: str = ""
    verts: Set[float] = dataclasses.field(default_factory=set)
    faces: List[int] = dataclasses.field(default_factory=list)
    uv: List[float] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class MeshObject:
    usemtl: str = ""
    mtlfile: str = ""
    name: str = ""
    verts: List[float] = dataclasses.field(default_factory=list)
    faces: List[int] = dataclasses.field(default_factory=list)
    normals: List[float] = dataclasses.field(default_factory=list)
    uv: List[float] = dataclasses.field(default_factory=list)
    uv2: List[float] = dataclasses.field(default_factory=list)
    uv3: List[float] = dataclasses.field(default_factory=list)
    components: List[MeshComponent] = dataclasses.field(default_factory=list)


# TL;DR:
# Step one: Repack OBJ into meshObject
# Step two: Repack meshObject into wmoGroups
# Step three: Generate blenderObjects from wmoGroups
@dataclasses.dataclass
class wmoGroup:
    # FIXME: Is the Optional[] bit needed on some of these?
    mesh_data: Optional[MeshObject] = None
    mesh_batches: List[MeshComponent] = dataclasses.field(default_factory=list)

    json_group: Optional[JsonWmoGroup] = None
    group_offset: int = -1

    json_batches: JsonWmoRenderBatches = dataclasses.field(default_factory=list)
    batch_count: int = -1

    colors: List[List[int]] = dataclasses.field(default_factory=list)


# FIXME: return type
def import_wmo(context: bpy.types.Context, filepath: str, reuse_mats: bool, base_shader: str, op_args: Dict[str, Any]) -> None:
    '''
    The pre-sorting and initializing function called by the import operator.
    Most of the actual data-handling is handled by an import_container object.
    '''

    file = Path(filepath)
    name_override = op_args.get("name_override")

    # if do_search:
    if file.with_suffix(".json").exists():
        with file.with_suffix(".json").open() as p:
            # FIXME: error handling here
            json_config = json.load(p)
    else:
        # FIXME: user-facing error handling
        print(f"failed to load metadata from '{file.with_suffix('.json')}, can't continue")
        return

    if not json_config:
        print(f"failed to load metadata file {file.with_suffix('.json')}")
        return

    # to get the type right and not have it be a union with 'None' forever,
    # we assign to itself with a cast.
    # FIXME: Is there a better way?
    json_config = cast(JsonWmoMetadata, json_config)

    if name_override:
        basename = name_override
    else:
        basename = file.stem

    print(f"importing using base name: {basename}")


    # START def do_setup(self, files, directory, op_args, **kwargs):
    if True:
        # START def setup_json_data(self, **kwargs):
        if ".wmo" not in json_config["fileName"]:
            print("ERROR: trying to import a non-WMO file")
            return
        # END setup_json_data

        # START def setup_bl_object(self, progress):
        # END -- tail call to import_obj

        # START def import_obj(file, directory, reuse_mats, name_override, merge_verts, make_quads, use_collections, import_container, progress, **kwargs):
        if True:
            # FIXME: Is the poll needed? Is it even valid? select_all is a function?
            if bpy.ops.object.select_all.poll():
                bpy.ops.object.select_all('INVOKE_DEFAULT', False, action='DESELECT')

            print("Reading OBJ File")

            # START def initialize_mesh(mesh_path: str):
            mesh_data = MeshObject()
            meshIndex = -1

            # TODO: Replace with a more robust port of the ImportObj add-on's process
            # FIXME: what -is- the right encoding for obj files? Can we make this
            # read as utf-8 or ascii instead?
            with file.open('rb') as f:
                f_count = 0
                for line in f:
                    line_split = line.split()
                    if not line_split:
                        continue
                    line_start = line_split[0]
                    if line_start == b'mtllib':
                        mesh_data.mtlfile = str(line_split[1])
                    elif line_start == b'v':
                        # FIXME: replace all the things like this with proper
                        # vec2/vec3/vec4 tuples
                        mesh_data.verts.append(tuple([float(v) for v in line_split[1:]]))
                    elif line_start == b'vn':
                        mesh_data.normals.append(tuple([float(v) for v in line_split[1:]]))
                    elif line_start == b'vt3':
                        mesh_data.uv3.append(tuple([float(v) for v in line_split[1:]]))
                    elif line_start == b'vt2':
                        if not line_split[1] == b'undefined':
                            mesh_data.uv2.append(tuple([float(v) for v in line_split[1:]]))
                        else:
                            mesh_data.uv2.append((0.0, 0.0))
                    elif line_start == b'vt':
                        mesh_data.uv.append(tuple([float(v) for v in line_split[1:]]))
                    elif line_start == b'f':
                        line_split = line_split[1:]
                        fv = [int(v.split(b'/')[0]) for v in line_split]
                        mesh_data.components[meshIndex].faces.append((fv[0], fv[1], fv[2]))
                        mesh_data.components[meshIndex].verts.update([i - 1 for i in fv])
                        f_count += 1
                    elif line_start == b'g':
                        meshIndex += 1
                        mesh_data.components.append(MeshComponent())
                        mesh_data.components[meshIndex].name = line_split[1].decode('utf-8')
                    elif line_start == b'usemtl':
                        mesh_data.components[meshIndex].usemtl = line_split[1].decode('utf-8')
            # END INLINE: initialize_mesh

            # FIXME: Can I do this in a way without a cast?
            newMesh = bpy.data.meshes.new(basename)
            newMesh.use_auto_smooth = True
            newMesh.auto_smooth_angle = radians(60)


            # FIXME: Not sure how to annotate the dynamic attribute here
            newObj = bpy.data.objects.new(basename, newMesh)
            WBJ = cast(WoWbject_ObjectProperties, newObj.WBJ)

            # FIXME: Not sure how to type annotate the props to make these not
            # complain? But should be possible?
            WBJ.source_asset = str(file.name)
            WBJ.source_directory = str(file.parent)
            WBJ.initialized = True

            # if import_container.wmo:
            json_mats = json_config["materials"]
            json_groups = json_config["groups"]

            # START def repack_wmo(import_container, groups: dict, mesh_data: meshObject, config: dict):
            groups: List[wmoGroup] = []
            offset = 0

            flat_colors: List[List[int]] = [[], [], []]

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
                    groups.append(wmo_group)

                    vcolors = group.get("vertexColours", [])
                    last_color = g_batches[-1].get("lastVertex", -1) + 1

                    vertex_count = 0
                    for comp in wmo_group.mesh_batches:
                        vertex_count += len(comp.verts)

                    if len(vcolors) == 2:
                        flat_colors[0] += vcolors[0][0:last_color]
                        flat_colors[1] += vcolors[1][0:last_color]
                    elif len(vcolors) == 1:
                        flat_colors[0] += vcolors[0][0:last_color]
                        flat_colors[1] += [0 for _ in vcolors[0]]
                    elif len(vcolors) == 0:
                        if vertex_count > 0:
                            flat_colors[0] += [0 for _ in range(vertex_count)]
                            flat_colors[1] += [0 for _ in range(vertex_count)]

                    wmo_group.colors = flat_colors

                    offset += g_length
                    wmo_group.group_offset = offset

                else:
                    wmo_group = wmoGroup()
                    wmo_group.json_group = group
                    wmo_group.batch_count = 0
                    groups.append(wmo_group)

                    err_gname = group.get("groupName", "")
                    err_gdesc = group.get("groupDescription", "")
                    print(f"{err_gname} {err_gdesc} Batchless")

                    err_numbatch = group.get("numPortals", "")
                    print(f"numPortals: {err_numbatch}")

                    err_numbatch = group.get("numBatchesA", "")
                    print(f"numBatchesA: {err_numbatch}")

                    err_numbatch = group.get("numBatchesB", "")
                    print(f"numBatchesB: {err_numbatch}")

                    err_numbatch = group.get("numBatchesC", "")
                    print(f"numBatchesC: {err_numbatch}")

            wmo_groups = groups
            # END repack_wmo

            # FIXME: Is mat_dict a dict or a list?
            mat_dict: Dict[int, bpy.types.Material] = {}

            for i, mat in enumerate(json_mats):
                mat = bpy.data.materials.new(name=basename + "_mat_" + str(i))
                mat.use_nodes = True
                mat_dict[i] = mat

            objects: List[bpy.types.Object] = []

            steps = len(wmo_groups)
            print(f"working on {steps} groups")

            print("Generating meshes")
            for i, group in enumerate(wmo_groups):
                sub = group.json_group.get("groupName", "")
                print(f"Constructing object {i + 1}/{steps} | {sub}")

                # FIXME: revisit -- should inline this probably, too
                bl_obj = wmo_setup_blender_object(
                    # FIXME: make group num into metadata
                    base_name=f"{i:03d}_{basename}",
                    group=group,
                    mesh_data=mesh_data,
                    mat_dict=mat_dict,
                    # merge_verts=merge_verts,
                    # make_quads=make_quads,
                    # use_collections=use_collections
                )

                if bl_obj:
                    objects.append(bl_obj)

            # END initialize_mesh (maybe?)
        # END import_obj

        print("leaving substeps")

        print("generating materials")

        # START def setup_materials(self):
        # START def do_wmo_mats(**kwargs):
        mats = json_config["materials"]

        configured_mats: Set[bpy.types.Material] = set()

        # for obj in container.bl_obj:
        for obj in objects:
            # FIXME: give MaterialSlot an __iter__  method instead of the typecast?
            for slot in obj.material_slots:
                mat_number = slot.material.name.split('_')[-1]
                if '.' in mat_number:
                    mat_number = mat_number.split('.')[0]
                mat = mats[int(mat_number)]

                # next bits simplified from node_groups.py:get_tex
                # tex1 = get_tex(container, str(mat.get("texture1")))
                tex1: Optional[bpy.types.Image] = None
                texnum = mat['texture1']
                texfilename = f"{texnum}.png"
                texfile = file.parent / texfilename

                if texnum > 0 and texfile.exists():
                    if texfilename in bpy.data.images:
                        tex1 = bpy.data.images[texfilename]
                    else:
                        tex1 = bpy.data.images.load(str(texfile.resolve()))
                        tex1.alpha_mode = 'CHANNEL_PACKED'

                # tex2 = get_tex(container, str(mat.get("texture2")))
                tex2: Optional[bpy.types.Image] = None
                texnum = mat.get('texture2')
                texfilename = f"{texnum}.png"
                texfile = file.parent / texfilename

                if texnum > 0 and texfile.exists():
                    if texfilename in bpy.data.images:
                        tex2 = bpy.data.images[texfilename]
                    else:
                        tex2 = bpy.data.images.load(str(texfile.resolve()))
                        tex2.alpha_mode = 'CHANNEL_PACKED'

                # tex3 = get_tex(container, str(mat.get("texture3")))
                tex3: Optional[bpy.types.Image] = None
                texnum = mat.get('texture3')
                texfilename = f"{texnum}.png"
                texfile = file.parent / texfilename
                if texnum > 0 and texfile.exists():
                    if texfilename in bpy.data.images:
                        tex3 = bpy.data.images[texfilename]
                    else:
                        tex3 = bpy.data.images.load(str(texfile.resolve()))
                        tex3.alpha_mode = 'CHANNEL_PACKED'

                tex_list = [tex1, tex2, tex3]

                bl_mat = slot.material
                tree = bl_mat.node_tree
                nodes = tree.nodes

                if bl_mat in configured_mats:
                    continue

                shader: Optional[bpy.types.Node] = None
                out_node = None
                # FIXME: give Nodes an __iter__ instead of using this typecast?
                for node in nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        shader = cast(bpy.types.ShaderNodeBsdfPrincipled, node)
                        shader.inputs["Roughness"].default_value = 1.0

                    if node.type == 'OUTPUT_MATERIAL':
                        out_node = node

                    if shader and out_node:
                        break

                if not out_node:
                    out_node = nodes.new('ShaderNodeOutputMaterial')

                if not shader:
                    # FIXME
                    print("DO LATER")

                # FIXME: What's this for?
                if shader:
                    nodes.remove(shader)

                # FIXME: wtf is this base shader thing actually doing?
                prefs = get_prefs()
                base = prefs.get_base_shader(base_shader)

                if base == 'Experimental':
                    shader = nodes.new('ShaderNodeGroup')
                    shader.node_tree = get_utility_group(name="TheStumpFargothHidTheRingIn")
                elif (base != ''):
                    shader = cast(bpy.types.ShaderNode, nodes.new(base))
                else:
                    shader = nodes.new("ShaderNodeEmission")

                tree.links.new(shader.outputs[0], out_node.inputs[0])

                baseColor = nodes.new('ShaderNodeRGB')
                baseColor.location += Vector((-1200.0, 400.0))
                baseColor.outputs["Color"].default_value = wmo_read_color(
                    mat["color2"], 'CArgb')
                baseColor.label = 'BASE COLOR'

                tex_nodes: List[bpy.types.ShaderNodeTexImage] = []

                for i, tex in enumerate(tex_list):
                    if tex:
                        tex_node = nodes.new('ShaderNodeTexImage')
                        tex_node.image = tex
                        tex_node.location += Vector((-1200.0, (200 - i * 300.0)))
                        tex_node.label = ("TEXTURE_%s" % str(i + 1))
                        tex_nodes.append(tex_node)

                ambColor = wmo_read_color(json_config["ambientColor"], 'CImVector')


                do_wmo_combiner(
                    tex_nodes=tex_nodes,
                    bl_mat=bl_mat,
                    shader_out=shader,
                    mat_info=mat,
                    ambient=ambColor,
                )

                configured_mats.add(bl_mat)
            # END do_wmo_mats
            # END setup_materials


# FIXME: Legit needs fewer arguments
def wmo_setup_blender_object(base_name: str, group: wmoGroup,
                             mesh_data: MeshObject, mat_dict: Dict[int, bpy.types.Material],
                             merge_verts: bool = False, make_quads: bool = False,
                             use_collections: bool = True) -> Optional[bpy.types.Object]:
    if group.batch_count < 1:
        return None

    json_group = group.json_group

    full_name = base_name + "_" + json_group.get("groupName", "section")
    collection_name = json_group.get("groupDescription", None)
    flags = wmo_read_group_flags(json_group.get("flags", 0))

    mesh = bpy.data.meshes.new(base_name)
    mesh.use_auto_smooth = True
    mesh.auto_smooth_angle = radians(60)

    newObj = bpy.data.objects.new(full_name, mesh)
    WBJ = cast(WoWbject_ObjectProperties, newObj.WBJ)
    WBJ.wow_model_type = 'WMO'
    WBJ.initialized = True

    # if "INTERIOR" in flags:
    #     newObj.pass_index = 1
    if 'INTERIOR' in flags and 'EXTERIOR' in flags:
        WBJ.wmo_lighting_type = 'TRANSITION'
    elif 'INTERIOR' in flags:
        WBJ.wmo_lighting_type = 'INTERIOR'
    elif 'EXTERIOR' in flags:
        WBJ.wmo_lighting_type = 'EXTERIOR'
    else:
        WBJ.wmo_lighting_type = 'UNLIT'


    bm = bmesh.new()
    # vcols = bm.loops.layers.color.new("vcols")
    uv_layer = bm.loops.layers.uv.new()

    batches = group.mesh_batches
    json_batches = group.json_batches
    color_list = [clist for clist in group.colors if len(clist) > 0]
    do_colors = True if len(color_list) > 0 else False

    colors = {}
    v_dict: Dict[int, bmesh.types.BMVert] = {}
    # uv_dict = {}

    for i, batch in enumerate(batches):
        exampleFaceSet = False
        # cull_list = []
        for face in batch.faces:
            for v in face:
                # if type(v_dict.get(v)) == bmesh.types.BMVert:
                #     vert = v_dict[v]
                # else:
                #     vert = bm.verts.new(mesh_data.verts[v - 1])
                #     v_dict[v] = vert
                if v in v_dict:
                    vert = v_dict[v]
                else:
                    xx = mesh_data.verts[v - 1]
                    vert = bm.verts.new(mesh_data.verts[v - 1])
                    v_dict[v] = vert

                # The data layer for vertex color is actually in the face loop.
                # We can't set the color until after all of the faces are made,
                # So we throw it all into a dictionary and brute-force it later.
                # Note: There can theoretically be three sets of vertex colors.
                if do_colors:
                    if type(color_list[0]) == list:
                        v_color = []
                        for sublist in color_list:
                            v_color.append(wmo_read_color(sublist[v - 1], 'CImVector'))
                    else:
                        v_color = wmo_read_color(color_list[v - 1], 'CImVector')

                    colors[vert] = v_color

            try:
                if exampleFaceSet == False:
                    bface = bm.faces.new((
                        v_dict[face[0]],
                        v_dict[face[1]],
                        v_dict[face[2]]
                    ))
                    exampleFace = bface
                    exampleFaceSet = True

                    if json_batches[i].get("flags") == 2:
                        mat_ID = json_batches[i].get("possibleBox2")[2]
                    else:
                        mat_ID = json_batches[i].get("materialID")

                    # vvvv FIXME vvvv
                    local_index = cast(bpy.types.Mesh, newObj.data).materials.find(
                        mat_dict[mat_ID].name)

                    if local_index == -1:
                        newObj.data.materials.append(mat_dict[mat_ID])
                        bface.material_index = newObj.data.materials.find(
                            mat_dict[mat_ID].name)
                    else:
                        bface.material_index = local_index

                else:
                    bface = bm.faces.new((
                        v_dict[face[0]],
                        v_dict[face[1]],
                        v_dict[face[2]]
                    ), exampleFace)

            except ValueError as err:
                v1 = bm.verts.new(mesh_data.verts[face[0] - 1])
                v2 = bm.verts.new(mesh_data.verts[face[1] - 1])
                v3 = bm.verts.new(mesh_data.verts[face[2] - 1])

                colors[v1] = colors[v_dict[face[0]]]
                colors[v2] = colors[v_dict[face[1]]]
                colors[v3] = colors[v_dict[face[2]]]

                if exampleFaceSet == False:
                    bface = bm.faces.new((v1, v2, v3))
                    exampleFace = bface
                    exampleFaceSet = True

                    if json_batches[i].get("flags") == 2:
                        mat_ID = json_batches[i].get("possibleBox2")[2]
                    else:
                        mat_ID = json_batches[i].get("materialID")

                    local_index = newObj.data.materials.find(mat_dict[mat_ID].name)

                    if local_index == -1:
                        newObj.data.materials.append(mat_dict[mat_ID])
                        bface.material_index = newObj.data.materials.find(
                            mat_dict[mat_ID].name)
                    else:
                        bface.material_index = local_index
                else:
                    bface = bm.faces.new((v1, v2, v3), exampleFace)

                err_detail = (
                    f"Duplicate Face: {face[0]}/{face[0]}/{face[0]} {face[1]}/{face[1]}/{face[1]} {face[2]}/{face[2]}/{face[2]}")
                print(err_detail)
                pass

    if len(mesh_data.uv2) > 0:
        uv2_layer = bm.loops.layers.uv.new('UV2Map')

    if len(mesh_data.uv3) > 0:
        uv3_layer = bm.loops.layers.uv.new('UV3Map')

    bm.faces.ensure_lookup_table()

    face_list = [batch.faces for batch in batches]
    face_list = [face for sublist in face_list for face in sublist]

    for i, face in enumerate(face_list):
        for j, loop in enumerate(bm.faces[i].loops):
            loop[uv_layer].uv = mesh_data.uv[face[j] - 1]

            if len(mesh_data.uv2) > 0:
                loop[uv2_layer].uv = mesh_data.uv2[face[j] - 1]

            if len(mesh_data.uv3) > 0:
                loop[uv3_layer].uv = mesh_data.uv3[face[j] - 1]

    # bm.verts.ensure_lookup_table()

    if len(color_list) > 0:
        vcols = []
        for i, clist in enumerate(color_list):
            vcols.append(bm.loops.layers.color.new(f"vcols_{i}"))

        for i, vert in enumerate(bm.verts):
            for loop in vert.link_loops:
                for i, vcol_list in enumerate(vcols):
                    loop[vcol_list] = colors[vert][i]

    if merge_verts:
        st = recursive_remove_doubles(bm, verts=bm.verts, dist=0.00001)
        print(
            f"{newObj.name}:"
            f" {st['removed_verts']} of {st['start_verts']} verts removed"
            f" in {st['merge_passes']} passes"
            f" in {st['total_time']:1.6f}s"
            f" ({st['end_verts']} verts remain)"
        )

    bm.to_mesh(mesh)
    bm.free()

    newObj.rotation_euler = [0, 0, 0]
    newObj.rotation_euler.x = radians(90)

    if use_collections and collection_name:
        if collection_name in bpy.data.collections:
            collection = bpy.data.collections[collection_name]
        else:
            collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(collection)

        collection.objects.link(newObj)
    else:
        bpy.context.view_layer.active_layer_collection.collection.objects.link(
            newObj)


    if make_quads:
        st = tris_to_quads(newObj, 5.0)
        print(
            f"{newObj.name}:"
            f" {st['removed_faces']} of {st['start_faces']} faces removed"
            f" in {st['total_time']:1.6f}s"
            f" ({st['end_faces']} faces remain)"
        )

    # Give us a reasonable origin on everything
    bpy.ops.object.select_all('INVOKE_DEFAULT', False, action='DESELECT')
    newObj.select_set(True)
    bpy.ops.object.origin_set('INVOKE_DEFAULT', False, type='ORIGIN_GEOMETRY', center='MEDIAN')
    bpy.ops.object.shade_smooth('INVOKE_DEFAULT', False)

    return newObj