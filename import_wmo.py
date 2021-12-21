
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
from mathutils import Vector, Euler

import dataclasses
import json
from math import radians
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, cast

from .lookup_funcs import wmo_read_color, wmo_read_group_flags
from .node_groups import do_wmo_combiner, get_utility_group
from .preferences import WoWbject_ObjectProperties, get_prefs
from .wbjtypes import JsonWmoGroup, JsonWmoMetadata, JsonWmoRenderBatch, Vec2, Vec3, Vec4, Tri, iColor3, iColor4, fColor3, fColor4

from .vendor import mashumaro
from .utilities import recursive_remove_doubles, tris_to_quads

# FIXME: Which of these should be general, and which wmo-specific?
@dataclasses.dataclass
class ImportedSubmesh:
    """
    An individual object group from within an obj. There is one of these
    per obj object group.
    """
    mtlname: Optional[str] = None
    name: Optional[str] = None
    # FIXME: should this be 1-based like other obj things?
    vert_indexes: Set[int] = dataclasses.field(default_factory=set)
    """set of vertex indexes (0-based!) used in group"""
    faces: List[Tri] = dataclasses.field(default_factory=list)
    """list of faces in group, using vertex indexes (1-based)"""
    # uv: List[Vec2] = dataclasses.field(default_factory=list)  # not used?


@dataclasses.dataclass
class ImportedMesh:
    """
    Raw data as read from an obj file, as exported from wow.export. Includes
    vertexes, faces (as indexes into vertex list), normals, UV maps, etc for
    the entire WMO, root + groups
    """
    usemtl: str = ""
    mtlfile: str = ""
    name: Optional[str] = None
    verts: List[Vec3] = dataclasses.field(default_factory=list)
    """vertexes (x,y,z) - 1-indexed when referenced by 'faces' field"""
    # Pretty sure 'faces' isn't needed, because all the faces are defined in
    # the individual groups?
    # faces: List[Tri] = dataclasses.field(default_factory=list)
    # """faces (v1, v2, v3) - right-handed; indexes into 'verts' (1-based)"""
    normals: List[Vec3] = dataclasses.field(default_factory=list)
    """vertex normals (x, y, z) - might not be unit vectors"""
    uv: List[Vec2] = dataclasses.field(default_factory=list)
    uv2: List[Vec2] = dataclasses.field(default_factory=list)
    uv3: List[Vec2] = dataclasses.field(default_factory=list)
    submeshes: List[ImportedSubmesh] = dataclasses.field(default_factory=list)



@dataclasses.dataclass(init=False)
class WmoGroup:
    """
    An individual group from within a WMO. There is one of these per WMO
    group. This should (maybe? hopefully?) contain all the info needed to
    render a single group.
    """

    # needed because it has our actual vert coordinates and such
    imported_mesh: ImportedMesh
    # """the full obj data for the entire import"""

    group_metadata: JsonWmoGroup
    """the metadata, from json, for this specific WMO group"""

    # group_offset: int = -1

    batch_count: int = -1
    imported_submeshes: List[ImportedSubmesh] = dataclasses.field(default_factory=list)
    batches_metadata: List[JsonWmoRenderBatch] = dataclasses.field(default_factory=list)
    vertex_colors: List[List[int]] = dataclasses.field(default_factory=list)


# originally "initialize_mesh"
# format description: https://en.wikipedia.org/wiki/Wavefront_.obj_file
# TODO: Replace with a more robust port of the ImportObj add-on's process
def read_obj(file: Path) -> ImportedMesh:
    print(f"Importing obj data from {file}")
    # START def initialize_mesh(mesh_path: str):
    imported_mesh = ImportedMesh()
    groupIndex: int = -1

    # FIXME: what -is- the right encoding for obj files? Can we make this
    # read as utf-8 or ascii instead?
    with file.open('rb') as f:
        for line in f:
            line_split = line.split()
            if not line_split:
                continue
            line_start = line_split[0]

            # actual obj can have multiple mtllib files, but wow.export only
            # exports one. We probably don't need this though.
            if line_start == b'mtllib':
                imported_mesh.mtlfile = str(line_split[1])

            # Vertexes
            elif line_start == b'v':
                imported_mesh.verts.append(
                    cast(Vec3, tuple([float(v) for v in line_split[1:4]])))

            # Vertex Normals
            elif line_start == b'vn':
                imported_mesh.normals.append(
                    cast(Vec3, tuple([float(v) for v in line_split[1:4]])))

            # UV/texture coordinates (3rd set)
            elif line_start == b'vt3':
                imported_mesh.uv3.append(
                    cast(Vec2, tuple([float(v) for v in line_split[1:3]])))

            # UV/texture coordinates (2nd set)
            elif line_start == b'vt2':
                # FIXME: What is the 'undefined' bit about?
                if not line_split[1] == b'undefined':
                    imported_mesh.uv2.append(
                        cast(Vec2, tuple([float(v) for v in line_split[1:3]])))
                else:
                    imported_mesh.uv2.append((0.0, 0.0))

            # UV/texture coordinates (1st set)
            elif line_start == b'vt':
                imported_mesh.uv.append(
                    cast(Vec2, tuple([float(v) for v in line_split[1:3]])))

            # Faces -- 3 fields (for WoW), in the format of vertex/uv/normal
            elif line_start == b'f':
                if groupIndex < 0:
                    raise RuntimeError("obj file specifies faces before a face group")

                line_split = line_split[1:]
                # makes list from first element (vertex index) of each vertex
                fv = [int(v.split(b'/')[0]) for v in line_split]

                imported_mesh.submeshes[groupIndex].faces.append((fv[0], fv[1], fv[2]))
                imported_mesh.submeshes[groupIndex].vert_indexes.update([i - 1 for i in fv])

            # Object name
            elif line_start == b'o':
                imported_mesh.name = str(line_split[1])

            # Groups
            elif line_start == b'g':
                groupIndex += 1
                imported_mesh.submeshes.append(ImportedSubmesh())
                imported_mesh.submeshes[groupIndex].name = line_split[1].decode('utf-8')

            # Smooth shading
            # Materials
            elif line_start == b'usemtl':
                imported_mesh.submeshes[groupIndex].mtlname = line_split[1].decode('utf-8')

    total_verts = sum([len(g.vert_indexes) for g in imported_mesh.submeshes])
    total_faces = sum([len(g.faces) for g in imported_mesh.submeshes])
    print(f"Read {groupIndex + 1} groups, {total_verts} total verts and {total_faces} total faces")

    return imported_mesh



# FIXME: return type
def import_wmo(context: bpy.types.Context, filepath: str, reuse_mats: bool, base_shader: str, op_args: Dict[str, Any]) -> None:
    debug = True

    file = Path(filepath)
    name_override = op_args.get("name_override")

    print("loading json metadata")
    # if do_search:
    if not file.with_suffix(".json").exists():
        # FIXME: user-facing error handling
        raise RuntimeError(
            f"failed to load metadata from '{file.with_suffix('.json')}, can't continue")

    with file.with_suffix(".json").open() as p:
        # FIXME: error handling here
        metadata = json.load(p)

    if not metadata:
        raise RuntimeError(f"failed to load metadata file {file.with_suffix('.json')}")

    if name_override:
        basename = name_override
    else:
        basename = file.stem

    print(f"will be importing using base name: {basename}")

    # START def do_setup(self, files, directory, op_args, **kwargs):
    if True:
        # START def setup_json_data(self, **kwargs):
        if ".wmo" not in metadata["fileName"]:
            raise ValueError("import_wmo called to import a non-WMO file")

        try:
            metadata = JsonWmoMetadata.from_dict(metadata)  # type: ignore
        # FIXME: Not sure why pylance can't figure out the types here
        except mashumaro.exceptions.MissingField as e:
            raise RuntimeError(str(e))
        except mashumaro.exceptions.InvalidFieldValue as e:
            raise RuntimeError("invalid field value (not repeating)")
        # END setup_json_data

        # START def setup_bl_object(self, progress):
        # END -- tail call to import_obj

        # START def import_obj(file, directory, reuse_mats, name_override, merge_verts, make_quads, use_collections, import_container, progress, **kwargs):
        if True:
            # FIXME: Is the poll needed? Is it even valid? select_all is a function?
            if bpy.ops.object.select_all.poll():  # type: ignore
                bpy.ops.object.select_all('INVOKE_DEFAULT', False, action='DESELECT')

            print("Reading OBJ File")

            # START def initialize_mesh(mesh_path: str):
            imported_mesh = read_obj(file)

            # for i, group in enumerate(obj_data.groups):
            #     print(f"obj group {i} has {len(group.verts)} verts")

            # The blender object stuff is all done in wmo_setup_blender_object
            # right now, so don't need it here.
            if False:
                newMesh = bpy.data.meshes.new(basename)
                newMesh.use_auto_smooth = True
                newMesh.auto_smooth_angle = radians(60)

                newObj = bpy.data.objects.new(basename, newMesh)
                WBJ = cast(WoWbject_ObjectProperties, newObj.WBJ)  # type: ignore

                WBJ.source_file = str(file.name)
                WBJ.source_directory = str(file.parent)
                WBJ.initialized = True

            # START def repack_wmo(import_container, groups: dict, obj_data: meshObject, config: dict):

            # ? Why was this all the way up here? Seems only needed much further down?
            # offset = 0

            # not sure why we need the big flat vertex color list -- ask Asher,
            # if he reappears
            flat_colors: List[List[int]] = [[], [], []]

            # So, there's going to be more vertex colors than there are verts.
            # This is because the collision meshes (as definedd in MOBN and MOBR
            # chunks in the WMO) reference verts that are not actually included
            # in the OBJ export, but the vertex color data (from MOCV) includes
            # those verts, and is passed through unchanged.
            #
            # An extremely brief eyeball suggests that vertex colors for verts
            # which got elided have a vertex color of 4286545791 (0xff7f7f7f
            # (in abgr, I think)), which might be worth checking for as a
            # sanity check to make sure we're not off in our count somewhere.
            # This only applies to the first set of vertex colors.

            # A bunch of stuff for info/debugging
            if False:
                total_groups = -1   # Just for info/debugging
                total_batches = -1  # Just for info/debugging

                # For each WMO group (metadata group)
                for i, group in enumerate(metadata.groups):
                    total_groups += 1  # Just for info/debugging

                    # each group has a bunch of render batches. Each render batch
                    # has some set of verts/faces, and (I think) a single material.
                    for j, batch in enumerate(group.renderBatches):
                        # Stuff just for info purposes, not needed for building things
                        total_batches += 1
                        verts_in_metadata_batch = batch.lastVertex - batch.firstVertex + 1
                        obj_group_verts = len(imported_mesh.submeshes[total_batches].verts)
                        if debug:
                            print(
                                f"verts in json group {i:-2d} batch {j:-2d} (global {total_groups:-2d}, {total_batches:-3d}) = {verts_in_metadata_batch:-3d}     verts in obj group: {obj_group_verts}")

                        if verts_in_metadata_batch != obj_group_verts:
                            print(
                                f"WARNING: sanity check failed: unequal vert counts; verts in json group {i:-2d} batch {j:-2d} (global {total_batches:-3d}): {verts_in_metadata_batch:-3d}     verts in obj group: {obj_group_verts}")

                    # if len(group.vertexColours) == 0:
                    #     vcol_count = 0
                    # else:
                    #     vcol_count = len(group.vertexColours[0])


            wmo_groups: List[WmoGroup] = []

            # the obj is all the batches, each as a 'group' inside the obj,
            # which we will herein call submeshes. This counter lets us know
            # how far into the obj we currently need to be indexing.
            submesh_offset = 0

            for group_metadata in metadata.groups:
                wmo_group = WmoGroup()
                wmo_group.batch_count = len(group_metadata.renderBatches)

                if wmo_group.batch_count <= 0:
                    print(
                        f"{group_metadata.groupName} {group_metadata.groupDescription} has no render batches?")
                    print(f"numPortals: {group_metadata.numPortals}")
                    print(f"numBatchesA: {group_metadata.numBatchesA}")
                    print(f"numBatchesB: {group_metadata.numBatchesB}")
                    print(f"numBatchesC: {group_metadata.numBatchesC}")

                    wmo_groups.append(wmo_group)
                    continue

                # FIXME: Do we actually need all the metadata as a whole? Can
                # we split it up to make it easier to follow?
                wmo_group.group_metadata = group_metadata
                wmo_group.batches_metadata = group_metadata.renderBatches

                submesh_low = submesh_offset
                submesh_high = submesh_low + wmo_group.batch_count - 1

                batch_range = slice(submesh_low, submesh_high + 1)  # need + 1
                wmo_group.imported_mesh = imported_mesh

                # FIXME: Should we just make this a min/max value, rather than
                # the entire submesh range, since we have the full mesh
                # structure along for the ride anyhow?
                wmo_group.imported_submeshes = imported_mesh.submeshes[batch_range]

                # These are the vertex colors for the entire WMO group,
                # which consists of multiple submeshes/render batches.
                vcolors = group_metadata.vertexColours

                # The last vertex in the last batch. lastVertex defaults to
                # -1, so if there are no vertexes, count will be 0
                group_vertex_count = group_metadata.renderBatches[-1].lastVertex + 1

                # FIXME: Can/does this differ from the vertex count in
                # the json metadata?
                # for batch in wmo_group.import_submeshes:
                #     group_vertex_count += len(batch.verts)

                # if group_vertex_count != last_vertex:
                #     print(
                #         f"WARNING: vertex count mismatch: {group_vertex_count} != {last_vertex}")

                # Not sure why we're doing this, rather than just updating the
                # group.vertexColours struct in place, or copying/updating
                # to wmo_group.something   ... should we?
                if len(vcolors) == 2:
                    flat_colors[0] += vcolors[0][0:group_vertex_count]
                    flat_colors[1] += vcolors[1][0:group_vertex_count]
                elif len(vcolors) == 1:
                    flat_colors[0] += vcolors[0][0:group_vertex_count]
                    flat_colors[1] += [0 for _ in range(group_vertex_count)]
                elif len(vcolors) == 0:
                    if group_vertex_count > 0:
                        # FIXME: I think first group might need alpha = 1.0?
                        flat_colors[0] += [0 for _ in range(group_vertex_count)]
                        flat_colors[1] += [0 for _ in range(group_vertex_count)]

                # l1 = len(flat_colors[0])
                # l2 = len(flat_colors[1])

                # if debug:
                #     print(
                #         f"color1 count: {l1}   color2 count: {l2}   group vertex count: {group_vertex_count}")

                # if l1 != group_vertex_count:
                #     print(
                #         f"WARNING: vertex color count mismatch: {group_vertex_count} != {l1}")

                wmo_group.vertex_colors = flat_colors

                submesh_offset += wmo_group.batch_count
                # wmo_group.group_offset = submesh_offset

                wmo_groups.append(wmo_group)
            # END repack_wmo


            bl_materials: List[bpy.types.Material] = []

            for i, mat in enumerate(metadata.materials):
                mat = bpy.data.materials.new(name=f"{basename}_mat_{i}")
                mat.use_nodes = True
                bl_materials.append(mat)

            bl_objects: List[bpy.types.Object] = []

            steps = len(wmo_groups)
            print(f"working on {steps} groups")

            print("Generating meshes")
            for i, wmo_group in enumerate(wmo_groups):
                # sub = group.json_group.groupName or ""
                #### print(f"Constructing object {i + 1}/{steps} | {group.json_group.groupName}")

                # FIXME: revisit -- should inline this probably, too... maybe
                bl_obj = wmo_setup_blender_object(
                    # FIXME: make group num into metadata
                    base_name=f"{i:03d}_{basename}",
                    wmo_group=wmo_group,
                    bl_materials=bl_materials,
                    # merge_verts=merge_verts,
                    # make_quads=make_quads,
                    # use_collections=use_collections
                )

                if bl_obj:
                    bl_objects.append(bl_obj)

            # END initialize_mesh (maybe?)
        # END import_obj

        print("leaving substeps")

        print("generating materials")

        # START def setup_materials(self):
        # START def do_wmo_mats(**kwargs):

        configured_mats: Set[bpy.types.Material] = set()

        # for obj in container.bl_obj:
        for obj in bl_objects:
            # FIXME: give MaterialSlot an __iter__  method instead of the typecast?
            for slot in obj.material_slots:
                mat_number = slot.material.name.split('_')[-1]
                if '.' in mat_number:
                    mat_number = mat_number.split('.')[0]
                mat = metadata.materials[int(mat_number)]

                # next bits simplified from node_groups.py:get_tex
                # tex1 = get_tex(container, str(mat.get("texture1")))
                tex1: Optional[bpy.types.Image] = None
                texnum = mat.texture1
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
                texnum = mat.texture2
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
                texnum = mat.texture3
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
                    mat.color2, 'CArgb')
                baseColor.label = 'BASE COLOR'

                tex_nodes: List[bpy.types.ShaderNodeTexImage] = []

                for i, tex in enumerate(tex_list):
                    if tex:
                        tex_node = nodes.new('ShaderNodeTexImage')
                        tex_node.image = tex
                        tex_node.location += Vector((-1200.0, (200 - i * 300.0)))
                        tex_node.label = ("TEXTURE_%s" % str(i + 1))
                        tex_nodes.append(tex_node)

                ambColor = wmo_read_color(metadata.ambientColor, 'CImVector')

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
def wmo_setup_blender_object(base_name: str, wmo_group: WmoGroup,
                             bl_materials: List[bpy.types.Material],
                             merge_verts: bool = False, make_quads: bool = False,
                             use_collections: bool = True) -> Optional[bpy.types.Object]:
    if wmo_group.batch_count < 1:
        return None

    imported_mesh = wmo_group.imported_mesh
    group_submeshes = wmo_group.imported_submeshes
    metadata = wmo_group.group_metadata

    full_name = base_name + "_" + (metadata.groupName or "section")

    bl_mesh = bpy.data.meshes.new(base_name)
    bl_mesh.use_auto_smooth = True
    bl_mesh.auto_smooth_angle = radians(60)

    bl_obj = bpy.data.objects.new(full_name, bl_mesh)
    WBJ = cast(WoWbject_ObjectProperties, bl_obj.WBJ)  # type: ignore
    WBJ.wow_model_type = 'WMO'
    WBJ.initialized = True

    flags = wmo_read_group_flags(metadata.flags)  # FIXME: do we need a 0 default?
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

    # batches = group.imported_submeshes
    batches = wmo_group.batches_metadata

    # FIXME: I think we guarantee we have colors before calling here, so do we
    # need to check here?  (answer: yes, probably, when doing more than WMOs)
    vertex_colors = [clist for clist in wmo_group.vertex_colors if len(clist) > 0]
    do_colors = True if len(vertex_colors) > 0 else False

    # from pprint import pformat
    # before = str(group.colors)
    # after = str(color_list)
    # Path(f"before_{group.json_group.groupID}.txt").write_text(pformat(before))
    # Path(f"after_{group.json_group.groupID}.txt").write_text(pformat(after))

    # if before != after:
    #     print("color comparison differs")

    colors = {}

    # needs to be a dict, since we might be inserting the verts out of order
    bm_verts: Dict[int, bmesh.types.BMVert] = {}
    # uv_dict = {}

    for i, batch in enumerate(batches):
        example_face: Optional[bmesh.types.BMFace] = None
        # cull_list = []
        for face in group_submeshes[i].faces:
            # vertex indexes
            for v in face:
                # FIXME: what's up with the switcheroo types here?
                # if type(v_dict.get(v)) == bmesh.types.BMVert:
                #     vert = v_dict[v]
                # else:
                #     vert = bm.verts.new(obj_data.verts[v - 1])
                #     v_dict[v] = vert
                if v in bm_verts:
                    vert = bm_verts[v]
                else:
                    vert = bm.verts.new(imported_mesh.verts[v - 1])
                    bm_verts[v] = vert

                # The data layer for vertex color is actually in the face loop.
                # We can't set the color until after all of the faces are made,
                # So we throw it all into a dictionary and brute-force it later.
                # Note: There can theoretically be three sets of vertex colors.
                if do_colors:
                    # if type(vertex_colors[0]) == list:
                    v_color: List[fColor4] = []
                    for sublist in vertex_colors:
                        v_color.append(wmo_read_color(sublist[v - 1], 'CImVector'))

                    # else:
                    #     # FIXME: What even -is- this?
                    #     x = vertex_colors
                    #     v_color = wmo_read_color(vertex_colors[v - 1], 'CImVector')  # ????

                    colors[vert] = v_color

            try:
                if not example_face:
                    bface = bm.faces.new((
                        bm_verts[face[0]],
                        bm_verts[face[1]],
                        bm_verts[face[2]]
                    ))
                    example_face = bface

                    if batches[i].flags == 2:
                        # FIXME: what is this?
                        mat_ID = batches[i].possibleBox2[2]
                    else:
                        mat_ID = batches[i].materialID

                    # FIXME: is there a way to not have to always repeat this cast?
                    local_index = cast(bpy.types.Mesh, bl_obj.data).materials.find(
                        bl_materials[int(mat_ID)].name)

                    if local_index == -1:
                        # FIXME: typing
                        cast(bpy.types.Mesh, bl_obj.data).materials.append(
                            bl_materials[int(mat_ID)])
                        bface.material_index = cast(bpy.types.Mesh, bl_obj.data).materials.find(
                            bl_materials[int(mat_ID)].name)
                    else:
                        bface.material_index = local_index

                else:
                    bface = bm.faces.new((
                        bm_verts[face[0]],
                        bm_verts[face[1]],
                        bm_verts[face[2]]
                    ), example_face)

            except ValueError as e:
                # v1 = bm.verts.new(imported_submeshes.verts[face[0] - 1])
                # v2 = bm.verts.new(imported_submeshes.verts[face[1] - 1])
                # v3 = bm.verts.new(imported_submeshes.verts[face[2] - 1])
                v1 = bm.verts.new(imported_mesh.verts[face[0] - 1])
                v2 = bm.verts.new(imported_mesh.verts[face[1] - 1])
                v3 = bm.verts.new(imported_mesh.verts[face[2] - 1])

                colors[v1] = colors[bm_verts[face[0]]]
                colors[v2] = colors[bm_verts[face[1]]]
                colors[v3] = colors[bm_verts[face[2]]]

                if not example_face:
                    bface = bm.faces.new((v1, v2, v3))
                    example_face = bface

                    if batches[i].flags == 2:
                        mat_ID = int(batches[i].possibleBox2[2])  # WTF is this?
                    else:
                        mat_ID = batches[i].materialID

                    local_index = cast(bpy.types.Mesh, bl_obj.data).materials.find(
                        bl_materials[mat_ID].name)

                    if local_index == -1:
                        cast(bpy.types.Mesh, bl_obj.data).materials.append(bl_materials[mat_ID])
                        bface.material_index = cast(bpy.types.Mesh, bl_obj.data).materials.find(
                            bl_materials[mat_ID].name)
                    else:
                        bface.material_index = local_index
                else:
                    bface = bm.faces.new((v1, v2, v3), example_face)

                err_detail = (
                    f"Duplicate Face: {face[0]}/{face[0]}/{face[0]} {face[1]}/{face[1]}/{face[1]} {face[2]}/{face[2]}/{face[2]}")
                print(err_detail)


    uv_layer = bm.loops.layers.uv.new("UVMap")

    if len(imported_mesh.uv2) > 0:
        uv2_layer = bm.loops.layers.uv.new('UV2Map')

    if len(imported_mesh.uv3) > 0:
        uv3_layer = bm.loops.layers.uv.new('UV3Map')

    bm.faces.ensure_lookup_table()

    # face_list_tmp = [submesh.faces for submesh in imported_mesh.submeshes]
    face_list_tmp = [submesh.faces for submesh in group_submeshes]
    face_list = [face for sublist in face_list_tmp for face in sublist]

    # face_list = [batch.faces for batch in batches]
    # face_list = [face for sublist in face_list for face in sublist]


    for i, face in enumerate(face_list):
        for j, loop in enumerate(bm.faces[i].loops):
            loop[uv_layer].uv = imported_mesh.uv[face[j] - 1]

            if len(imported_mesh.uv2) > 0:
                loop[uv2_layer].uv = imported_mesh.uv2[face[j] - 1]

            if len(imported_mesh.uv3) > 0:
                loop[uv3_layer].uv = imported_mesh.uv3[face[j] - 1]

    # bm.verts.ensure_lookup_table()

    if len(vertex_colors) > 0:
        vcols = []
        for i, clist in enumerate(vertex_colors):
            vcols.append(bm.loops.layers.color.new(f"vcols_{i}"))

        for i, vert in enumerate(bm.verts):
            for loop in vert.link_loops:
                for i, vcol_list in enumerate(vcols):
                    loop[vcol_list] = colors[vert][i]

    if merge_verts:
        st = recursive_remove_doubles(bm, verts=bm.verts, dist=0.00001)
        print(
            f"{bl_obj.name}:"
            f" {st['removed_verts']} of {st['start_verts']} verts removed"
            f" in {st['merge_passes']} passes"
            f" in {st['total_time']:1.6f}s"
            f" ({st['end_verts']} verts remain)"
        )

    bm.to_mesh(bl_mesh)
    bm.free()

    bl_obj.rotation_euler = Euler((0, 0, 0))
    bl_obj.rotation_euler.x = radians(90)

    collection_name = metadata.groupDescription
    if use_collections and collection_name:
        if collection_name in bpy.data.collections:
            collection = bpy.data.collections[collection_name]
        else:
            collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(collection)

        collection.objects.link(bl_obj)
    else:
        bpy.context.view_layer.active_layer_collection.collection.objects.link(
            bl_obj)


    if make_quads:
        st = tris_to_quads(bl_obj, 5.0)
        print(
            f"{bl_obj.name}:"
            f" {st['removed_faces']} of {st['start_faces']} faces removed"
            f" in {st['total_time']:1.6f}s"
            f" ({st['end_faces']} faces remain)"
        )

    # Give us a reasonable origin on everything
    bpy.ops.object.select_all('INVOKE_DEFAULT', False, action='DESELECT')
    bl_obj.select_set(True)
    bpy.ops.object.origin_set('INVOKE_DEFAULT', False, type='ORIGIN_GEOMETRY', center='MEDIAN')
    bpy.ops.object.shade_smooth('INVOKE_DEFAULT', False)

    return bl_obj
