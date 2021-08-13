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

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

def run_blender_python(scriptpath: str, scriptargs: List[str], timeout: int = 60, stdin=None):
    blender_bin = "blender"
    blender_args = [
        blender_bin,
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
        # subprocess.run(blender_args, stdin=stdin, stdout=testlog,
        #                stderr=testlog, timeout=timeout, check=True)
        subprocess.run(blender_args, stdin=stdin,
                       timeout=timeout, check=True)

    except (subprocess.CalledProcessError) as e:
        # If I don"t raise a new exception from None, pytest tries to show us
        # the origin of the error inside the subprocess module, and that"s
        # pretty useless.
        t = type(e).__name__
        # raise Exception(f"blender import/rendering failed ({t})") from None
        success = False
        failmsg = f"blender import/rendering failed ({t})"

    except (OSError) as e:
        t = type(e).__name__
        # raise Exception(f"error executing blender: {t} - {e}") from None
        success = False
        failmsg = f"error executing blender: {t} - {e}"

    # assert success, failmsg
    #
    # FIXME: This apparently doesn't work? Things that render but don't
    # compare ok still return the blender output?
    # capsys.readouterr()

    return success, failmsg


compare_re = re.compile(r"""
    \s*
    (?P<field>Red|Green|Blue|Opacity|Total):
    \s+
    (?P<normalized>[0-9.]+)
    \s+
    (?P<absolute>[0-9.]+)
""", re.VERBOSE)

def parse_gm_compare(output: str):
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


def compare_images(refimg: str, checkimg: str, diffimg: str = None, threshold: float = 0.0, timeout: int = 10):
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
        res = subprocess.run(gm_args, stdin=None, check=True,
                             capture_output=True, text=True)

    except (subprocess.CalledProcessError, OSError) as e:
        # If I don"t raise a new exception from None, pytest tries to show us
        # the origin of the error inside the subprocess module, and that"s
        # pretty useless.
        t = type(e).__name__
        raise Exception(f"{t}: {e}") from None

    compared = parse_gm_compare(res.stdout)

    assert compared["Total"] <= threshold, "image difference exceeds threshold"

    # if we tested ok, delete the diff image
    if os.path.exists(diffimg):
        os.remove(diffimg)


def tlist(category=None):
    with open("testlist.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile, dialect='excel')
        if category:
            tests = [v for v in reader if v["category"] == category]
        else:
            tests = [v for v in reader]
        # tests = [v for v in reader]

    return tests


def test_render(t_render):
    r = t_render.param
    success = t_render.success

    assert success, t_render.failmsg


def test_render_check(request, t_render):
    r = t_render.param
    fn = mkname(r['category'], r['subcategory'], r['test_name'])

    refimg = os.path.join("render_references", f"{fn}.png")
    checkimg = os.path.join("render_results", f"{fn}.png")
    diffimg = os.path.join("render_diffs", f"{fn}.png")

    if not os.path.exists(refimg):
        pytest.skip(f"no image {refimg}")

    if not os.path.exists(checkimg):
        pytest.skip(f"no image {checkimg}")

    compare_images(refimg=refimg, checkimg=checkimg, diffimg=diffimg,
                   threshold=0.00001)


def mkname(category, subcategory, test_name):
    if subcategory is None or len(subcategory) == 0:
        return str.join("_", [category, test_name])
    else:
        return str.join("_", [category, subcategory, test_name])


def idfn(fv):
    return mkname(fv['category'], fv['subcategory'], fv['test_name'])


# @pytest.fixture(params=tlist(), ids=idfn)
# def t_render(request):
#     r = request.param

#     fn = str.join("_", [r['category'], r['subcategory'], r['test_name']])
#     obj = r["obj_file"].replace(posixpath.sep, os.sep)
#     run_blender_python(
#         "wowbject_render.py",
#         [
#             "-o", os.path.join("render_results", f"{fn}.png"),
#             os.path.join("test_data", obj),
#         ]
#     )

#     compare_renders(os.path.join("render_references", f"{fn}.png"),
#                     os.path.join("render_results", f"{fn}.png"),
#                     os.path.join("render_diffs", f"{fn}.png"))

RenderReturn = collections.namedtuple(
    "RenderReturn", ["param", "success", "failmsg"])

@pytest.fixture(params=tlist(), ids=idfn)
def t_render(request, capsys):
    r = request.param

    fn = mkname(r['category'], r['subcategory'], r['test_name'])
    outimg = os.path.join("render_results", f"{fn}.png")

    if os.path.exists(outimg):
        os.remove(outimg)

    objdata = os.path.join(
        "test_data", r["obj_file"].replace(posixpath.sep, os.sep))
    assert os.path.exists(objdata), f"no source file '{objdata}'"

    success, failmsg = run_blender_python(
        "wowbject_render.py",
        ["-o", outimg, objdata, ]
    )

    # This clears stdout/stderr captures, so that we don't get the blender
    # output if something fails further along (is there a better way to
    # do this?)
    if success:
        capsys.readouterr()

    # just give the whole test blob back
    return RenderReturn(r, success, failmsg)
