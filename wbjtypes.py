from typing import List, Dict, TypedDict, Tuple
import mathutils

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

# FIXME: Do we need the multiples versions ("JsonWmoMaterials"), or is it
# enough to just use "List[JsonWmoMaterial]" or similar where needed? And
# should these be aliases, or actual types?

# FIXME: Turn these into proper vector types?
JsonVertex = Tuple[float, float, float]

JsonPosition = Tuple[float, float, float]

JsonRotation = Tuple[float, float, float, float]

class JsonBoundingBox(TypedDict, total=True):
    min: JsonVertex
    max: JsonVertex


JsonM2Materials = List['JsonM2Material']
class JsonM2Material(TypedDict, total=True):
    flags: int
    blendingMode: int


JsonTextures = List['JsonTexture']
class JsonTexture(TypedDict, total=True):
    fileNameInternal: str
    fileNameExternal: str
    mtlName: str
    flags: int  # FIXME: Not in WMO ... needs separate type?
    fileDataID: int


JsonTextureUnits = List['JsonTextureUnit']
class JsonTextureUnit(TypedDict, total=True):
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


JsonTextureCombos = List[int]

JsonTextureTypes = List[int]

JsonSubMeshes = List['JsonSubMesh']
class JsonSubMesh(TypedDict, total=True):
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


class JsonSkin(TypedDict, total=True):
    subMeshes: JsonSubMeshes
    textureUnits: JsonTextureUnits
    fileName: str
    fileDataID: int


class JsonM2Metadata(TypedDict, total=True):
    fileDataID: int
    fileName: str
    internalName: str  # FIXME: optional?
    textures: JsonTextures
    textureTypes: JsonTextureTypes
    materials: JsonM2Materials
    textureCombos: JsonTextureCombos
    # colors:  ???
    # textureWeights: ???
    transparencyLookup: List[int]
    # textureTransforms: ???
    textureTransformsLookup: List[int]
    boundingBox: JsonBoundingBox
    boundingSphereRadius: float
    collisionBox: JsonBoundingBox
    collisionSphereRadius: float
    skin: JsonSkin


class JsonWmoCounts(TypedDict, total=True):
    material: int
    group: int
    portal: int
    light: int
    model: int
    doodad: int
    set: int
    lod: int


class JsonPortalInformation(TypedDict, total=True):
    startVertex: int
    count: int
    plane: Tuple[float, float, float, float]  # FIXME: what is this?


class JsonPortalMapObjectReference(TypedDict, total=True):
    portalIndex: int
    groupIndex: int
    side: int


class JsonWmoMaterialInformation(TypedDict, total=True):
    flags: int
    materialID: int


JsonWmoRenderBatches = List['JsonWmoRenderBatch']
class JsonWmoRenderBatch(TypedDict, total=True):
    # FIXME: what are these?
    possibleBox1: JsonVertex   # actually int though?
    possibleBox2: JsonVertex   # actually int though?
    firstFace: int
    numFaces: int
    firstVertex: int
    lastVertex: int
    flags: int
    materialID: int


JsonVertexColorLayer = List[int]

JsonWmoGroups = List['JsonWmoGroup']
class JsonWmoGroup(TypedDict, total=True):
    groupName: str
    groupDescription: str
    enabled: bool
    version: int
    flags: int
    boundingBox1: JsonVertex
    boundingBox2: JsonVertex
    numPortals: int
    numBatchesA: int
    numBatchesB: int
    numBatchesC: int
    liquidType: int
    groupID: int
    materialInfo: List[JsonWmoMaterialInformation]
    renderBatches: JsonWmoRenderBatches
    vertexColours: List[JsonVertexColorLayer]


class JsonWmoGroupInformation(TypedDict, total=True):
    flags: int
    boundingBox1: JsonVertex
    boundingBox2: JsonVertex
    nameIndex: int


JsonWmoMaterials = List['JsonWmoMaterial']
class JsonWmoMaterial(TypedDict, total=True):
    flags: int
    shader: int
    blendMode: int
    texture1: int
    color1: int
    color1b: int
    texture2: int
    color2: int
    groupType: int
    texture3: int
    color3: int
    flags3: int


JsonWmoDoodadSets = List['JsonWmoDoodadSet']
class JsonWmoDoodadSet(TypedDict, total=True):
    name: str
    firstInstanceIndex: int
    doodadCount: int
    # unused: int


JsonWmoDoodads = List['JsonWmoDoodad']
class JsonWmoDoodad(TypedDict, total=True):
    offset: int
    flags: int
    position: JsonPosition
    rotation: JsonRotation
    scale: float
    color: Tuple[int, int, int, int]  # FIXME: proper datatype


class JsonWmoMetadata(TypedDict, total=True):
    fileDataID: int
    fileName: str
    version: int
    counts: JsonWmoCounts
    portalVertices: List[JsonVertex]
    portalInfo: List[JsonPortalInformation]
    portalMapObjectRef: List[JsonPortalMapObjectReference]
    ambientColor: int
    areaTableID: int
    boundingBox1: JsonVertex
    boundingBox2: JsonVertex
    flags: int
    groups: JsonWmoGroups
    groupNames: List[str]
    groupInfo: List[JsonWmoGroupInformation]
    textures: JsonTextures
    materials: JsonWmoMaterials
    doodadSets: JsonWmoDoodadSets
    fileDataIDs: List[int]
    doodads: JsonWmoDoodads
    groupIDs: List[int]
