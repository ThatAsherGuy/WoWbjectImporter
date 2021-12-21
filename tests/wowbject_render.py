# thing to import a WoW thing and render. Run with something like:
# blender --factory-startup -noaudio --background --python <this script> -- -o output.png input.blend
import argparse
import math
import os
import re
import sys
import time
from typing import *

import bpy
from mathutils import Euler

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from testutil import util


def now() -> float:
    """Return the current time, in epoch time, as a float"""
    return float(time.time())


def camera_reset(camera: bpy.types.Camera):
    """Reset the camera to a fixed position and rotation"""
    camera.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')
    camera.location.x = 0.0
    camera.location.y = 0.0
    camera.location.z = 0.0


locseries_re = re.compile(r"""
# Either of the following
(
    # location or rotation, keywords
    (?P<keyword>default|front|left|right|back|top|bottom)

|   # or

    # location or rotation, xyz
    (?P<degrad>d|r)?
    \(\s*
        (?P<x> -?[\d.]+)
        \s*,\s*
        (?P<y> -?[\d.]+)
        \s*,\s*
        (?P<z> -?[\d.]+)
        \s*
    \)
)
[\s,]*
""", re.VERBOSE)

# Types of 'simple' camera placement currently implemented
camera_loc_types = ["default", "front", "left", "top"]

def camera_set_position_simple(camera: bpy.types.Camera, loc: str) -> None:
    """Position a camera in a 'simple' automatic way useful on many models"""
    if loc not in camera_loc_types:
        raise ValueError(
            f"unimplemented camera location type '{loc}' specified")

    if loc == "front":
        camera.rotation_euler = Euler(
            (math.radians(75), 0, math.radians(75)), 'XYZ')
    elif loc == "left":
        camera.rotation_euler = Euler(
            (math.radians(75), 0, math.radians(15)), 'XYZ')
    elif loc == "top":
        camera.rotation_euler = Euler(
            (0, 0, 0), 'XYZ')
    else:
        camera.rotation_euler = Euler(
            (math.radians(-90), math.radians(-145), math.radians(0)), 'XYZ')

    # Stupid trick -- have it do the camera_view_to_selected with  a slightly
    # zoomed lens, then zoom it out to what we really want to be at, and we
    # get a little buffer on the edges of the image
    #
    # FIXME: We might want to do this less for a larger model. Needs study.
    camera.data.lens = camera.data.lens + 2
    bpy.ops.view3d.camera_to_view_selected()
    camera.data.lens = camera.data.lens - 0


# FIXME: Accepting regex match objects is FUGLY
def camera_set_position(camera: bpy.types.Camera, loc: re.Match, rot: re.Match) -> None:
    """Set camera position and rotation"""

    # is this one of our 'simple' cases?
    if loc.group("keyword"):
        return camera_set_position_simple(camera, loc.group("keyword"))

    # not a 'simple' case, so do the full thing, location first
    if loc.group("degrad") is not None:
        raise ValueError(
            f"invalid location string (includes degrees/radian specifier")

    camera.location.x = float(loc.group("x"))
    camera.location.y = float(loc.group("y"))
    camera.location.z = float(loc.group("z"))

    # and then the rotation
    x = float(rot.group("x"))
    y = float(rot.group("y"))
    z = float(rot.group("z"))

    # convert to radians if we're not already there
    if rot.group("degrad") != "r":
        x = math.radians(x)
        y = math.radians(y)
        z = math.radians(z)

    camera.rotation_euler = Euler((x, y, z), 'XYZ')


def camera_prep(_args, cameraloc, camerarot) -> bpy.types.Camera:
    """Create camera if needed, reset it, and set its location/rotation"""

    # retrieve the existing camera or make a new one
    # FIXME: This should probably store an id and not the actual camera,
    # otherwise blender may crash if memory gets shuffled (I think)
    camera_prep.camera = cast(bpy.types.Camera, getattr(
        camera_prep, 'camera', util.add_camera(lens_length=50.0)))

    camera = camera_prep.camera

    camera.data.clip_end = 100000
    bpy.ops.object.select_all(action='SELECT')
    camera_reset(camera)
    camera_set_position(camera, cameraloc, camerarot)

    # find a better way to do this, since this is a silly return value
    return camera


def dorender(args):
    """Render our test image(s) for this test, based on cli arguments"""

    # set a nonzero frame so that animated UVs that aren't animating will
    # get caught
    bpy.context.scene.frame_set(25)

    # We can add a sun to our render if we need one, but we don't right now
    # bpy.ops.object.light_add(type='SUN', radius=1, align='WORLD',
    #                          location=(0, 0, 0), scale=(1, 1, 1))

    # Set a background. Black presumably lets us see everything without any
    # external light/color, though we might want to use medium grey? The
    # background also emits light (based on light_rgb/light_strength), but
    # that light isn't visible to the camera
    util.build_background(
        bpy.context.scene.world, bg_rgb=(0.0, 0.0, 0.0, 1.0),
        light_rgb=(1.0, 1.0, 1.0, 1.0), light_strength=1.0)

    locs = list(locseries_re.finditer(args.cameraloc))
    rots = list(locseries_re.finditer(args.camerarot))

    # FIXME: Ideally we'd do this before the model was imported, but that
    # would be even fuglier
    if len(locs) != len(rots):
        raise ValueError(f"'loc' and 'rot' lists are of unequal sizes")

    rendercount = 0

    for loc, rot in zip(locs, rots):
        rendercount += 1

        # FIXME: passing the match objects is FUGLY
        camera = camera_prep(args, loc, rot)

        # set output filename, varied depending on whether or not this is
        # a multi-image test
        if len(locs) == 1:
            outfile = args.output
        else:
            outfile = args.output % (rendercount)

        # Make sure our renderer is set up appropriately
        util.set_cycles_renderer(bpy.context.scene)
        util.set_render_properties(bpy.context.scene, camera, num_samples=16,
                                   use_denoising=False, use_transparent_bg=False)
        util.set_output_properties(scene=bpy.context.scene,
                                   resolution_percentage=100, output_file_path=outfile)

        # Update the tile size as one of the last things we do, after everything
        # is prepped and ready to render.
        # FIXME: can we abstract this better?
        # bpy.ops.render.autotilesize_set()
        # tsize = f"{bpy.context.scene.render.tile_x},{bpy.context.scene.render.tile_y}"

        # Do the actual render
        print(f"camera len: {camera.data.lens}")
        # print(
        #     f"Starting render #{rendercount} with tile size ({tsize})")
        print(
            f"Starting render #{rendercount}")
        start_time = now()
        bpy.ops.render.render(animation=False, write_still=True,
                              use_viewport=False)
        render_time = now() - start_time
        print(f"Render complete in {render_time:.02f}s")


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
        "--norender",
        "--no-render",
        action='store_true',
        default=False,

        help="import model but do not render",
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
    if (("--" in argv) == False):
        print("Usage: blender --factory-startup --background --python thisfile.py "
              "-- -o output.png input.obj")
        sys.exit(1)

    # chop argv down to just our arguments (and not blender's)
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

    if args.norender:
        print("SKIPPING RENDER BECAUSE --NO-RENDER WAS SPECIFIED")
    else:
        print("STARTING WOWBJECT RENDER(S)")
        dorender(args)
        print("COMPLETED WOWBJECT RENDER(S) SUCCESSFULLY")

    # exit unless we've been explicitly asked not to (for testing)
    if not args.noexit:
        sys.exit(0)


if __name__ == "__main__":
    main(sys.argv)
