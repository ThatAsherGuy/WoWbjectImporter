meta:
    id: m2
    endian: le
    bit-endian: le
    encoding: UTF-8
seq:
  # This will parse an m2 file. Comment this out if you want a different type
  - id: chunks
    type: chunk
    repeat: until
    repeat-until: _io.eof

  # Uncomment this if you want a .skin file
  #  - id: chunks
  #    type: chunk_skin

enums:
    wow_versions:
      260: tbc
      264: wotlk
      265: cata
      272: mop
      273: wod
      274: legion

    m2array_types:
      0: todo
      1: uint8
      2: uint16
      3: uint32
      4: fixed16
      5: float
      6: ubyte4

      21: c3vector
      22: c4quaternion

      101: m2sequencefallback
      102: m2compbone
      103: m2vertex
      104: m2color
      105: m2texture
      106: m2textureweight
      107: m2texturetransform
      108: m2material
      109: m2attachment
      110: m2event
      111: m2light
      112: m2camera
      113: m2ribbon
      114: m2particle
      115: m2loop
      116: m2sequence
      117: m2skinsection
      118: m2batch
      119: m2shadowbatch

      201: m2array_uint32

    m2track_types:
      0: todo

      1: uint8
      4: fixed16
      5: float

      21: c3vector
      22: c4quaternion



types:
    #
    # Our basic types first

    # FIXME: Figure out if we implemented this right
    fixed16:
      seq:
        - id: value_raw
          type: s2
      instances:
        value:
          value: value_raw / 32767.0

    ubyte4:
      seq:
        - id: value
          type: u1
          repeat: expr
          repeat-expr: 4

    m2range:
      seq:
        - id: minimum
          type: u4
        - id: maximum
          type: u4

    m2bounds:
      seq:
        - id: extent
          type: caabox
        - id: radius
          type: f4

    m2compquat:
      seq:
        - id: x
          type: u2
        - id: y
          type: u2
        - id: z
          type: u2
        - id: w
          type: u2

    c2vector:
      seq:
        - id: x
          type: f4
        - id: y
          type: f4

    c2ivector:
      seq:
        - id: x
          type: s4    # FIXME: check type ("int" in docs)
        - id: y
          type: s4

    c3vector:
      seq:
        - id: x
          type: f4
        - id: y
          type: f4
        - id: z
          type: f4

    c3ivector:
      seq:
        - id:  x
          type: s4
        - id:  y
          type: s4
        - id:  z
          type: s4

    c4vector:
      seq:
        - id: x
          type: f4
        - id: y
          type: f4
        - id: z
          type: f4
        - id: w
          type: f4

    c4ivector:
      seq:
        - id:  x
          type: s4
        - id:  y
          type: s4
        - id:  z
          type: s4
        - id:  w
          type: s4

    # For the matrix types, wowdev.wiki isn't sure if these are row- or column- first
    c33matrix:
      seq:
        - id: columns
          type: c3vector
          repeat: expr
          repeat-expr: 3

    c34matrix:
      seq:
        - id: columns
          type: c3vector
          repeat: expr
          repeat-expr: 4

    # wowdev.wiki says "todo: verify"
    c4plane:
      seq:
        - id: normal
          type: c3vector
        - id: distance
          type: f4

    c4quaternion:
      seq:
        - id: x
          type: f4
        - id: y
          type: f4
        - id: z
          type: f4
        - id: w
          type: f4
          doc: "Unlike Quaternions elsewhere, scalar part w is last instead of first"

    crange:
      seq:
        - id: min
          type: f4
        - id: max
          type: f4

    cirange:
      seq:
        - id: min
          type: s4 # FIXME: verify these are 4 bytes
        - id: max
          type: s4

    # Axis-aligned box
    caabox:
      seq:
        - id: min
          type: c3vector
        - id: max
          type: c3vector

    # Axis-aligned sphere
    caasphere:
      seq:
        - id: position
          type: c3vector
        - id: radius
          type: f4

    cargb:
      seq:
        - id: r
          type: u1
        - id: g
          type: u1
        - id: b
          type: u1
        - id: a
          type: u1

    # "color given in values of blue, green, red, and alpha
    cimvector:
      seq:
        - id: b
          type: u1
        - id: g
          type: u1
        - id: r
          type: u1
        - id: a
          type: u1

    # "three component vector of shorts"
    c3svector:
      seq:
        - id:  x
          type: s2
        - id:  y
          type: s2
        - id:  z
          type: s2

    c3segment:
      seq:
        - id: start
          type: c3vector
        - id: end
          type: c3vector

    cfacet:
      seq:
        - id: plane
          type: c4plane
        - id: vertices
          type: c3vector
          repeat: expr
          repeat-expr: 3

    c3ray:
      seq:
        - id: origin
          type: c3vector
        - id: dir
          type: c3vector

    crect:
      seq:
        - id: top
          type: f4
        - id: miny
          type: f4
        - id: left
          type: f4
        - id: minx
          type: f4
        - id: bottom
          type: f4
        - id: maxy
          type: f4
        - id: right
          type: f4
        - id: maxx
          type: f4


    cirect:
      seq:
        - id: top
          type: s4
        - id: miny
          type: s4
        - id: left
          type: s4
        - id: minx
          type: s4
        - id: bottom
          type: s4
        - id: maxy
          type: s4
        - id: right
          type: s4
        - id: maxx
          type: s4



    #
    # And now, our special 'template' types
    m2array:
      params:
        - id: m2array_type
          type: s4
          enum: m2array_types
      seq:
        - id: num
          type: u4
        - id: offset
          type: u4
      instances:
        items:
          pos: offset
          type:
            switch-on: m2array_type
            cases:
              m2array_types::todo: todo
              m2array_types::uint8: u1
              m2array_types::uint16: u2
              m2array_types::uint32: u4
              m2array_types::fixed16: fixed16
              m2array_types::float: f4
              m2array_types::ubyte4: ubyte4
              m2array_types::c3vector: c3vector
              m2array_types::m2sequencefallback: m2sequencefallback
              m2array_types::m2compbone: m2compbone
              m2array_types::m2vertex: m2vertex
              m2array_types::m2color: m2color
              m2array_types::m2texture: m2texture
              m2array_types::m2textureweight: m2textureweight
              m2array_types::m2texturetransform: m2texturetransform
              m2array_types::m2material: m2material
              m2array_types::m2attachment: m2attachment
              m2array_types::m2event: m2event
              m2array_types::m2light: m2light
              m2array_types::m2camera: m2camera
              m2array_types::m2ribbon: m2ribbon
              # m2array_types::m2particle: m2particle
              m2array_types::m2loop: m2loop
              m2array_types::m2sequence: m2sequence
              m2array_types::m2skinsection: m2skinsection
              m2array_types::m2batch: m2batch
              m2array_types::m2shadowbatch: m2shadowbatch
              m2array_types::m2array_uint32: m2array(m2array_types::uint32)
          repeat: expr
          repeat-expr: num

    # base m2track without extra data
    # FIXME: Is there any way we can roll this into the normal m2track case/switch?
    m2trackbase:
      seq:
        - id: interpolation_type
          type: u2
        - id: global_sequence
          type: u2
        - id: timestamps
          type: m2array(m2array_types::m2array_uint32)

    m2track:
      params:
        - id: m2track_type
          type: s4
          enum: m2track_types
      seq:
        - id: interpolation_type
          type: u2
        - id: global_sequence
          type: u2
        - id: timestamps
          type: m2array(m2array_types::m2array_uint32)
        - id: values
          type:
            switch-on: m2track_type
            cases:
              m2track_types::uint8: m2array(m2array_types::uint8)
              m2track_types::fixed16: m2array(m2array_types::fixed16)
              m2track_types::float: m2array(m2array_types::float)
              m2track_types::c3vector: m2array(m2array_types::c3vector)

    m2array_todo:
        seq:
            - id: num
              type: u4
            - id: offset
              type: u4

    m2array_str:
      seq:
        - id: num
          type: u4
        - id: offset
          type: u4
      instances:
        arraydata:
          io: _io
          type: str
          encoding: UTF-8
          size: num
          pos: offset

    #
    # And now, actual things that hold actual data
    m2sequence:
      seq:
        - id: id
          type: u2
        - id: variation_index
          type: u2
        - id: duration
          type: u4
        - id: movespeed
          type: f4
        - id: flags
          type: u4
        - id: frequency
          type: s2
        - id: padding
          type: u2
        - id: replay
          type: m2range
        - id: blend_time_in
          type: u2
        - id: blend_time_out
          type: u2
        - id: bounds
          type: m2bounds
        - id: variation_next
          -orig-id: variationNext
          type: s2
        - id: alias_next
          -orig-id: aliasNext
          type: u2

    # FIXME: enums
    m2texture:
      seq:
        - id: type
          type: u4
        - id: flags
          type: u4
        - id: filename
          type: m2array_str



    m2compbone:
      seq:
        - id: key_bone_id
          type: s4
        - id: flags     # FIXME
          type: u4
        - id: parent_bone
          type: s2
        - id: submesh_id
          type: u2
        - id: bone_name_crc
          -orig-id: boneNameCRC
          type: u4
        - id: translation
          type: m2track(m2track_types::c3vector)
        - id: rotation
          type: m2track(m2track_types::compquat)
        - id: scale
          type: m2track(m2track_types::c3vector)
        - id: pivot
          type: c3vector

    # m2trackbase:
    #   seq:
    #     - id: interpolation_type
    #       type: u2
    #     - id: global_sequence
    #       type: u2
    #     - id: timestamps
    #       type: m2array_array_uint32

    # m2track_compquat:
    #   seq:
    #     - id: base
    #       type: m2trackbase
    #     - id: values
    #       type: m2array_array_compquat



    # m2track_c3vector:
    #   seq:
    #     - id: base
    #       type: m2trackbase
    #     - id: values
    #       type: m2array_array_c3vector

    m2vertex:
      seq:
        - id: pos
          type: c3vector
        - id: bone_weights
          type: u1
          repeat: expr
          repeat-expr: 4
        - id: bone_indices
          type: u1
          repeat: expr
          repeat-expr: 4
        - id: normal
          type: c3vector
        - id: tex_coords
          type: c2vector
          repeat: expr
          repeat-expr: 2





    m2ribbon:
      seq:
        - id: ribbon_id
          type: u4
        - id: bone_index
          type: u4
        - id: position
          type: c3vector
        - id: texture_indices
          type: m2array(m2array_types::uint16)
        - id: material_indices
          type: m2array(m2array_types::uint16)
        - id: color_track
          type: m2track(m2track_types::c3vector)
        - id: alpha_track
          type: m2track(m2track_types::fixed16)
        - id: height_above_track
          type: m2track(m2track_types::float)
        - id: height_below_track
          type: m2track(m2track_types::float)
        - id: edges_per_second
          type: f4
        - id: edge_lifetime
          type: f4
        - id: gravity
          type: f4
        - id: texture_rows
          type: u2
        - id: texture_cols
          type: u2
        - id: tex_slot_track
          type: m2track(m2track_types::uint16)
        - id: visibility_track
          type: m2track(m2track_types::uint8)
        - id: priority_plane
          type: s2
        - id: padding
          type: u2



    m2light:
      seq:
        - id: type
          type: u2   # FIXME: actually an enum
        - id: bone
          type: s2
          doc: "-1 if not attached to a bone"
        - id: position
          type: c3vector
          doc: "relative to bone"
        - id: ambient_color
          type: m2track(m2track_types::c3vector)
        - id: ambient_intensity
          type: m2track(m2track_types::float)
          doc: "defaults to 1.0"
        - id: diffuse_color
          type: m2track(m2track_types::c3vector)
        - id: diffuse_intensity
          type: m2track(m2track_types::float)
          doc: "defaults to 1.0"
        - id: attenuation_start
          type: m2track(m2track_types::float)
        - id: attenuation_end
          type: m2track(m2track_types::float)
        - id: visibility
          type: m2track(m2track_types::uint8)


    m2sequencefallback:
      seq:
        - id: something
          type: u4
        - id: somethingelse
          type: u4

    m2event:
      seq:
        - id: identifier
          type: str
          size: 4
          encoding: ASCII
          doc: "usually a 3 character string prefixed with $"
        - id: data
          type: u4
          doc: "passed when event is fired"
        - id: bone
          type: u4
          doc: "where event is attached"
        - id: position
          type: c3vector
          doc: "relative to that bone"
        - id: enabled
          type: m2trackbase

    m2texturetransform:
      seq:
        - id: translation
          type: m2track(m2track_types::c3vector)
        - id: rotation
          type: m2track(m2track_types::c4quaternion)
        - id: scaling
          type: m2track(m2track_types::c3vector)

    # m2particle:
    #   seq:
    #     - id: old
    #       type: m2particleold
        # FIXME: two more fields here of type vector_2fp_6_9


    m2color:
      seq:
        - id: color
          type: m2track(m2track_types::c3vector)
        - id: alpha
          type: m2track(m2track_types::fixed16)

    m2attachment:
      seq:
        - id: id
          type: u4
        - id: bone
          type: u2
        - id: unknown
          type: u2
        - id: position
          type: c4vector
        - id: animate_attached
          type: m2track(m2track_types::u1)

    m2material:
      seq:
        - id: flags
          type: u2
        - id: blending_mode
          type: u2

    m2camera:
      seq:
        - id: type
          type: u4
          doc: "0 portait, 1 characterinfo, -1 otherwise"
        - id: far_clip
          type: f4
        - id: near_clip
          type: f4
        - id: positions
          type: m2track(m2track_types::todo)   # FIXME: M2Track<M2SplineKey<C3Vector>>
        - id: position_base
          type: c3vector
        - id: target_position
          type: m2track(m2track_types::todo)  # FIXME: M2Track<M2SplineKey<C3Vector>>
        - id: target_position_base
          type: c3vector
        - id: roll
          type: m2track(m2track_types::todo)  # FIXME: M2Track<M2SplineKey<float>>
          doc: "0 to 2*pi"
        - id: fov
          type: m2track(m2track_types::todo)  # FIXME: M2Track<M2SplineKey<float>>
          doc: "diagonal FoV in radians"

    m2textureweight:
      seq:
        - id: weight
          type: m2track(m2track_types::fixed16)

    m2loop:
      seq:
        - id: timestamp
          type: u4

    m2skinsection:
      seq:
        - id: skin_section_id
          type: u2
        - id: level
          type: u2
        - id: vertex_start
          type: u2
        - id: vertex_end
          type: u2
        - id: index_start
          type: u2
        - id: index_count
          type: u2
        - id: bone_count
          type: u2
        - id: bone_combo_index
          type: u2
        - id: bone_influences
          type: u2
        - id: center_bone_index
          type: u2
        - id: center_position
          type: c3vector
        - id: sort_center_position
          type: c3vector
        - id: sort_radius
          type: f4

    m2batch:
      seq:
        - id: flags
          type: u1
        - id: priority_plane
          type: s1
        - id: shader_id
          type: u2
        - id: skin_section_index
          type: u2
        - id: geoset_index
          type: u2
        - id: color_index
          type: u2
        - id: material_index
          type: u2
        - id: material_layer
          type: u2
        - id: texture_count
          type: u2
        - id: texture_combo_index
          type: u2
        - id: texture_coord_combo_index
          type: u2
        - id: texture_weight_combo_index
          type: u2
        - id: texture_transform_combo_index
          type: u2

    m2shadowbatch:
      seq:
        - id: flags
          type: u1
        - id: flags2
          type: u1
        - id: unknown1
          type: u2
        - id: submesh_id
          type: u2
        - id: texture_id
          type: u2
        - id: color_id
          type: u2
        - id: transparency_id
          type: u2

    todo:
      seq:
        - id: nothing
          type: u4


    #
    # And finally, chunk definitions

    chunk_md21:
      seq:
        - id: data
          type: chunk_md20

    # FIXME: Pretty sure the flags are fucked up in one way or another
    md20_global_flags:
      seq:
        - id: flag_tilt_x
          type: b1
        - id: flag_tilt_y
          type: b1
        - id: flag_unk_0x04
          type: b1
        - id: flag_use_texture_combiner_combos
          type: b1
        - id: flag_unk_0x10
          type: b1
        - id: flag_load_phys_data
          type: b1
        - id: flag_unk_0x40
          type: b1
        - id: flag_unk_0x80
          type: b1
        - id: flag_camera_related
          type: b1
        - id: flag_new_particle_record
          type: b1
        - id: flag_unk_0x400
          type: b1
        - id: flag_texture_transforms_use_bone_sequences
          type: b1
        - id: flag_unk_0x1000
          type: b1
        - id: flag_unk_0x2000
          type: b1
        - id: flag_unk_0x4000
          type: b1
        - id: flag_unk_0x8000
          type: b1
        - id: flag_unk_0x10000
          type: b1
        - id: flag_unk_0x20000
          type: b1
        - id: flag_unk_0x40000
          type: b1
        - id: flag_unk_0x80000
          type: b1
        - id: flag_unk_0x100000
          type: b1
        - id: flag_unk_0x200000
          type: b1

    chunk_md20:
      seq:
        - id: magic2
          contents: 'MD20'
        - id: version
          type: u4
          enum: wow_versions
        - id: name
          type: m2array_str
          doc: "should be globally unique"
        - id: global_flags
          type: md20_global_flags
          size: 4   # FIXME: Is this right?
        - id: global_loops
          type: m2array(m2array_types::m2loop)

        - id: sequences
          type: m2array(m2array_types::m2sequence)
        - id: sequence_idx_hash_by_id
          type: m2array(m2array_types::uint16)

        - id: bones
          type: m2array(m2array_types::m2compbone)
        - id: bone_indices_by_id
          type: m2array(m2array_types::uint16)

        - id: vertices
          type: m2array(m2array_types::m2vertex)

        # used in .skin file, supposedly
        - id: num_skin_profiles
          type: u4

        - id: colors
          type: m2array(m2array_types::m2color)
          doc: "Color and alpha animations definitions"
        - id: textures
          type: m2array(m2array_types::m2texture)
        - id: texture_weights
          type: m2array(m2array_types::m2textureweight)
          doc: "Transparency of textures"
        - id: texture_transforms
          type: m2array(m2array_types::m2texturetransform)

        # alternate name "replaceable_texture_lookup"
        - id: texture_indices_by_id
          type: m2array(m2array_types::uint16)

        # blending modes / render flags
        - id: materials
          type: m2array(m2array_types::todo)

        # alternate name "bone_lookup_table"
        - id: bone_combos
          type: m2array(m2array_types::uint16)

        # alternate name "texture_lookup_table"
        - id: texture_combos
          type: m2array(m2array_types::uint16)

        # alternate name "tex_unit_lookup_table"
        - id: texture_transform_bone_map
          type: m2array(m2array_types::uint16)

        # alternate name "transparency_lookup_table"
        - id: texture_weight_combos
          type: m2array(m2array_types::uint16)

        # alternate name "texture_transforms_lookup_table"
        - id: texture_transform_combos
          type: m2array(m2array_types::uint16)

        - id: bounding_box
          type: caabox
        - id: bounding_sphere_radius
          type: f4
        - id: collision_box
          type: caabox
        - id: collision_sphere_radius
          type: f4
        - id: collision_indices
          type: m2array(m2array_types::uint16)
        - id: collision_positions
          type: m2array(m2array_types::c3vector)
        - id: collision_face_normals
          type: m2array(m2array_types::c3vector)
        - id: attachments
          type: m2array(m2array_types::m2attachment)
        - id: attachment_indices_by_id
          type: m2array(m2array_types::uint16)
        - id: events
          type: m2array(m2array_types::m2event)
        - id: lights
          type: m2array(m2array_types::m2light)
        - id: cameras
          type: m2array(m2array_types::m2camera)
        - id: camera_indices_by_id
          type: m2array(m2array_types::uint16)
        - id: ribbon_emitters
          type: m2array(m2array_types::m2ribbon)
        - id: particle_emitters
          type: m2array(m2array_types::todo)
        - id: texture_combiner_combos
          type: m2array(m2array_types::uint16)
          if: global_flags.flag_use_texture_combiner_combos

    chunk_ldv1:
      seq:
        - id: unk0
          type: u2
        - id: lod_count
          type: u2
        - id: unk2_f
          type: f4
        - id: particle_bone_lod
          type: u1
          repeat: expr
          repeat-expr: 4

    chunk_txid:
      seq:
        - id: file_data_id
          type: u4
          repeat: eos

    chunk_skin:
      seq:
        - id: magic
          contents: 'SKIN'
        - id: vertices
          type: m2array(m2array_types::uint16)
        - id: indices
          type: m2array(m2array_types::uint16)
        - id: bones
          type: m2array(m2array_types::ubyte4)
        - id: submeshes
          type: m2array(m2array_types::m2skinsection)
        - id: batches
          type: m2array(m2array_types::m2batch)
        - id: bone_count_max
          type: u4
        - id: shadow_batches
          type: m2array(m2array_types::m2shadowbatch)

    noop: {}

    chunk:
      seq:
      - id: chunk_type
        type: str
        size: 4
        encoding: UTF-8
      - id: chunk_size
        type: u4
      - id: data
        size: chunk_size
        type:
          switch-on: chunk_type
          cases:
            '"MD21"': chunk_md21
            '"LDV1"': chunk_ldv1
            '"TXID"': chunk_txid
            _: noop
