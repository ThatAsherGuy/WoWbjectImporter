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
from .lookup_funcs import get_vertex_shader, get_shadereffects, wmo_read_color, WMO_Shaders_New
import os
import json

# This function does a lot; likely too much.
# A lot of the code here is rote node-connecting, though.
def build_shader(unit, mat, asset_mats, asset_textures, asset_tex_combos, base_shader, **kwargs):
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

    blend_seq = blend_type.split('_')
    if blend_seq[2] == 'Opaque':
        mat.blend_method = 'CLIP'

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

        if textures[i].get("name") in bpy.data.images:
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
    if os.path.isfile(tex.get("path")):
        image = bpy.data.images.load(tex.get("path"))
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
        mixer = nodes.new('ShaderNodeGroup')
        mixer.node_tree = get_utility_group('SpecDownmix')
        mixer.location += Vector((-200.0, 0.0))

        tree.links.new(combiner.outputs[0], mixer.inputs[0])
        tree.links.new(combiner.outputs[2], mixer.inputs[1])
        tree.links.new(mixer.outputs[0], shader.inputs[0])
        tree.links.new(shader.outputs[0], output.inputs[0])
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

    if settings_container:
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
        node.inputs[3].default_value = 0.2


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
        ('M2BLEND_BlendAdd', 'BLEND'),
    )
    mat.blend_method = blend_values[flags][1]
    return blend_values[flags][0]


# def fetch_fallback_texture(import_container):
#     print("fetching")
#     if import_container.has_fallback:
#         return import_container.fallback
#     else:



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
    print("Setting up WMO Materials")

    container = kwargs.get("container")
    config = kwargs.get("json")
    mats = config.get("materials")

    for i, mat in enumerate(mats):
        # i = min(i, (len(container.bl_obj.material_slots)-1) )

        tex1 = get_tex(container, str(mat.get("texture1")))
        tex2 = get_tex(container, str(mat.get("texture2")))
        tex3 = get_tex(container, str(mat.get("texture3")))

        tex_list = (tex1, tex2, tex3)

        if i >= len(container.bl_obj.material_slots):
            bl_mat = bpy.data.materials.new(name="jim bob")
            bl_mat.use_nodes = True
            container.bl_obj.data.materials.append(bl_mat)
        else:
            bl_mat = container.bl_obj.material_slots[i].material
        tree = bl_mat.node_tree
        nodes= tree.nodes

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
                tex_nodes.append(tex_node)

        if len(tex_nodes) > 1:
            mix_node = nodes.new("ShaderNodeMixRGB")
            mix_node.location += Vector((-600.0, 0.0))
            tree.links.new(tex_nodes[0].outputs[0], mix_node.inputs[1])
            tree.links.new(tex_nodes[1].outputs[0], mix_node.inputs[2])
            tree.links.new(mix_node.outputs[0], shader.inputs[0])

            connect_mode = WMO_Shaders_New[mat.get("shader", 0)][1]

            if connect_mode in {'MapObjDiffuse_T1_Env_T2', 'MapObjDiffuse_T1_Refl'}:
                env_map = nodes.new('ShaderNodeGroup')
                env_map.node_tree = get_utility_group(name="SphereMap_Alt")
                env_map.location += Vector((-1400.0, (300 - 2 * 325.0)))
                tree.links.new(env_map.outputs[0], tex_nodes[-1].inputs[0])
                tree.links.new(tex_nodes[0].outputs[1], mix_node.inputs[0])
            elif connect_mode in {'MapObjDiffuse_Comp'}:
                v_colors = nodes.new("ShaderNodeVertexColor")
                v_colors.layer_name = 'vcols'
                v_colors.location += Vector((-800.0, 0.0))

                tree.links.new(v_colors.outputs[1], mix_node.inputs[0])

                # These need to be flipped, for whatever reason
                tree.links.new(tex_nodes[0].outputs[0], mix_node.inputs[2])
                tree.links.new(tex_nodes[1].outputs[0], mix_node.inputs[1])
        else:
            tree.links.new(tex_nodes[0].outputs[0], shader.inputs[0])

            if mat.get("blendMode") == 2:
                tree.links.new(tex_nodes[0].outputs[1], shader.inputs[19])
                bl_mat.blend_method = 'BLEND'

    setup_wmo_batches(container, config)


def get_tex(container, tex_num):
    if tex_num == 0:
        return None

    name = tex_num + ".png"
    path = os.path.join(container.source_directory, name)
    if os.path.isfile(path):
        if name in bpy.data.images:
            return bpy.data.images[name]
        else:
            img = bpy.data.images.load(path)
            img.alpha_mode = 'CHANNEL_PACKED'
            return img
    else:
        return None

def setup_wmo_batches(container, config):
    # bpy.ops.object.editmode_toggle()
    obj = container.bl_obj
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    vcols = bm.loops.layers.color.new("vcols")

    groups = config.get("groups")
    mat_offset = 0
    color_offset = 0
    for group in groups:
        triangles = [i for i in group.get("materialInfo") if not i.get("materialID") == 255]
        colors = group.get("vertexColours")

        for i, tri in enumerate(triangles):
            i += mat_offset
            if i < (len(bm.faces)):
                bm.faces[i].material_index = tri.get("materialID")
            else:
                break

        mat_offset += len(triangles)

        if colors:
            for j, col in enumerate(colors):
                j += color_offset
                if j < (len(bm.verts)):
                    for loop in bm.verts[j].link_loops:
                        loop[vcols] = wmo_read_color(col, 'CImVector')
                else:
                    break

            color_offset += j

    bm.to_mesh(mesh)
    mesh.update()
    bm.free()
