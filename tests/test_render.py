#!/usr/bin/env python3
import collections
import csv
import os
import posixpath
import pprint
import re
import subprocess
import sys

from typing import *

import pytest
from pytest_html import extras

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


# returns from an underlying check
CheckReturn = collections.namedtuple(
    "CheckReturn", ["param", "success", "failmsg"])


def mktestid(category, subcategory, test_name):
    """make id for a test based on category, (optional) subcategory, and test name"""
    if subcategory is None or len(subcategory) == 0:
        return str.join("_", [category, test_name])
    else:
        return str.join("_", [category, subcategory, test_name])


# Just gives us the name of the blender executable, which is configurable
# with the --blender-exe command line option
@pytest.fixture()
def blender_exe(pytestconfig):
    """Gives the name of the blender executable (set w/ --blender-exe)"""
    return pytestconfig.getoption("blender_executable")


@pytest.mark.tryfirst
def test_blender_exe(blender_exe):
    """Test to verify that blender works, before running tests depending on it"""
    success, failmsg = run_blender_python(
        "wowbject_render.py",
        ["--ping"],
        blender_exe=blender_exe,
    )

    # is this the best way to abort everything if we can't run blender?
    if not success:
        pytest.exit(f"couldn't exec blender with executable '{blender_exe}'")


def run_blender_python(scriptpath: str, scriptargs: List[str],
                       timeout: int = 60, blender_exe: str = "blender"):
    """Run a python script with blender, with optional script arguments"""
    blender_args = [
        blender_exe,
        "--background",
        "-noaudio",
        "--factory-startup",
        "--python-exit-code", "88",
        "--python",
        scriptpath,
        "--",
    ] + scriptargs

    print("Executing blender: ", str.join(" ", blender_args))

    success = True
    failmsg = None

    try:
        subprocess.run(blender_args, stdin=None, timeout=timeout, check=True)

    except (subprocess.CalledProcessError) as e:
        t = type(e).__name__

        success = False
        failmsg = f"blender import/rendering failed ({t})"

    except (OSError) as e:
        t = type(e).__name__

        success = False
        failmsg = f"error executing blender: {t} - {e}"


    return success, failmsg


# FIXME: Use PIL here instead, maybe?
#
# output format being parsed:
#
#   Image Difference(MeanAbsoluteError):
#              Normalized    Absolute
#             ============  ==========
#        Red: 0.0509441923     3338.6
#      Green: 0.0482937613     3164.9
#       Blue: 0.0434155269     2845.2
#    Opacity: 0.0000000000        0.0
#      Total: 0.0356633701     2337.2
compare_re = re.compile(r"""
    \s*
    (?P<field>Red|Green|Blue|Opacity|Total):
    \s+
    (?P<normalized>[0-9.]+)
    \s+
    (?P<absolute>[0-9.]+)
""", re.VERBOSE)

def parse_gm_compare(output: str):
    """Parse the output of 'gm compare' and return a map with the values"""
    ret = {}
    for line in output.split("\n"):
        m = compare_re.search(line)

        # Not a line we care about
        if not m:
            continue

        ret[m.group("field")] = float(m.group("normalized"))

    if len(ret.keys()) != 5:
        raise ValueError("gm command output parse failure")

    return ret


def compare_images(refimg: str, checkimg: str, diffimg: str = None,
                   timeout: int = 10):
    """Compare two images for similarity and assert based on a threshold"""
    gm_bin = "gm"
    gm_args = [
        gm_bin,
        "compare",
        "-highlight-style",
        "assign",
        # "xor",
        "-metric",
        "MAE",
        refimg,
        checkimg,
    ]

    assert os.path.exists(
        refimg), f"comparison image '{refimg}' does not exist"
    assert os.path.exists(
        checkimg), f"comparison image '{checkimg}' does not exist"

    # Does this arg need a better name?
    if diffimg:
        gm_args += ["-file", diffimg]

    try:
        res = subprocess.run(gm_args, stdin=None, check=True, timeout=timeout,
                             capture_output=True, text=True)

    except (subprocess.CalledProcessError, OSError) as e:
        # If I don"t raise a new exception from None, pytest tries to show us
        # the origin of the error inside the subprocess module, and that"s
        # pretty useless.
        t = type(e).__name__
        raise Exception(f"{t}: {e}") from None

    return parse_gm_compare(res.stdout)


valid_marks = {
    # Needs to be kept in sync with pytest.ini  (grrf)
    "m2": pytest.mark.m2,
    "wmo": pytest.mark.wmo,
    "top10m2": pytest.mark.top10m2,
    "top10wmo": pytest.mark.top10wmo,
    "top10": pytest.mark.top10,
    "fancy": pytest.mark.fancy,
    "bug": pytest.mark.bug,
    "superfast": pytest.mark.superfast,
    "test": pytest.mark.test,

    # built-in marks, do not need to be in sync with pytest.ini
    "xfail": pytest.mark.xfail,
    "skip": pytest.mark.skip,
    "knownfail": pytest.mark.xfail(reason="Known currently broken", run=False)
}


# I'm not exactly thrilled with how multi-image tests are set up, but here's
# at least a defense of why it is as it is...   --A
#
# So, there are times we want to do tests of things, where we want to render
# multiple images from the same import. Right now, "import obj + render scene +
# compare image" is a single pair of pytest steps (one for import + render, one
# for compare). If we wanted to have a separate pair of tests for every
# individual image in a set of N, we would have to import the scene N separate
# times, which isn't so bad for small imports, but sucks for something like,
# say, Stormwind. And since there's not really a way (currently) to have
# separate tests that all work off the same blender instance, that's our
# only choie if we want separate tests. That sucks.
#
# So, instead, we need to make things so that one 'test' can render multiple
# images, and compares all of them. This sucks because only the entire test
# will end up failing (or not), but it's the best I can figure out right now,
# without having the test suite run entirely within Blender (which is damned
# tempting, tbh)
#
# The way this ends up working is if a test in the CSV has no category but
# has a camera location specified for it, the camera info will be added to
# the camera info for the previous test (etc), and passed as a list to all
# the various code. And then the various code has special cases for outputting
# and checking the whatever_imgXX.png results. It'll do, but man some of the
# special-case code makes things long-winded in places.
def tlist():
    """Generate a list of image-generation tests and associated parameters"""
    tests = []
    with open("testlist.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile, dialect='excel')

        for test in reader:
            # no category && no camera location == no test on this line
            if not test["category"] and not test["cameraloc"]:
                continue

            # no category && yes cameraloc == multi-image test
            if not test["category"]:
                prev = tests[-1]

                # Convert camera loc & rot to lists if they're not
                if not isinstance(prev["cameraloc"], list):
                    prev["cameraloc"] = [prev["cameraloc"]]
                if not isinstance(prev["camerarot"], list):
                    prev["camerarot"] = [prev["camerarot"]]

                # FIXME: should probably check to make sure both fields set
                prev["cameraloc"].append(test["cameraloc"])
                prev["camerarot"].append(test["camerarot"])

                # We're just adjusting an existing test, no need to do more
                # processing, just go to next line
                continue

            # convert our flags text list into a real boy^W list^W set
            textflags = test["flags"]
            test["flags"] = set()
            for flag in textflags.split(","):
                if len(flag) > 0:
                    test["flags"].add(flag)

            # done, add the test to the list to be marked and shipped
            tests.append(test)

        # We have all our tests (and multi-image subtests), add metadata
        marked_tests = []

        for test in tests:
            marks = []

            # set marks based on categories, where those marks exist
            cat = test["category"]
            if cat in valid_marks:
                marks.append(valid_marks[cat])

            # set marks based on explicit "marks" column of CSV
            m = test["marks"].split(",")
            if len(m) > 0:
                for mark in m:
                    if mark in valid_marks:
                        marks.append(valid_marks[mark])

            # generate an id for the test
            id = mktestid(test['category'], test['subcategory'],
                          test['test_name'])
            test['id'] = id

            # done with this test, add it to the list and move on
            marked_tests.append(pytest.param(test, marks=marks, id=id))

    return marked_tests


# t_render is automatically run as a fixture, with its return value being
# a named tuple with 'success' and 'failure message' fields. All the work
# for this test is done in that fixture, with the test itself just checking
# for success.
def test_render(t_render, extra):
    """Validate a test render happens without error"""
    success = t_render.success

    assert success, t_render.failmsg

    r = t_render.param
    id = r['id']
    # Not sure how to display images if it's a multi-image
    if not isinstance(r["cameraloc"], list):
        imgpath = os.path.join("render_results", f"{id}.png")
        extra.append(caption_png_extra(imgpath, "Rendered Image"))



def checkimage(refimg, checkimg, diffimg):
    """Verify we have a reference image and compare to test render"""
    if not os.path.exists(refimg):
        pytest.skip(f"no reference image {refimg}")

    if not os.path.exists(checkimg):
        pytest.skip(f"no image to check {checkimg}")

    return compare_images(refimg=refimg, checkimg=checkimg, diffimg=diffimg)


def caption_png_extra(img, caption):
    img_html = f"""
    <div class="image">
        <a href="{img}">
            <img src="{img}" />
        </a>
        <div class="caption">
            {caption}
        </div>
    </div>
    """

    return extras.html(img_html)

def test_render_check(t_render, extra):
    "Verify the result of a test render looks like it's expected to look"
    threshold = 0.00001
    r = t_render.param

    if "norender" in r["flags"]:
        pytest.skip("import-only (--no-render) test, nothing to check")

    if not t_render.success:
        pytest.skip("image render failed, nothing to check")

    knownbad = "badrender" in r["flags"]
    assert not knownbad, "known bad render, not running comparison"

    id = r["id"]

    if isinstance(r["cameraloc"], list):
        fn = f"{id}_img%02d.png"
        # cameraloc = ",".join(r["cameraloc"])
        # camerarot = ",".join(r["camerarot"])
        # outimg = os.path.join("render_results", f"{fn}_img%02d.png")

        for i in range(1, len(r["cameraloc"]) + 1):
            refimg = os.path.join("render_references_temp_test", fn % (i))
            checkimg = os.path.join("render_results", fn % (i))
            diffimg = os.path.join("render_diffs", fn % (i))

            compared = checkimage(refimg, checkimg, diffimg)

            # FIXME: verify the filename/test name/subname is visible in the assert
            difference = compared["Total"]
            assert difference <= threshold, f"image difference {difference} greater than threshold {threshold}"

            # if we didn't assert, get rid of the difference image
            if os.path.exists(diffimg):
                os.remove(diffimg)

    else:
        refimg = os.path.join("render_references_temp_test", f"{id}.png")
        checkimg = os.path.join("render_results", f"{id}.png")
        diffimg = os.path.join("render_diffs", f"{id}.png")

        compared = checkimage(refimg, checkimg, diffimg)


        difference = compared["Total"]
        if difference > threshold:
            # extra.append(extras.png(diffimg, name="Images Diff"))
            # extra.append(extras.png(checkimg, name="Rendered Image"))
            # extra.append(extras.png(refimg, name="Reference Image"))
            extra.append(caption_png_extra(diffimg, "Image Diff"))
            extra.append(caption_png_extra(checkimg, "Rendered Image"))
            extra.append(caption_png_extra(refimg, "Reference Image"))

        assert difference <= threshold, f"image difference {difference} greater than threshold {threshold}"

        extra.append(caption_png_extra(checkimg, "Rendered Image"))
        extra.append(caption_png_extra(refimg, "Reference Image"))


@pytest.fixture(scope="module", params=tlist())
def t_render(request):
    """test fixture that performs a test render on a test from our test list"""
    r = request.param

    # normalize our input file path, and make sure it exists
    objdata = os.path.join(
        "test_data", r["obj_file"].replace(posixpath.sep, os.sep))
    assert os.path.exists(objdata), f"no source file '{objdata}'"

    id = mktestid(r['category'], r['subcategory'], r['test_name'])

    # if we have multiple cameras, generate a "template" output filename and
    # a list of camera parameters, otherwise just use a straight output
    # filename and normal camera params.
    #
    # Also, remove any existing output images of the same names, first, so
    # that we don't end up accidentally comparing against the wrong image if
    # something goes wrong and doesn't get caught at this stage.
    if isinstance(r["cameraloc"], list):
        cameraloc = ",".join(r["cameraloc"])
        camerarot = ",".join(r["camerarot"])
        outimg = os.path.join("render_results", f"{id}_img%02d.png")

        for i in range(1, len(r["cameraloc"]) + 1):
            checkfn = outimg % (i)
            if os.path.exists(checkfn):
                os.remove(checkfn)

    else:
        cameraloc = r["cameraloc"]
        camerarot = r["camerarot"]
        outimg = os.path.join("render_results", f"{id}.png")

        if os.path.exists(outimg):
            os.remove(outimg)


    # Call the render script w/ blender + our arguments
    success, failmsg = run_blender_python(
        "wowbject_render.py",
        [
            "--cameraloc", cameraloc, "--camerarot", camerarot,
            "-o", outimg, objdata,
        ]
    )

    # This clears stdout/stderr captures, so that we don't get the blender
    # output if something fails further along (is there a better way to
    # do this? (does this even work?)
    # if success:
    #     capsys.readouterr()

    return CheckReturn(r, success, failmsg)
