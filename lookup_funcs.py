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

# various tables. Right now these are bundled together because autopep8 has
# a bug that makes "disable formatting for this section" only work once in
# a file, and we really want that to make these tables understandable after
# autoformatting. See https://github.com/hhatto/autopep8/issues/611

# autopep8: off
# Pulled directly from the 8.0.1 table: https://wowdev.wiki/M2/.skin
# Note that there are repeats; you can (theoretically)
# hash the full combos in order to treat it as a set,
# but you can't rely on just pixel shaders for unique keys
shader_table =(
    ("PS_Combiners_Opaque_Mod2xNA_Alpha",           "VS_Diffuse_T1_Env",         "HS_T1_T2",    "DS_T1_T2"   , 2),
    ("PS_Combiners_Opaque_AddAlpha",                "VS_Diffuse_T1_Env",         "HS_T1_T2",    "DS_T1_T2"   , 2),
    ("PS_Combiners_Opaque_AddAlpha_Alpha",          "VS_Diffuse_T1_Env",         "HS_T1_T2",    "DS_T1_T2"   , 2),
    ("PS_Combiners_Opaque_Mod2xNA_Alpha_Add",       "VS_Diffuse_T1_Env_T1",      "HS_T1_T2_T3", "DS_T1_T2_T3", 3),
    ("PS_Combiners_Mod_AddAlpha",                   "VS_Diffuse_T1_Env",         "HS_T1_T2",    "DS_T1_T2"   , 2),
    ("PS_Combiners_Opaque_AddAlpha",                "VS_Diffuse_T1_T1",          "HS_T1_T2",    "DS_T1_T2"   , 2),
    ("PS_Combiners_Mod_AddAlpha",                   "VS_Diffuse_T1_T1",          "HS_T1_T2",    "DS_T1_T2"   , 2),
    ("PS_Combiners_Mod_AddAlpha_Alpha",             "VS_Diffuse_T1_Env",         "HS_T1_T2",    "DS_T1_T2"   , 2),
    ("PS_Combiners_Opaque_Alpha_Alpha",             "VS_Diffuse_T1_Env",         "HS_T1_T2",    "DS_T1_T2"   , 2),
    ("PS_Combiners_Opaque_Mod2xNA_Alpha_3s",        "VS_Diffuse_T1_Env_T1",      "HS_T1_T2_T3", "DS_T1_T2_T3", 3),
    ("PS_Combiners_Opaque_AddAlpha_Wgt",            "VS_Diffuse_T1_T1",          "HS_T1_T2",    "DS_T1_T2"   , 2),
    ("PS_Combiners_Mod_Add_Alpha",                  "VS_Diffuse_T1_Env",         "HS_T1_T2",    "DS_T1_T2"   , 2),
    ("PS_Combiners_Opaque_ModNA_Alpha",             "VS_Diffuse_T1_Env",         "HS_T1_T2",    "DS_T1_T2"   , 2),
    ("PS_Combiners_Mod_AddAlpha_Wgt",               "VS_Diffuse_T1_Env",         "HS_T1_T2",    "DS_T1_T2"   , 2),
    ("PS_Combiners_Mod_AddAlpha_Wgt",               "VS_Diffuse_T1_T1",          "HS_T1_T2",    "DS_T1_T2"   , 2),
    ("PS_Combiners_Opaque_AddAlpha_Wgt",            "VS_Diffuse_T1_T2",          "HS_T1_T2",    "DS_T1_T2"   , 2),
    ("PS_Combiners_Opaque_Mod_Add_Wgt",             "VS_Diffuse_T1_Env",         "HS_T1_T2",    "DS_T1_T2"   , 2),
    ("PS_Combiners_Opaque_Mod2xNA_Alpha_UnshAlpha", "VS_Diffuse_T1_Env_T1",      "HS_T1_T2_T3", "DS_T1_T2_T3", 3),
    ("PS_Combiners_Mod_Dual_Crossfade",             "VS_Diffuse_T1",             "HS_T1",       "DS_T1"      , 1),
    ("PS_Combiners_Mod_Depth",                      "VS_Diffuse_EdgeFade_T1",    "HS_T1",       "DS_T1"      , 2),
    ("PS_Combiners_Opaque_Mod2xNA_Alpha_Alpha",     "VS_Diffuse_T1_Env_T2",      "HS_T1_T2_T3", "DS_T1_T2_T3", 3),
    ("PS_Combiners_Mod_Mod",                        "VS_Diffuse_EdgeFade_T1_T2", "HS_T1_T2",    "DS_T1_T2"   , 2),
    ("PS_Combiners_Mod_Masked_Dual_Crossfade",      "VS_Diffuse_T1_T2",          "HS_T1_T2",    "DS_T1_T2"   , 2),
    ("PS_Combiners_Opaque_Alpha",                   "VS_Diffuse_T1_T1",          "HS_T1_T2",    "DS_T1_T2"   , 2),
    ("PS_Combiners_Opaque_Mod2xNA_Alpha_UnshAlpha", "VS_Diffuse_T1_Env_T2",      "HS_T1_T2_T3", "DS_T1_T2_T3", 3),
    ("PS_Combiners_Mod_Depth",                      "VS_Diffuse_EdgeFade_Env",   "HS_T1",       "DS_T1"      , 1),
    ("PS_Guild",                                    "VS_Diffuse_T1_T2_T1",       "HS_T1_T2_T3", "DS_T1_T2"   , 3),
    ("PS_Guild_NoBorder",                           "VS_Diffuse_T1_T2",          "HS_T1_T2",    "DS_T1_T2_T3", 2),
    ("PS_Guild_Opaque",                             "VS_Diffuse_T1_T2_T1",       "HS_T1_T2_T3", "DS_T1_T2"   , 3),
    ("PS_Illum",                                    "VS_Diffuse_T1_T1",          "HS_T1_T2",    "DS_T1_T2"   , 2),
    ("PS_Combiners_Mod_Mod_Mod_Const",              "VS_Diffuse_T1_T2_T3",       "HS_T1_T2_T3", "DS_T1_T2_T3", 3),
    ("PS_Combiners_Mod_Mod_Mod_Const",              "VS_Color_T1_T2_T3",         "HS_T1_T2_T3", "DS_T1_T2_T3", 3),
    ("PS_Combiners_Opaque",                         "VS_Diffuse_T1",             "HS_T1",       "DS_T1"      , 1),
    ("PS_Combiners_Mod_Mod2x",                      "VS_Diffuse_EdgeFade_T1_T2", "HS_T1_T2",    "DS_T1_T2"   , 2),
)


WMO_Shaders_Old = (
    ("Diffuse",                 1, 1, 1, 1),
    ("Specular",                1, 1, 1, 1),
    ("Metal",                   1, 1, 1, 1),
    ("Env",                     1, 2, 1, 1),
    ("Opaque",                  1, 1, 1, 1),
    ("EnvMetal",                1, 2, 1, 1),
    ("TwoLayerDiffuse",         1, 2, 2, 2),
    ("TwoLayerEnvMetal",        1, 3, 2, 2),
    ("TwoLayerTerrain",         1, 2, 1, 2),
    ("DiffuseEmissive",         1, 2, 2, 2),
    ("waterWindow",             1, 1, 1, 1),
    ("MaskedEnvMetal",          1, 3, 2, 2),
    ("EnvMetalEmissive",        1, 3, 2, 2),
    ("TwoLayerDiffuseOpaque",   1, 2, 2, 2),
    ("submarineWindow",         1, 1, 1, 1),
    ("TwoLayerDiffuseEmissive", 1, 2, 2, 2),
    ("DiffuseTerrain",          1, 1, 1, 1),
    ("AdditiveMaskedEnvMetal",  1, 3, 2, 2),
)



WMO_Shaders_New = (
    ("Diffuse",	                  "MapObjDiffuse_T1",	        "MapObjDiffuse"),
    ("Specular",	              "MapObjSpecular_T1",	        "MapObjSpecular"),
    ("Metal",	                  "MapObjSpecular_T1",	        "MapObjMetal"),
    ("Env",	                      "MapObjDiffuse_T1_Refl",	    "MapObjEnv"),
    ("Opaque",	                  "MapObjDiffuse_T1",	        "MapObjOpaque"),
    ("EnvMetal",	              "MapObjDiffuse_T1_Refl",	    "MapObjEnvMetal"),
    ("TwoLayerDiffuse",	          "MapObjDiffuse_Comp",	        "MapObjTwoLayerDiffuse"),
    ("TwoLayerEnvMetal",	      "MapObjDiffuse_T1",	        "MapObjTwoLayerEnvMetal"),
    ("TwoLayerTerrain",	          "MapObjDiffuse_Comp_Terrain",	"MapObjTwoLayerTerrain"	),
    ("DiffuseEmissive",	          "MapObjDiffuse_Comp",	        "MapObjDiffuseEmissive"),
    ("waterWindow",	              "FFXWaterWindow",	            "FFXWaterWindow"),
    ("MaskedEnvMetal",	          "MapObjDiffuse_T1_Env_T2",	"MapObjMaskedEnvMetal"),
    ("EnvMetalEmissive",	      "MapObjDiffuse_T1_Env_T2",	"MapObjEnvMetalEmissive"),
    ("TwoLayerDiffuseOpaque",     "MapObjDiffuse_Comp",	        "MapObjTwoLayerDiffuseOpaque"),
    ("submarineWindow",	          "FFXSubmarineWindow",	        "FFXSubmarineWindow"),
    ("TwoLayerDiffuseEmissive",   "MapObjDiffuse_Comp",	        "MapObjTwoLayerDiffuseEmissive"),
    ("DiffuseTerrain",	          "MapObjDiffuse_T1",	        "MapObjDiffuse"),
    ("AdditiveMaskedEnvMetal",    "MapObjDiffuse_T1_Env_T2",	"MapObjAdditiveMaskedEnvMetal"),
    ("TwoLayerDiffuseMod2x",      "MapObjDiffuse_CompAlpha",	"MapObjTwoLayerDiffuseMod2x"),
    ("TwoLayerDiffuseMod2xNA",    "MapObjDiffuse_Comp",	        "MapObjTwoLayerDiffuseMod2xNA"),
    ("TwoLayerDiffuseAlpha",      "MapObjDiffuse_CompAlpha",	"MapObjTwoLayerDiffuseAlpha"),
    ("Lod",	                      "MapObjDiffuse_T1",	        "MapObjLod"),
    ("Parallax",	              "MapObjParallax",	            "MapObjParallax"),
)


WMO_Blend_Modes = (
    "OPAQUE",
    "ALPHA_KEY",
    "ALPHA",
    "ADD",
    "MOD",
    "MOD_2X",
    "MOD_ADD",
    "INV_SRC_ALPHA_ADD",
    "INV_SRC_ALPHA_OPAQUE",
    "SRC_ALPHA_OPAQUE",
    "NO_ALPHA_ADD",
    "CONST_ALPHA",
    "SCREEN",
    "BLEND_ADD"
)
# autopep8: on


# Bone Flags
# ignoreParentTranslate = 0x1,
# ignoreParentScale = 0x2,
# ignoreParentRotation = 0x4,
# spherical_billboard = 0x8,
# cylindrical_billboard_lock_x = 0x10,
# cylindrical_billboard_lock_y = 0x20,
# cylindrical_billboard_lock_z = 0x40,
# transformed = 0x200,
# kinematic_bone = 0x400,
# helmet_anim_scaled = 0x1000,
# something_sequence_id = 0x2000,

# A really hacky bitfield unpacker.
# I should be able to abstract this into an enum-agnostic function.
def get_bone_flags(flags):
    flag_list = []

    if flags & 0x1:
        flag_list.append("ignoreParentTranslate")

    if flags & 0x2:
        flag_list.append("ignoreParentScale")

    if flags & 0x4:
        flag_list.append("ignoreParentRotation")

    if flags & 0x8:
        flag_list.append("spherical_billboard")

    if flags & 0x10:
        flag_list.append("cylindrical_billboard_lock_x")

    if flags & 0x20:
        flag_list.append("cylindrical_billboard_lock_y")

    if flags & 0x40:
        flag_list.append("cylindrical_billboard_lock_z")

    if flags & 0x200:
        flag_list.append("transformed")

    if flags & 0x400:
        flag_list.append("kinematic_bone")

    if flags & 0x1000:
        flag_list.append("helmet_anim_scaled")

    if flags & 0x2000:
        flag_list.append("something_sequence_id")

    return flag_list


# Based on M2GetPixelShaderID() from: https://wowdev.wiki/M2/.skin
def get_shadereffects(shaderID, op_count=2):
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
def get_vertex_shader(shader_id, op_count=2):
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
def get_interpolation_type(index):
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


def wmo_read_color(color, color_type):
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


def read_wmo_face_flags(flag_in, func):
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
        backup = True if ((flag_in & F_RENDER) and not (flag_in & F_DETAIL)) else False
        return result
    elif func == 'is_collidable':
        result = True if ((flag_in & F_COLLISION) or (flag_in & F_RENDER)
                          or not (flag_in & F_DETAIL)) else False
        return result


def wmo_read_mat_flags(flag):
    flag_list = []
    if flag & 1:
        flag_list.append('UNLIT')

    if flag & 2:
        flag_list.append('UNFOGGED')

    if flag & 4:
        flag_list.append('TWO_SIDED')

    if flag & 8:
        flag_list.append('EXT_LIGHT')

    if flag & 16:
        flag_list.append('SIDN')

    if flag & 32:
        flag_list.append('WINDOW')

    if flag & 64:
        flag_list.append('CLAMP_S')

    if flag & 128:
        flag_list.append('CLAMP_T')

    if flag & 256:
        flag_list.append('0x100')

    return flag_list


def wmo_read_group_flags(flag):
    flag_list = set()

    if flag & 0x1:
        flag_list.add('HAS_BSP')

    if flag & 0x2:
        flag_list.add('HAS_LIGHTMAP')

    if flag & 0x4:
        flag_list.add('HAS_VC1')

    if flag & 0x8:
        flag_list.add('EXTERIOR')

    if flag & 0x10:
        pass  # unused flag

    if flag & 0x20:
        pass  # unused flag

    if flag & 0x40:
        flag_list.add('EXTERIOR_LIT')

    if flag & 0x80:
        flag_list.add('UNREACHABLE')


    if flag & 0x100:
        flag_list.add('EXTERIOR_SKY')

    if flag & 0x200:
        flag_list.add('HAS_LIGHTS')

    if flag & 0x400:
        flag_list.add('HAS_LOD')

    if flag & 0x800:
        flag_list.add('HAS_DOODADS')

    if flag & 0x1000:
        flag_list.add('HAS_WATER')

    if flag & 0x2000:
        flag_list.add('INTERIOR')

    if flag & 0x4000:
        pass  # unused

    if flag & 0x8000:
        flag_list.add('QUERY_MOUNT')


    if flag & 0x10000:
        flag_list.add('ALWAYS_DRAW')

    if flag & 0x20000:
        flag.list.add('HAS_MORI')

    if flag & 0x40000:
        flag_list.add('SHOW_SKY')

    if flag & 0x80000:
        flag_list.add('HAS_OCEAN')

    if flag & 0x100000:
        pass  # unused

    if flag & 0x200000:
        flag_list.add('MOUNT_ALLOWED')

    if flag & 0x400000:
        pass  # unused

    if flag & 0x800000:
        pass  # unused


    if flag & 0x1000000:
        flag_list.add('HAS_VC2')

    if flag & 0x2000000:
        flag_list.add('HAS_UV2')

    if flag & 0x4000000:
        flag_list.add('ANTIPORTAL')

    if flag & 0x8000000:
        flag_list.add('0x8000000')  # Unknown, but not unused

    if flag & 0x10000000:
        pass  # unused

    if flag & 0x20000000:
        flag_list.add('EXTERIOR_CULL')

    if flag & 0x40000000:
        flag_list.add('HAS_UV3')

    if flag & 0x80000000:
        flag_list.add('0x80000000')  # Unknown, but not unused

    return flag_list
