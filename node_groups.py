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

import bmesh
import bpy
from mathutils import Vector
from . import preferences
from .lookup_funcs import get_vertex_shader, get_shadereffects, wmo_read_color, WMO_Shaders_New, read_wmo_face_flags, wmo_read_mat_flags
import os
import json

# This function does a lot; likely too much.
# A lot of the code here is rote node-connecting, though.
def build_shader(unit, mat, asset_mats, asset_textures, asset_tex_combos, base_shader, **kwargs):
    cwd = os.getcwd()
    texCount = unit.get("textureCount")
    texOffset = unit.get("textureComboIndex")

    texIndicies = asset_tex_combos[texOffset:texOffset+texCount]
    textures = [asset_textures[i] for i in texIndicies]

    uvAnimOffset = unit.get("textureTransformComboIndex")
    accurate_offsets = kwargs.get("anim_combos", [])
    if not accurate_offsets == []:
        texAnimIndicies = accurate_offsets[uvAnimOffset:uvAnimOffset+texCount]
    else:
        texAnimIndicies = []

    mat_flags = asset_mats[unit.get("materialIndex")]
    blend_type = get_shadereffects(unit.get("shaderID"),  unit.get("textureCount"))
    uv_type = get_vertex_shader(unit.get("shaderID"),  unit.get("textureCount"))

    tree = mat.node_tree
    nodes = tree.nodes

    principled = None
    outNode = None
    override = ""

    import_container = kwargs.get("import_container", None)
    obj = import_container.bl_obj

    # Arbitrarily breaking things out into different material passes
    # so they can be composited later. Only matters for Cycles.
    mat.pass_index = 1
    mat.use_backface_culling = True

    blend_seq = blend_type.split('_')
    if blend_seq[2] == 'Opaque':
        mat.blend_method = 'CLIP'

    blend_flag = mat_flags.get('blendingMode')
    downmix = set_blend(mat, blend_flag)

    render_flags = read_render_flags(mat_flags['flags'])
    for flag in render_flags:
        if flag == "UNLIT":
            override = "ShaderNodeEmission"
            mat.pass_index = 2
        elif flag == "NOFOG":
            mat.pass_index = 3
        elif flag == "BACKFACING":
            mat.use_backface_culling = False
        elif flag == "DTEST":
            mat.pass_index = 4
        elif flag == "DWRITE":
            mat.pass_index = 5
        elif flag == "ACLIP":
            mat.blend_method = 'CLIP'
            mat.pass_index = 6
        else:
            print("NOFLAG")

    # TODO: this should use node.bl_idname instead of node.type
    for node in nodes:
        if not principled and node.type == 'BSDF_PRINCIPLED':
            principled = node

        if not outNode and node.type == 'OUTPUT_MATERIAL':
            outNode = node

        if principled and outNode:
            break

    # If there is no Material Output node, create one.
    if not outNode:
        outNode = nodes.new('ShaderNodeOutputMaterial')

    # Nuke the defaul node, if it's there, so we can set up our own.
    if principled:
        nodes.remove(principled)

    # TODO: This should technically be derived from the vertex colors
    baseColor = nodes.new('ShaderNodeRGB')
    baseColor.location += Vector((-1200.0, 400.0))
    baseColor.outputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
    baseColor.label = 'BASE COLOR'

    mixer = nodes.new('ShaderNodeGroup')
    mixer.node_tree = get_utility_group(name=blend_type[3:])
    mixer.location += Vector((-500.0, 50.0))
    mixer.inputs[1].default_value = 1.0

    fmix, main_shader = get_output_nodes(mat, mixer, outNode, override, base_shader, downmix)

    tree.links.new(baseColor.outputs[0], mixer.inputs[0])

    mapping = uv_type.split("_")[2:]
    tex_nodes = []

    for i, tex in enumerate(textures):
        t_node = nodes.new('ShaderNodeTexImage')
        t_node.location += Vector((-1200.0, (200 - i * 300.0)))

        i = min(i, len(mapping) - 1)

        if mapping[i] == 'T1':
            uv_channel = 'UVMap'
        elif mapping[i] == 'T2':
            uv_channel = 'UV2Map'
        elif mapping[i] == 'Env':
            uv_channel = 'Env'
        elif mapping[i] == 'EdgeFade':
            uv_channel = 'UVMap'
        else:
            print("Bad Mapping: " + mapping[i])

        if uv_channel in {'UVMap', 'UV2Map'}:
            uv_map = nodes.new('ShaderNodeUVMap')
            uv_map.uv_map = uv_channel
        elif uv_channel == 'Env':
            uv_map = nodes.new('ShaderNodeGroup')
            uv_map.node_tree = get_utility_group(name="SphereMap_Alt")
            uv_map.label = "Sphere Map"
        else:
            uv_map = nodes.new('ShaderNodeUVMap')
            uv_map.uv_map = uv_channel
            uv_map.label = "REPLACE WITH EDGE FADE"

        uv_map.location += Vector((-1600.0, (300 - i * 325.0)))

        if not texAnimIndicies == []:
            if not texAnimIndicies[i] in {-1, 65535 }:
                sb = 1
                map_node = nodes.new('ShaderNodeGroup')
                map_node.node_tree = get_utility_group(name="TexturePanner")
                if import_container:
                    setup_panner(map_node, texAnimIndicies[i], settings_container=import_container)
            else:
                sb = 0
                map_node = nodes.new('ShaderNodeMapping')
                map_node.vector_type = 'TEXTURE'
        else:
            sb = 0
            map_node = nodes.new('ShaderNodeMapping')
            map_node.vector_type = 'TEXTURE'

        map_node.location += Vector((-1400.0, (300 - i * 325.0)))

        tree.links.new(uv_map.outputs[0], map_node.inputs[0+sb])
        tree.links.new(map_node.outputs[0], t_node.inputs[0])

        if textures[i].get("name", "ERR") in bpy.data.images:
            image = bpy.data.images[textures[i].get("name")]
            if not os.path.isfile(image.filepath):
                import_container.reports.warnings.append(textures[i].get("name") + " has an invalid path.")
                image = load_texture(textures[i], import_container, uv_map.label)
        else:
            image = load_texture(textures[i], import_container, uv_map.label)

        jim = obj.WBJ.textures.add()
        jim.path = image.filepath
        jim.datablock = image

        t_node.image = image
        t_node.label = 'TEX ' + str(i)

        socket_index = i * 2 + 2
        tree.links.new(t_node.outputs[0], mixer.inputs[socket_index])
        tree.links.new(t_node.outputs[1], mixer.inputs[socket_index+1])

        tex_nodes.append(t_node)


def load_texture(tex, import_container, mapping):
    path = os.path.realpath(tex.get("path", ""))
    if path and os.path.isfile(path):
        image = bpy.data.images.load(path)
        image.name = tex.get("name")
    else:
        image = import_container.get_fallback_tex()

    if mapping == "Sphere Map":
        image.colorspace_settings.name = 'Linear'

    image.alpha_mode = 'CHANNEL_PACKED'
    return image


def get_utility_group(name):
    '''
    Appends a node group from the bundled .blend file
    For whatever reason it appends the entire file, though.
    '''
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]

    addon_dir = os.path.dirname(__file__)
    blend_file = os.path.join(addon_dir, "BlendFunctions.blend")
    section = "NodeTree"

    filepath = os.path.join(blend_file, section, name)
    directory = os.path.join(blend_file, section)

    bpy.ops.wm.append(
        'EXEC_DEFAULT',
        filepath=filepath,
        directory=directory,
        filename=name,
        link=False,
        autoselect=False,
        set_fake=True,
        use_recursive=True
        )

    # So it turns out, if you import a node with a driver on it,
    # it imports all of its dependencies. Like the entire scene,
    # and all of its contents. Which is bad. So we do this:
    if name == 'TexturePanner':
        panner = bpy.data.node_groups[name]

        value_node = None
        for node in panner.nodes:
            if node.bl_idname  == 'ShaderNodeValue':
                value_node = node
                break

        if value_node:
            fcurve = value_node.outputs[0].driver_add('default_value')
            driver = fcurve.driver
            var = driver.variables.new()
            var.name = 'rate'
            var.targets[0].id_type = 'SCENE'
            var.targets[0].id = bpy.context.scene
            var.targets[0].data_path = 'render.fps'
            driver.expression = "frame/rate"

    return bpy.data.node_groups[name]


def get_output_nodes(mat, combiner, output, override, base, downmix, *args):
    '''Sets up the shader node & mix shader (if needed)'''

    prefs = preferences.get_prefs()
    base = prefs.get_base_shader(base)

    tree = mat.node_tree
    nodes = tree.nodes
    mixer = None


    if not base == "Experimental":
        shader = nodes.new(base)
    else:
        if not override == "":
            shader = nodes.new(override)
        else:
            shader = nodes.new('ShaderNodeGroup')
            shader.node_tree = get_utility_group(name="TheStumpFargothHidTheRingIn")

    # TODO: This doesn't work for materials with specular output below 0.5
    if len(combiner.outputs) > 2:
        combiner.location = Vector((-600.0, 100.0))
        shader.location += Vector((-200.0, 0.0))

        mixer = nodes.new('ShaderNodeGroup')
        mixer.node_tree = get_utility_group('SpecDownmix')
        mixer.location += Vector((-380.0, 0.0))

        transparent = nodes.new("ShaderNodeBsdfTransparent")
        transparent.location += Vector((-200.0, 140.0))

        tree.links.new(combiner.outputs[0], mixer.inputs[0])
        tree.links.new(combiner.outputs[2], mixer.inputs[1])

        if downmix in {'M2BLEND_NO_ALPHA_ADD', 'M2BLEND_ADD', 'M2BLEND_BLENDADD'}:
            mix_shader = nodes.new("ShaderNodeAddShader")
            tree.links.new(transparent.outputs[0], mix_shader.inputs[0])
            tree.links.new(shader.outputs[0], mix_shader.inputs[1])
            tree.links.new(mixer.outputs[0], shader.inputs[0])

        else:
            mix_shader = nodes.new("ShaderNodeMixShader")
            tree.links.new(shader.outputs[0], mix_shader.inputs[2])
            tree.links.new(combiner.outputs[1], mix_shader.inputs[0])
            tree.links.new(transparent.outputs[0], mix_shader.inputs[1])
            tree.links.new(mixer.outputs[0], shader.inputs[0])

        mix_shader.location += Vector((50.0, 100.0))

        tree.links.new(mix_shader.outputs[0], output.inputs[0])
    else:
        tree.links.new(combiner.outputs[0], shader.inputs[0])
        if base == 'ShaderNodeBsdfPrincipled':
            tree.links.new(combiner.outputs[1], shader.inputs[19])
            tree.links.new(shader.outputs[0], output.inputs[0])
            shader.inputs[5].default_value = 0.025
            shader.inputs[7].default_value = 0.95
        else:
            # TODO: Setup a mix node for transparency.
            shader.location += Vector((-200.0, 0.0))

            transparent = nodes.new("ShaderNodeBsdfTransparent")
            transparent.location += Vector((-200.0, 100.0))

            if downmix in {'M2BLEND_NO_ALPHA_ADD', 'M2BLEND_ADD'}:
                mix_shader = nodes.new("ShaderNodeAddShader")
                tree.links.new(transparent.outputs[0], mix_shader.inputs[0])
                tree.links.new(shader.outputs[0], mix_shader.inputs[1])
                tree.links.new(mix_shader.outputs[0], output.inputs[0])
                tree.links.new(combiner.outputs[1], shader.inputs[1])
            else:
                mix_shader = nodes.new("ShaderNodeMixShader")
                tree.links.new(combiner.outputs[1], mix_shader.inputs[0])
                tree.links.new(transparent.outputs[0], mix_shader.inputs[1])
                tree.links.new(shader.outputs[0], mix_shader.inputs[2])
                tree.links.new(mix_shader.outputs[0], output.inputs[0])

        if base == 'ShaderNodeEeveeSpecular':
            shader.inputs[2].default_value = 0.95
        elif base == 'ShaderNodeBsdfDiffuse':
            shader.inputs[1].default_value = 0.95

    if base in {'EMIT', 'SPEC', 'DIFF'}:
        pass

    return (mixer, shader)


def setup_panner(node, index, **kwargs):
    settings_container = None
    for arg, val in kwargs.items():
        if arg == 'settings_container':
            settings_container = val
            break

    if not (settings_container == None) and (len(settings_container.anim_transforms) > 0):
        anim_transforms = settings_container.anim_transforms
        panner_vectors = anim_transforms[min(index, len(anim_transforms))]
        # print(str(panner_vectors))
        for item, val in panner_vectors.items():
            if item == 'translate':
                node.inputs[2].default_value = val[0]
                node.inputs[3].default_value = val[1]

            # I haven't found any objects that have rotation.
            # The ones that look like they rotating typically have some UV trickery going on.
            elif item == 'rotate':
                node.inputs[4].default_value = 0.2
            elif item == 'scale':
                # Scaling hasn't been implemented yet.
                pass
    else:
        node.inputs[3].default_value = 0.0


def read_render_flags(flags):
    '''A really hacky way to read a bitfield'''
    ops = []

    if flags & 0x01:
        ops.append("UNLIT")

    if flags & 0x02:
        ops.append("NOFOG")

    if flags & 0x04:
        ops.append("BACKFACING")

    if flags & 0x08:
        ops.append("DTEST")

    if flags & 0x10:
        ops.append("DWRITE")

    if flags & 0x800:
        ops.append("ACLIP")

    return ops


def set_blend(mat, flags):
    blend_values = (
        ('M2BLEND_OPAQUE', 'CLIP'),
        ('M2BLEND_ALPHA_KEY', 'CLIP'),
        ('M2BLEND_ALPHA', 'BLEND'),
        ('M2BLEND_NO_ALPHA_ADD', 'BLEND'),
        ('M2BLEND_ADD', 'BLEND'),
        ('M2BLEND_MOD', 'BLEND'),
        ('M2BLEND_MOD2X', 'BLEND'),
        ('M2BLEND_BLENDADD', 'BLEND'),
    )
    mat.blend_method = blend_values[flags][1]
    return blend_values[flags][0]


def socket_type_helper(sock_type):
    if sock_type == "RGBA":
        return "NodeSocketColor"
    elif sock_type == "VALUE":
        return "NodeSocketFloat"
    elif sock_type == "VECTOR":
        return "NodeSocketVector"
    else:
        print("Unhandled Type: " + sock_type)
        return "FIX"


def serialize_nodegroups(path):
    '''Operates on the open file. Tries to serialize EVERY node group.'''
    if not os.path.isfile(path):
        print("No hoop to scoop")

    group_dict = {}

    for group in bpy.data.node_groups:
        g = group_dict[group.name] = {}
        g['nodes'] = {}
        g['links'] = {}
        g['inputs'] = {}
        g['outputs'] = {}

        for node in group.nodes:
            n = g['nodes'][node.name] = {}
            n['ID'] = node.bl_idname

            n['inputs'] = {}
            n['outputs'] = {}

            # Mathutils vectors aren't serializable, for some damn reason
            unpacked_location = (node.location[0], node.location[1])
            n['location'] = unpacked_location

            if node.name[:3] == "Mix":
                n['inputs']['blend_type'] = node.blend_type

            if node.name[:4] == "Math":
                n['inputs']['operation'] = node.operation

            if node.bl_idname == "ShaderNodeVectorTransform":
                n['inputs']['convert_from'] = node.convert_from
                n['inputs']['convert_to'] = node.convert_to
                n['inputs']['vector_type'] = node.vector_type

            for node_input in node.inputs:
                i = n['inputs'][node_input.name] = {}
                i['name'] = node_input.name
                i['type'] = socket_type_helper(node_input.type)

                if node.name in {"Group Input", "Group Output"}:
                    continue

                if node_input.type in {'VECTOR', 'RGBA'}:
                    i['value'] = (
                        node_input.default_value[0],
                        node_input.default_value[1],
                        node_input.default_value[2])
                else:
                    i['value'] = node_input.default_value

            for node_output in node.outputs:
                o = n['outputs'][node_output.name] = {}
                o['name'] = node_output.name
                o['type'] = socket_type_helper(node_output.type)

        for i, link in enumerate(group.links):
            l = g['links'][i] = {}

            l['from_node'] = link.from_node.name
            l['from_socket'] = link.from_socket.name

            l['to_node'] = link.to_node.name
            l['to_socket'] = link.to_socket.name

    with open("nodes.json", 'w') as outfile:
        dump = json.dump(group_dict, outfile, indent=4)


def generate_nodegroups(path):
    '''
    Creates node groups based on a JSON file. 80% accurate.
    Haven't quite figured out how to handle groups with drivers.
    '''
    with open("nodes.json", 'r') as data:
        node_dict = json.load(data)

        for name, group_def in node_dict.items():
            ng = bpy.data.node_groups.new(name, 'ShaderNodeTree')

            nodes = group_def.get('nodes')
            links = group_def.get('links')

            for name, node_def in nodes.items():

                if name == "Group Input":
                    outputs = node_def.get('outputs')
                    for item_name, socket in outputs.items():
                        sock_type = socket.get('type')
                        ng.inputs.new(sock_type, socket.get('name'))

                if name == "Group Output":
                    inputs = node_def.get('inputs')
                    for item_name, socket in inputs.items():
                        sock_type = socket.get('type')
                        ng.outputs.new(sock_type, socket.get('name'))

                node = ng.nodes.new(node_def.get('ID'))
                node.name = name
                node.location = Vector(node_def.get('location'))

                if node_def.get('ID') == 'ShaderNodeMath':
                    node.operation = node_def['inputs'].get('operation')

                if node_def.get('ID') == 'ShaderNodeVectorTransform':
                    node.convert_from = node_def['inputs'].get('convert_from')
                    node.convert_to = node_def['inputs'].get('convert_to')
                    node.vector_type = node_def['inputs'].get('vector_type')

                if node_def.get('ID') == 'ShaderNodeMixRGB':
                    node.blend_type = node_def['inputs'].get('blend_type')
                    node.inputs[0].default_value = 1.0

            for name, link_def in links.items():
                from_node = ng.nodes[link_def.get('from_node')]
                from_socket = from_node.outputs[link_def.get('from_socket')]

                to_node = ng.nodes[link_def.get('to_node')]
                to_socket = to_node.inputs[link_def.get('to_socket')]

                for output in from_node.outputs:
                    if output.name == link_def.get('from_socket'):
                        from_socket = output
                        break

                ng.links.new(from_node.outputs[link_def.get('from_socket')], to_node.inputs[link_def.get('to_socket')])


def do_wmo_mats(**kwargs):
    container = kwargs.get("container")
    config = kwargs.get("json")
    mats = config.get("materials")

    configured_mats = set()

    for obj in container.bl_obj:
        for slot in obj.material_slots:
            mat_number = slot.material.name.split('_')[-1]
            if '.' in mat_number:
                mat_number = mat_number.split('.')[0]
            mat = mats[int(mat_number)]

            tex1 = get_tex(container, str(mat.get("texture1")))
            tex2 = get_tex(container, str(mat.get("texture2")))
            tex3 = get_tex(container, str(mat.get("texture3")))

            tex_list = (tex1, tex2, tex3)

            bl_mat = slot.material
            tree = bl_mat.node_tree
            nodes = tree.nodes

            if bl_mat in configured_mats:
                continue

            shader = None
            out_node = None
            for node in nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    shader = node
                    shader.inputs[7].default_value = 1.0

                if node.type == 'OUTPUT_MATERIAL':
                    out_node = node

                if shader and out_node:
                    break

            if not out_node:
                out_node = nodes.new('ShaderNodeOutputMaterial')

            if not shader:
                print("DO LATER")

            baseColor = nodes.new('ShaderNodeRGB')
            baseColor.location += Vector((-1200.0, 400.0))
            baseColor.outputs[0].default_value = wmo_read_color(mat.get("color2"), 'CArgb')
            baseColor.label = 'BASE COLOR'

            tex_nodes = []

            for i, tex in enumerate(tex_list):
                if tex:
                    tex_node = nodes.new('ShaderNodeTexImage')
                    tex_node.image = tex
                    tex_node.location += Vector((-1200.0, (200 - i * 300.0)))
                    tex_node.label = ("TEXTURE_%s" % str(i + 1))
                    tex_nodes.append(tex_node)

            do_wmo_combiner(
                tex_nodes=tex_nodes,
                bl_mat=bl_mat,
                shader_out=shader,
                mat_info=mat)

            configured_mats.add(bl_mat)

        # setup_wmo_batches(container, config)


def get_tex(container, tex_num):
    if tex_num == 0:
        return None

    name = tex_num + ".png"
    path = os.path.join(container.source_directory, name)
    if os.path.isfile(path):
        if name in bpy.data.images:
            return bpy.data.images[name]
        else:
            img = bpy.data.images.load(os.path.realpath(path))
            img.alpha_mode = 'CHANNEL_PACKED'
            return img
    else:
        return None

def do_wmo_combiner(**kwargs):
    use_combiner_nodes = True

    tex_nodes = kwargs.get("tex_nodes")
    bl_mat = kwargs.get("bl_mat")
    shader_out = kwargs.get("shader_out")
    mat_info = kwargs.get("mat_info")

    shader_info = WMO_Shaders_New[mat_info.get("shader", 0)]
    blend_info = mat_info.get("blendMode")
    group_type = mat_info.get("groupType", -1)

    tree = bl_mat.node_tree
    nodes = tree.nodes

    shader_out.label = shader_info[0]
    shader_out.inputs[5].default_value = 0.0 # Breaking all measures of physical accuracy here.

    bl_mat.use_backface_culling = True

    flags = wmo_read_mat_flags(mat_info.get("flags", 0))

    for flag in flags:
        if flag == 'TWO_SIDED':
            bl_mat.use_backface_culling = False


    if blend_info == 2:
        bl_mat.blend_method = 'BLEND'
        tree.links.new(tex_nodes[0].outputs[1], shader_out.inputs[19])
    elif blend_info == 1:
        bl_mat.blend_method = 'CLIP'
        tree.links.new(tex_nodes[0].outputs[1], shader_out.inputs[19])

    mixer = nodes.new('ShaderNodeGroup')
    mixer.node_tree = get_utility_group(name=shader_info[2])
    mixer.location = Vector((-575.0, 30.0))

    offset = 0
    if use_combiner_nodes:
        for node_input in mixer.inputs:
            if node_input.name == "Vertex RGB":
                v_colors = nodes.new("ShaderNodeVertexColor")
                v_colors.layer_name = 'vcols_1'
                v_colors.location = Vector((-975.0, 30.0))

                # This part doesn't work yet; need to figure out vertex lighting.
                # tree.links.new(v_colors.outputs[0], mixer.inputs[0])
                # tree.links.new(v_colors.outputs[1], mixer.inputs[1])

            elif node_input.name == "Vertex2 RGB":
                v_colors = nodes.new("ShaderNodeVertexColor")
                v_colors.layer_name = 'vcols_1'
                v_colors.location = Vector((-975.0, 30.0))
                tree.links.new(v_colors.outputs[0], mixer.inputs[2])
                tree.links.new(v_colors.outputs[1], mixer.inputs[3])
                offset += 2

            elif node_input.name == "Tex0 RGB":
                tex_nodes[0].location = Vector((-975.0, -100.0))
                tree.links.new(tex_nodes[0].outputs[0], mixer.inputs[2 + offset])
                tree.links.new(tex_nodes[0].outputs[1], mixer.inputs[3 + offset])

            elif node_input.name == "Tex1 RGB":
                if len(tex_nodes) > 1:
                    tex_nodes[1].location = Vector((-975.0, -200.0))
                    tree.links.new(tex_nodes[1].outputs[0], mixer.inputs[4 + offset])
                    tree.links.new(tex_nodes[1].outputs[1], mixer.inputs[5 + offset])

                    if "Env" in shader_info[2]:
                        env_map = nodes.new('ShaderNodeGroup')
                        env_map.node_tree = get_utility_group(name="SphereMap_Alt")
                        env_map.location += Vector((-1400.0, (300 - 2 * 325.0)))
                        tree.links.new(env_map.outputs[0], tex_nodes[1].inputs[0])
                else:
                    mixer.inputs[5].default_value = 0.0

            elif node_input.name == "Tex2 RGB":
                if len(tex_nodes) > 2:
                    tex_nodes[2].location = Vector((-975.0, -400.0))
                    tree.links.new(tex_nodes[2].outputs[0], mixer.inputs[6 + offset])
                    tree.links.new(tex_nodes[2].outputs[1], mixer.inputs[7 + offset])

        if len(mixer.outputs) > 2:
            mix_1 = nodes.new("ShaderNodeMixRGB")
            mix_1.blend_type = 'ADD'
            mix_1.label = "Mix 1"
            mix_1.location = Vector((-275.0, 200.0))
            mix_1.inputs[0].default_value = 1.0

            tree.links.new(mixer.outputs[0], mix_1.inputs[1])
            tree.links.new(mixer.outputs[2], mix_1.inputs[2])
            tree.links.new(mix_1.outputs[0], shader_out.inputs[0])

        else:
            tree.links.new(mixer.outputs[0], shader_out.inputs[0])
        # tree.links.new(mixer.outputs[1], shader_out.inputs[19])
        return

    if shader_info[0] == "Diffuse":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "Specular":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])
        shader_out.inputs[5].default_vaule = 0.5
        shader_out.inputs[7].default_value = 0.5

    elif shader_info[0] == "Metal":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])
        shader_out.inputs[4].default_value = 1.0
        shader_out.inputs[5].default_vaule = 0.5
        shader_out.inputs[7].default_value = 0.5

    elif shader_info[0] == "Env":

        env_map = nodes.new('ShaderNodeGroup')
        env_map.node_tree = get_utility_group(name="SphereMap_Alt")
        env_map.location += Vector((-1400.0, (300 - 2 * 325.0)))

        tree.links.new(env_map.outputs[0], tex_nodes[-1].inputs[0])

        mix_node = nodes.new("ShaderNodeMixRGB")
        mix_node.location += Vector((-600.0, 0.0))
        mix_node.label = "Env"
        mix_node.blend_type = 'ADD'

        tree.links.new(tex_nodes[0].outputs[0], mix_node.inputs[1])
        tree.links.new(tex_nodes[-1].outputs[0], mix_node.inputs[2])

        tree.links.new(mix_node.outputs[0], shader_out.inputs[0])

        tex_nodes[-1].projection = 'SPHERE'
    elif shader_info[0] == "Opaque":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "EnvMetal":
        tex_nodes[0].location = Vector((-1250.0, 200.0))
        tex_nodes[1].location = Vector((-1000.0, -120.0))

        v_colors = nodes.new("ShaderNodeVertexColor")
        v_colors.layer_name = 'vcols_1'
        v_colors.location = Vector((-975.0, 30.0))

        mix_0 = nodes.new("ShaderNodeMath")
        mix_0.operation = 'MULTIPLY'
        mix_0.label = "Mix 0"
        mix_0.location = Vector((-800.0, 150.0))
        mix_0.inputs[0].default_value = 1.0

        tree.links.new(v_colors.outputs[1], mix_0.inputs[1])
        tree.links.new(tex_nodes[0].outputs[1], mix_0.inputs[0])

        mix_1 = nodes.new("ShaderNodeMixRGB")
        mix_1.blend_type = 'MULTIPLY'
        mix_1.label = "Mix 1"
        mix_1.location = Vector((-575.0, 480.0))
        mix_1.inputs[0].default_value = 1.0

        tree.links.new(tex_nodes[0].outputs[0], mix_1.inputs[1])
        tree.links.new(mix_0.outputs[0], mix_1.inputs[2])

        mix_2 = nodes.new("ShaderNodeMixRGB")
        mix_2.blend_type = 'MULTIPLY'
        mix_2.label = "Mix 2"
        mix_2.location = Vector((-400.0, 450.0))
        mix_2.inputs[0].default_value = 1.0

        tree.links.new(tex_nodes[1].outputs[0], mix_2.inputs[1])
        tree.links.new(mix_1.outputs[0], mix_2.inputs[2])

        mix_3 = nodes.new("ShaderNodeMixRGB")
        mix_3.blend_type = 'ADD'
        mix_3.label = "Mix 2"
        mix_3.location = Vector((-190.0, 300.0))
        mix_3.inputs[0].default_value = 1.0

        tree.links.new(tex_nodes[0].outputs[0], mix_3.inputs[1])
        tree.links.new(mix_2.outputs[0], mix_3.inputs[2])
        tree.links.new(mix_3.outputs[0], shader_out.inputs[0])

        env_map = nodes.new('ShaderNodeGroup')
        env_map.node_tree = get_utility_group(name="SphereMap_Alt")
        env_map.location += Vector((-1400.0, (300 - 2 * 325.0)))

        tree.links.new(env_map.outputs[0], tex_nodes[-1].inputs[0])
        tree.links.new(mix_0.outputs[0], shader_out.inputs[4])

        shader_out.inputs[4].default_value = 1.0
        # shader_out.inputs[7].default_value = 0.5

        tex_nodes[-1].projection = 'SPHERE'

    elif shader_info[0] == "TwoLayerDiffuse":
        tex_nodes[0].location = Vector((-475.0, 150.0))
        tex_nodes[1].location = Vector((-750.0, 200.0))
        tex_nodes[1].extension = 'CLIP'

        map_node = nodes.new("ShaderNodeUVMap")
        map_node.location += Vector((-950.0, 60.0))
        map_node.uv_map = "UV2Map"

        tree.links.new(map_node.outputs[0], tex_nodes[1].inputs[0])

        v_colors = nodes.new("ShaderNodeVertexColor")
        v_colors.layer_name = 'vcols_1'
        v_colors.location += Vector((-1000.0, 300))

        mix_0 = nodes.new("ShaderNodeMath")
        mix_0.operation = 'MULTIPLY'
        mix_0.label = 'Mix 0'
        mix_0.location += Vector((-450.0, 335.0))
        mix_0.inputs[0].default_value = 1.0

        tree.links.new(v_colors.outputs[1], mix_0.inputs[0])
        tree.links.new(tex_nodes[1].outputs[1], mix_0.inputs[1])

        mix_1 = nodes.new("ShaderNodeMixRGB")
        mix_1.location += Vector((-190.0, 300.0))
        mix_1.label = "Mix 1"
        mix_1.blend_type = 'MIX'

        if group_type == 2:
            tree.links.new(tex_nodes[0].outputs[0], mix_1.inputs[2])
            tree.links.new(tex_nodes[1].outputs[0], mix_1.inputs[1])
        else:
            tree.links.new(tex_nodes[0].outputs[0], mix_1.inputs[1])
            tree.links.new(tex_nodes[1].outputs[0], mix_1.inputs[2])

        tree.links.new(mix_1.outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "TwoLayerEnvMetal":

        tex_nodes[0].location = Vector((-1000.0, 120.0))
        tex_nodes[1].location = Vector((-620.0, 20.0))
        tex_nodes[2].location = Vector((-1000.0, -160.0))
        tex_nodes[-1].projection = 'SPHERE'

        mix_0 = nodes.new("ShaderNodeMixRGB")
        mix_0.location += Vector((-620.0, 200.0))
        mix_0.label = "Mix 0"
        mix_0.blend_type = 'MIX'
        mix_0.inputs[0].default_value = 1.0

        tree.links.new(tex_nodes[0].outputs[1], mix_0.inputs[0])
        tree.links.new(tex_nodes[0].outputs[0], mix_0.inputs[1])
        tree.links.new(tex_nodes[2].outputs[0], mix_0.inputs[2])

        mix_1 = nodes.new("ShaderNodeMixRGB")
        mix_1.location += Vector((-190.0, 300.0))
        mix_1.label = "Mix 1"
        mix_1.blend_type = 'MIX'

        v_colors = nodes.new("ShaderNodeVertexColor")
        v_colors.layer_name = 'vcols_1'
        v_colors.location = Vector((-380.0, 350.0))

        tree.links.new(v_colors.outputs[1], mix_1.inputs[0])
        tree.links.new(mix_0.outputs[0], mix_1.inputs[1])
        tree.links.new(tex_nodes[1].outputs[0], mix_1.inputs[2])
        tree.links.new(mix_1.outputs[0], shader_out.inputs[0])

        env_map = nodes.new('ShaderNodeGroup')
        env_map.node_tree = get_utility_group(name="SphereMap_Alt")
        env_map.location += Vector((-1200.0, -320.0))

        tree.links.new(env_map.outputs[0], tex_nodes[-1].inputs[0])

    elif shader_info[0] == "TwoLayerTerrain":

        v_colors = nodes.new("ShaderNodeVertexColor")
        v_colors.layer_name = 'vcols_1'
        v_colors.location += Vector((-800.0, 0.0))

        mix_node = nodes.new("ShaderNodeMixRGB")
        mix_node.location += Vector((-600.0, 0.0))
        mix_node.label = "TwoLayerTerrain"
        mix_node.blend_type = 'ADD'
        mix_node.inputs[0].default_value = 0.0

        map_node = nodes.new("ShaderNodeUVMap")
        map_node.location += Vector((-1800.0, 0.0))
        map_node.uv_map = "UV2Map"
        tree.links.new(map_node.outputs[0], tex_nodes[1].inputs[0])

        tree.links.new(tex_nodes[0].outputs[0], mix_node.inputs[2])
        tree.links.new(tex_nodes[1].outputs[0], mix_node.inputs[1])

        tree.links.new(mix_node.outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "DiffuseEmissive":
        tex_nodes[0].location = Vector((-290.0, 260.0))
        tex_nodes[1].location = Vector((-780.0, -137.0))

        v_colors = nodes.new("ShaderNodeVertexColor")
        v_colors.layer_name = 'vcols_1'
        v_colors.location = Vector((-520.0, -300.0))

        mix_0 = nodes.new("ShaderNodeMath")
        mix_0.operation = 'MULTIPLY'
        mix_0.label = "Mix 0"
        mix_0.location = Vector((-360.0, -180.0))
        mix_0.inputs[0].default_value = 1.0

        tree.links.new(tex_nodes[1].outputs[1], mix_0.inputs[0])
        tree.links.new(v_colors.outputs[1], mix_0.inputs[1])

        mix_1 = nodes.new("ShaderNodeMixRGB")
        mix_1.blend_type = 'MULTIPLY'
        mix_1.label = "Mix 1"
        mix_1.location = Vector((-190.0, -40.0))
        mix_1.inputs[0].default_value = 1.0

        tree.links.new(tex_nodes[1].outputs[0], mix_1.inputs[1])
        tree.links.new(mix_0.outputs[0], mix_1.inputs[2])

        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])
        tree.links.new(mix_1.outputs[0], shader_out.inputs[17])
        shader_out.inputs[18].default_value = 2.0

    elif shader_info[0] == "waterWindow":
        tex_nodes[0].location = Vector((-475.0, 220.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[17])
        tree.links.new(tex_nodes[0].outputs[1], shader_out.inputs[18])

    elif shader_info[0] == "MaskedEnvMetal":
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "EnvMetalEmissive":

        mix_node = nodes.new("ShaderNodeMixRGB")
        mix_node.location += Vector((-600.0, 0.0))
        mix_node.label = "EnvMetal"
        mix_node.blend_type = 'ADD'

        env_map = nodes.new('ShaderNodeGroup')
        env_map.node_tree = get_utility_group(name="SphereMap_Alt")
        env_map.location += Vector((-1400.0, (300 - 2 * 325.0)))

        tree.links.new(env_map.outputs[0], tex_nodes[-1].inputs[0])

        # Tex 1 Alpha and Color
        tree.links.new(tex_nodes[0].outputs[1], mix_node.inputs[0])
        tree.links.new(tex_nodes[0].outputs[0], mix_node.inputs[1])

        # Tex 2 Color
        tree.links.new(tex_nodes[1].outputs[0], mix_node.inputs[2])

        tree.links.new(mix_node.outputs[0], shader_out.inputs[0])

        tex_nodes[-1].projection = 'SPHERE'

    elif shader_info[0] == "TwoLayerDiffuseOpaque":
        tex_nodes[0].location = Vector((-860.0, 40.0))
        tex_nodes[1].location = Vector((-660.0, 500.0))

        v_colors = nodes.new("ShaderNodeVertexColor")
        v_colors.layer_name = 'vcols_1'
        v_colors.location += Vector((-760.0, 220.0))

        mix_0 = nodes.new("ShaderNodeMath")
        mix_0.operation = 'MULTIPLY'
        mix_0.label = ("Mix 0")
        mix_0.location += Vector((-560.0, 220.0))
        mix_0.inputs[0].default_value = 1.0

        tree.links.new(v_colors.outputs[1], mix_0.inputs[0])
        tree.links.new(tex_nodes[0].outputs[1], mix_0.inputs[1])

        mix_1 = nodes.new("ShaderNodeMixRGB")
        mix_1.location += Vector((-190.0, 300.0))
        mix_1.label = "Mix 1"
        mix_1.blend_type = 'MIX'

        tree.links.new(mix_0.outputs[0], mix_1.inputs[0])

        if group_type == 2:
            tree.links.new(tex_nodes[0].outputs[0], mix_1.inputs[2])
            tree.links.new(tex_nodes[1].outputs[0], mix_1.inputs[1])
        else:
            tree.links.new(tex_nodes[0].outputs[0], mix_1.inputs[1])
            tree.links.new(tex_nodes[1].outputs[0], mix_1.inputs[2])

        tree.links.new(mix_1.outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "submarineWindow":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "TwoLayerDiffuseEmissive":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "DiffuseTerrain":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "AdditiveMaskedEnvMetal":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "TwoLayerDiffuseMod2x":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "TwoLayerDiffuseMod2xNA":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "TwoLayerDiffuseAlpha":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "Lod":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])

    elif shader_info[0] == "Parallax":
        tex_nodes[0].location = Vector((-270.0, 300.0))
        tree.links.new(tex_nodes[0].outputs[0], shader_out.inputs[0])
