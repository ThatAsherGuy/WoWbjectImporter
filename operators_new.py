
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

# from line_profiler import LineProfiler
# profile = LineProfiler()

import os
from pathlib import Path

import bpy
import bmesh
import bpy.props
from bpy_extras.io_utils import ImportHelper
from mathutils import Vector
from math import radians

from typing import TYPE_CHECKING, Optional, Dict, List, Tuple, Union, Any
from .node_groups import serialize_nodegroups
from .node_groups import generate_nodegroups
from .node_groups import get_utility_group
# from .utilties import do_import
from . import preferences
from .obj_import import wmo_setup_blender_object
from .lookup_funcs import wmo_read_color, WMO_Shaders_New, wmo_read_mat_flags

import json

# FIXME: do we need to make this local/tweak this/etc?
# from .node_groups import do_wmo_mats


# ripped from obj_import.py, which was ripped from Kruinthe's addoon.
# There may or may not be a better way to manage all this.
#
# FIXME: Can we make these a dataclass?
class meshComponent:
    usemtl: str
    name: str
    verts: set[float]
    faces: list[int]
    uv: list[float]

    def __init__(self):
        self.usemtl = ''
        self.name = ''
        self.verts = set()
        self.faces = []
        self.uv = []


class meshObject:
    usemtl: str
    mtlfile: str
    name: str
    verts: list[float]
    faces: list[int]
    normals: list[float]
    uv: list[float]
    uv2: list[float]
    uv3: list[float]
    components: list[meshComponent]

    def __init__(self):
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

    json_group: Optional[Dict[str, Any]]
    group_offset: int

    json_batches: List[Dict]
    batch_count: int

    colors: List[List[int]]

    def __init__(self):
        self.mesh_data = None
        self.mesh_batches = []

        self.json_group = None
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
        files: bpy.props.CollectionProperty(  # type: ignore
            name='File Path',
            type=bpy.types.OperatorFileListElement,
        )


    # filepath: bpy.props.StringProperty(  # type: ignore
    #     name="File Path",
    #     description="Filepath used for importing the file",
    #     maxlen=1024,
    #     subtype='FILE_PATH',
    # )
    if TYPE_CHECKING:
        name_override: str
    else:
        name_override: bpy.props.StringProperty(  # type: ignore
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


    def invoke(self, context, _event):
        prefs = preferences.get_prefs()
        default_dir = prefs.default_dir
        if not default_dir == "":
            self.directory = default_dir
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


    def execute(self, context):
        print("new import execute")
        prefs = preferences.get_prefs()
        verbosity = prefs.reporting
        default_dir = prefs.default_dir
        args = self.as_keywords(ignore=("filter_glob", "directory", "filepath", "files"))

        reports = do_import(self, context, self.filepath,
                            self.reuse_materials, self.base_shader, args)

        # if (len(reports.warnings) > 0):
        #     if 'WARNING' in verbosity:
        #         self.report({'WARNING'}, "Warnings encountered. Check the console for details")

        #     for report in reports.warnings:
        #         print(report)

        # if (len(reports.errors) > 0):
        #     if 'ERROR' in verbosity:
        #         self.report({'ERROR'}, "Errors ecountered. Check the console for details")

        #     for report in reports.errors:
        #         print(report)

        # if (len(reports.info) > 0):
        #     if 'INFO' in verbosity:
        #         self.report({'INFO'}, "Info messages generated. Check the console for details")

        #     for report in reports.info:
        #         print(report)

        # if (len(reports.sub_steps) > 0):
        #     if 'PROPERTY' in verbosity:
        #         self.report(
        #             {'PROPERTY'}, "Sub-step report generated. Check the console for details")

        #     for report in reports.sub_steps:
        #         print(report)

        return {'FINISHED'}

    def draw(self, context):
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

        selector_params = context.space_data.params

        col = root.column(align=True)
        col.use_property_split = True
        col.label(text="WMO Settings:")
        col.prop(self, 'use_vertex_lighting', expand=False)

        col.label(text="Misc:")
        op = col.operator('wowbj.set_default_dir', text="Use as Default Directory")
        op.new_dir = selector_params.directory



# @profile
def do_import(operator, context, filepath, reuse_mats, base_shader, op_args, **kwargs):
    '''
    The pre-sorting and initializing function called by the import operator.
    Most of the actual data-handling is handled by an import_container object.
    '''

    # files = op_args.get("files")
    # directory = op_args.get("directory")
    # file = os.path.basename(filepath)
    # directory = os.path.dirname(filepath)
    file = Path(filepath)

    # FIXME: these first two aren't needed?
    reuse_mats = op_args.get("reuse_materials")
    base_shader = op_args.get("base_shader")
    name_override = op_args.get("name_override")

    # textures = []
    # objects = []
    # mtl = []
    # configs = []
    # m2 = []

    # for file in files:
    # basename, ext = os.path.splitext(file)

    # FIXME: Do we actually need this? We're not multi-selecting non-obj files now
    # if ext == '.png':
    #     textures.append(file)
    # elif ext == '.obj':
    #     objects.append(file)
    # elif ext == '.mtl':
    #     mtl.append(file)
    # elif ext == '.json':
    #     configs.append(file)
    # elif ext == '.m2':
    #     m2.append(file)

    # file_lists = (textures, objects, configs, m2)

    # do_search = False

    # for L in file_lists:
    #     if len(L) < 1:
    #         do_search = True
    #         break

    # if do_search:
    if True:
        # ref_name = ''
        # if len(objects) == 1:
        #     ref_name = os.path.splitext(objects[0])[0]

        # dir_files = []
        # subdirs = []
        # tex_dir = ''

        # for thing in os.listdir(directory):
        #     if os.path.isfile(os.path.join(directory, thing)):
        #         dir_files.append(thing)
        #     elif os.path.isdir(os.path.join(directory, thing)):
        #         subdirs.append(thing)
        #         if thing == 'textures':
        #             tex_dir = thing

        # config_found = False
        # m2_found = False
        # mtl_found = False

        # Search source directory for missing files
        # for file in dir_files:
        #     basename, ext = os.path.splitext(file)

        #     if len(configs) < 1:
        #         if (basename == ref_name) and (ext == '.json'):
        #             configs.append(file)
        #             config_found = True
        #             continue

        #     if len(m2) < 1:
        #         if (basename == ref_name) and (ext == '.m2'):
        #             m2.append(file)
        #             m2_found = True
        #             continue

        #     if len(mtl) < 1:
        #         if (basename == ref_name) and (ext == '.mtl'):
        #             mtl.append(file)
        #             mtl_found = True
        #             continue

        # # Find missing textures by checking configs
        # # Doesn't handle situations where only some are missing
        # if len(textures) < 1:
        #     if mtl_found == 1:
        #         textures = read_mtl(directory, mtl[0])
        #     elif config_found:
        #         with open(os.path.join(directory, configs[0])) as p:
        #             json_config = json.load(p)
        #             tex_defs = json_config.get("textures")
        #             for tdef in tex_defs:
        #                 tID = tdef.get("fileDataID")
        #                 textures.append(str(tID) + ".png")

        if file.with_suffix(".json").exists():
            with file.with_suffix(".json").open() as p:
                json_config = json.load(p)

        if not(json_config):
            print(f"failed to load json file {file}")

        # if len(objects) == 1:
        #     if name_override == '':
        #         basename = os.path.splitext(objects[0])[0]
        #     else:
        #         basename = name_override

        #     print(basename)

        if name_override:
            basename = name_override
        else:
            basename = file.stem

        print(f"importing using base name: {basename}")

    # files = textures + objects + mtl + configs + m2

    # import_obj = import_container()
    # import_obj.tex_dir = tex_dir
    # import_obj.name = basename
    # reports = import_obj.do_setup(
    #     files,
    #     directory,
    #     op_args,
    #     reuse_mats=reuse_mats,
    #     base_shader=base_shader
    # )
    # return reports


    # INLINE: do_setup
    # def do_setup(self, files, directory, op_args, **kwargs):
    if True:
        # self.op_args = op_args
        # self.source_directory = directory
        # for arg, val in kwargs.items():
        #     if arg == 'base_shader':
        #         self.base_shader = val
        #     elif arg == 'reuse_mats':
        #         self.reuse_mats = val

        # don't think this is needed, because we get it direct, above?
        # for arg, val in kwargs.items():
        #     if arg == 'base_shader':
        #         base_shader = val
        #     elif arg == 'reuse_mats':
        #         reuse_mats = val

        # for file in files:
        #     name, ext = os.path.splitext(file)
        #     if ext == '.png':
        #         self.source_files['texture'].append(file)
        #     elif ext == '.obj':
        #         self.source_files['OBJ'].append(file)
        #     elif ext == '.mtl':
        #         self.source_files['MTL'].append(file)
        #     elif ext == '.json':
        #         self.source_files['config'].append(file)
        #     elif ext == '.m2':
        #         self.source_files['M2'].append(file)
        #     elif ext == '.blp':
        #         self.source_files['BLP'].append(file)
        #     elif ext == '.skin':
        #         self.source_files['skin'].append(file)
        #     elif ext == '.wmo':
        #         self.source_files['skin'].append(file)
        #     else:
        #         print("Unhandled File Type: " + str(file))
        #         self.source_files['unhandled'].append(file)



        # INLINE: setup_json_data
        # load_step = self.setup_json_data()
        # def setup_json_data(self, **kwargs):
        if True:
            # if not kwargs.get('config') == None:
            #     self.json_config = kwargs.get('config')
            # else:
            #     source = self.source_files['config']

            #     if len(source) > 1:
            #         return False

            #     if len(source) == 0:
            #         return False

            #     config_path = os.path.join(self.source_directory, source[0])
            #     with open(config_path) as p:
            #         self.json_config = json.load(p)

            # if ".wmo" in self.json_config.get("fileName", ""):
            #     self.wmo = True

            if ".wmo" not in json_config.get("fileName", ""):
                print("ERROR: trying to import a non-WMO file")

            # FIXME: Make sure this is sane/we need this
            json_textures = json_config.get(
                "textures", json_config.get("fileDataIDs", []))
            json_tex_combos = json_config.get("textureCombos", [])
            json_tex_units = json_config.get(
                "skin", {}).get("textureUnits", [])
            json_submeshes = json_config.get(
                "skin", {}).get("subMeshes", [])
        # END INLINE: setup_json_data



        # print("Unpacking Textures")
        # if not self.wmo:
        #     load_step = self.setup_textures()
        # if not load_step:
        #     self.reports.append('Failed to load textures')

        # progress.step()
        # progress.enter_substeps(2, "Initializing Object")

        # load_step = self.setup_bl_object(progress)
        # if not load_step:
        #     self.reports.errors.append(
        #         'Failed to initialize blender object')

        # INLINE: setup_bl_object
        # def setup_bl_object(self, progress):
            # source = self.source_files['OBJ']

            # # TODO: Setup a report logging system here.
            # if len(source) == 0:
            #     return False

            # # TODO: set up multi-object importing
            # if len(source) > 1:
            #     return False

            # self.bl_obj = import_obj(
            #     source[0],
            #     self.source_directory,
            #     self.reuse_mats,
            #     self.op_args.get("name_override"),
            #     self.op_args.get("merge_verts"),
            #     self.op_args.get("make_quads"),
            #     self.op_args.get("use_collections"),
            #     self,
            #     progress
            # )
        # END INLINE: setup_bl_object


        # INLINE: import_obj
        # def import_obj(file, directory, reuse_mats, name_override, merge_verts, make_quads, use_collections, import_container, progress, **kwargs):
        if True:  # import_obj()
            if bpy.ops.object.select_all.poll():
                bpy.ops.object.select_all('INVOKE_DEFAULT', False, action='DESELECT')

            # if name_override:
            #     mesh_name = name_override
            # else:
            #     mesh_name = os.path.splitext(file)[0]
            basename = basename   # we calculate far above

            print("Reading OBJ File")
            # mesh_data = initialize_mesh(os.path.join(directory, file))

            # INLINE: initialize_mesh
            # def initialize_mesh(mesh_path: str):
            if True:
                obj = meshObject()
                meshIndex = -1

                # when there are faces that end with \
                # it means they are multiline-
                # since we use xreadline we cant skip to the next line
                # so we need to know whether
                context_multi_line = b''

                # with open(mesh_path, 'rb') as f:
                with file.open('rb') as f:
                    for line in f:
                        line_split = line.split()

                        if not line_split:
                            continue

                        line_start = line_split[0]

                        if len(line_split) == 1 and not context_multi_line and line_start != b'end':
                            print("WARNING, skipping malformatted line: %s" %
                                  line.decode('UTF-8', 'replace').rstrip())
                            continue

                # TODO: Replace with a more robust port of the ImportObj add-on's process
                # with open(mesh_path, 'rb') as f:
                with file.open('rb') as f:
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
                        elif line_start == b'vt3':
                            obj.uv3.append([float(v) for v in line_split[1:]])
                        elif line_start == b'vt2':
                            if not line_split[1] == b'undefined':
                                obj.uv2.append([float(v) for v in line_split[1:]])
                            else:
                                obj.uv2.append([0.0, 0.0])
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
                # return obj
                mesh_data = obj
            # END INLINE: initialize_mesh

            # (back to import_obj, I think?)
            newMesh = bpy.data.meshes.new(basename)
            newMesh.use_auto_smooth = True
            newMesh.auto_smooth_angle = radians(60)

            newObj = bpy.data.objects.new(basename, newMesh)

            newObj.WBJ.source_asset = str(file.name)
            newObj.WBJ.source_directory = str(file.parent)
            newObj.WBJ.initialized = True

            bm = bmesh.new()
            output_meshes = []

            # if import_container.wmo:
            if True:
                # config = import_container.json_config
                # json_mats = config.get("materials")
                # groups = config.get("groups")
                json_mats = json_config.get("materials")
                json_groups = json_config.get("groups")


                # wmo_groups = repack_wmo(import_container=import_container,
                #                         groups=groups, mesh_data=mesh_data, config=config)

                # INLINE: repack_wmo
                # def repack_wmo(import_container, groups: dict, mesh_data: meshObject, config: dict):
                if True:  # repack_wmo()
                    # json_groups = import_container.json_config.get("groups")
                    groups = []
                    offset = 0

                    flat_colors = [[], [], []]

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
                                flat_colors[1] += [0 for j in vcolors[0]]
                            elif len(vcolors) == 0:
                                if vertex_count > 0:
                                    flat_colors[0] += [0 for j in range(vertex_count)]
                                    flat_colors[1] += [0 for j in range(vertex_count)]

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

                    # return groups
                    wmo_groups = groups
                # END INLINE: repack_wmo

                # (back to import_obj, I think? (maybe?))
                # FIXME: Is mat_dict a dict or a list?
                mat_dict = {}
                for i, mat in enumerate(json_mats):
                    mat = bpy.data.materials.new(name=basename + "_mat_" + str(i))
                    mat.use_nodes = True
                    mat_name = mat.name
                    mat_dict[i] = mat

                objects = []

                # steps = len(wmo_groups)
                print(f"working on {len(wmo_groups)} groups")

                # progress.step()
                # progress.enter_substeps(steps, "Generating Meshes")
                print(f"Generating meshes")

                for i, group in enumerate(wmo_groups):
                    sub = group.json_group.get("groupName", "")
                    # progress.step(f"Constructing object {i + 1}/{steps} | {sub}")
                    print(f"Constructing object {i + 1} | {sub}")

                    # FIXME: revisit
                    bl_obj = wmo_setup_blender_object(
                        base_name=f"{i:03d}_{basename}",  # FIXME: make group num into metadata
                        group=group,
                        mesh_data=mesh_data,
                        mat_dict=mat_dict,
                        # merge_verts=merge_verts,
                        # make_quads=make_quads,
                        # use_collections=use_collections
                    )

                    if bl_obj:
                        objects.append(bl_obj)

                # progress.leave_substeps("Mesh Generation Complete")
                # return objects
            # END INLINE: initialize_mesh

            # Big block below used only for non-WMO, eliding
            # for i, v in enumerate(mesh_data.verts):
            #     vert = bm.verts.new(v)
            #     vert.normal = mesh_data.normals[i]

            # bm.verts.ensure_lookup_table()
            # bm.verts.index_update()

            # group_faces = []

            # for i, component in enumerate(mesh_data.components):
            #     create_mat = True
            #     exampleFaceSet = False
            #     mat_name = mesh_name + "_" + component.name + "_mat"
            #     fallback_name = os.path.splitext(file)[0] + "_" + component.name + "_mat"

            #     if reuse_mats:
            #         for bl_mat in bpy.data.materials:
            #             if bl_mat.name == mat_name:
            #                 mat = bl_mat
            #                 create_mat = False
            #                 break

            #             elif bl_mat.name == fallback_name:
            #                 mat = bl_mat
            #                 create_mat = False
            #                 break

            #     if create_mat:
            #         if not import_container.wmo:
            #             mat = bpy.data.materials.new(name=mat_name)
            #             mat.use_nodes = True
            #             mat_name = mat.name
            #             newObj.data.materials.append(mat)

            #     for face in component.faces:
            #         try:
            #             if exampleFaceSet == False:
            #                 face = bm.faces.new((
            #                     bm.verts[face[0] - 1],
            #                     bm.verts[face[1] - 1],
            #                     bm.verts[face[2] - 1]
            #                 ))
            #                 bm.faces.ensure_lookup_table()

            #                 bm.faces[-1].material_index = newObj.data.materials.find(mat_name)

            #                 bm.faces[-1].smooth = True
            #                 exampleFace = bm.faces[-1]
            #                 exampleFaceSet = True
            #             else:
            #                 # Use example face if set to speed up material copy!
            #                 face = bm.faces.new((
            #                     bm.verts[face[0] - 1],
            #                     bm.verts[face[1] - 1],
            #                     bm.verts[face[2] - 1]
            #                 ), exampleFace)

            #             group_faces.append(face)

            #         except ValueError:
            #             # sometimes there are duplicate faces. Spot checking these,
            #             # the duplicates tend to be the same as a previous, except
            #             # with a vert order of (2,1,3) instead of (1,2,3), which
            #             # gives the duplicate face the opposite normal of the one
            #             # it is duplicating. We're pretty sure these are used for
            #             # cloaks and other double-sided things, since the WoW engine
            #             # doesn't believe in double-sided polys. There may be some
            #             # situations where there's something different going on,
            #             # and we'd really like to find/investigate those if they
            #             # exist, but for now, just ignoring duplicate faces will
            #             # stop the addon from crashing, with no apparent downsides.
            #             pass

            # uv_layer = bm.loops.layers.uv.new()
            # for face in bm.faces:
            #     for loop in face.loops:
            #         loop[uv_layer].uv = mesh_data.uv[loop.vert.index]

            # if len(mesh_data.uv2) > 0:
            #     uv2_layer = bm.loops.layers.uv.new('UV2Map')
            #     for face in bm.faces:
            #         for loop in face.loops:
            #             loop[uv2_layer].uv = mesh_data.uv2[loop.vert.index]

            # if merge_verts:
            #     st = recursive_remove_doubles(bm, verts=bm.verts, dist=0.00001)
            #     print(
            #         f"{newObj.name}:"
            #         f" {st['removed_verts']} of {st['start_verts']} verts removed"
            #         f" in {st['merge_passes']} passes"
            #         f" in {st['total_time']:1.6f}s"
            #         f" ({st['end_verts']} verts remain)"
            #     )

            # bm.to_mesh(newMesh)
            # bm.free()

            # # needed to have a mesh before we can create vertex groups, so do that now
            # # FIXME: Can we do this without doing bm.to_mesh first?
            # # FIXME: disabled pending further consideration. If re-enabled, ensure
            # # it happens before vertex deduplication happens.
            # # for i, component in enumerate(mesh_data.components):
            # #     vg = newObj.vertex_groups.new(name=f"{component.name}")
            # #     vg.add(list(component.verts), 1.0, "REPLACE")

            # # Rotate object the right way
            # # TODO: Add an option to rotate the geometry instead of the object
            # newObj.rotation_euler = [0, 0, 0]
            # newObj.rotation_euler.x = radians(90)

            # # Defaults to main collection if no collection exists.
            # bpy.context.view_layer.active_layer_collection.collection.objects.link(newObj)

            # if make_quads:
            #     st = tris_to_quads(newObj, 5.0)
            #     print(
            #         f"{newObj.name}:"
            #         f" {st['removed_faces']} of {st['start_faces']} faces removed"
            #         f" in {st['total_time']:1.6f}s"
            #         f" ({st['end_faces']} faces remain)"
            #     )

            # return newObj




        # progress.leave_substeps()
        print("leaving substeps")

        # raw = self.source_files.get('M2')
        # if len(raw) > 0:
        #     progress.step("Reading M2")
        #     self.m2 = raw[0]
        #     load_step = self.unpack_m2()

        # Work-in-progress particle system importer
        # do_particles = False
        # if do_particles:
        #     self.setup_particles()

        # progress.step("Generating Materials")
        print("generating materials")

        # load_step = self.setup_materials()

        # INLINE: setup_materials
        # def setup_materials(self):
        if True:  # setup_materials
            # if self.wmo:
            #     do_wmo_mats(container=self, json=self.json_config)

            # INLINE: do_wmo_mats
            # def do_wmo_mats(**kwargs):
            if True:  # do_wmo_mats
                # container = kwargs.get("container")
                # config = kwargs.get("json")
                config = json_config
                mats = config.get("materials")

                configured_mats = set()

                # for obj in container.bl_obj:
                for obj in objects:
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
                                tex1 = bpy.data.images[texfilename]
                            else:
                                print(f"loading texture, cwd is: {os.getcwd()}")
                                tex1 = bpy.data.images.load(str(texfile.resolve()))
                                tex1.alpha_mode = 'CHANNEL_PACKED'

                        else:
                            tex1 = None


                        # tex2 = get_tex(container, str(mat.get("texture2")))
                        texnum = mat.get('texture2')
                        texfilename = f"{texnum}.png"
                        texfile = file.parent / texfilename
                        if texnum > 0 and texfile.exists():
                            if texfilename in bpy.data.images:
                                tex2 = bpy.data.images[texfilename]
                            else:
                                tex2 = bpy.data.images.load(str(texfile.resolve()))
                                tex2.alpha_mode = 'CHANNEL_PACKED'

                        else:
                            tex2 = None


                        # tex3 = get_tex(container, str(mat.get("texture3")))
                        texnum = mat.get('texture3')
                        texfilename = f"{texnum}.png"
                        texfile = file.parent / texfilename
                        if texnum > 0 and texfile.exists():
                            if texfilename in bpy.data.images:
                                tex3 = bpy.data.images[texfilename]
                            else:
                                tex3 = bpy.data.images.load(str(texfile.resolve()))
                                tex3.alpha_mode = 'CHANNEL_PACKED'

                        else:
                            tex3 = None


                        tex_list = (tex1, tex2, tex3)

                        bl_mat = slot.material
                        tree = bl_mat.node_tree
                        nodes = tree.nodes

                        if bl_mat in configured_mats:
                            continue

                        shader = None
                        out_node = None
                        for node in nodes:
                            if node.type == 'BSDF_PRINCIPLED':
                                shader = node
                                # FIXME: use input name?
                                shader.inputs[7].default_value = 1.0

                            if node.type == 'OUTPUT_MATERIAL':
                                out_node = node

                            if shader and out_node:
                                break

                        if not out_node:
                            out_node = nodes.new('ShaderNodeOutputMaterial')

                        if not shader:
                            print("DO LATER")

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

                        tree.links.new(shader.outputs[0], out_node.inputs[0])

                        baseColor = nodes.new('ShaderNodeRGB')
                        baseColor.location += Vector((-1200.0, 400.0))
                        baseColor.outputs[0].default_value = wmo_read_color(
                            mat.get("color2"), 'CArgb')
                        baseColor.label = 'BASE COLOR'

                        tex_nodes = []

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



def do_wmo_combiner(**kwargs):
    use_combiner_nodes = True
    do_vertex_lighting = kwargs.get("do_vertex_lighting", False)

    tex_nodes = kwargs.get("tex_nodes")
    bl_mat = kwargs.get("bl_mat")
    shader_out = kwargs.get("shader_out")
    mat_info = kwargs.get("mat_info")
    ambColor = kwargs.get("ambient")

    shader_info = WMO_Shaders_New[mat_info.get("shader", 0)]
    blend_info = mat_info.get("blendMode")
    group_type = mat_info.get("groupType", -1)

    tree = bl_mat.node_tree
    nodes = tree.nodes

    shader_out.label = shader_info[0]
    # shader_out.inputs[5].default_value = 0.0 # Breaking all measures of physical accuracy here.

    bl_mat.use_backface_culling = True

    flags = wmo_read_mat_flags(mat_info.get("flags", 0))

    for flag in flags:
        if flag == 'TWO_SIDED':
            bl_mat.use_backface_culling = False

    if blend_info == 2:
        bl_mat.blend_method = 'BLEND'
    elif blend_info == 1:
        bl_mat.blend_method = 'CLIP'

    mixer = nodes.new('ShaderNodeGroup')
    mixer.node_tree = get_utility_group(name=shader_info[2])
    mixer.location = Vector((-575.0, 30.0))

    offset = 0
    if use_combiner_nodes:
        v_colors = None
        v_colors2 = None

        for node_input in mixer.inputs:
            if node_input.name == "Vertex RGB":

                if do_vertex_lighting:
                    v_colors = nodes.new("ShaderNodeVertexColor")
                    v_colors.layer_name = 'vcols_0'
                    v_colors.location = Vector((-975.0, 200.0))

                    lighting = nodes.new('ShaderNodeGroup')
                    lighting.node_tree = get_utility_group(name="WMO_VertexLightingFancy")
                    lighting.location = Vector((-775.0, 150.0))

                    lighting.inputs[2].default_value = ambColor

                    tree.links.new(lighting.outputs[0], mixer.inputs[0])

                    tree.links.new(v_colors.outputs[0], lighting.inputs[4])
                    tree.links.new(v_colors.outputs[1], mixer.inputs[1])

            elif node_input.name == "Vertex2 RGB":
                v_colors2 = nodes.new("ShaderNodeVertexColor")
                v_colors2.layer_name = 'vcols_1'
                v_colors2.location = Vector((-975.0, 30.0))
                tree.links.new(v_colors2.outputs[0], mixer.inputs[2])
                tree.links.new(v_colors2.outputs[1], mixer.inputs[3])
                offset += 2

            elif node_input.name == "Tex0 RGB":
                tex_nodes[0].location = Vector((-975.0, -100.0))
                tree.links.new(tex_nodes[0].outputs[0], mixer.inputs[2 + offset])
                tree.links.new(tex_nodes[0].outputs[1], mixer.inputs[3 + offset])

            elif node_input.name == "Tex1 RGB":
                if len(tex_nodes) > 1:
                    tex_nodes[1].location = Vector((-975.0, -200.0))
                    tree.links.new(tex_nodes[1].outputs[0], mixer.inputs[4 + offset])
                    tree.links.new(tex_nodes[1].outputs[1], mixer.inputs[5 + offset])

                    if "Env" in shader_info[2]:
                        env_map = nodes.new('ShaderNodeGroup')
                        env_map.node_tree = get_utility_group(name="SphereMap_Alt")
                        env_map.location += Vector((-1400.0, (300 - 2 * 325.0)))
                        tree.links.new(env_map.outputs[0], tex_nodes[1].inputs[0])
                else:
                    mixer.inputs[5].default_value = 0.0

            elif node_input.name == "Tex2 RGB":
                if len(tex_nodes) > 2:
                    tex_nodes[2].location = Vector((-975.0, -400.0))
                    tree.links.new(tex_nodes[2].outputs[0], mixer.inputs[6 + offset])
                    tree.links.new(tex_nodes[2].outputs[1], mixer.inputs[7 + offset])

        if len(mixer.outputs) > 2:
            mix_1 = nodes.new("ShaderNodeMixRGB")
            mix_1.blend_type = 'ADD'
            mix_1.label = "Mix 1"
            mix_1.location = Vector((-275.0, 200.0))
            mix_1.inputs[0].default_value = 1.0

            tree.links.new(mixer.outputs[0], mix_1.inputs[1])
            tree.links.new(mixer.outputs[2], mix_1.inputs[2])
            tree.links.new(mix_1.outputs[0], shader_out.inputs[0])

        else:
            tree.links.new(mixer.outputs[0], shader_out.inputs[0])
        return

    if shader_info[0] == "Diffuse":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "Specular":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])
        shader_out.inputs[5].default_vaule = 0.5
        shader_out.inputs[7].default_value = 0.5

    elif shader_info[0] == "Metal":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])
        shader_out.inputs[4].default_value = 1.0
        shader_out.inputs[5].default_vaule = 0.5
        shader_out.inputs[7].default_value = 0.5

    elif shader_info[0] == "Env":

        env_map = nodes.new('ShaderNodeGroup')
        env_map.node_tree = get_utility_group(name="SphereMap_Alt")
        env_map.location += Vector((-1400.0, (300 - 2 * 325.0)))

        tree.links.new(env_map.outputs[0], tex_nodes[-1].inputs[0])

        mix_node = nodes.new("ShaderNodeMixRGB")
        mix_node.location += Vector((-600.0, 0.0))
        mix_node.label = "Env"
        mix_node.blend_type = 'ADD'

        tree.links.new(tex_nodes[0].outputs[0], mix_node.inputs[1])
        tree.links.new(tex_nodes[-1].outputs[0], mix_node.inputs[2])

        tree.links.new(mix_node.outputs[0], shader_out.inputs[0])

        tex_nodes[-1].projection = 'SPHERE'
    elif shader_info[0] == "Opaque":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "EnvMetal":
        tex_nodes[0].location = Vector((-1250.0, 200.0))
        tex_nodes[1].location = Vector((-1000.0, -120.0))

        v_colors = nodes.new("ShaderNodeVertexColor")
        v_colors.layer_name = 'vcols_1'
        v_colors.location = Vector((-975.0, 30.0))

        mix_0 = nodes.new("ShaderNodeMath")
        mix_0.operation = 'MULTIPLY'
        mix_0.label = "Mix 0"
        mix_0.location = Vector((-800.0, 150.0))
        mix_0.inputs[0].default_value = 1.0

        tree.links.new(v_colors.outputs[1], mix_0.inputs[1])
        tree.links.new(tex_nodes[0].outputs[1], mix_0.inputs[0])

        mix_1 = nodes.new("ShaderNodeMixRGB")
        mix_1.blend_type = 'MULTIPLY'
        mix_1.label = "Mix 1"
        mix_1.location = Vector((-575.0, 480.0))
        mix_1.inputs[0].default_value = 1.0

        tree.links.new(tex_nodes[0].outputs[0], mix_1.inputs[1])
        tree.links.new(mix_0.outputs[0], mix_1.inputs[2])

        mix_2 = nodes.new("ShaderNodeMixRGB")
        mix_2.blend_type = 'MULTIPLY'
        mix_2.label = "Mix 2"
        mix_2.location = Vector((-400.0, 450.0))
        mix_2.inputs[0].default_value = 1.0

        tree.links.new(tex_nodes[1].outputs[0], mix_2.inputs[1])
        tree.links.new(mix_1.outputs[0], mix_2.inputs[2])

        mix_3 = nodes.new("ShaderNodeMixRGB")
        mix_3.blend_type = 'ADD'
        mix_3.label = "Mix 2"
        mix_3.location = Vector((-190.0, 300.0))
        mix_3.inputs[0].default_value = 1.0

        tree.links.new(tex_nodes[0].outputs[0], mix_3.inputs[1])
        tree.links.new(mix_2.outputs[0], mix_3.inputs[2])
        tree.links.new(mix_3.outputs[0], shader_out.inputs[0])

        env_map = nodes.new('ShaderNodeGroup')
        env_map.node_tree = get_utility_group(name="SphereMap_Alt")
        env_map.location += Vector((-1400.0, (300 - 2 * 325.0)))

        tree.links.new(env_map.outputs[0], tex_nodes[-1].inputs[0])
        tree.links.new(mix_0.outputs[0], shader_out.inputs[4])

        shader_out.inputs[4].default_value = 1.0
        # shader_out.inputs[7].default_value = 0.5

        tex_nodes[-1].projection = 'SPHERE'

    elif shader_info[0] == "TwoLayerDiffuse":
        tex_nodes[0].location = Vector((-475.0, 150.0))
        tex_nodes[1].location = Vector((-750.0, 200.0))
        tex_nodes[1].extension = 'CLIP'

        map_node = nodes.new("ShaderNodeUVMap")
        map_node.location += Vector((-950.0, 60.0))
        map_node.uv_map = "UV2Map"

        tree.links.new(map_node.outputs[0], tex_nodes[1].inputs[0])

        v_colors = nodes.new("ShaderNodeVertexColor")
        v_colors.layer_name = 'vcols_1'
        v_colors.location += Vector((-1000.0, 300))

        mix_0 = nodes.new("ShaderNodeMath")
        mix_0.operation = 'MULTIPLY'
        mix_0.label = 'Mix 0'
        mix_0.location += Vector((-450.0, 335.0))
        mix_0.inputs[0].default_value = 1.0

        tree.links.new(v_colors.outputs[1], mix_0.inputs[0])
        tree.links.new(tex_nodes[1].outputs[1], mix_0.inputs[1])

        mix_1 = nodes.new("ShaderNodeMixRGB")
        mix_1.location += Vector((-190.0, 300.0))
        mix_1.label = "Mix 1"
        mix_1.blend_type = 'MIX'

        if group_type == 2:
            tree.links.new(tex_nodes[0].outputs[0], mix_1.inputs[2])
            tree.links.new(tex_nodes[1].outputs[0], mix_1.inputs[1])
        else:
            tree.links.new(tex_nodes[0].outputs[0], mix_1.inputs[1])
            tree.links.new(tex_nodes[1].outputs[0], mix_1.inputs[2])

        tree.links.new(mix_1.outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "TwoLayerEnvMetal":

        tex_nodes[0].location = Vector((-1000.0, 120.0))
        tex_nodes[1].location = Vector((-620.0, 20.0))
        tex_nodes[2].location = Vector((-1000.0, -160.0))
        tex_nodes[-1].projection = 'SPHERE'

        mix_0 = nodes.new("ShaderNodeMixRGB")
        mix_0.location += Vector((-620.0, 200.0))
        mix_0.label = "Mix 0"
        mix_0.blend_type = 'MIX'
        mix_0.inputs[0].default_value = 1.0

        tree.links.new(tex_nodes[0].outputs[1], mix_0.inputs[0])
        tree.links.new(tex_nodes[0].outputs[0], mix_0.inputs[1])
        tree.links.new(tex_nodes[2].outputs[0], mix_0.inputs[2])

        mix_1 = nodes.new("ShaderNodeMixRGB")
        mix_1.location += Vector((-190.0, 300.0))
        mix_1.label = "Mix 1"
        mix_1.blend_type = 'MIX'

        v_colors = nodes.new("ShaderNodeVertexColor")
        v_colors.layer_name = 'vcols_1'
        v_colors.location = Vector((-380.0, 350.0))

        tree.links.new(v_colors.outputs[1], mix_1.inputs[0])
        tree.links.new(mix_0.outputs[0], mix_1.inputs[1])
        tree.links.new(tex_nodes[1].outputs[0], mix_1.inputs[2])
        tree.links.new(mix_1.outputs[0], shader_out.inputs[0])

        env_map = nodes.new('ShaderNodeGroup')
        env_map.node_tree = get_utility_group(name="SphereMap_Alt")
        env_map.location += Vector((-1200.0, -320.0))

        tree.links.new(env_map.outputs[0], tex_nodes[-1].inputs[0])

    elif shader_info[0] == "TwoLayerTerrain":

        v_colors = nodes.new("ShaderNodeVertexColor")
        v_colors.layer_name = 'vcols_1'
        v_colors.location += Vector((-800.0, 0.0))

        mix_node = nodes.new("ShaderNodeMixRGB")
        mix_node.location += Vector((-600.0, 0.0))
        mix_node.label = "TwoLayerTerrain"
        mix_node.blend_type = 'ADD'
        mix_node.inputs[0].default_value = 0.0

        map_node = nodes.new("ShaderNodeUVMap")
        map_node.location += Vector((-1800.0, 0.0))
        map_node.uv_map = "UV2Map"
        tree.links.new(map_node.outputs[0], tex_nodes[1].inputs[0])

        tree.links.new(tex_nodes[0].outputs[0], mix_node.inputs[2])
        tree.links.new(tex_nodes[1].outputs[0], mix_node.inputs[1])

        tree.links.new(mix_node.outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "DiffuseEmissive":
        tex_nodes[0].location = Vector((-290.0, 260.0))
        tex_nodes[1].location = Vector((-780.0, -137.0))

        v_colors = nodes.new("ShaderNodeVertexColor")
        v_colors.layer_name = 'vcols_1'
        v_colors.location = Vector((-520.0, -300.0))

        mix_0 = nodes.new("ShaderNodeMath")
        mix_0.operation = 'MULTIPLY'
        mix_0.label = "Mix 0"
        mix_0.location = Vector((-360.0, -180.0))
        mix_0.inputs[0].default_value = 1.0

        tree.links.new(tex_nodes[1].outputs[1], mix_0.inputs[0])
        tree.links.new(v_colors.outputs[1], mix_0.inputs[1])

        mix_1 = nodes.new("ShaderNodeMixRGB")
        mix_1.blend_type = 'MULTIPLY'
        mix_1.label = "Mix 1"
        mix_1.location = Vector((-190.0, -40.0))
        mix_1.inputs[0].default_value = 1.0

        tree.links.new(tex_nodes[1].outputs[0], mix_1.inputs[1])
        tree.links.new(mix_0.outputs[0], mix_1.inputs[2])

        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])
        tree.links.new(mix_1.outputs[0], shader_out.inputs[17])
        shader_out.inputs[18].default_value = 2.0

    elif shader_info[0] == "waterWindow":
        tex_nodes[0].location = Vector((-475.0, 220.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[17])
        tree.links.new(tex_nodes[0].outputs[1], shader_out.inputs[18])

    elif shader_info[0] == "MaskedEnvMetal":
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "EnvMetalEmissive":

        mix_node = nodes.new("ShaderNodeMixRGB")
        mix_node.location += Vector((-600.0, 0.0))
        mix_node.label = "EnvMetal"
        mix_node.blend_type = 'ADD'

        env_map = nodes.new('ShaderNodeGroup')
        env_map.node_tree = get_utility_group(name="SphereMap_Alt")
        env_map.location += Vector((-1400.0, (300 - 2 * 325.0)))

        tree.links.new(env_map.outputs[0], tex_nodes[-1].inputs[0])

        # Tex 1 Alpha and Color
        tree.links.new(tex_nodes[0].outputs[1], mix_node.inputs[0])
        tree.links.new(tex_nodes[0].outputs[0], mix_node.inputs[1])

        # Tex 2 Color
        tree.links.new(tex_nodes[1].outputs[0], mix_node.inputs[2])

        tree.links.new(mix_node.outputs[0], shader_out.inputs[0])

        tex_nodes[-1].projection = 'SPHERE'

    elif shader_info[0] == "TwoLayerDiffuseOpaque":
        tex_nodes[0].location = Vector((-860.0, 40.0))
        tex_nodes[1].location = Vector((-660.0, 500.0))

        v_colors = nodes.new("ShaderNodeVertexColor")
        v_colors.layer_name = 'vcols_1'
        v_colors.location += Vector((-760.0, 220.0))

        mix_0 = nodes.new("ShaderNodeMath")
        mix_0.operation = 'MULTIPLY'
        mix_0.label = ("Mix 0")
        mix_0.location += Vector((-560.0, 220.0))
        mix_0.inputs[0].default_value = 1.0

        tree.links.new(v_colors.outputs[1], mix_0.inputs[0])
        tree.links.new(tex_nodes[0].outputs[1], mix_0.inputs[1])

        mix_1 = nodes.new("ShaderNodeMixRGB")
        mix_1.location += Vector((-190.0, 300.0))
        mix_1.label = "Mix 1"
        mix_1.blend_type = 'MIX'

        tree.links.new(mix_0.outputs[0], mix_1.inputs[0])

        if group_type == 2:
            tree.links.new(tex_nodes[0].outputs[0], mix_1.inputs[2])
            tree.links.new(tex_nodes[1].outputs[0], mix_1.inputs[1])
        else:
            tree.links.new(tex_nodes[0].outputs[0], mix_1.inputs[1])
            tree.links.new(tex_nodes[1].outputs[0], mix_1.inputs[2])

        tree.links.new(mix_1.outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "submarineWindow":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "TwoLayerDiffuseEmissive":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "DiffuseTerrain":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "AdditiveMaskedEnvMetal":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "TwoLayerDiffuseMod2x":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "TwoLayerDiffuseMod2xNA":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "TwoLayerDiffuseAlpha":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "Lod":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "Parallax":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])














        # the rest is for m2, eliding
        # else:
        #     limit = len(self.bl_obj.material_slots) - 1
        #     # if self.damage_control == True, self.json_tex_units wil be empty.
        #     for unit in self.json_tex_units:
        #         bl_mat = self.bl_obj.material_slots[
        #             min(unit.get("skinSectionIndex"), limit)].material
        #         tree = bl_mat.node_tree

        #         # Lazy check to avoid re-building existing materials
        #         if len(tree.nodes.items()) == 2:
        #             if self.use_m2:
        #                 build_shader(
        #                     unit,
        #                     bl_mat,
        #                     self.json_mats,
        #                     self.json_textures,
        #                     self.json_tex_combos,
        #                     self.base_shader,
        #                     import_container=self,
        #                     anim_combos=self.anim_combos,
        #                 )
        #             else:
        #                 build_shader(
        #                     unit,
        #                     bl_mat,
        #                     self.json_mats,
        #                     self.json_textures,
        #                     self.json_tex_combos,
        #                     self.base_shader,
        #                     import_container=self
        #                 )

        # return True





        # if not load_step:
        #     self.reports.errors.append('Failed to setup materials')

        # progress.leave_substeps("WMO Loaded")

        # return self.reports
