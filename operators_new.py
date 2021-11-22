
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
import os
import sys
from math import radians

from pathlib import Path
from typing import (TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple, Union, cast)

from bpy_extras.io_utils import ImportHelper


from .lookup_funcs import wmo_read_color, wmo_read_group_flags
from .node_groups import do_wmo_combiner, get_utility_group
from .preferences import WoWbject_ObjectProperties, get_prefs
from .wbjtypes import JsonWmoGroup, JsonWmoMetadata
from .import_wmo import import_wmo

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

    json_group: JsonWmoGroup
    group_offset: int

    json_batches: List[Any]  # FIXME: type
    batch_count: int

    colors: List[List[int]]

    def __init__(self) -> None:
        self.mesh_data = None
        self.mesh_batches = []

        self.json_group = None  # type: ignore
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
        directory: str
    else:
        directory: bpy.props.StringProperty(subtype='DIR_PATH')

    filename_ext = '.obj'
    if TYPE_CHECKING:
        filter_glob: str
    else:
        filter_glob: bpy.props.StringProperty(default='*.obj')

    if TYPE_CHECKING:
        files: bpy.types.Collection
    else:
        files: bpy.props.CollectionProperty(
            name='File Paths',
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

    if TYPE_CHECKING:
        do_coverage: bool
    else:
        do_coverage: bpy.props.BoolProperty(
            name="Code Coverage Analysis",
            description="Use pycoverage to analyze code coverage",
            default=False
        )

    if TYPE_CHECKING:
        do_profiling: bool
    else:
        do_profiling: bpy.props.BoolProperty(
            name="Code Profiling",
            description="Profile import execution with cProfile",
            default=False
        )


    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        box = layout.box()
        box.label(text="Basic Options:")

        # FIXME: Do we want rename anymore? Especially since we (theoretically?)
        # subbox = box.box()
        # support multi-import now?
        # subbox.label(text="Rename to:")
        # subbox.prop(self, 'name_override', text="")

        box.prop(self, 'reuse_materials')
        box.prop(self, 'merge_verts')
        box.prop(self, 'make_quads')
        box.prop(self, 'use_collections')

        box = layout.box()
        box.label(text="Shading:")
        box.prop(self, 'base_shader', text="Shader", expand=False)
        box.prop(self, 'use_vertex_lighting', expand=False)



        box = layout.box()
        box.label(text="Developer:")

        box.prop(self, 'do_coverage')
        box.prop(self, 'do_profiling')


    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> Union[Set[str], Set[int]]:
        prefs = get_prefs()
        default_dir = prefs.default_dir
        if not default_dir == "":
            self.directory = default_dir
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


    def execute(self, context: bpy.types.Context) -> Union[Set[str], Set[int]]:
        if len(self.files) == 0 and self.filepath:
            self.import_file(context, self.filepath)
            return {'FINISHED'}

        # else
        for file in self.files:
            filepath = os.path.join(self.directory, file.name)
            self.import_file(context, filepath)

        return {'FINISHED'}


    # FIXME: should this be a method, or a standalone function?
    def import_file(self, context: bpy.types.Context, filepath: str) -> Union[Set[str], Set[int]]:
        print(f"IMPORTING {filepath}")
        # FIXME: not sure what the best type for args actually is
        args: Dict[str, bpy.types.Property] = self.as_keywords(
            ignore=("filter_glob", "directory", "filepath", "files"))

        if self.do_coverage and self.do_profiling:
            print("WARNING: code coverage and code profiling both enabled, results will be inaccurate")
        self.do_coverage = False
        if self.do_coverage:
            print("Performing code coverage analysis")
            import coverage
            cov = coverage.Coverage(source=["."], omit=["tests", "addon_updater*"])
            cov.start()

        if self.do_profiling:
            print("Performing code profiling")
            import cProfile
            import pstats
            pr = cProfile.Profile()
            pr.enable()

        do_import(context, filepath, self.reuse_materials, str(self.base_shader), args)

        if self.do_profiling:
            pr.disable()
            prof_savedir = os.path.join(os.path.dirname(__file__), "prof")
            prof_modelname = os.path.basename(filepath)
            prof_savepath = os.path.join(prof_savedir, f"{prof_modelname}.prof")
            if not os.path.exists(prof_savedir):
                os.mkdir(prof_savedir)

            ps = pstats.Stats(pr, stream=sys.stdout).sort_stats('cumulative')
            print("")
            print("Partial profiling results:")
            print("")
            ps.print_stats(20)

            pr.dump_stats(prof_savepath)
            print("")
            print(f"Saved code profiling data to {prof_savepath}")
            print(f"View with: snakeviz \"{prof_savepath}\"")

        if self.do_coverage:
            cov.stop()
            cov.save()
            cov_savepath = os.path.join(os.path.dirname(__file__), "covhtml")
            cov_htmlpath = os.path.join(cov_savepath, "index.html")
            cov.html_report(directory=cov_savepath)
            print(f"Saved coverage analysis to {cov_htmlpath}")

        return {'FINISHED'}


# FIXME: roll reuse_mats and base_shader into op_args
def do_import(context: bpy.types.Context, filepath: str, reuse_mats: bool, base_shader: str, op_args: Dict[str, Any]) -> None:
    '''
    The pre-sorting and initializing function called by the import operator.
    Most of the actual data-handling is handled by an import_container object.
    '''

    file = Path(filepath)

    if file.with_suffix(".json").exists():
        with file.with_suffix(".json").open() as p:
            # FIXME: error handling here
            json_config = json.load(p)
    else:
        # FIXME: user-facing error handling
        print(f"failed to load metadata from '{file}', can't continue")
        return

    if not json_config:
        # FIXME: user-facing error handling
        print(f"failed to load metadata file {file.with_suffix('.json')}")
        return


    if ".wmo" in json_config["fileName"]:
        import_wmo(context, filepath, reuse_mats, base_shader, op_args)
    else:
        print("ERROR: trying to import an unsupported file type")
