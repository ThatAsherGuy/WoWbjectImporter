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


WMO_Shaders = (
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
