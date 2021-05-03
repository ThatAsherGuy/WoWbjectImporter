# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Bls(KaitaiStruct):

    class M2materialBlendmodes(Enum):
        m2blend_opaque = 0
        m2blend_alpha_key = 1
        m2blend_alpha = 2
        m2blend_no_alpha_add = 3
        m2blend_add = 4
        m2blend_mod = 5
        m2blend_mod2x = 6
        m2blend_blendadd = 7

    class Blendmodes(Enum):
        opaque = 0
        src_color_one = 1
        src_alpha_one_minus_src_alpha = 2
        opaque_alphaclip = 3
        src_alpha_one = 4

    class M2arrayTypes(Enum):
        todo = 0
        uint8 = 1
        uint16 = 2
        uint32 = 3
        fixed16 = 4
        float = 5
        ubyte4 = 6
        int8 = 7
        int16 = 8
        c2vector = 21
        c3vector = 22
        c4vector = 23
        c4quaternion = 24
        frgb = 25
        m2sequencefallback = 101
        m2compbone = 102
        m2vertex = 103
        m2color = 104
        m2texture = 105
        m2textureweight = 106
        m2texturetransform = 107
        m2material = 108
        m2attachment = 109
        m2event = 110
        m2light = 111
        m2camera = 112
        m2ribbon = 113
        m2particle = 114
        m2loop = 115
        m2sequence = 116
        m2skinsection = 117
        m2batch = 118
        m2shadowbatch = 119
        m2compquat = 120
        m2extended_particle = 121
        pgd1_entry = 122
        m2array_uint32 = 201
        m2array_m2compquat = 202
        m2array_c2vector = 203
        m2array_c3vector = 204
        m2array_c4vector = 205
        m2array_c4quaternion = 206
        m2array_fixed16 = 207
        m2array_uint8 = 208
        m2array_float = 209
        m2array_uint16 = 210

    class M2trackTypes(Enum):
        todo = 0
        uint8 = 1
        uint16 = 2
        fixed16 = 4
        float = 5
        c2vector = 21
        c3vector = 22
        c4vector = 23
        c4quaternion = 24
        m2compquat = 25

    class WowVersions(Enum):
        tbc = 260
        wotlk = 264
        cata = 265
        mop = 272
        wod = 273
        legion = 274

    class EmitterTypes(Enum):
        plane = 1
        sphere = 2
        spline = 3
        bone = 4
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.magic = self._io.read_bytes(4)
        if not self.magic == b"\x48\x53\x58\x47":
            raise kaitaistruct.ValidationNotEqualError(b"\x48\x53\x58\x47", self.magic, self._io, u"/seq/0")
        self.unknown1 = self._io.read_u4le()
        self.version = self._io.read_u4le()
        self.num_shaders = self._io.read_u4le()
        self.ofs_compressed_chunks = self._io.read_u4le()
        self.num_compressed_chunks = self._io.read_u4le()
        self.ofs_compressed_data = self._io.read_u4le()
        self.ofs_shader_blocks = [None] * ((self.num_shaders + 1))
        for i in range((self.num_shaders + 1)):
            self.ofs_shader_blocks[i] = self._io.read_u4le()

        self.shader_offsets = [None] * ((self.num_compressed_chunks + 1))
        for i in range((self.num_compressed_chunks + 1)):
            self.shader_offsets[i] = self._io.read_u4le()


    class C3segment(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.start = Bls.C3vector(self._io, self, self._root)
            self.end = Bls.C3vector(self._io, self, self._root)


    class M2light(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type = self._io.read_u2le()
            self.bone = self._io.read_s2le()
            self.position = Bls.C3vector(self._io, self, self._root)
            self.ambient_color = Bls.M2track(Bls.M2trackTypes.c3vector, self._io, self, self._root)
            self.ambient_intensity = Bls.M2track(Bls.M2trackTypes.float, self._io, self, self._root)
            self.diffuse_color = Bls.M2track(Bls.M2trackTypes.c3vector, self._io, self, self._root)
            self.diffuse_intensity = Bls.M2track(Bls.M2trackTypes.float, self._io, self, self._root)
            self.attenuation_start = Bls.M2track(Bls.M2trackTypes.float, self._io, self, self._root)
            self.attenuation_end = Bls.M2track(Bls.M2trackTypes.float, self._io, self, self._root)
            self.visibility = Bls.M2track(Bls.M2trackTypes.uint8, self._io, self, self._root)


    class M2extendedParticle(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.z_source = self._io.read_f4le()
            self.unknown1 = self._io.read_u4le()
            self.unknown2 = self._io.read_u4le()
            self.unknown3 = Bls.M2parttrack(Bls.M2arrayTypes.fixed16, self._io, self, self._root)


    class M2sequence(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.id = self._io.read_u2le()
            self.variation_index = self._io.read_u2le()
            self.duration = self._io.read_u4le()
            self.movespeed = self._io.read_f4le()
            self.flags = self._io.read_u4le()
            self.frequency = self._io.read_s2le()
            self.padding = self._io.read_u2le()
            self.replay = Bls.M2range(self._io, self, self._root)
            self.blend_time_in = self._io.read_u2le()
            self.blend_time_out = self._io.read_u2le()
            self.bounds = Bls.M2bounds(self._io, self, self._root)
            self.variation_next = self._io.read_s2le()
            self.alias_next = self._io.read_u2le()


    class M2texturetransform(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.translation = Bls.M2track(Bls.M2trackTypes.c3vector, self._io, self, self._root)
            self.rotation = Bls.M2track(Bls.M2trackTypes.c4quaternion, self._io, self, self._root)
            self.scaling = Bls.M2track(Bls.M2trackTypes.c3vector, self._io, self, self._root)


    class M2batch(KaitaiStruct):
        """Texture Units.
        
        .. seealso::
           Source - https://wowdev.wiki/M2/.skin#Texture_units
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.flags = self._io.read_u1()
            self.priority_plane = self._io.read_s1()
            self.shader_id = self._io.read_u2le()
            self.skin_section_index = self._io.read_u2le()
            self.geoset_index = self._io.read_u2le()
            self.color_index = self._io.read_s2le()
            self.material_index = self._io.read_u2le()
            self.material_layer = self._io.read_u2le()
            self.texture_count = self._io.read_u2le()
            self.texture_combo_index = self._io.read_u2le()
            self.texture_coord_combo_index = self._io.read_u2le()
            self.texture_weight_combo_index = self._io.read_u2le()
            self.texture_transform_combo_index = self._io.read_u2le()


    class M2particleOld(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.particle_id = self._io.read_s4le()
            self.flags = Bls.M2particlesFlags(self._io, self, self._root)
            self.position = Bls.C3vector(self._io, self, self._root)
            self.bone = self._io.read_u2le()
            self.texture_0 = self._io.read_bits_int_le(5)
            self.texture_1 = self._io.read_bits_int_le(5)
            self.texture_2 = self._io.read_bits_int_le(5)
            self._io.align_to_byte()
            self.geometry_model_filename = Bls.M2arrayStr(self._io, self, self._root)
            self.recursion_model_filename = Bls.M2arrayStr(self._io, self, self._root)
            self.blending_type = KaitaiStream.resolve_enum(Bls.Blendmodes, self._io.read_u1())
            self.emitter_type = KaitaiStream.resolve_enum(Bls.EmitterTypes, self._io.read_u1())
            self.particle_color_index = self._io.read_u2le()
            self.multi_texture_param_x = self._io.read_u1()
            self.multi_texture_param_y = self._io.read_u1()
            self.texture_tile_rotation = self._io.read_s2le()
            self.texture_dimensions_rows = self._io.read_u2le()
            self.texture_dimensions_columns = self._io.read_u2le()
            self.emission_speed = Bls.M2track(Bls.M2trackTypes.float, self._io, self, self._root)
            self.speed_variation = Bls.M2track(Bls.M2trackTypes.float, self._io, self, self._root)
            self.vertical_range = Bls.M2track(Bls.M2trackTypes.float, self._io, self, self._root)
            self.horizontal_range = Bls.M2track(Bls.M2trackTypes.float, self._io, self, self._root)
            self.gravity = Bls.M2track(Bls.M2trackTypes.float, self._io, self, self._root)
            self.lifespan = Bls.M2track(Bls.M2trackTypes.float, self._io, self, self._root)
            self.lifespan_vary = self._io.read_f4le()
            self.emission_rate = Bls.M2track(Bls.M2trackTypes.float, self._io, self, self._root)
            self.emission_rate_vary = self._io.read_f4le()
            self.emission_area_length = Bls.M2track(Bls.M2trackTypes.float, self._io, self, self._root)
            self.emission_area_width = Bls.M2track(Bls.M2trackTypes.float, self._io, self, self._root)
            self.z_source = Bls.M2track(Bls.M2trackTypes.float, self._io, self, self._root)
            self.p = Bls.ModelParticleParams(self._io, self, self._root)
            self.enabled_in = Bls.M2track(Bls.M2trackTypes.uint16, self._io, self, self._root)


    class Cfacet(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.plane = Bls.C4plane(self._io, self, self._root)
            self.vertices = [None] * (3)
            for i in range(3):
                self.vertices[i] = Bls.C3vector(self._io, self, self._root)



    class M2array(KaitaiStruct):
        def __init__(self, m2array_type, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.m2array_type = m2array_type
            self._read()

        def _read(self):
            self.num = self._io.read_u4le()
            self.offset = self._io.read_u4le()

        @property
        def values(self):
            if hasattr(self, '_m_values'):
                return self._m_values if hasattr(self, '_m_values') else None

            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._m_values = [None] * (self.num)
            for i in range(self.num):
                _on = self.m2array_type
                if _on == Bls.M2arrayTypes.fixed16:
                    self._m_values[i] = Bls.Fixed16(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2ribbon:
                    self._m_values[i] = Bls.M2ribbon(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.int16:
                    self._m_values[i] = self._io.read_s2le()
                elif _on == Bls.M2arrayTypes.m2array_c4quaternion:
                    self._m_values[i] = Bls.M2array(Bls.M2arrayTypes.c4quaternion, self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2vertex:
                    self._m_values[i] = Bls.M2vertex(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2light:
                    self._m_values[i] = Bls.M2light(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2sequence:
                    self._m_values[i] = Bls.M2sequence(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2array_fixed16:
                    self._m_values[i] = Bls.M2array(Bls.M2arrayTypes.fixed16, self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2array_c3vector:
                    self._m_values[i] = Bls.M2array(Bls.M2arrayTypes.c3vector, self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2loop:
                    self._m_values[i] = Bls.M2loop(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2sequencefallback:
                    self._m_values[i] = Bls.M2sequencefallback(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.uint8:
                    self._m_values[i] = self._io.read_u1()
                elif _on == Bls.M2arrayTypes.uint32:
                    self._m_values[i] = self._io.read_u4le()
                elif _on == Bls.M2arrayTypes.todo:
                    self._m_values[i] = Bls.M2arrayTodo(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2event:
                    self._m_values[i] = Bls.M2event(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.c4quaternion:
                    self._m_values[i] = Bls.C4quaternion(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2texturetransform:
                    self._m_values[i] = Bls.M2texturetransform(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.c3vector:
                    self._m_values[i] = Bls.C3vector(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2particle:
                    self._m_values[i] = Bls.M2particle(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2color:
                    self._m_values[i] = Bls.M2color(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2shadowbatch:
                    self._m_values[i] = Bls.M2shadowbatch(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.float:
                    self._m_values[i] = self._io.read_f4le()
                elif _on == Bls.M2arrayTypes.c4vector:
                    self._m_values[i] = Bls.C4vector(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2texture:
                    self._m_values[i] = Bls.M2texture(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.c2vector:
                    self._m_values[i] = Bls.C2vector(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2array_c4vector:
                    self._m_values[i] = Bls.M2array(Bls.M2arrayTypes.c4vector, self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2extended_particle:
                    self._m_values[i] = Bls.M2extendedParticle(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.uint16:
                    self._m_values[i] = self._io.read_u2le()
                elif _on == Bls.M2arrayTypes.m2array_m2compquat:
                    self._m_values[i] = Bls.M2array(Bls.M2arrayTypes.m2compquat, self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2attachment:
                    self._m_values[i] = Bls.M2attachment(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.int8:
                    self._m_values[i] = self._io.read_s1()
                elif _on == Bls.M2arrayTypes.m2array_float:
                    self._m_values[i] = Bls.M2array(Bls.M2arrayTypes.float, self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2array_c2vector:
                    self._m_values[i] = Bls.M2array(Bls.M2arrayTypes.c2vector, self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.frgb:
                    self._m_values[i] = Bls.Frgb(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2material:
                    self._m_values[i] = Bls.M2material(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2array_uint32:
                    self._m_values[i] = Bls.M2array(Bls.M2arrayTypes.uint32, self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2compquat:
                    self._m_values[i] = Bls.M2compquat(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.ubyte4:
                    self._m_values[i] = Bls.Ubyte4(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2camera:
                    self._m_values[i] = Bls.M2camera(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2compbone:
                    self._m_values[i] = Bls.M2compbone(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.pgd1_entry:
                    self._m_values[i] = Bls.Pgd1Entry(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2array_uint16:
                    self._m_values[i] = Bls.M2array(Bls.M2arrayTypes.uint16, self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2batch:
                    self._m_values[i] = Bls.M2batch(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2skinsection:
                    self._m_values[i] = Bls.M2skinsection(self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2array_uint8:
                    self._m_values[i] = Bls.M2array(Bls.M2arrayTypes.uint8, self._io, self, self._root)
                elif _on == Bls.M2arrayTypes.m2textureweight:
                    self._m_values[i] = Bls.M2textureweight(self._io, self, self._root)

            self._io.seek(_pos)
            return self._m_values if hasattr(self, '_m_values') else None


    class M2textureweight(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.weight = Bls.M2track(Bls.M2trackTypes.fixed16, self._io, self, self._root)


    class M2bounds(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.extent = Bls.Caabox(self._io, self, self._root)
            self.radius = self._io.read_f4le()


    class M2camera(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type = self._io.read_u4le()
            self.far_clip = self._io.read_f4le()
            self.near_clip = self._io.read_f4le()
            self.positions = Bls.M2track(Bls.M2trackTypes.todo, self._io, self, self._root)
            self.position_base = Bls.C3vector(self._io, self, self._root)
            self.target_position = Bls.M2track(Bls.M2trackTypes.todo, self._io, self, self._root)
            self.target_position_base = Bls.C3vector(self._io, self, self._root)
            self.roll = Bls.M2track(Bls.M2trackTypes.todo, self._io, self, self._root)
            self.fov = Bls.M2track(Bls.M2trackTypes.todo, self._io, self, self._root)


    class Ubyte4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.value = [None] * (4)
            for i in range(4):
                self.value[i] = self._io.read_u1()



    class C34matrix(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.columns = [None] * (4)
            for i in range(4):
                self.columns[i] = Bls.C3vector(self._io, self, self._root)



    class C3ray(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.origin = Bls.C3vector(self._io, self, self._root)
            self.dir = Bls.C3vector(self._io, self, self._root)


    class Cimvector(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.b = self._io.read_u1()
            self.g = self._io.read_u1()
            self.r = self._io.read_u1()
            self.a = self._io.read_u1()


    class C4plane(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.normal = Bls.C3vector(self._io, self, self._root)
            self.distance = self._io.read_f4le()


    class Cirect(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.top = self._io.read_s4le()
            self.miny = self._io.read_s4le()
            self.left = self._io.read_s4le()
            self.minx = self._io.read_s4le()
            self.bottom = self._io.read_s4le()
            self.maxy = self._io.read_s4le()
            self.right = self._io.read_s4le()
            self.maxx = self._io.read_s4le()


    class C2ivector(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_s4le()
            self.y = self._io.read_s4le()


    class C3ivector(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_s4le()
            self.y = self._io.read_s4le()
            self.z = self._io.read_s4le()


    class M2material(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.flags_unlit = self._io.read_bits_int_le(1) != 0
            self.flags_unfogged = self._io.read_bits_int_le(1) != 0
            self.flags_twosided = self._io.read_bits_int_le(1) != 0
            self.flags_depthtest = self._io.read_bits_int_le(1) != 0
            self.flags_depthwrite = self._io.read_bits_int_le(1) != 0
            self.flags_unused1 = self._io.read_bits_int_le(1) != 0
            self.flags_shadowbatch1 = self._io.read_bits_int_le(1) != 0
            self.flags_shadowbatch2 = self._io.read_bits_int_le(1) != 0
            self.flags_unused2 = self._io.read_bits_int_le(1) != 0
            self.flags_unused3 = self._io.read_bits_int_le(1) != 0
            self.flags_unknown1 = self._io.read_bits_int_le(1) != 0
            self.flags_preventalpha = self._io.read_bits_int_le(1) != 0
            self._io.align_to_byte()
            self.blending_mode = KaitaiStream.resolve_enum(Bls.M2materialBlendmodes, self._io.read_u2le())


    class M2color(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.color = Bls.M2track(Bls.M2trackTypes.c3vector, self._io, self, self._root)
            self.alpha = Bls.M2track(Bls.M2trackTypes.fixed16, self._io, self, self._root)


    class Frgb(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.r = self._io.read_f4le()
            self.g = self._io.read_f4le()
            self.b = self._io.read_f4le()


    class M2sequencefallback(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.something = self._io.read_u4le()
            self.somethingelse = self._io.read_u4le()


    class ModelParticleParams(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.colors = Bls.Fblock(Bls.M2arrayTypes.frgb, self._io, self, self._root)
            self.opacity = Bls.Fblock(Bls.M2arrayTypes.uint16, self._io, self, self._root)
            self.sizes = Bls.Fblock(Bls.M2arrayTypes.c2vector, self._io, self, self._root)
            self.d = [None] * (2)
            for i in range(2):
                self.d[i] = self._io.read_u4le()

            self.intensity = Bls.Fblock(Bls.M2arrayTypes.uint16, self._io, self, self._root)
            self.unk2 = Bls.Fblock(Bls.M2arrayTypes.uint16, self._io, self, self._root)
            self.unk = [None] * (3)
            for i in range(3):
                self.unk[i] = self._io.read_f4le()

            self.scales = Bls.C3vector(self._io, self, self._root)
            self.slowdown = self._io.read_f4le()
            self.unknown1 = [None] * (2)
            for i in range(2):
                self.unknown1[i] = self._io.read_f4le()

            self.rotation = self._io.read_f4le()
            self.unknown2 = [None] * (2)
            for i in range(2):
                self.unknown2[i] = self._io.read_f4le()

            self.rot1 = Bls.C3vector(self._io, self, self._root)
            self.rot2 = Bls.C3vector(self._io, self, self._root)
            self.trans = Bls.C3vector(self._io, self, self._root)
            self.f2 = [None] * (4)
            for i in range(4):
                self.f2[i] = self._io.read_f4le()

            self.unknown_reference = Bls.M2array(Bls.M2arrayTypes.todo, self._io, self, self._root)


    class M2event(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.identifier = (self._io.read_bytes(4)).decode(u"ASCII")
            self.data = self._io.read_u4le()
            self.bone = self._io.read_u4le()
            self.position = Bls.C3vector(self._io, self, self._root)
            self.enabled = Bls.M2trackbase(self._io, self, self._root)


    class C2vector(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()


    class M2texture(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type = self._io.read_u4le()
            self.flags = self._io.read_u4le()
            self.filename = Bls.M2arrayStr(self._io, self, self._root)


    class M2range(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.minimum = self._io.read_u4le()
            self.maximum = self._io.read_u4le()


    class C4ivector(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_s4le()
            self.y = self._io.read_s4le()
            self.z = self._io.read_s4le()
            self.w = self._io.read_s4le()


    class M2compbone(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.key_bone_id = self._io.read_s4le()
            self.flags = self._io.read_u4le()
            self.parent_bone = self._io.read_s2le()
            self.submesh_id = self._io.read_u2le()
            self.bone_name_crc = self._io.read_u4le()
            self.translation = Bls.M2track(Bls.M2trackTypes.c3vector, self._io, self, self._root)
            self.rotation = Bls.M2track(Bls.M2trackTypes.m2compquat, self._io, self, self._root)
            self.scale = Bls.M2track(Bls.M2trackTypes.c3vector, self._io, self, self._root)
            self.pivot = Bls.C3vector(self._io, self, self._root)


    class M2arrayStr(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.num = self._io.read_u4le()
            self.offset = self._io.read_u4le()

        @property
        def arraydata(self):
            if hasattr(self, '_m_arraydata'):
                return self._m_arraydata if hasattr(self, '_m_arraydata') else None

            io = self._io
            _pos = io.pos()
            io.seek(self.offset)
            self._m_arraydata = (io.read_bytes(self.num)).decode(u"UTF-8")
            io.seek(_pos)
            return self._m_arraydata if hasattr(self, '_m_arraydata') else None


    class M2vertex(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pos = Bls.C3vector(self._io, self, self._root)
            self.bone_weights = [None] * (4)
            for i in range(4):
                self.bone_weights[i] = self._io.read_u1()

            self.bone_indices = [None] * (4)
            for i in range(4):
                self.bone_indices[i] = self._io.read_u1()

            self.normal = Bls.C3vector(self._io, self, self._root)
            self.tex_coords = [None] * (2)
            for i in range(2):
                self.tex_coords[i] = Bls.C2vector(self._io, self, self._root)



    class Fp69(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.value = self._io.read_u2le()


    class Pgd1Entry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.geoset = self._io.read_u2le()


    class Caasphere(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Bls.C3vector(self._io, self, self._root)
            self.radius = self._io.read_f4le()


    class Fixed16(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.value_raw = self._io.read_s2le()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value if hasattr(self, '_m_value') else None

            self._m_value = (self.value_raw / 32767.0)
            return self._m_value if hasattr(self, '_m_value') else None


    class C3vector(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()


    class M2track(KaitaiStruct):
        def __init__(self, m2track_type, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.m2track_type = m2track_type
            self._read()

        def _read(self):
            self.interpolation_type = self._io.read_s2le()
            self.global_sequence = self._io.read_s2le()
            self.timestamps = Bls.M2array(Bls.M2arrayTypes.m2array_uint32, self._io, self, self._root)
            _on = self.m2track_type
            if _on == Bls.M2trackTypes.uint8:
                self.values = Bls.M2array(Bls.M2arrayTypes.m2array_uint8, self._io, self, self._root)
            elif _on == Bls.M2trackTypes.c2vector:
                self.values = Bls.M2array(Bls.M2arrayTypes.m2array_c2vector, self._io, self, self._root)
            elif _on == Bls.M2trackTypes.c4quaternion:
                self.values = Bls.M2array(Bls.M2arrayTypes.m2array_c4quaternion, self._io, self, self._root)
            elif _on == Bls.M2trackTypes.m2compquat:
                self.values = Bls.M2array(Bls.M2arrayTypes.m2array_m2compquat, self._io, self, self._root)
            elif _on == Bls.M2trackTypes.uint16:
                self.values = Bls.M2array(Bls.M2arrayTypes.m2array_uint16, self._io, self, self._root)
            elif _on == Bls.M2trackTypes.float:
                self.values = Bls.M2array(Bls.M2arrayTypes.m2array_float, self._io, self, self._root)
            elif _on == Bls.M2trackTypes.fixed16:
                self.values = Bls.M2array(Bls.M2arrayTypes.m2array_fixed16, self._io, self, self._root)
            elif _on == Bls.M2trackTypes.todo:
                self.values = Bls.M2array(Bls.M2arrayTypes.todo, self._io, self, self._root)
            elif _on == Bls.M2trackTypes.c3vector:
                self.values = Bls.M2array(Bls.M2arrayTypes.m2array_c3vector, self._io, self, self._root)


    class Crange(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.min = self._io.read_f4le()
            self.max = self._io.read_f4le()


    class M2parttrack(KaitaiStruct):
        def __init__(self, m2array_type, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.m2array_type = m2array_type
            self._read()

        def _read(self):
            self.times = Bls.M2array(Bls.M2arrayTypes.fixed16, self._io, self, self._root)
            _on = self.m2array_type
            if _on == Bls.M2arrayTypes.fixed16:
                self.values = Bls.M2array(Bls.M2arrayTypes.fixed16, self._io, self, self._root)


    class Vector2fp69(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = Bls.Fp69(self._io, self, self._root)
            self.y = Bls.Fp69(self._io, self, self._root)


    class CompressedChunk(KaitaiStruct):
        def __init__(self, i, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.i = i
            self._read()

        def _read(self):
            pass

        @property
        def chunk(self):
            if hasattr(self, '_m_chunk'):
                return self._m_chunk if hasattr(self, '_m_chunk') else None

            _pos = self._io.pos()
            self._io.seek(self.chunk_pos)
            self._m_chunk = self._io.read_bytes(self.chunk_size)
            self._io.seek(_pos)
            return self._m_chunk if hasattr(self, '_m_chunk') else None

        @property
        def chunk_pos(self):
            if hasattr(self, '_m_chunk_pos'):
                return self._m_chunk_pos if hasattr(self, '_m_chunk_pos') else None

            self._m_chunk_pos = (self._parent.ofs_compressed_data + self._parent.shader_offsets[self.i])
            return self._m_chunk_pos if hasattr(self, '_m_chunk_pos') else None

        @property
        def chunk_size(self):
            if hasattr(self, '_m_chunk_size'):
                return self._m_chunk_size if hasattr(self, '_m_chunk_size') else None

            self._m_chunk_size = (self._parent.shader_offsets[(self.i + 1)] - self._parent.shader_offsets[self.i])
            return self._m_chunk_size if hasattr(self, '_m_chunk_size') else None


    class Cargb(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.r = self._io.read_u1()
            self.g = self._io.read_u1()
            self.b = self._io.read_u1()
            self.a = self._io.read_u1()


    class M2compquat(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_s2le()
            self.y = self._io.read_s2le()
            self.z = self._io.read_s2le()
            self.w = self._io.read_s2le()


    class M2shadowbatch(KaitaiStruct):
        """Shadow Batches
        
        Generated on the fly, conditionally:
        if !(batches[i].flags & 4) && !batches[i].texunit
           && !(renderflags[batches[i].renderFlag].flags & 0x40)
           && (renderflags[batches[i].renderFlag].blendingmode < 2u
           || renderflags[batches[i].renderFlag].flags & 0x80)
        
        .. seealso::
           Source - https://wowdev.wiki/M2/.skin#shadow_batches
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.flags = self._io.read_u1()
            self.flags2 = self._io.read_u1()
            self.unknown1 = self._io.read_u2le()
            self.submesh_id = self._io.read_u2le()
            self.texture_id = self._io.read_u2le()
            self.color_id = self._io.read_u2le()
            self.transparency_id = self._io.read_u2le()


    class M2trackbase(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.interpolation_type = self._io.read_u2le()
            self.global_sequence = self._io.read_u2le()
            self.timestamps = Bls.M2array(Bls.M2arrayTypes.m2array_uint32, self._io, self, self._root)


    class C4vector(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self.w = self._io.read_f4le()


    class C33matrix(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.columns = [None] * (3)
            for i in range(3):
                self.columns[i] = Bls.C3vector(self._io, self, self._root)



    class M2particle(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.old = Bls.M2particleOld(self._io, self, self._root)
            self.multi_texture_param0 = [None] * (2)
            for i in range(2):
                self.multi_texture_param0[i] = Bls.Vector2fp69(self._io, self, self._root)

            self.multi_texture_param1 = [None] * (2)
            for i in range(2):
                self.multi_texture_param1[i] = Bls.Vector2fp69(self._io, self, self._root)



    class Fblock(KaitaiStruct):
        def __init__(self, m2array_type, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.m2array_type = m2array_type
            self._read()

        def _read(self):
            self.timestamps = Bls.M2array(Bls.M2arrayTypes.uint16, self._io, self, self._root)
            _on = self.m2array_type
            if _on == Bls.M2arrayTypes.fixed16:
                self.values = Bls.M2array(Bls.M2arrayTypes.fixed16, self._io, self, self._root)
            elif _on == Bls.M2arrayTypes.uint8:
                self.values = Bls.M2array(Bls.M2arrayTypes.uint8, self._io, self, self._root)
            elif _on == Bls.M2arrayTypes.todo:
                self.values = Bls.M2array(Bls.M2arrayTypes.todo, self._io, self, self._root)
            elif _on == Bls.M2arrayTypes.c4quaternion:
                self.values = Bls.M2array(Bls.M2arrayTypes.c4quaternion, self._io, self, self._root)
            elif _on == Bls.M2arrayTypes.c3vector:
                self.values = Bls.M2array(Bls.M2arrayTypes.c3vector, self._io, self, self._root)
            elif _on == Bls.M2arrayTypes.float:
                self.values = Bls.M2array(Bls.M2arrayTypes.float, self._io, self, self._root)
            elif _on == Bls.M2arrayTypes.c4vector:
                self.values = Bls.M2array(Bls.M2arrayTypes.c4vector, self._io, self, self._root)
            elif _on == Bls.M2arrayTypes.c2vector:
                self.values = Bls.M2array(Bls.M2arrayTypes.c2vector, self._io, self, self._root)
            elif _on == Bls.M2arrayTypes.uint16:
                self.values = Bls.M2array(Bls.M2arrayTypes.uint16, self._io, self, self._root)
            elif _on == Bls.M2arrayTypes.frgb:
                self.values = Bls.M2array(Bls.M2arrayTypes.frgb, self._io, self, self._root)
            elif _on == Bls.M2arrayTypes.m2compquat:
                self.values = Bls.M2array(Bls.M2arrayTypes.m2compquat, self._io, self, self._root)


    class Todo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.todo_nothing = self._io.read_u4le()


    class M2box(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.model_rotation_speed_min = Bls.C3vector(self._io, self, self._root)
            self.model_rotation_speed_max = Bls.C3vector(self._io, self, self._root)


    class Caabox(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.min = Bls.C3vector(self._io, self, self._root)
            self.max = Bls.C3vector(self._io, self, self._root)


    class M2skinsection(KaitaiStruct):
        """Submesh information.
        
        .. seealso::
           Source - https://wowdev.wiki/M2/.skin#Submeshes
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.skin_section_id = self._io.read_u2le()
            self.level = self._io.read_u2le()
            self.vertex_start = self._io.read_u2le()
            self.vertex_count = self._io.read_u2le()
            self.index_start = self._io.read_u2le()
            self.index_count = self._io.read_u2le()
            self.bone_count = self._io.read_u2le()
            self.bone_combo_index = self._io.read_u2le()
            self.bone_influences = self._io.read_u2le()
            self.center_bone_index = self._io.read_u2le()
            self.center_position = Bls.C3vector(self._io, self, self._root)
            self.sort_center_position = Bls.C3vector(self._io, self, self._root)
            self.sort_radius = self._io.read_f4le()


    class M2loop(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = self._io.read_u4le()


    class M2particlesFlags(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.lit = self._io.read_bits_int_le(1) != 0
            self.unknown1 = self._io.read_bits_int_le(1) != 0
            self.unknown2 = self._io.read_bits_int_le(1) != 0
            self.worldspace = self._io.read_bits_int_le(1) != 0
            self.notrail = self._io.read_bits_int_le(1) != 0
            self.unlightning = self._io.read_bits_int_le(1) != 0
            self.burst_multiplier = self._io.read_bits_int_le(1) != 0
            self.modelspace = self._io.read_bits_int_le(1) != 0
            self.unknown3 = self._io.read_bits_int_le(1) != 0
            self.randomspawn = self._io.read_bits_int_le(1) != 0
            self.pinned = self._io.read_bits_int_le(1) != 0
            self.unknown4 = self._io.read_bits_int_le(1) != 0
            self.nobillboard = self._io.read_bits_int_le(1) != 0
            self.groundclamp = self._io.read_bits_int_le(1) != 0
            self.unknown5 = self._io.read_bits_int_le(1) != 0
            self.unknown6 = self._io.read_bits_int_le(1) != 0
            self.random_texture = self._io.read_bits_int_le(1) != 0
            self.outward = self._io.read_bits_int_le(1) != 0
            self.inward_maybe = self._io.read_bits_int_le(1) != 0
            self.scale_vary_separately = self._io.read_bits_int_le(1) != 0
            self.unknown7 = self._io.read_bits_int_le(1) != 0
            self.random_flipbookstart = self._io.read_bits_int_le(1) != 0
            self.no_throttle_distance = self._io.read_bits_int_le(1) != 0
            self.compressed_gravity = self._io.read_bits_int_le(1) != 0
            self.bone_generator = self._io.read_bits_int_le(1) != 0
            self.unknown8 = self._io.read_bits_int_le(1) != 0
            self.no_throttle_distance2 = self._io.read_bits_int_le(1) != 0
            self.unknown9 = self._io.read_bits_int_le(1) != 0
            self.multi_texture = self._io.read_bits_int_le(1) != 0
            self.unknown10 = self._io.read_bits_int_le(1) != 0
            self.unknown11 = self._io.read_bits_int_le(1) != 0
            self.unknown12 = self._io.read_bits_int_le(1) != 0


    class M2arrayTodo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            pass


    class C4quaternion(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self.w = self._io.read_f4le()


    class Crect(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.top = self._io.read_f4le()
            self.miny = self._io.read_f4le()
            self.left = self._io.read_f4le()
            self.minx = self._io.read_f4le()
            self.bottom = self._io.read_f4le()
            self.maxy = self._io.read_f4le()
            self.right = self._io.read_f4le()
            self.maxx = self._io.read_f4le()


    class M2attachment(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.id = self._io.read_u4le()
            self.bone = self._io.read_u2le()
            self.unknown = self._io.read_u2le()
            self.position = Bls.C3vector(self._io, self, self._root)
            self.animate_attached = Bls.M2track(Bls.M2trackTypes.uint8, self._io, self, self._root)


    class M2ribbon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ribbon_id = self._io.read_u4le()
            self.bone_index = self._io.read_u4le()
            self.position = Bls.C3vector(self._io, self, self._root)
            self.texture_indices = Bls.M2array(Bls.M2arrayTypes.uint16, self._io, self, self._root)
            self.material_indices = Bls.M2array(Bls.M2arrayTypes.uint16, self._io, self, self._root)
            self.color_track = Bls.M2track(Bls.M2trackTypes.c3vector, self._io, self, self._root)
            self.alpha_track = Bls.M2track(Bls.M2trackTypes.fixed16, self._io, self, self._root)
            self.height_above_track = Bls.M2track(Bls.M2trackTypes.float, self._io, self, self._root)
            self.height_below_track = Bls.M2track(Bls.M2trackTypes.float, self._io, self, self._root)
            self.edges_per_second = self._io.read_f4le()
            self.edge_lifetime = self._io.read_f4le()
            self.gravity = self._io.read_f4le()
            self.texture_rows = self._io.read_u2le()
            self.texture_cols = self._io.read_u2le()
            self.tex_slot_track = Bls.M2track(Bls.M2trackTypes.uint16, self._io, self, self._root)
            self.visibility_track = Bls.M2track(Bls.M2trackTypes.uint8, self._io, self, self._root)
            self.priority_plane = self._io.read_s2le()
            self.padding = self._io.read_u2le()


    class C3svector(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_s2le()
            self.y = self._io.read_s2le()
            self.z = self._io.read_s2le()


    class Cirange(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.min = self._io.read_s4le()
            self.max = self._io.read_s4le()


    @property
    def compressed_chunks(self):
        if hasattr(self, '_m_compressed_chunks'):
            return self._m_compressed_chunks if hasattr(self, '_m_compressed_chunks') else None

        self._m_compressed_chunks = [None] * (self.num_compressed_chunks)
        for i in range(self.num_compressed_chunks):
            self._m_compressed_chunks[i] = Bls.CompressedChunk(i, self._io, self, self._root)

        return self._m_compressed_chunks if hasattr(self, '_m_compressed_chunks') else None


