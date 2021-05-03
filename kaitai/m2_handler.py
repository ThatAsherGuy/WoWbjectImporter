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

# This module serves as an abstraction layer between the generated m2.py file and the rest of the add-on
# It's meant to handle things like dependency imports, and a lot of it is based on how DECALMachine handles its PIL install

import importlib
import bpy
import sys
import os
import platform
import site
import subprocess
import mathutils
import math
from ..lookup_funcs import get_interpolation_type

enc = sys.getdefaultencoding()

# Yoinked directly from DECALMachine.
# These are called by load_kaitai(), which'll pull the module for you if the bundled one causes issues.
def get_python_paths():
    pythonbinpath = bpy.app.binary_path_python if bpy.app.version < (2, 91, 0) else sys.executable

    if platform.system() == "Windows":
        pythonlibpath = os.path.join(os.path.dirname(os.path.dirname(pythonbinpath)), "lib")

    else:
        pythonlibpath = os.path.join(os.path.dirname(os.path.dirname(pythonbinpath)), "lib", os.path.basename(pythonbinpath)[:-1])

    ensurepippath = os.path.join(pythonlibpath, "ensurepip")
    sitepackagespath = os.path.join(pythonlibpath, "site-packages")
    usersitepackagespath = site.getusersitepackages()

    easyinstallpath = os.path.join(sitepackagespath, "easy_install.py")
    easyinstalluserpath = os.path.join(usersitepackagespath, "easy_install.py")

    modulespaths = [os.path.join(path, 'modules') for path in bpy.utils.script_paths() if path.endswith('scripts')]

    print("Python Binary: %s %s" % (pythonbinpath, os.path.exists(pythonbinpath)))
    print("Python Library: %s %s" % (pythonlibpath, os.path.exists(pythonlibpath)))
    print("Ensurepip: %s %s\n" % (ensurepippath, os.path.exists(ensurepippath)))

    for path in modulespaths:
        print("Modules: %s %s" % (path, os.path.exists(path)))

    print("Site-Packages: %s %s" % (sitepackagespath, os.path.exists(sitepackagespath)))
    print("User Site-Packages: %s %s" % (usersitepackagespath, os.path.exists(usersitepackagespath)))
    print("EasyInstall Path: %s %s" % (easyinstallpath, os.path.exists(easyinstallpath)))
    print("EasyInstall User Path: %s %s\n" % (easyinstalluserpath, os.path.exists(easyinstalluserpath)))

    return pythonbinpath, pythonlibpath, ensurepippath, modulespaths, sitepackagespath, usersitepackagespath, easyinstallpath, easyinstalluserpath


def do_pip(pythonbinpath, ensurepippath):
    cmd = [pythonbinpath, ensurepippath, "--upgrade"]
    pip = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    pipout = [out.strip() for out in pip.stdout.decode(enc).split("\n") if out]
    piperr = [err.strip() for err in pip.stderr.decode(enc).split("\n") if err]

    if pip.returncode == 0:
        for out in pipout + piperr:
            print(" »", out)

        print("Sucessfully installed pip!\n")
        return True

    else:
        for out in pipout + piperr:
            print(" »", out)

        print("Failed to install pip!\n")
        return False, pipout + piperr


def do_kaitai(pythonbinpath):
    cmd = [pythonbinpath, "-m", "pip", "install", "--upgrade", "kaitaistruct"]

    pil = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    pilout = [out.strip() for out in pil.stdout.decode(enc).split("\n") if out]
    pilerr = [err.strip() for err in pil.stderr.decode(enc).split("\n") if err]

    if pil.returncode == 0:
        for out in pilout + pilerr:
            print(" »", out)

        print("Sucessfully installed Kaitai!\n")
        return True
    else:
        for out in pilout + pilerr:
            print(" »", out)

        print("Failed to install Kaitai!\n")
        return False


def update_sys_path(usersitepackagespath):
    if usersitepackagespath in sys.path:
        print("\nFound %s in sys.path." % (usersitepackagespath))

    else:
        sys.path.append(usersitepackagespath)
        print("\nAdded %s to sys.path" % (usersitepackagespath))


def load_kaitai():
    kaitai_module = importlib.util.find_spec('kaitaistruct')
    if kaitai_module == None:
        print("Installing Kaitai...")
        pythonbinpath, pythonlibpath, ensurepippath, modulespaths, sitepackagespath, usersitepackagespath, _, _ = get_python_paths()
        pip = do_pip(pythonbinpath, ensurepippath)
        if pip:
            kai = do_kaitai(pythonbinpath)
            update_sys_path(usersitepackagespath)
            bpy.utils.refresh_script_paths()
        else:
            print("Failed to Install Pip!")

    kaitai_module = importlib.util.find_spec('kaitaistruct')
    if kaitai_module == None:
        print("MODULE HARD FAIL")


def read_m2(directory, file):
    '''
    A more accurate name for this function would be read_tex_transforms_from_m2(),
    since that's the main focus here. The import process relies mostly on the JSON data.
    '''
    from .m2 import M2

    # TODO: Make sure this file isn't left open
    with M2.from_file(os.path.join(directory, file)) as m2_struct:
        m2_dict = m2_struct.__dict__

        md21_chunk = None
        uv_anim_chunk = None

        for entry, item in m2_dict.items():
            if entry == "chunks":
                for chunk in item:
                    if chunk.chunk_type == "MD21":
                        md21_chunk = chunk.data.data
                        break

        if md21_chunk:
            uv_anim_chunk = md21_chunk.texture_transform_combos
            anim_chunk_combos = uv_anim_chunk.values
            texTransforms = md21_chunk.texture_transforms.values

            unpacked_transforms = []

            bones = md21_chunk.bones.values

            for transform in texTransforms:
                transform_container = {}
                
                translation = transform.translation
                rotation = transform.rotation
                scaling = transform.scaling

                do_translate, translate_interp, translate_rate = read_track(translation, 'VEC')
                do_rotate, rotate_interp, rotate_rate = read_track(rotation, 'QUAT')
                do_scale, scale_interp, scale_rate = read_track(scaling, 'VEC')

                if do_translate:
                    translate_vectors = translation.values.values[0].values[1]
                    translate_vectors = mathutils.Vector((translate_vectors.x, translate_vectors.y, translate_vectors.z))
                    transform_container['translate'] = translate_vectors * translate_rate

                if do_rotate:
                    if rotate_interp == 'CONST':
                        i = 0
                        rate = 20
                    else:
                        i = 1
                        rate = rotation.timestamps.values[0].values[1] / 1000  # TODO: Double-check time unit

                    r_vec = rotation.values.values[0].values[i]
                    rotate_vectors = mathutils.Quaternion((r_vec.w, r_vec.x, r_vec.y, r_vec.z))
                    transform_container['rotate'] = rotate_vectors

                if do_scale:
                    rate = scaling.timestamps.values[0].values[-1] / 1000 if not (scale_interp == 'CONST') else 15
                    scale_vectors = scaling.values.values[0].values[-1]
                    transform_container['scale'] = (scale_vectors.x / rate, scale_vectors.y / rate, scale_vectors.z / rate)

                unpacked_transforms.append(transform_container)

            return (True, md21_chunk, anim_chunk_combos, unpacked_transforms, bones)

        return (False, None, None, None, None)


def read_track(track, type):
    track_type = get_interpolation_type(track.interpolation_type)
    has_values = True if len(track.timestamps.values) > 0 else False

    if has_values:
        nvals = len(track.values.values[0].values)
        
        if type == 'VEC':
            delta = (0.0, 0.0, 0.0)
            prev = (0.0, 0.0, 0.0)
            for val in track.values.values[0].values:
                delta = (
                    delta[0] + val.x - prev[0],
                    delta[1] + val.y - prev[1],
                    delta[2] + val.z - prev[2]
                    )
                prev = (val.x, val.y, val.z)

            avg = (delta[0]/nvals, delta[1]/nvals, delta[2]/nvals)
            
        elif type == 'QUAT':
            delta = (0.0, 0.0, 0.0, 0.0)
            prev = (0.0, 0.0, 0.0, 0.0)
            for val in track.values.values[0].values:
                delta = (
                    delta[0] + val.x - prev[0],
                    delta[1] + val.y - prev[1],
                    delta[2] + val.z - prev[2],
                    delta[3] + val.w - prev[3]
                    )
                prev = (val.x, val.y, val.z, val.w)

            avg = (delta[0]/nvals, delta[1]/nvals, delta[2]/nvals, delta[3]/nvals)

        # True if the interp type is constant
        if nvals == 1:
            avg = 4
        elif nvals == 2:
            rate = track.timestamps.values[0].values[1] / 1000
            avg = mathutils.Vector([i/rate for i in avg])
        else:
            rate = 0.0
            prev_step = 0

            for step in track.timestamps.values[0].values:
                rate += abs(step - prev_step)
                prev_step = step

            # keyframes are given in milliseconds, rate/nvals gives avg time step per frame
            # 1000/(rate/nvals) gives us the rate per second.
            rate = 1000 / (rate/nvals)
            avg = mathutils.Vector([i * rate for i in avg])

        return (has_values, track_type, avg)
    else:
        return (has_values, track_type, 0)
