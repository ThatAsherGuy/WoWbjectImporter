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


# various tables. In their own file, so that we can turn off various type
# checking and formatting options so that they stay nice and neat.
# autopep8: off
# flake8: noqa    # wish this could be more explicit about what's being ignored

from dataclasses import dataclass
from typing import List
import enum

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

@dataclass
class WMOShader:
    name: str
    vertex: str
    pixel: str


WMO_Shaders: List[WMOShader] = [
              # Name,                    Vertex Shader,                Pixel Shader
    WMOShader("Diffuse",	             "MapObjDiffuse_T1",	       "MapObjDiffuse"),
    WMOShader("Specular",	             "MapObjSpecular_T1",	       "MapObjSpecular"),
    WMOShader("Metal",	                 "MapObjSpecular_T1",	       "MapObjMetal"),
    WMOShader("Env",	                 "MapObjDiffuse_T1_Refl",	   "MapObjEnv"),
    WMOShader("Opaque",	                 "MapObjDiffuse_T1",	       "MapObjOpaque"),

    # 5
    WMOShader("EnvMetal",	             "MapObjDiffuse_T1_Refl",	   "MapObjEnvMetal"),
    WMOShader("TwoLayerDiffuse",	     "MapObjDiffuse_Comp",	       "MapObjTwoLayerDiffuse"),
    WMOShader("TwoLayerEnvMetal",	     "MapObjDiffuse_T1",	       "MapObjTwoLayerEnvMetal"),
    WMOShader("TwoLayerTerrain",	     "MapObjDiffuse_Comp_Terrain", "MapObjTwoLayerTerrain"	),
    WMOShader("DiffuseEmissive",	     "MapObjDiffuse_Comp",	       "MapObjDiffuseEmissive"),

    # 10
    WMOShader("waterWindow",	         "vxFFXWaterWindow",	       "FFXWaterWindow"),
    WMOShader("MaskedEnvMetal",	         "MapObjDiffuse_T1_Env_T2",	   "MapObjMaskedEnvMetal"),
    WMOShader("EnvMetalEmissive",	     "MapObjDiffuse_T1_Env_T2",	   "MapObjEnvMetalEmissive"),
    WMOShader("TwoLayerDiffuseOpaque",   "MapObjDiffuse_Comp",	       "MapObjTwoLayerDiffuseOpaque"),
    WMOShader("submarineWindow",	     "vxFFXSubmarineWindow",	   "FFXSubmarineWindow"),

    # 15
    WMOShader("TwoLayerDiffuseEmissive", "MapObjDiffuse_Comp",	       "MapObjTwoLayerDiffuseEmissive"),
    WMOShader("DiffuseTerrain",	         "MapObjDiffuse_T1",	       "MapObjDiffuse"),
    WMOShader("AdditiveMaskedEnvMetal",  "MapObjDiffuse_T1_Env_T2",	   "MapObjAdditiveMaskedEnvMetal"),
    WMOShader("TwoLayerDiffuseMod2x",    "MapObjDiffuse_CompAlpha",	   "MapObjTwoLayerDiffuseMod2x"),
    WMOShader("TwoLayerDiffuseMod2xNA",  "MapObjDiffuse_Comp",	       "MapObjTwoLayerDiffuseMod2xNA"),

    # 20
    WMOShader("TwoLayerDiffuseAlpha",    "MapObjDiffuse_CompAlpha",	   "MapObjTwoLayerDiffuseAlpha"),
    WMOShader("Lod",	                 "MapObjDiffuse_T1",	       "MapObjLod"),
    WMOShader("Parallax",	             "MapObjParallax",	           "MapObjParallax"),
]


class EGxBlend(enum.Enum):
    OPAQUE = 0
    ALPHA_KEY = 1
    ALPHA = 2
    ADD = 3
    MOD = 4
    MOD_2X = 5
    MOD_ADD = 6
    INV_SRC_ALPHA_ADD = 7
    INV_SRC_ALPHA_OPAQUE = 8
    SRC_ALPHA_OPAQUE = 9
    NO_ALPHA_ADD = 10
    CONST_ALPHA = 11
    SCREEN = 12
    BLEND_ADD = 13


# WMO_Blend_Modes = [
#     "OPAQUE",
#     "ALPHA_KEY",
#     "ALPHA",
#     "ADD",
#     "MOD",
#     "MOD_2X",
#     "MOD_ADD",
#     "INV_SRC_ALPHA_ADD",
#     "INV_SRC_ALPHA_OPAQUE",
#     "SRC_ALPHA_OPAQUE",
#     "NO_ALPHA_ADD",
#     "CONST_ALPHA",
#     "SCREEN",
#     "BLEND_ADD"
# ]


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
