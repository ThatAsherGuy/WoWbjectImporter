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

