# other possibilities for json-to-something-checkable:
#   https://stackoverflow.com/questions/53376099/python-dataclass-from-a-nested-dict/53498623#53498623
#
# We started with TypedDict for the json-related types at the moment, to at
# least give some sort of type checking and field typing and such to the data
# we're reading in. Sadly, this means that we can't use get() and still have
# type checking, which sucks. We also can't use .attribute type accesses,
# either, which also sucks a bit.
#
# TypedDict is fast, though. Loading dalaran with it takes 0.93s, and loading
# stormwind with it takes 0.56s. This is more than a full order of magnitude
# faster than the other options investigated:
#
# tried to use dataclasses-json, but after it got working (which required
# some futzing), it was pretty slow -- 51s for dalaran, 41s for stormwind.
# This is a complete non-starter
#
# marshmallow-dataclass does a bit better, but still slow. Loading dalaran
# with it takes 28s, stormwind takes 18s. This is a lot closer to the realm
# of reasonable, but is still an order of magnitude slower than TypedDict.
#
# ...looks like mashumaro loads them in 2s and 1.36s, respectively, though.
# Assuming we don't run into issues with it, we may have a winner!

from typing import List, Dict, TypedDict, Tuple
import dataclasses
from dataclasses import dataclass
from .vendor.mashumaro import DataClassJSONMixin
# from mashumaro import DataClassJSONMixin
# import mathutils
# from .lookup_tables import EGxBlend
import enum

# class Vec2(mathutils.Vector):
#     def __init__(self, seq: Tuple[float, float]):
#         super().__init__(seq)


# class Vec3(mathutils.Vector):
#     def __init__(self, seq: Tuple[float, float, float]):
#         super().__init__(seq)


# class Vec4(mathutils.Vector):
#     def __init__(self, seq: Tuple[float, float, float, float]):
#         super().__init__(seq)


Vec2 = Tuple[float, float]
Vec3 = Tuple[float, float, float]
Vec4 = Tuple[float, float, float, float]
Tri = Tuple[int, int, int]

iColor3 = Tuple[int, int, int]
iColor4 = Tuple[int, int, int, int]

fColor3 = Tuple[float, float, float]
fColor4 = Tuple[float, float, float, float]

FDID = int

# FIXME: Do we need the multiples versions ("JsonWmoMaterials"), or is it
# enough to just use "List[JsonWmoMaterial]" or similar where needed? And
# should these be aliases, or actual types?

# FIXME: Turn these into proper vector types?
JsonVertex = Tuple[float, float, float]

JsonPosition = Tuple[float, float, float]

JsonRotation = Tuple[float, float, float, float]

JsonTextureCombos = List[int]

JsonTextureTypes = List[int]

JsonVertexColorLayer = List[int]

@dataclass
class JsonBoundingBox(DataClassJSONMixin):
    min: 'JsonVertex'
    max: 'JsonVertex'


@dataclass
class JsonM2Material(DataClassJSONMixin):
    flags: int
    blendingMode: int


@dataclass
class JsonTexture(DataClassJSONMixin):
    fileNameInternal: str
    fileNameExternal: str
    mtlName: str
    fileDataID: int
    flags: int = 0  # FIXME: Not in WMO ... needs separate type?


@dataclass
class JsonTextureUnit(DataClassJSONMixin):
    flags: int
    priority: int
    shaderID: int
    skinSectionIndex: int
    geosetIndex: int
    colorIndex: int
    materialIndex: int
    materialLayer: int
    textureCount: int
    textureComboIndex: int
    textureCoordComboIndex: int
    textureWeightComboIndex: int
    textureTransformComboIndex: int


@dataclass
class JsonSkin(DataClassJSONMixin):
    fileName: str
    fileDataID: int
    subMeshes: List['JsonSubMesh'] = dataclasses.field(default_factory=list)
    textureUnits: List['JsonTextureUnit'] = dataclasses.field(default_factory=list)

@dataclass
class JsonSubMesh(DataClassJSONMixin):
    enabled: bool
    submeshID: int
    level: int
    vertexStart: int
    vertexCount: int
    triangleStart: int
    triangleCount: int
    boneCount: int
    boneStart: int
    boneInfluences: int
    centerBoneIndex: int
    centerPosition: Tuple[float, float, float]
    sortCenterPosition: Tuple[float, float, float]
    sortRadius: float


@dataclass
class JsonM2Metadata(DataClassJSONMixin):
    fileDataID: int
    fileName: str
    internalName: str  # FIXME: optional?
    textureTypes: 'JsonTextureTypes'
    textureCombos: 'JsonTextureCombos'
    # colors:  ???
    boundingBox: 'JsonBoundingBox'
    boundingSphereRadius: float
    collisionBox: 'JsonBoundingBox'
    collisionSphereRadius: float
    skin: 'JsonSkin'
    textures: List['JsonTexture'] = dataclasses.field(default_factory=list)
    materials: List['JsonM2Material'] = dataclasses.field(default_factory=list)
    # textureWeights: ???
    transparencyLookup: List[int] = dataclasses.field(default_factory=list)
    # textureTransforms: ???
    textureTransformsLookup: List[int] = dataclasses.field(default_factory=list)

@dataclass
class JsonWmoCounts(DataClassJSONMixin):
    material: int
    group: int
    portal: int
    light: int
    model: int
    doodad: int
    set: int
    lod: int


@dataclass
class JsonPortalInformation(DataClassJSONMixin):
    """
    MOPT / SMOPortal - describes one portal separating two WMO groups. A single portal is usually made up of four vertices in a quad (starting at startVertex and going to startVertex + count). However, portals support more complex shapes, and can fully encompass holes such as the archway leading into Ironforge and parts of the Caverns of Time.
    """
    startVertex: int
    count: int
    plane: Tuple[float, float, float, float]  # FIXME: what is this?


@dataclass
class JsonPortalMapObjectReference(DataClassJSONMixin):
    """
    MOPR / SMOPortalRef - Map Object Portal References from groups.
    """
    portalIndex: int
    groupIndex: int
    side: int


@dataclass
class JsonWmoMaterialInformation(DataClassJSONMixin):
    flags: int
    materialID: int


@dataclass
class JsonWmoRenderBatch(DataClassJSONMixin):
    # FIXME: what are these?
    possibleBox1: 'JsonVertex'   # actually int though?
    possibleBox2: 'JsonVertex'   # actually int though?
    firstFace: int
    numFaces: int
    firstVertex: int
    materialID: int
    flags: int = 0
    lastVertex: int = -1


@dataclass
class JsonWmoGroup(DataClassJSONMixin):
    version: int
    groupID: int
    boundingBox1: 'JsonVertex'
    boundingBox2: 'JsonVertex'
    numPortals: int = 0
    numBatchesA: int = 0
    numBatchesB: int = 0
    numBatchesC: int = 0
    liquidType: int = 0
    flags: int = 0
    materialInfo: List['JsonWmoMaterialInformation'] = dataclasses.field(default_factory=list)
    renderBatches: List['JsonWmoRenderBatch'] = dataclasses.field(default_factory=list)
    vertexColours: List['JsonVertexColorLayer'] = dataclasses.field(default_factory=list)
    groupName: str = ""
    groupDescription: str = ""
    enabled: bool = True


@dataclass
class JsonWmoGroupInformation(DataClassJSONMixin):
    """MOGI / SMOGroupInfo - Information for WMO Groups"""
    flags: int  # FIXME: make real flags
    """Same as flags from MOGP"""
    boundingBox1: 'JsonVertex'
    boundingBox2: 'JsonVertex'
    nameIndex: int


# MOMT / SMOMaterial
# FIXME: make all the names here match up with kaitai-wow (or visa versa)
# @dataclass
# class WmoMaterialFlags(enum.Flag):
#     F_UNLIT = 0x01
#     """disable lighting logic in shader (but can still use vertex colors)"""
#     F_UNFOGGED = 0x02
#     """disable fog shading (rarely used)"""
#     F_UNCULLED = 0x04
#     """two-sided"""
#     F_EXTLIGHT = 0x08
#     """darkened (internal face of windows?)"""
#     F_SIDN = 0x10
#     """bright at night, unshaded (used on windows and lamps)"""
#     F_WINDOW = 0x20
#     """unknown (lighting related)"""
#     F_CLAMP_S = 0x40
#     """force this material's textures to use clamp s addressing"""
#     F_CLAMP_T = 0x80
#     """force this material's textures to use clamp t addressing"""
#     flag_0x100 = 0x100


@dataclass
class JsonWmoMaterial(DataClassJSONMixin):
    """[summary]
     MOMT / SMOMaterial - Materials used in this map object, one per texture/blp
    """
    # flags: WmoMaterialFlags
    flags: int
    shader: int
    """shader to use from WMO_Shaders table"""
    # blendMode: 'EGxBlend'
    blendMode: int
    """blend mode"""
    texture1: FDID
    color1: int
    """sidnColor -- "self-illuminated day/night" - emissive color"""
    color1b: int
    """frameSidnColor"""
    texture2: FDID
    color2: int
    """diffColor (???)"""
    groupType: int
    """terrain type from TerrainType table"""
    texture3: FDID
    color3: int
    flags3: int


@dataclass
class JsonWmoDoodadSet(DataClassJSONMixin):
    """
    MODS / SMODoodadSet - Doodad Sets. specify several versions of "interior
    decoration" for a WMO. Sets are exclusive except for the first one,
    "Set_$DefaultGlobal", which is additive and always displayed.
    """
    name: str
    """doodad set name (informational only)"""
    firstInstanceIndex: int
    """index of first doodad instance in set (into MODD chunk)"""
    doodadCount: int
    # unused: int


@dataclass
class JsonWmoDoodad(DataClassJSONMixin):
    """
    MODD / SMODoodadDef - information for doodad instances"""
    offset: int
    flags: int
    position: 'JsonPosition'
    """position as (X,Z,-Y)   WARNING: Might be adjusted by wow.export"""
    rotation: 'JsonRotation'
    """rotation as (X, Y, Z, W) quaternion   WARNING: might be just Euler by wow.export"""
    scale: float
    """doodad scale factor"""
    color: Tuple[int, int, int, int]  # FIXME: check & provide proper datatype
    """overrides pc_sunColor, see notes on wiki"""


@dataclass
class JsonWmoMetadata(DataClassJSONMixin):
    fileDataID: int
    fileName: str
    version: int
    counts: 'JsonWmoCounts'

    ambientColor: int
    areaTableID: int
    boundingBox1: 'JsonVertex'
    boundingBox2: 'JsonVertex'
    flags: int
    portalVertices: List['JsonVertex'] = dataclasses.field(default_factory=list)
    portalInfo: List['JsonPortalInformation'] = dataclasses.field(default_factory=list)
    portalMapObjectRef: List['JsonPortalMapObjectReference'] = dataclasses.field(
        default_factory=list)
    groups: List['JsonWmoGroup'] = dataclasses.field(default_factory=list)
    groupNames: List[str] = dataclasses.field(default_factory=list)
    groupInfo: List['JsonWmoGroupInformation'] = dataclasses.field(default_factory=list)
    textures: List['JsonTexture'] = dataclasses.field(default_factory=list)
    materials: List['JsonWmoMaterial'] = dataclasses.field(default_factory=list)
    doodadSets: List['JsonWmoDoodadSet'] = dataclasses.field(default_factory=list)
    fileDataIDs: List[int] = dataclasses.field(default_factory=list)
    doodads: List['JsonWmoDoodad'] = dataclasses.field(default_factory=list)
    groupIDs: List[int] = dataclasses.field(default_factory=list)
