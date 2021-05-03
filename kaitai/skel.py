# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Skel(KaitaiStruct):

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
        self.chunks = []
        i = 0
        while True:
            _ = Skel.SkelChunk(self._io, self, self._root)
            self.chunks.append(_)
            if self._io.is_eof():
                break
            i += 1

    class C3segment(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.start = Skel.C3vector(self._io, self, self._root)
            self.end = Skel.C3vector(self._io, self, self._root)


    class M2light(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type = self._io.read_u2le()
            self.bone = self._io.read_s2le()
            self.position = Skel.C3vector(self._io, self, self._root)
            self.ambient_color = Skel.M2track(Skel.M2trackTypes.c3vector, self._io, self, self._root)
            self.ambient_intensity = Skel.M2track(Skel.M2trackTypes.float, self._io, self, self._root)
            self.diffuse_color = Skel.M2track(Skel.M2trackTypes.c3vector, self._io, self, self._root)
            self.diffuse_intensity = Skel.M2track(Skel.M2trackTypes.float, self._io, self, self._root)
            self.attenuation_start = Skel.M2track(Skel.M2trackTypes.float, self._io, self, self._root)
            self.attenuation_end = Skel.M2track(Skel.M2trackTypes.float, self._io, self, self._root)
            self.visibility = Skel.M2track(Skel.M2trackTypes.uint8, self._io, self, self._root)


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
            self.unknown3 = Skel.M2parttrack(Skel.M2arrayTypes.fixed16, self._io, self, self._root)


    class ChunkSka1(KaitaiStruct):
        """Skeleton Attachment Data.
        
        .. seealso::
           Source - https://wowdev.wiki/M2/.skel#SKA1
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.attachments = Skel.M2array(Skel.M2arrayTypes.m2attachment, self._io, self, self._root)
            self.attachment_lookup_table = Skel.M2array(Skel.M2arrayTypes.int16, self._io, self, self._root)


    class ChunkSkpd(KaitaiStruct):
        """Skeleton Parent Data. Parent skeleton file data id is used for
        de-duplication.   e.g. `lightforgeddraeneimale` references
        `draeneimale_hd`. The former does not have any .anim files, but
        uses those of the latter via parent-link (does not even have an
        AFID chunk).
        
        Note that it appears the child .skels still have SKx1 chunks, so
        apparently only FID are shared?
        
        .. seealso::
           Source - https://wowdev.wiki/M2/.skel#SKPD
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown1 = [None] * (8)
            for i in range(8):
                self.unknown1[i] = self._io.read_u1()

            self.parent_skel_file_id = self._io.read_u4le()
            self.unknown2 = [None] * (4)
            for i in range(4):
                self.unknown2[i] = self._io.read_u1()



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
            self.replay = Skel.M2range(self._io, self, self._root)
            self.blend_time_in = self._io.read_u2le()
            self.blend_time_out = self._io.read_u2le()
            self.bounds = Skel.M2bounds(self._io, self, self._root)
            self.variation_next = self._io.read_s2le()
            self.alias_next = self._io.read_u2le()


    class M2texturetransform(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.translation = Skel.M2track(Skel.M2trackTypes.c3vector, self._io, self, self._root)
            self.rotation = Skel.M2track(Skel.M2trackTypes.c4quaternion, self._io, self, self._root)
            self.scaling = Skel.M2track(Skel.M2trackTypes.c3vector, self._io, self, self._root)


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
            self.flags = Skel.M2particlesFlags(self._io, self, self._root)
            self.position = Skel.C3vector(self._io, self, self._root)
            self.bone = self._io.read_u2le()
            self.texture_0 = self._io.read_bits_int_le(5)
            self.texture_1 = self._io.read_bits_int_le(5)
            self.texture_2 = self._io.read_bits_int_le(5)
            self._io.align_to_byte()
            self.geometry_model_filename = Skel.M2arrayStr(self._io, self, self._root)
            self.recursion_model_filename = Skel.M2arrayStr(self._io, self, self._root)
            self.blending_type = KaitaiStream.resolve_enum(Skel.Blendmodes, self._io.read_u1())
            self.emitter_type = KaitaiStream.resolve_enum(Skel.EmitterTypes, self._io.read_u1())
            self.particle_color_index = self._io.read_u2le()
            self.multi_texture_param_x = self._io.read_u1()
            self.multi_texture_param_y = self._io.read_u1()
            self.texture_tile_rotation = self._io.read_s2le()
            self.texture_dimensions_rows = self._io.read_u2le()
            self.texture_dimensions_columns = self._io.read_u2le()
            self.emission_speed = Skel.M2track(Skel.M2trackTypes.float, self._io, self, self._root)
            self.speed_variation = Skel.M2track(Skel.M2trackTypes.float, self._io, self, self._root)
            self.vertical_range = Skel.M2track(Skel.M2trackTypes.float, self._io, self, self._root)
            self.horizontal_range = Skel.M2track(Skel.M2trackTypes.float, self._io, self, self._root)
            self.gravity = Skel.M2track(Skel.M2trackTypes.float, self._io, self, self._root)
            self.lifespan = Skel.M2track(Skel.M2trackTypes.float, self._io, self, self._root)
            self.lifespan_vary = self._io.read_f4le()
            self.emission_rate = Skel.M2track(Skel.M2trackTypes.float, self._io, self, self._root)
            self.emission_rate_vary = self._io.read_f4le()
            self.emission_area_length = Skel.M2track(Skel.M2trackTypes.float, self._io, self, self._root)
            self.emission_area_width = Skel.M2track(Skel.M2trackTypes.float, self._io, self, self._root)
            self.z_source = Skel.M2track(Skel.M2trackTypes.float, self._io, self, self._root)
            self.p = Skel.ModelParticleParams(self._io, self, self._root)
            self.enabled_in = Skel.M2track(Skel.M2trackTypes.uint16, self._io, self, self._root)


    class Cfacet(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.plane = Skel.C4plane(self._io, self, self._root)
            self.vertices = [None] * (3)
            for i in range(3):
                self.vertices[i] = Skel.C3vector(self._io, self, self._root)



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
                if _on == Skel.M2arrayTypes.fixed16:
                    self._m_values[i] = Skel.Fixed16(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2ribbon:
                    self._m_values[i] = Skel.M2ribbon(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.int16:
                    self._m_values[i] = self._io.read_s2le()
                elif _on == Skel.M2arrayTypes.m2array_c4quaternion:
                    self._m_values[i] = Skel.M2array(Skel.M2arrayTypes.c4quaternion, self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2vertex:
                    self._m_values[i] = Skel.M2vertex(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2light:
                    self._m_values[i] = Skel.M2light(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2sequence:
                    self._m_values[i] = Skel.M2sequence(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2array_fixed16:
                    self._m_values[i] = Skel.M2array(Skel.M2arrayTypes.fixed16, self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2array_c3vector:
                    self._m_values[i] = Skel.M2array(Skel.M2arrayTypes.c3vector, self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2loop:
                    self._m_values[i] = Skel.M2loop(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2sequencefallback:
                    self._m_values[i] = Skel.M2sequencefallback(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.uint8:
                    self._m_values[i] = self._io.read_u1()
                elif _on == Skel.M2arrayTypes.uint32:
                    self._m_values[i] = self._io.read_u4le()
                elif _on == Skel.M2arrayTypes.todo:
                    self._m_values[i] = Skel.M2arrayTodo(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2event:
                    self._m_values[i] = Skel.M2event(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.c4quaternion:
                    self._m_values[i] = Skel.C4quaternion(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2texturetransform:
                    self._m_values[i] = Skel.M2texturetransform(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.c3vector:
                    self._m_values[i] = Skel.C3vector(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2particle:
                    self._m_values[i] = Skel.M2particle(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2color:
                    self._m_values[i] = Skel.M2color(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2shadowbatch:
                    self._m_values[i] = Skel.M2shadowbatch(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.float:
                    self._m_values[i] = self._io.read_f4le()
                elif _on == Skel.M2arrayTypes.c4vector:
                    self._m_values[i] = Skel.C4vector(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2texture:
                    self._m_values[i] = Skel.M2texture(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.c2vector:
                    self._m_values[i] = Skel.C2vector(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2array_c4vector:
                    self._m_values[i] = Skel.M2array(Skel.M2arrayTypes.c4vector, self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2extended_particle:
                    self._m_values[i] = Skel.M2extendedParticle(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.uint16:
                    self._m_values[i] = self._io.read_u2le()
                elif _on == Skel.M2arrayTypes.m2array_m2compquat:
                    self._m_values[i] = Skel.M2array(Skel.M2arrayTypes.m2compquat, self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2attachment:
                    self._m_values[i] = Skel.M2attachment(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.int8:
                    self._m_values[i] = self._io.read_s1()
                elif _on == Skel.M2arrayTypes.m2array_float:
                    self._m_values[i] = Skel.M2array(Skel.M2arrayTypes.float, self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2array_c2vector:
                    self._m_values[i] = Skel.M2array(Skel.M2arrayTypes.c2vector, self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.frgb:
                    self._m_values[i] = Skel.Frgb(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2material:
                    self._m_values[i] = Skel.M2material(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2array_uint32:
                    self._m_values[i] = Skel.M2array(Skel.M2arrayTypes.uint32, self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2compquat:
                    self._m_values[i] = Skel.M2compquat(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.ubyte4:
                    self._m_values[i] = Skel.Ubyte4(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2camera:
                    self._m_values[i] = Skel.M2camera(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2compbone:
                    self._m_values[i] = Skel.M2compbone(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.pgd1_entry:
                    self._m_values[i] = Skel.Pgd1Entry(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2array_uint16:
                    self._m_values[i] = Skel.M2array(Skel.M2arrayTypes.uint16, self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2batch:
                    self._m_values[i] = Skel.M2batch(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2skinsection:
                    self._m_values[i] = Skel.M2skinsection(self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2array_uint8:
                    self._m_values[i] = Skel.M2array(Skel.M2arrayTypes.uint8, self._io, self, self._root)
                elif _on == Skel.M2arrayTypes.m2textureweight:
                    self._m_values[i] = Skel.M2textureweight(self._io, self, self._root)

            self._io.seek(_pos)
            return self._m_values if hasattr(self, '_m_values') else None


    class M2textureweight(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.weight = Skel.M2track(Skel.M2trackTypes.fixed16, self._io, self, self._root)


    class M2bounds(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.extent = Skel.Caabox(self._io, self, self._root)
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
            self.positions = Skel.M2track(Skel.M2trackTypes.todo, self._io, self, self._root)
            self.position_base = Skel.C3vector(self._io, self, self._root)
            self.target_position = Skel.M2track(Skel.M2trackTypes.todo, self._io, self, self._root)
            self.target_position_base = Skel.C3vector(self._io, self, self._root)
            self.roll = Skel.M2track(Skel.M2trackTypes.todo, self._io, self, self._root)
            self.fov = Skel.M2track(Skel.M2trackTypes.todo, self._io, self, self._root)


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



    class ChunkPgd1(KaitaiStruct):
        """Particle Geoset Data - Sets geoset for each Particle emitter.
        And with this value Particle Emitter start to obey same geoset
        rules as in M2SkinSection
        
        .. seealso::
           Source - https://wowdev.wiki/M2#PGD1
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.p_g_d_v1 = Skel.M2array(Skel.M2arrayTypes.pgd1_entry, self._io, self, self._root)


    class C34matrix(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.columns = [None] * (4)
            for i in range(4):
                self.columns[i] = Skel.C3vector(self._io, self, self._root)



    class ChunkMd21(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = Skel.ChunkMd20(self._io, self, self._root)


    class C3ray(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.origin = Skel.C3vector(self._io, self, self._root)
            self.dir = Skel.C3vector(self._io, self, self._root)


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
            self.normal = Skel.C3vector(self._io, self, self._root)
            self.distance = self._io.read_f4le()


    class ChunkDetl(KaitaiStruct):
        """Literally nothing is known about this chunk type.
        
        .. seealso::
           Source - https://wowdev.wiki/M2#DETL
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            pass


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
            self.blending_mode = KaitaiStream.resolve_enum(Skel.M2materialBlendmodes, self._io.read_u2le())


    class M2color(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.color = Skel.M2track(Skel.M2trackTypes.c3vector, self._io, self, self._root)
            self.alpha = Skel.M2track(Skel.M2trackTypes.fixed16, self._io, self, self._root)


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
            self.colors = Skel.Fblock(Skel.M2arrayTypes.frgb, self._io, self, self._root)
            self.opacity = Skel.Fblock(Skel.M2arrayTypes.uint16, self._io, self, self._root)
            self.sizes = Skel.Fblock(Skel.M2arrayTypes.c2vector, self._io, self, self._root)
            self.d = [None] * (2)
            for i in range(2):
                self.d[i] = self._io.read_u4le()

            self.intensity = Skel.Fblock(Skel.M2arrayTypes.uint16, self._io, self, self._root)
            self.unk2 = Skel.Fblock(Skel.M2arrayTypes.uint16, self._io, self, self._root)
            self.unk = [None] * (3)
            for i in range(3):
                self.unk[i] = self._io.read_f4le()

            self.scales = Skel.C3vector(self._io, self, self._root)
            self.slowdown = self._io.read_f4le()
            self.unknown1 = [None] * (2)
            for i in range(2):
                self.unknown1[i] = self._io.read_f4le()

            self.rotation = self._io.read_f4le()
            self.unknown2 = [None] * (2)
            for i in range(2):
                self.unknown2[i] = self._io.read_f4le()

            self.rot1 = Skel.C3vector(self._io, self, self._root)
            self.rot2 = Skel.C3vector(self._io, self, self._root)
            self.trans = Skel.C3vector(self._io, self, self._root)
            self.f2 = [None] * (4)
            for i in range(4):
                self.f2[i] = self._io.read_f4le()

            self.unknown_reference = Skel.M2array(Skel.M2arrayTypes.todo, self._io, self, self._root)


    class ChunkSkb1(KaitaiStruct):
        """Skeleton Bone Data.
        
        .. seealso::
           Source - https://wowdev.wiki/M2/.skel#SKB1
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.bones = Skel.M2array(Skel.M2arrayTypes.m2compbone, self._io, self, self._root)
            self.key_bone_lookup = Skel.M2array(Skel.M2arrayTypes.int16, self._io, self, self._root)


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
            self.position = Skel.C3vector(self._io, self, self._root)
            self.enabled = Skel.M2trackbase(self._io, self, self._root)


    class ChunkSks1(KaitaiStruct):
        """Skeleton Sequence Data.
        
        .. seealso::
           Source - https://wowdev.wiki/M2/.skel#SKS1
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.global_loops = Skel.M2array(Skel.M2arrayTypes.m2loop, self._io, self, self._root)
            self.sequences = Skel.M2array(Skel.M2arrayTypes.m2sequence, self._io, self, self._root)
            self.sequence_lookups = Skel.M2array(Skel.M2arrayTypes.int16, self._io, self, self._root)
            self.unknown1 = [None] * (8)
            for i in range(8):
                self.unknown1[i] = self._io.read_u1()



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
            self.filename = Skel.M2arrayStr(self._io, self, self._root)


    class ChunkSkl1(KaitaiStruct):
        """Skeleton Data.
        
        .. seealso::
           Source - https://wowdev.wiki/M2/.skel#SKL1
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.flags = self._io.read_u4le()
            self.name = Skel.M2arrayStr(self._io, self, self._root)
            self.unknown1 = [None] * (4)
            for i in range(4):
                self.unknown1[i] = self._io.read_u1()



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
            self.translation = Skel.M2track(Skel.M2trackTypes.c3vector, self._io, self, self._root)
            self.rotation = Skel.M2track(Skel.M2trackTypes.m2compquat, self._io, self, self._root)
            self.scale = Skel.M2track(Skel.M2trackTypes.c3vector, self._io, self, self._root)
            self.pivot = Skel.C3vector(self._io, self, self._root)


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


    class SkelChunk(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.chunk_type = (self._io.read_bytes(4)).decode(u"UTF-8")
            self.chunk_size = self._io.read_u4le()
            _on = self.chunk_type
            if _on == u"SKA1":
                self._raw_data = self._io.read_bytes(self.chunk_size)
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Skel.ChunkSka1(_io__raw_data, self, self._root)
            elif _on == u"AFID":
                self._raw_data = self._io.read_bytes(self.chunk_size)
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Skel.ChunkAfid(_io__raw_data, self, self._root)
            elif _on == u"BFID":
                self._raw_data = self._io.read_bytes(self.chunk_size)
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Skel.ChunkBfid(_io__raw_data, self, self._root)
            elif _on == u"SKPD":
                self._raw_data = self._io.read_bytes(self.chunk_size)
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Skel.ChunkSkpd(_io__raw_data, self, self._root)
            elif _on == u"SKS1":
                self._raw_data = self._io.read_bytes(self.chunk_size)
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Skel.ChunkSks1(_io__raw_data, self, self._root)
            elif _on == u"SKB1":
                self._raw_data = self._io.read_bytes(self.chunk_size)
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Skel.ChunkSkb1(_io__raw_data, self, self._root)
            elif _on == u"SKL1":
                self._raw_data = self._io.read_bytes(self.chunk_size)
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Skel.ChunkSkl1(_io__raw_data, self, self._root)
            else:
                self._raw_data = self._io.read_bytes(self.chunk_size)
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Skel.Noop(_io__raw_data, self, self._root)


    class M2vertex(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pos = Skel.C3vector(self._io, self, self._root)
            self.bone_weights = [None] * (4)
            for i in range(4):
                self.bone_weights[i] = self._io.read_u1()

            self.bone_indices = [None] * (4)
            for i in range(4):
                self.bone_indices[i] = self._io.read_u1()

            self.normal = Skel.C3vector(self._io, self, self._root)
            self.tex_coords = [None] * (2)
            for i in range(2):
                self.tex_coords[i] = Skel.C2vector(self._io, self, self._root)



    class ChunkMd20(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magic2 = self._io.read_bytes(4)
            if not self.magic2 == b"\x4D\x44\x32\x30":
                raise kaitaistruct.ValidationNotEqualError(b"\x4D\x44\x32\x30", self.magic2, self._io, u"/types/chunk_md20/seq/0")
            self.version = KaitaiStream.resolve_enum(Skel.WowVersions, self._io.read_u4le())
            self.name = Skel.M2arrayStr(self._io, self, self._root)
            self._raw_global_flags = self._io.read_bytes(4)
            _io__raw_global_flags = KaitaiStream(BytesIO(self._raw_global_flags))
            self.global_flags = Skel.Md20GlobalFlags(_io__raw_global_flags, self, self._root)
            self.global_loops = Skel.M2array(Skel.M2arrayTypes.m2loop, self._io, self, self._root)
            self.sequences = Skel.M2array(Skel.M2arrayTypes.m2sequence, self._io, self, self._root)
            self.sequence_idx_hash_by_id = Skel.M2array(Skel.M2arrayTypes.uint16, self._io, self, self._root)
            self.bones = Skel.M2array(Skel.M2arrayTypes.m2compbone, self._io, self, self._root)
            self.bone_indices_by_id = Skel.M2array(Skel.M2arrayTypes.uint16, self._io, self, self._root)
            self.vertices = Skel.M2array(Skel.M2arrayTypes.m2vertex, self._io, self, self._root)
            self.num_skin_profiles = self._io.read_u4le()
            self.colors = Skel.M2array(Skel.M2arrayTypes.m2color, self._io, self, self._root)
            self.textures = Skel.M2array(Skel.M2arrayTypes.m2texture, self._io, self, self._root)
            self.texture_weights = Skel.M2array(Skel.M2arrayTypes.m2textureweight, self._io, self, self._root)
            self.texture_transforms = Skel.M2array(Skel.M2arrayTypes.m2texturetransform, self._io, self, self._root)
            self.texture_indices_by_id = Skel.M2array(Skel.M2arrayTypes.uint16, self._io, self, self._root)
            self.materials = Skel.M2array(Skel.M2arrayTypes.m2material, self._io, self, self._root)
            self.bone_combos = Skel.M2array(Skel.M2arrayTypes.uint16, self._io, self, self._root)
            self.texture_combos = Skel.M2array(Skel.M2arrayTypes.uint16, self._io, self, self._root)
            self.texture_transform_bone_map = Skel.M2array(Skel.M2arrayTypes.uint16, self._io, self, self._root)
            self.texture_weight_combos = Skel.M2array(Skel.M2arrayTypes.uint16, self._io, self, self._root)
            self.texture_transform_combos = Skel.M2array(Skel.M2arrayTypes.uint16, self._io, self, self._root)
            self.bounding_box = Skel.Caabox(self._io, self, self._root)
            self.bounding_sphere_radius = self._io.read_f4le()
            self.collision_box = Skel.Caabox(self._io, self, self._root)
            self.collision_sphere_radius = self._io.read_f4le()
            self.collision_indices = Skel.M2array(Skel.M2arrayTypes.uint16, self._io, self, self._root)
            self.collision_positions = Skel.M2array(Skel.M2arrayTypes.c3vector, self._io, self, self._root)
            self.collision_face_normals = Skel.M2array(Skel.M2arrayTypes.c3vector, self._io, self, self._root)
            self.attachments = Skel.M2array(Skel.M2arrayTypes.m2attachment, self._io, self, self._root)
            self.attachment_indices_by_id = Skel.M2array(Skel.M2arrayTypes.uint16, self._io, self, self._root)
            self.events = Skel.M2array(Skel.M2arrayTypes.m2event, self._io, self, self._root)
            self.lights = Skel.M2array(Skel.M2arrayTypes.m2light, self._io, self, self._root)
            self.cameras = Skel.M2array(Skel.M2arrayTypes.m2camera, self._io, self, self._root)
            self.camera_indices_by_id = Skel.M2array(Skel.M2arrayTypes.uint16, self._io, self, self._root)
            self.ribbon_emitters = Skel.M2array(Skel.M2arrayTypes.m2ribbon, self._io, self, self._root)
            self.particle_emitters = Skel.M2array(Skel.M2arrayTypes.m2particle, self._io, self, self._root)
            if self.global_flags.flag_use_texture_combiner_combos:
                self.texture_combiner_combos = Skel.M2array(Skel.M2arrayTypes.uint16, self._io, self, self._root)



    class ChunkTxac(KaitaiStruct):
        """Particle-texture Releated.
        
        .. seealso::
           Source - https://wowdev.wiki/M2#TXAC
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.txac_mesh = [None] * (self._root.chunks[0].data.data.materials.num)
            for i in range(self._root.chunks[0].data.data.materials.num):
                self.txac_mesh[i] = self._io.read_u2le()

            self.txac_m_particle = [None] * (self._root.chunks[0].data.data.particle_emitters.num)
            for i in range(self._root.chunks[0].data.data.particle_emitters.num):
                self.txac_m_particle[i] = self._io.read_u2le()



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
            self.position = Skel.C3vector(self._io, self, self._root)
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


    class Noop(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            pass


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
            self.timestamps = Skel.M2array(Skel.M2arrayTypes.m2array_uint32, self._io, self, self._root)
            _on = self.m2track_type
            if _on == Skel.M2trackTypes.uint8:
                self.values = Skel.M2array(Skel.M2arrayTypes.m2array_uint8, self._io, self, self._root)
            elif _on == Skel.M2trackTypes.c2vector:
                self.values = Skel.M2array(Skel.M2arrayTypes.m2array_c2vector, self._io, self, self._root)
            elif _on == Skel.M2trackTypes.c4quaternion:
                self.values = Skel.M2array(Skel.M2arrayTypes.m2array_c4quaternion, self._io, self, self._root)
            elif _on == Skel.M2trackTypes.m2compquat:
                self.values = Skel.M2array(Skel.M2arrayTypes.m2array_m2compquat, self._io, self, self._root)
            elif _on == Skel.M2trackTypes.uint16:
                self.values = Skel.M2array(Skel.M2arrayTypes.m2array_uint16, self._io, self, self._root)
            elif _on == Skel.M2trackTypes.float:
                self.values = Skel.M2array(Skel.M2arrayTypes.m2array_float, self._io, self, self._root)
            elif _on == Skel.M2trackTypes.fixed16:
                self.values = Skel.M2array(Skel.M2arrayTypes.m2array_fixed16, self._io, self, self._root)
            elif _on == Skel.M2trackTypes.todo:
                self.values = Skel.M2array(Skel.M2arrayTypes.todo, self._io, self, self._root)
            elif _on == Skel.M2trackTypes.c3vector:
                self.values = Skel.M2array(Skel.M2arrayTypes.m2array_c3vector, self._io, self, self._root)


    class Crange(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.min = self._io.read_f4le()
            self.max = self._io.read_f4le()


    class ChunkTxid(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.file_data_id = []
            i = 0
            while not self._io.is_eof():
                self.file_data_id.append(self._io.read_u4le())
                i += 1



    class M2parttrack(KaitaiStruct):
        def __init__(self, m2array_type, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.m2array_type = m2array_type
            self._read()

        def _read(self):
            self.times = Skel.M2array(Skel.M2arrayTypes.fixed16, self._io, self, self._root)
            _on = self.m2array_type
            if _on == Skel.M2arrayTypes.fixed16:
                self.values = Skel.M2array(Skel.M2arrayTypes.fixed16, self._io, self, self._root)


    class Md20GlobalFlags(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.flag_tilt_x = self._io.read_bits_int_le(1) != 0
            self.flag_tilt_y = self._io.read_bits_int_le(1) != 0
            self.flag_unk_0x04 = self._io.read_bits_int_le(1) != 0
            self.flag_use_texture_combiner_combos = self._io.read_bits_int_le(1) != 0
            self.flag_unk_0x10 = self._io.read_bits_int_le(1) != 0
            self.flag_load_phys_data = self._io.read_bits_int_le(1) != 0
            self.flag_unk_0x40 = self._io.read_bits_int_le(1) != 0
            self.flag_unk_0x80 = self._io.read_bits_int_le(1) != 0
            self.flag_camera_related = self._io.read_bits_int_le(1) != 0
            self.flag_new_particle_record = self._io.read_bits_int_le(1) != 0
            self.flag_unk_0x400 = self._io.read_bits_int_le(1) != 0
            self.flag_texture_transforms_use_bone_sequences = self._io.read_bits_int_le(1) != 0
            self.flag_unk_0x1000 = self._io.read_bits_int_le(1) != 0
            self.flag_unk_0x2000 = self._io.read_bits_int_le(1) != 0
            self.flag_unk_0x4000 = self._io.read_bits_int_le(1) != 0
            self.flag_unk_0x8000 = self._io.read_bits_int_le(1) != 0
            self.flag_unk_0x10000 = self._io.read_bits_int_le(1) != 0
            self.flag_unk_0x20000 = self._io.read_bits_int_le(1) != 0
            self.flag_unk_0x40000 = self._io.read_bits_int_le(1) != 0
            self.flag_unk_0x80000 = self._io.read_bits_int_le(1) != 0
            self.flag_unk_0x100000 = self._io.read_bits_int_le(1) != 0
            self.flag_unk_0x200000 = self._io.read_bits_int_le(1) != 0


    class Vector2fp69(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = Skel.Fp69(self._io, self, self._root)
            self.y = Skel.Fp69(self._io, self, self._root)


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
            self.timestamps = Skel.M2array(Skel.M2arrayTypes.m2array_uint32, self._io, self, self._root)


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
                self.columns[i] = Skel.C3vector(self._io, self, self._root)



    class M2particle(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.old = Skel.M2particleOld(self._io, self, self._root)
            self.multi_texture_param0 = [None] * (2)
            for i in range(2):
                self.multi_texture_param0[i] = Skel.Vector2fp69(self._io, self, self._root)

            self.multi_texture_param1 = [None] * (2)
            for i in range(2):
                self.multi_texture_param1[i] = Skel.Vector2fp69(self._io, self, self._root)



    class AnimFileId(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.anim_id = self._io.read_u2le()
            self.sub_anim_id = self._io.read_u2le()
            self.file_id = self._io.read_u4le()


    class Fblock(KaitaiStruct):
        def __init__(self, m2array_type, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.m2array_type = m2array_type
            self._read()

        def _read(self):
            self.timestamps = Skel.M2array(Skel.M2arrayTypes.uint16, self._io, self, self._root)
            _on = self.m2array_type
            if _on == Skel.M2arrayTypes.fixed16:
                self.values = Skel.M2array(Skel.M2arrayTypes.fixed16, self._io, self, self._root)
            elif _on == Skel.M2arrayTypes.uint8:
                self.values = Skel.M2array(Skel.M2arrayTypes.uint8, self._io, self, self._root)
            elif _on == Skel.M2arrayTypes.todo:
                self.values = Skel.M2array(Skel.M2arrayTypes.todo, self._io, self, self._root)
            elif _on == Skel.M2arrayTypes.c4quaternion:
                self.values = Skel.M2array(Skel.M2arrayTypes.c4quaternion, self._io, self, self._root)
            elif _on == Skel.M2arrayTypes.c3vector:
                self.values = Skel.M2array(Skel.M2arrayTypes.c3vector, self._io, self, self._root)
            elif _on == Skel.M2arrayTypes.float:
                self.values = Skel.M2array(Skel.M2arrayTypes.float, self._io, self, self._root)
            elif _on == Skel.M2arrayTypes.c4vector:
                self.values = Skel.M2array(Skel.M2arrayTypes.c4vector, self._io, self, self._root)
            elif _on == Skel.M2arrayTypes.c2vector:
                self.values = Skel.M2array(Skel.M2arrayTypes.c2vector, self._io, self, self._root)
            elif _on == Skel.M2arrayTypes.uint16:
                self.values = Skel.M2array(Skel.M2arrayTypes.uint16, self._io, self, self._root)
            elif _on == Skel.M2arrayTypes.frgb:
                self.values = Skel.M2array(Skel.M2arrayTypes.frgb, self._io, self, self._root)
            elif _on == Skel.M2arrayTypes.m2compquat:
                self.values = Skel.M2array(Skel.M2arrayTypes.m2compquat, self._io, self, self._root)


    class Todo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.todo_nothing = self._io.read_u4le()


    class ChunkSfid(KaitaiStruct):
        """Skin File Data IDs.
        
        .. seealso::
           Source - https://wowdev.wiki/M2#SFID
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.skin_file_data_ids = [None] * (self._root.chunks[0].data.data.num_skin_profiles)
            for i in range(self._root.chunks[0].data.data.num_skin_profiles):
                self.skin_file_data_ids[i] = self._io.read_u4le()

            self.lod__skin_file_data_ids = []
            i = 0
            while not self._io.is_eof():
                self.lod__skin_file_data_ids.append(self._io.read_u4le())
                i += 1



    class M2box(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.model_rotation_speed_min = Skel.C3vector(self._io, self, self._root)
            self.model_rotation_speed_max = Skel.C3vector(self._io, self, self._root)


    class ChunkBfid(KaitaiStruct):
        """Bone File IDs.
        
        .. seealso::
           Source - https://wowdev.wiki/M2#BFID
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.bone_file_data_ids = []
            i = 0
            while not self._io.is_eof():
                self.bone_file_data_ids.append(self._io.read_u4le())
                i += 1



    class ChunkAfid(KaitaiStruct):
        """Animation File IDs.
        
        .. seealso::
           Source - https://wowdev.wiki/M2#AFID
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.anim_file_ids = []
            i = 0
            while not self._io.is_eof():
                self.anim_file_ids.append(Skel.AnimFileId(self._io, self, self._root))
                i += 1



    class ChunkExp2(KaitaiStruct):
        """Extended particle information, one entry per particle_emitter.
        
        .. seealso::
           Source - https://wowdev.wiki/M2#EXP2
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.content = Skel.M2array(Skel.M2arrayTypes.m2extended_particle, self._io, self, self._root)


    class Caabox(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.min = Skel.C3vector(self._io, self, self._root)
            self.max = Skel.C3vector(self._io, self, self._root)


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
            self.center_position = Skel.C3vector(self._io, self, self._root)
            self.sort_center_position = Skel.C3vector(self._io, self, self._root)
            self.sort_radius = self._io.read_f4le()


    class M2loop(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = self._io.read_u4le()


    class ChunkLdv1(KaitaiStruct):
        """LoD (Level of Detail) Data.
        
        .. seealso::
           Source - https://wowdev.wiki/M2#LDV1
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unk0 = self._io.read_u2le()
            self.lod_count = self._io.read_u2le()
            self.unk2 = self._io.read_f4le()
            self.particle_bone_lod = [None] * (4)
            for i in range(4):
                self.particle_bone_lod[i] = self._io.read_u1()

            self.unk4 = self._io.read_u4le()


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
            self.position = Skel.C3vector(self._io, self, self._root)
            self.animate_attached = Skel.M2track(Skel.M2trackTypes.uint8, self._io, self, self._root)


    class M2ribbon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ribbon_id = self._io.read_u4le()
            self.bone_index = self._io.read_u4le()
            self.position = Skel.C3vector(self._io, self, self._root)
            self.texture_indices = Skel.M2array(Skel.M2arrayTypes.uint16, self._io, self, self._root)
            self.material_indices = Skel.M2array(Skel.M2arrayTypes.uint16, self._io, self, self._root)
            self.color_track = Skel.M2track(Skel.M2trackTypes.c3vector, self._io, self, self._root)
            self.alpha_track = Skel.M2track(Skel.M2trackTypes.fixed16, self._io, self, self._root)
            self.height_above_track = Skel.M2track(Skel.M2trackTypes.float, self._io, self, self._root)
            self.height_below_track = Skel.M2track(Skel.M2trackTypes.float, self._io, self, self._root)
            self.edges_per_second = self._io.read_f4le()
            self.edge_lifetime = self._io.read_f4le()
            self.gravity = self._io.read_f4le()
            self.texture_rows = self._io.read_u2le()
            self.texture_cols = self._io.read_u2le()
            self.tex_slot_track = Skel.M2track(Skel.M2trackTypes.uint16, self._io, self, self._root)
            self.visibility_track = Skel.M2track(Skel.M2trackTypes.uint8, self._io, self, self._root)
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



