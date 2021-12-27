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

# Hell is other people's code. Also your own.

from typing import Dict, List, Set, Tuple, Union, Literal, Optional  # type: ignore # noqa: F401
from .lookup_tables import shader_table, WMOShader, WMO_Shaders


# General flag parsing
#
# This ends up duplicating the bit number as both a dict key, and in the tuple,
# but that means that we can do individual bit number lookups via the dict, *and*
# we have the option of pasing the FlagSpec tuple around and still have it be
# complete.
#
# FIXME: Do we really need that duplication?
#
# FIXME: Can we turn this into a proper enum when we read the json?
FlagSpec = Tuple[int, str, Optional[str]]  # bit number, name, description

def parse_flags(flags: int, flag_spec: Dict[int, FlagSpec]) -> Set[str]:
    flag_list: Set[str] = set()
    for k, v in flag_spec.items():
        if flags & 1 << k:
            flag_list.add(v[1])

    return flag_list


bone_flags: Dict[int, FlagSpec] = {
    0: (0, 'IGNORE_PARENT_TRANSLATE', None),
    1: (1, 'IGNORE_PARENT_SCALE', None),
    2: (2, 'IGNORE_PARENT_ROTATION', None),
    3: (3, 'SPHERICAL_BILLBOARD', None),
    4: (4, 'CYL_BILLBOARD_LOCK_X', None),
    5: (5, 'CYL_BILLBOARD_LOCK_Y', None),
    6: (6, 'CYL_BILLBOARD_LOCK_Z', None),
    # 7: (7, '', None),

    # 8: (8, '', None),
    9: (9, 'TRANSFORMED', None),
    10: (10, 'KINEMATIC_BONE', None),
    # 11: (11, '', None),
    12: (12, 'HELMET_ANIM_SCALED', None),
    13: (13, 'SOMETHING_SEQUENCE_ID', None),
    # 14: (14, '', None),
    # 15: (15, '', None),
}

# A really hacky bitfield unpacker.
# I should be able to abstract this into an enum-agnostic function.
def get_bone_flags(flags: int) -> Set[str]:
    return parse_flags(flags, bone_flags)


wmo_mat_flags: Dict[int, FlagSpec] = {
    0: (0, 'UNLIT', None),
    1: (1, 'UNFOGGED', None),
    2: (2, 'TWO_SIDED', None),
    3: (3, 'EXT_LIGHT', None),
    4: (4, 'SIDN', None),
    5: (5, 'WINDOW', None),
    6: (6, 'CLAMP_S', None),
    7: (7, 'CLAMP_T', None),

    8: (8, 'unknown1', None),
    # 32-bit flag, but bits 9 - 31 are unused
}

def wmo_read_mat_flags(flags: int) -> Set[str]:
    return parse_flags(flags, wmo_mat_flags)


wmo_root_flags: Dict[int, FlagSpec] = {
    0: (0, 'NO_ATTENUATE_PORTAL_DIST', None),
    1: (1, 'UNIFIED_RENDER_PATH', "Use unified render path for all objects in this WMO"),
    2: (2, 'LIQUID_FROM_DBC', "Liquid type is from DBC (see MLIQ)"),
    3: (3, 'NO_FIX_VCOLOR_ALPHA', "Don't call FixColorVertexAlpha (and other effects)"),
    4: (4, 'LOD', None),
    5: (5, 'DEFAULT_MAX_LOD', None),
}

def wmo_read_root_flags(flags: int) -> Set[str]:
    return parse_flags(flags, wmo_root_flags)


# FIXME: Wouldn't it be cool if we could create this entirely from kaitai defs?
wmo_group_flags: Dict[int, FlagSpec] = {
    0: (0, 'HAS_BSP_TREE', None),
    1: (1, 'HAS_LIGHT_MAP', None),
    2: (2, 'HAS_VERTEX_COLORS', None),
    3: (3, 'EXTERIOR', None),
    # 4: (4, '', None),
    # 5: (5, '', None),
    6: (6, 'EXTERIOR_LIT', None),
    7: (7, 'UNREACHABLE', None),

    8: (8, 'EXTERIOR_SKYBOX', None),
    9: (9, 'HAS_LIGHTS', None),
    10: (10, 'HAS_LOD', None),
    11: (11, 'HAS_DOODADS', None),
    12: (12, 'HAS_WATER', None),
    13: (13, 'INTERIOR', None),
    # 14: (14, '', None),
    # 15: (15, '', None),

    16: (16, 'ALWAYS_DRAW', None),
    17: (17, 'HAS_MORI', None),
    18: (18, 'SHOW_SKYBOX', None),
    19: (19, 'HAS_OCEAN', None),
    20: (20, 'UNKNOWN1', None),
    21: (21, 'MOUNT_ALLOWED', None),
    # 22: (22, '', None),
    # 23: (23, '', None),

    24: (24, 'HAS_VC2', None),
    25: (25, 'HAS_UV2', None),
    26: (26, 'ANTIPORTAL', None),
    27: (27, 'UNKNOWN2', None),
    # 28: (28, '', None),
    29: (29, 'EXTERIOR_CULL', None),
    30: (30, 'HAS_UV3', None),
    31: (31, 'UNKNOWN3', None),
}

def wmo_read_group_flags(flags: int) -> Set[str]:
    return parse_flags(flags, wmo_group_flags)


# Based on M2GetPixelShaderID() from: https://wowdev.wiki/M2/.skin
def get_shadereffects(shaderID: int, op_count: int = 2) -> str:
    if shaderID == 0:
        print("WotLK Asset; uses a runtime shader selector")
    if shaderID & 0x8000:
        shaderID &= (~0x8000)
        ind = shaderID.bit_length()
        if not shader_table[ind][4] == op_count:
            return shader_table[ind + 1][0]
        else:
            return shader_table[ind][0]
    else:
        if op_count == 1:
            if shaderID & 0x70:
                return "PS_Combiners_Mod"
            else:
                return "PS_Combiners_Opaque"
        else:
            lower = shaderID & 7

            if shaderID & 0x70:
                if lower == 0:
                    return "PS_Combiners_Mod_Opaque"
                elif lower == 3:
                    return "PS_Combiners_Mod_Add"
                elif lower == 4:
                    return "PS_Combiners_Mod_Mod2x"
                elif lower == 6:
                    return "PS_Combiners_Mod_Mod2xNA"
                elif lower == 7:
                    return "PS_Combiners_Mod_AddNA"
                else:
                    return "PS_Combiners_Mod_Mod"
            else:
                if lower == 0:
                    return "PS_Combiners_Opaque_Opaque"
                elif lower == 3:
                    return "PS_Combiners_Opaque_AddAlpha"
                elif lower == 4:
                    return "PS_Combiners_Opaque_Mod2x"
                elif lower == 6:
                    return "PS_Combiners_Opaque_Mod2xNA"
                elif lower == 7:
                    return "PS_Combiners_Opaque_AddAlpha"
                else:
                    return "PS_Combiners_Opaque_Mod"


# Also from: https://wowdev.wiki/M2/.skin
def get_vertex_shader(shader_id: int, op_count: int = 2) -> str:
    if shader_id & 0x8000:
        shader_id &= (~0x8000)
        ind = shader_id.bit_length()
        return shader_table[ind + 1][1]
    else:
        if op_count == 1:
            if shader_id & 0x80:
                return "VS_Diffuse_Env"
            else:
                if shader_id & 0x4000:
                    return "VS_Diffuse_T2"
                else:
                    return "VS_Diffuse_T1"
        else:
            if shader_id & 0x80:
                if shader_id & 0x8:
                    return "VS_Diffuse_Env_Env"
                else:
                    return "VS_Diffuse_Env_T1"
            else:
                if shader_id & 0x8:
                    return "VS_Diffuse_T1_Env"
                else:
                    if shader_id & 0x4000:
                        return "VS_Diffuse_T1_T2"
                    else:
                        return "VS_Diffuse_T1_T1"


# Currently unused, needs actual interp functions to be useful.
def get_interpolation_type(index: int):
    types = (
        'CONST',
        'LINEAR',
        'BEZIER',
        'HERMITE'
    )
    return types[index]


# MODELPARTICLE_FLAGS_WORLDSPACE     0x8         Particles travel "up" in world space, rather than model
# MODELPARTICLE_FLAGS_DONOTTRAIL     0x10        Do not trail
# MODELPARTICLE_FLAGS_MODELSPACE     0x80        Particles in model space
# MODELPARTICLE_FLAGS_PINNED         0x400       Pinned Particles, their quad enlarges from their creation  position to where they expand
# MODELPARTICLE_FLAGS_DONOTBILLBOARD 0x1000      Wiki says: XYQuad Particles. They align to XY axis facing Z axis direction
# MODELPARTICLE_FLAGS_RANDOMTEXTURE  0x10000     Choose Random Texture
# MODELPARTICLE_FLAGS_OUTWARD        0x20000     "Outward" particles, most emitters have this and their particles move away from the origin, when they don't the particles start at origin+(speed*life) and move towards the origin
# MODELPARTICLE_FLAGS_RANDOMSTART    0x200000    Random Flip Book Start
# MODELPARTICLE_FLAGS_BONEGENERATOR  0x1000000   Bone generator = bone, not joint
# MODELPARTICLE_FLAGS_DONOTTHROTTLE  0x4000000   Do not throttle emission rate based on distance
# MODELPARTICLE_FLAGS_MULTITEXTURE   0x10000000  Particle uses multi-texturing. This affects emitter values
# MODELPARTICLE_EMITTER_PLANE  1
# MODELPARTICLE_EMITTER_SPHERE 2
# MODELPARTICLE_EMITTER_SPLINE 3


# FIXME: Come up with an easy 'color' vector type (mathutils.Color doesn't really
# seem to count))
def wmo_read_color(color: int, color_type: Literal["CImVector", "CArgb"]) -> Tuple[float, float, float, float]:
    c_bytes = color.to_bytes(4, 'little')

    if color_type == 'CImVector':
        red = c_bytes[2]
        green = c_bytes[1]
        blue = c_bytes[0]
        alpha = c_bytes[3]

    elif color_type == 'CArgb':
        red = c_bytes[0]
        green = c_bytes[1]
        blue = c_bytes[2]
        alpha = c_bytes[3]

    else:
        raise ValueError(f"Unknown color type: {color_type}")

    do_gamma = False

    if do_gamma:
        if (0 <= float(red) / 255 <= 0.04045):
            red = (float(red) / 255) / 12.92
        else:
            red = pow((float(red) / 255 + 0.55) / 1.055, 2.4)

        if (0 <= float(green) / 255 <= 0.04045):
            green = (float(green) / 255) / 12.92
        else:
            green = pow((float(green) / 255 + 0.55) / 1.055, 2.4)

        if (0 <= float(blue) / 255 <= 0.04045):
            blue = (float(blue) / 255) / 12.92
        else:
            blue = pow((float(blue) / 255 + 0.55) / 1.055, 2.4)
    else:
        red = (float(red) / 255)
        green = (float(green) / 255)
        blue = (float(blue) / 255)

    alpha = float(alpha) / 255

    return (red, green, blue, alpha)


def read_wmo_face_flags(flag_in: int, func: Literal["is_transition", "is_color", "is_render", "is_collidable"]) -> bool:
    # The flags, as per https://wowdev.wiki/WMO#MOPY_chunk
    F_UNK_0x01 = 0x01
    F_NOCAMCOLLIDE = 0x02
    F_DETAIL = 0x04
    F_COLLISION = 0x08
    F_HINT = 0x10
    F_RENDER = 0x20
    F_UNK_0x40 = 0x40
    F_COLLIDE_HIT = 0x80

    if func == "is_transition":
        result = True if ((flag_in & F_UNK_0x01) and (
            (flag_in & F_DETAIL) or (flag_in & F_RENDER))) else False
        if result:
            print("TRANSITION!")
        return result
    elif func == 'is_color':
        result = True if not flag_in & F_COLLISION else False
        return result
    elif func == 'is_render':
        result = True if (flag_in & F_RENDER) else False
        # backup = True if ((flag_in & F_RENDER) and not (flag_in & F_DETAIL)) else False
        return result
    elif func == 'is_collidable':
        result = True if ((flag_in & F_COLLISION) or (flag_in & F_RENDER)
                          or not (flag_in & F_DETAIL)) else False
        return result

    return False


def wmo_get_shader(shaderid: int) -> WMOShader:
    return WMO_Shaders[shaderid]
