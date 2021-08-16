# thing to import a WoW thing and render. Run with something like:
# blender --factory-startup -noaudio --background --python <this script> -- -o output.png input.blend
import argparse
import math
import os
import re
import sys
from typing import *

import bpy
from mathutils import Euler

sys.path.append(os.getcwd())
from testutil import util


locrot_re = re.compile(r"""
^\s*
(?P<degrad>d|r)?
\(\s*
    (?P<x> -?[\d.]+)
    \s*,\s*
    (?P<y> -?[\d.]+)
    \s*,\s*
    (?P<z> -?[\d.]+)
    \s*
\)\s*$
""", re.VERBOSE)

camera_loc_types = ["", "default", "front", "left"]

def cameraprep_simple(camera: bpy.types.Camera, loc: str) -> None:
    if loc == "front":
        camera.rotation_euler = Euler(
            (math.radians(75), 0, math.radians(75)), 'XYZ')
    elif loc == "left":
        camera.rotation_euler = Euler(
            (math.radians(75), 0, math.radians(15)), 'XYZ')
    else:
        camera.rotation_euler = Euler(
            (math.radians(-90), math.radians(-145), math.radians(0)), 'XYZ')

    bpy.ops.view3d.camera_to_view_selected()


def cameraprep(camera: bpy.types.Camera, loc: str, rot: str) -> None:
    # one of our special cases?
    if loc in camera_loc_types:
        return cameraprep_simple(camera, loc)

    # not special, so do the full thing
    m = locrot_re.match(loc)
    if not m or m.group("degrad") is not None:
        raise ValueError(f"invalid location string: {loc}")

    camera.location.x = float(m.group("x"))
    camera.location.y = float(m.group("y"))
    camera.location.z = float(m.group("z"))


    m = locrot_re.match(rot)
    if not m:
        raise ValueError(f"invalid rotation string: {rot}")
    if m:
        x = float(m.group("x"))
        y = float(m.group("y"))
        z = float(m.group("z"))

    # convert to radians if we're not already there
    if m.group("degrad") != "r":
        x = math.radians(x)
        y = math.radians(y)
        z = math.radians(z)

    camera.rotation_euler = Euler((x, y, z), 'XYZ')


def sceneprep(args) -> None:
    # bpy.ops.object.light_add(type='SUN', radius=1, align='WORLD',
    #                          location=(0, 0, 0), scale=(1, 1, 1))

    bpy.ops.object.select_all(action='SELECT')

    # Stupid trick -- have it do the camera_view_to_selected with  a slightly
    # zoomed lens, then zoom it out to what we really want to be at, and we
    # get a little buffer on the edges of the image
    camera = util.add_camera(lens_length=52.0)

    cameraprep(camera, args.cameraloc, args.camerarot)

    camera.data.lens = 50.0

    # FIXME: Should this be configurable?
    camera.data.clip_end = 100000

    # Black presumably lets us see everything without any external light/color,
    # though we might want to use medium grey?
    # util.build_background(bpy.context.scene.world, rgba=(0.0, 0.0, 0.0, 1.0))
    util.build_background(bpy.context.scene.world, bg_rgb=(
        0.0, 0.0, 0.0, 1.0), light_rgb=(1.0, 1.0, 1.0, 1.0), light_strength=1.0)

    # find a better way to do this, since this is a silly return value
    return camera


def dorender(args):
    camera = sceneprep(args)
    # set a nonzero frame so that animated UVs that aren't animating will
    # get caught
    bpy.context.scene.frame_set(50)

    # util.set_cycles_renderer(bpy.context.scene, camera, num_samples=16,
    #                          use_denoising=False, use_transparent_bg=False)
    util.set_cycles_renderer(bpy.context.scene)
    util.set_render_properties(bpy.context.scene, camera, num_samples=16,
                               use_denoising=False, use_transparent_bg=False)
    util.set_output_properties(scene=bpy.context.scene,
                               resolution_percentage=100, output_file_path=args.output)

    # Update the tile size as one of the last things we do, after everything
    # is prepped and ready to render.
    # FIXME: abstract this better
    bpy.ops.render.autotilesize_set()

    tsize = f"{bpy.context.scene.render.tile_x},{bpy.context.scene.render.tile_y}"
    print(
        f"Starting render with tile size ({tsize})")
    bpy.ops.render.render(animation=False, write_still=True,
                          use_viewport=False)


def parse_arguments(args):
    parser = argparse.ArgumentParser(
        prog="wowbject_render",
        description="A tool for importing and rendering WoW objects for testing",
    )

    parser.add_argument(
        "--verbose",
        action='store_const',
        const=True,
        default=False,
    )

    parser.add_argument(
        "--debug",
        action='store_const',
        const=True,
        default=False,
        # help="Read objects and prepare them for decimation",
    )

    parser.add_argument(
        "--cameraloc",
        action='store',
        type=str,
        required=False,
        default="default",

        help="location camera should be placed (see source for valid options)",
    )

    parser.add_argument(
        "--camerarot",
        action='store',
        type=str,
        required=False,
        default="default",

        help="rotation camera should have when placed (see source for valid options)",
    )

    # FIXME: make output name automatic if not specified
    parser.add_argument(
        "--output",
        "-o",
        action='store',
        type=str,
        # required=True,

        help="file to output resulting render to",
    )

    parser.add_argument(
        "--ping",
        action='store_const',
        const=True,
        default=False,

        help="print PONG and exit (for testing)"
    )

    parser.add_argument(
        "--noexit",
        "--no-exit",
        action='store_true',
        default=False,
        help="run Blender in foreground and don't exit",
    )

    parser.add_argument(
        "file",
        action='store',
        nargs='?',
        help="input file to be processed",
    )

    args = parser.parse_args(args)

    return args


def main(argv):
    # world = bpy.context.scene.world
    # world.use_nodes = True
    # node_tree = world.node_tree

    # mix_node = node_tree.nodes.new(type="ShaderNodeMixShader")
    # import inspect

    # for i in inspect.getmembers(mix_node):
    #     if not i[0].startswith('_'):
    #         # Ignores methods
    #         if not inspect.ismethod(i[1]):
    #             print(i)
    # sys.exit(0)

    # try:
    if (("--" in argv) == False):
        print("Usage: blender --factory-startup --background --python thisfile.py "
              "-- -o output.png input.obj")
        sys.exit(1)

    # chop argv down to just our arguments
    args_start = argv.index("--") + 1
    argv = argv[args_start:]

    args = parse_arguments(argv)

    if args.ping:
        print("PONG")
        sys.exit(0)

    if not args.output or not args.file:
        print("error: the following arguments are required: --output/-o, file", file=sys.stderr)
        sys.exit(1)

    util.init_blender()
    util.delete_all()

    print("STARTING WOWBJECT IMPORT")
    util.load_wowobj(args.file)
    print("COMPLETED WOWBJECT IMPORT SUCCESSFULLY")

    print("STARTING WOWBJECT RENDER")
    dorender(args)
    print("COMPLETED WOWBJECT RENDER SUCCESSFULLY")
    # except:
    #     print("Exception caught")
    #     sys.exit(2)

    if not args.noexit:
        sys.exit(0)


if __name__ == "__main__":
    main(sys.argv)
