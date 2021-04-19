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
from ..lookup_funcs import get_interpolation_type

enc = sys.getdefaultencoding()

# Yoinked directly from DECALMachine
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
    from .m2 import M2
    with M2.from_file(os.path.join(directory, file)) as m2_struct:
        m2_globals = m2_struct.Md20GlobalFlags
        m2_dict = m2_struct.__dict__

        md21_chunk = None
        uv_anim_chunk = None
        texTransform_chunk = None

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
            bone_combos = md21_chunk.bone_combos.values


            for transform in texTransforms:
                transform_container = {}
                
                translation = transform.translation
                rotation = transform.rotation
                scaling = transform.scaling

                do_translate, translate_interp = read_track(translation)
                do_rotate, rotate_interp = read_track(rotation)
                do_scale, scale_interp = read_track(scaling)

                if do_translate:
                    print("Translation interp: " + translate_interp)
                    rate = translation.timestamps.values[0].values[1] / 1000 # TODO: Double-check time unit
                    translate_vectors = translation.values.values[0].values[1]
                    transform_container['translate'] = (translate_vectors.x / rate, translate_vectors.y / rate, translate_vectors.z / rate)
                if do_rotate:
                    print("Rotation interp: " + rotate_interp)
                    rate = rotation.timestamps.values[0].values[1] / 1000  # TODO: Double-check time unit
                    rotate_vectors = rotation.values.values[0].values[1] / rate
                    transform_container['rotate'] = rotate_vectors
                if do_scale:
                    print("Scale interp: " + scale_interp)
                    rate = scaling.timestamps.values[0].values[1] / 1000  # TODO: Double-check time unit
                    scale_vectors = scaling.values.values[0].values[1] / rate
                    transform_container['scale'] = (scale_vectors.x / rate, scale_vectors.y / rate, scale_vectors.z / rate)

                unpacked_transforms.append(transform_container)

            return (True, m2_dict, anim_chunk_combos, unpacked_transforms, bones)

        return (False, None, None)


def read_track(track):
    track_type = get_interpolation_type(track.interpolation_type)
    has_values = True if len(track.timestamps.values) > 0 else False

    if has_values:
        stamps = track.timestamps.values
        values = track.values.values

        duration = stamps[0].values[1] / 100 # TODO: Double-check time unit
        val = values[0].values[1]


    return (has_values, track_type)
