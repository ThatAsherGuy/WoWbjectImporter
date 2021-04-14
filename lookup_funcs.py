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

# Shoved these over here to avoid circular dependencies

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
);

# Based on M2GetPixelShaderID() from: https://wowdev.wiki/M2/.skin
def get_shadereffects(shaderID, op_count = 2):
    if shaderID == 0:
        print("WotLK Asset; uses a runtime shader selector")
    if shaderID & 0x8000:
        shaderID &= (~0x8000)
        ind = shaderID.bit_length()
        if not shader_table[ind][4] == op_count:
            return shader_table[ind+1][0]
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


def get_vertex_shader(shader_id, op_count = 2):
    if shader_id & 0x8000:
        shader_id &= (~0x8000)
        ind = shader_id.bit_length()
        return shader_table[ind+1][1]
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

# Tex Transform Table Stuff
# -1 == Static
# 0 == Texture 1 moves
# 1 == Texture 2 moves

# table for sword = [-1, 0, -1, 1]
# table for staff = [-1, 2, -1, 1, -1, -1, 0]

def get_uv_anim(index):
    anim_table = (-1, 2, -1, 1, -1, -1, 0)
    return anim_table[index]
