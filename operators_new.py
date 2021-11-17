
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

# import os
from pathlib import Path

import bpy
import bpy.props
import bmesh
from bpy_extras.io_utils import ImportHelper
from mathutils import Vector
from math import radians

from typing import TYPE_CHECKING, cast, Optional, Dict, List, Set, Tuple, Union, Any
# from .node_groups import serialize_nodegroups
# from .node_groups import generate_nodegroups
from .node_groups import get_utility_group
from .node_groups import do_wmo_combiner

# from .utilties import do_import
from . import preferences
# from .obj_import import wmo_setup_blender_object
from .lookup_funcs import wmo_read_color, wmo_read_group_flags
# from .lookup_funcs import WMO_Shaders_New
# from .lookup_funcs import wmo_read_mat_flags
from .preferences import WoWbject_ObjectProperties

import json


def test():
    fred = "bob"


# FIXME: do we need to make this local/tweak this/etc?
# from .node_groups import do_wmo_mats

# ripped from obj_import.py, which was ripped from Kruinthe's addoon.
# There may or may not be a better way to manage all this.
#
# FIXME: Can we make these a dataclass?
class meshComponent:
    usemtl: str
    name: str
    verts: Set[float]
    faces: List[Tuple[int, ...]]
    uv: List[float]

    def __init__(self) -> None:
        self.usemtl = ''
        self.name = ''
        self.verts = set()
        self.faces = []
        self.uv = []


class meshObject:
    usemtl: str
    mtlfile: str
    name: str

    # These tuples actually are of a determinant size, but the type checker
    # doesn't know that, so we're cheating a little.
    verts: List[Tuple[float, ...]]
    faces: List[Tuple[int, ...]]
    normals: List[Tuple[float, ...]]
    uv: List[Tuple[float, ...]]
    uv2: List[Tuple[float, ...]]
    uv3: List[Tuple[float, ...]]
    components: List[meshComponent]

    def __init__(self) -> None:
        self.usemtl = ''
        self.mtlfile = ''
        self.name = ''
        self.verts = []
        self.faces = []
        self.normals = []
        self.uv = []
        self.uv2 = []
        self.uv3 = []
        self.components = []


class wmoGroup:
    mesh_data: Optional[meshObject]
    mesh_batches: List[meshComponent]

    json_group: Dict[str, Any]
    group_offset: int

    json_batches: List[Any]  # FIXME: type
    batch_count: int

    colors: List[List[int]]

    def __init__(self) -> None:
        self.mesh_data = None
        self.mesh_batches = []

        self.json_group = {}
        self.group_offset = -1

        # The renderBatches that map to the meshComponent objects
        self.json_batches = []
        self.batch_count = -1

        self.colors = []


class WOWBJ_OT_Import(bpy.types.Operator, ImportHelper):
    """Load a WoW .OBJ, with associated JSON and .m2 data"""
    bl_idname = 'import_scene.wowbject'
    bl_label = 'WoWbject Import'
    bl_options = {'PRESET', 'UNDO'}

    if TYPE_CHECKING:
        directory: bpy.types.StringProperty
    else:
        directory: bpy.props.StringProperty(subtype='DIR_PATH')

    filename_ext = '.obj'
    if TYPE_CHECKING:
        filter_glob: bpy.types.StringProperty
    else:
        filter_glob: bpy.props.StringProperty(default='*.obj')


    if TYPE_CHECKING:
        files: bpy.types.Collection
    else:
        files: bpy.props.CollectionProperty(
            name='File Path',
            type=bpy.types.OperatorFileListElement,
        )


    if TYPE_CHECKING:
        name_override: str
    else:
        name_override: bpy.props.StringProperty(
            name="Name",
            description="Defaults to asset name when left blank",
            default=''
        )

    if TYPE_CHECKING:
        merge_verts: bool
    else:
        merge_verts: bpy.props.BoolProperty(
            name='Dedupe Vertices',
            description='Deduplicate and merge vertices',
            default=True
        )

    if TYPE_CHECKING:
        make_quads: bool
    else:
        make_quads: bpy.props.BoolProperty(
            name='Tris to Quads',
            description='Automatically convert to quad-based geometry where possible',
            default=False
        )

    if TYPE_CHECKING:
        use_collections: bool
    else:
        use_collections: bpy.props.BoolProperty(
            name='Use Collections',
            description='Create objects inside collections when possible (WMO only)',
            default=True
        )

    if TYPE_CHECKING:
        reuse_materials: bool
    else:
        reuse_materials: bpy.props.BoolProperty(
            name='Reuse Materials',
            description='Re-use the existing materials in the scene if they match',
            default=False
        )

    if TYPE_CHECKING:
        create_aovs: bool
    else:
        create_aovs: bpy.props.BoolProperty(
            name='Create AOVs',
            description='[NOT IMPLEMENTED] Create AOVs for materials that use special blending modes',
            default=False
        )

    if TYPE_CHECKING:
        use_vertex_lighting: bool
    else:
        use_vertex_lighting: bpy.props.BoolProperty(
            name="Experimental Vertex Lighting",
            description="Use the experimental vertex lighting node in WMO shaders",
            default=False
        )

    base_shader_items = [
        ("EMIT", "Emission Shader", "Standard unlit look"),
        ("DIFF", "Diffuse Shader", "Lit look without additional specularity"),
        ("SPEC", "Specular Shader", "Lit look with extra downmixing for spec maps"),
        ("PRIN", "Principled Shader", "All the sliders"),
        ("EXPE", "Experimental", "You probably won't want to use this one"),
    ]

    if TYPE_CHECKING:
        base_shader: bpy.types.EnumProperty
    else:
        base_shader: bpy.props.EnumProperty(
            name="Shader Base",
            items=base_shader_items,
            default='EMIT',
        )

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> Union[Set[str], Set[int]]:
        prefs = preferences.get_prefs()
        default_dir = prefs.default_dir
        if not default_dir == "":
            self.directory = default_dir
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


    def execute(self, context: bpy.types.Context) -> Union[Set[str], Set[int]]:
        print("new import execute")

        # FIXME: not sure what the best type for args actually is
        args: Dict[str, bpy.types.Property] = self.as_keywords(
            ignore=("filter_glob", "directory", "filepath", "files"))

        # FIXME: figure out how to do enum types returning str -correctly-
        do_import(context, self.filepath, self.reuse_materials, str(self.base_shader), args)

        return {'FINISHED'}

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        root = layout.column(align=True)
        root.use_property_split = True

        root.label(text="Basic Settings:")
        root.prop(self, 'name_override', text="Rename to:")

        row = root.row(align=True)
        row.prop(self, 'reuse_materials')

        row = root.row(align=True)
        row.prop(self, 'merge_verts')

        row = root.row(align=True)
        row.prop(self, 'make_quads')

        row = root.row(align=True)
        row.prop(self, 'use_collections')

        col = root.column(align=True)
        col.use_property_split = True
        col.label(text="Shading:")
        col.prop(self, 'base_shader', expand=False)


        col = root.column(align=True)
        col.use_property_split = True
        col.label(text="WMO Settings:")
        col.prop(self, 'use_vertex_lighting', expand=False)


# FIXME: return type
def do_import(context: bpy.types.Context, filepath: str, reuse_mats: bool, base_shader: str, op_args: Dict[str, Any]) -> None:
    '''
    The pre-sorting and initializing function called by the import operator.
    Most of the actual data-handling is handled by an import_container object.
    '''

    file = Path(filepath)
    name_override = op_args.get("name_override")

    # if do_search:
    if True:
        if file.with_suffix(".json").exists():
            with file.with_suffix(".json").open() as p:
                # FIXME: error handling here
                json_config = json.load(p)
        else:
            # FIXME: user-facing error handling
            print(f"failed to load metadata from '{file}', can't continue")
            return

        if not json_config:
            print(f"failed to load metadata file {file.with_suffix('.json')}")

        if name_override:
            basename = name_override
        else:
            basename = file.stem

        print(f"importing using base name: {basename}")


    # START def do_setup(self, files, directory, op_args, **kwargs):
    if True:
        # START def setup_json_data(self, **kwargs):
        if ".wmo" not in json_config.get("fileName", ""):
            print("ERROR: trying to import a non-WMO file")
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
            obj = meshObject()
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
                        obj.mtlfile = str(line_split[1])
                    elif line_start == b'v':
                        # FIXME: replace all the things like this with proper
                        # vec2/vec3/vec4 tuples
                        obj.verts.append(tuple([float(v) for v in line_split[1:]]))
                    elif line_start == b'vn':
                        obj.normals.append(tuple([float(v) for v in line_split[1:]]))
                    elif line_start == b'vt3':
                        obj.uv3.append(tuple([float(v) for v in line_split[1:]]))
                    elif line_start == b'vt2':
                        if not line_split[1] == b'undefined':
                            obj.uv2.append(tuple([float(v) for v in line_split[1:]]))
                        else:
                            obj.uv2.append((0.0, 0.0))
                    elif line_start == b'vt':
                        obj.uv.append(tuple([float(v) for v in line_split[1:]]))
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

            mesh_data = obj
            # END INLINE: initialize_mesh

            # FIXME: Can I do this in a way without a cast?
            newMesh = bpy.data.meshes.new(basename)
            newMesh.use_auto_smooth = True
            newMesh.auto_smooth_angle = radians(60)


            # FIXME: Not sure how to annotate the dynamic attribute here
            newObj = bpy.data.objects.new(basename, newMesh)
            WBJ: WoWbject_ObjectProperties = newObj.WBJ

            # FIXME: Not sure how to type annotate the props to make these not
            # complain? But should be possible?
            WBJ.source_asset = str(file.name)
            WBJ.source_directory = str(file.parent)
            WBJ.initialized = True

            # if import_container.wmo:
            json_mats = json_config.get("materials")
            json_groups = json_config.get("groups")

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
                mat = cast(bpy.types.BlendDataMaterials, bpy.data.materials).new(
                    name=basename + "_mat_" + str(i))
                mat.use_nodes = True
                mat_dict[i] = mat

            print(f"mat type thing: {type(i)} - {type(mat_dict)}")

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
        config = json_config
        mats = config.get("materials")

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
                texnum = mat.get('texture1')
                texfilename = f"{texnum}.png"
                texfile = file.parent / texfilename
                if texnum > 0 and texfile.exists():
                    if texfilename in bpy.data.images:
                        tex1 = cast(bpy.types.BlendDataImages,
                                    bpy.data.images)[texfilename]
                    else:
                        tex1 = cast(bpy.types.BlendDataImages, bpy.data.images).load(
                            str(texfile.resolve()))
                        tex1.alpha_mode = 'CHANNEL_PACKED'
                else:
                    tex1 = None

                # tex2 = get_tex(container, str(mat.get("texture2")))
                texnum = mat.get('texture2')
                texfilename = f"{texnum}.png"
                texfile = file.parent / texfilename
                if texnum > 0 and texfile.exists():
                    if texfilename in bpy.data.images:
                        tex2 = cast(bpy.types.BlendDataImages,
                                    bpy.data.images)[texfilename]
                    else:
                        tex2 = cast(bpy.types.BlendDataImages, bpy.data.images).load(
                            str(texfile.resolve()))
                        tex2.alpha_mode = 'CHANNEL_PACKED'
                else:
                    tex2 = None

                # tex3 = get_tex(container, str(mat.get("texture3")))
                texnum = mat.get('texture3')
                texfilename = f"{texnum}.png"
                texfile = file.parent / texfilename
                if texnum > 0 and texfile.exists():
                    if texfilename in bpy.data.images:
                        tex3 = cast(bpy.types.BlendDataImages,
                                    bpy.data.images)[texfilename]
                    else:
                        tex3 = cast(bpy.types.BlendDataImages, bpy.data.images).load(
                            str(texfile.resolve()))
                        tex3.alpha_mode = 'CHANNEL_PACKED'
                else:
                    tex3 = None

                tex_list = (tex1, tex2, tex3)

                bl_mat = slot.material
                tree = bl_mat.node_tree
                nodes = cast(bpy.types.Nodes, tree.nodes)

                if bl_mat in configured_mats:
                    continue

                shader = None
                out_node = None
                # FIXME: give Nodes an __iter__ instead of using this typecast?
                for node in cast(List[bpy.types.Node], nodes):
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
                prefs = preferences.get_prefs()
                base = prefs.get_base_shader(base_shader)

                if base == 'Experimental':
                    shader = nodes.new('ShaderNodeGroup')
                    shader.node_tree = get_utility_group(
                        name="TheStumpFargothHidTheRingIn")
                elif (base != ''):
                    shader = nodes.new(base)
                else:
                    shader = nodes.new("ShaderNodeEmission")

                # FIXME: Can we clean up the type casting on this?
                cast(bpy.types.NodeLinks, tree.links).new(
                    cast(bpy.types.Node, shader).outputs[0], out_node.inputs[0])

                baseColor = nodes.new('ShaderNodeRGB')
                baseColor.location += Vector((-1200.0, 400.0))
                baseColor.outputs["Color"].default_value = wmo_read_color(
                    mat.get("color2"), 'CArgb')
                baseColor.label = 'BASE COLOR'

                tex_nodes: List[bpy.types.ShaderNodeTexImage] = []

                for i, tex in enumerate(tex_list):
                    if tex:
                        tex_node = nodes.new('ShaderNodeTexImage')
                        tex_node.image = tex
                        tex_node.location += Vector((-1200.0, (200 - i * 300.0)))
                        tex_node.label = ("TEXTURE_%s" % str(i + 1))
                        tex_nodes.append(tex_node)

                ambColor = wmo_read_color(config.get("ambientColor"), 'CImVector')


                do_wmo_combiner(
                    tex_nodes=tex_nodes,
                    bl_mat=bl_mat,
                    shader_out=shader,
                    mat_info=mat,
                    ambient=ambColor,
                    do_vertex_lighting=op_args.get("use_vertex_lighting", False))

                configured_mats.add(bl_mat)
            # END do_wmo_mats
            # END setup_materials


# FIXME: Legit needs fewer arguments
def wmo_setup_blender_object(base_name: str, group: wmoGroup,
                             mesh_data: meshObject, mat_dict: Dict[int, bpy.types.Material],
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
    v_dict = {}
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
                    print(type(newObj.data))
                    print(type(newObj.data.materials))

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
