import argparse
import math
import os
import sys
from typing import *

import bpy
from mathutils import Euler

def init_blender() -> None:
    bpy.context.preferences.view.show_splash = False
    # bpy.context.preferences.filepaths.use_save_preview_images = False
    # bpy.context.preferences.filepaths.file_preview_type = 'NONE'
    # bpy.context.space_data.shading.type = 'MATERIAL')
    bpy.ops.preferences.addon_enable(module="WoWbjectImporter")
    # bpy.ops.preferences.addon_enable(module="render_auto_tile_size")
    # bpy.context.scene.ats_settings.use_optimal = False


def load_wowobj(input: str):
    bpy.ops.import_scene.wowbject(filepath=input)


def delete_all() -> None:
    for item in bpy.data.objects:
        bpy.data.objects.remove(item)
    bpy.ops.outliner.orphans_purge(
        do_local_ids=True, do_linked_ids=True, do_recursive=True)


def add_camera(lens_length=50.0) -> bpy.types.Camera:
    camera_data = bpy.data.cameras.new(name='Camera')
    # A guess at some reasonable parameters
    camera_data.sensor_fit = 'HORIZONTAL'
    camera_data.sensor_width = 36.0
    camera_data.sensor_height = 24.0
    camera_data.lens = lens_length
    camera_data.dof.use_dof = False

    camera = bpy.data.objects.new('Camera', camera_data)
    bpy.context.scene.collection.objects.link(camera)
    bpy.context.scene.camera = camera

    return camera


def set_output_properties(scene: bpy.types.Scene,
                          resolution_x: int = 1080,
                          resolution_y: int = 1080,
                          resolution_percentage: int = 100,
                          output_file_path: str = "") -> None:
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.resolution_percentage = resolution_percentage

    if output_file_path:
        scene.render.filepath = os.path.realpath(output_file_path)


# FIXME: split this out from render engine properly
def set_render_properties(scene: bpy.types.Scene,
                          camera_object: bpy.types.Object,
                          num_samples: int,
                          use_denoising: bool = False,
                          use_motion_blur: bool = False,
                          use_transparent_bg: bool = False) -> None:
    scene.camera = camera_object

    scene.render.image_settings.file_format = 'PNG'
    scene.render.use_motion_blur = use_motion_blur

    scene.render.film_transparent = use_transparent_bg
    scene.view_layers[0].cycles.use_denoising = use_denoising

    scene.cycles.samples = num_samples


# The juggling required to get this to actually get this to enable
# correctly is... precise. Courtesy https://blender.stackexchange.com/a/187968
# FIXME: How can this support Optix?
def enable_gpus(device_type='CUDA'):
    preferences = bpy.context.preferences
    cycles_preferences = preferences.addons["cycles"].preferences
    optix_devices = cycles_preferences.get_devices_for_type('OPTIX')
    cuda_devices = cycles_preferences.get_devices_for_type('CUDA')

    if len(optix_devices) > 0:
        devices = optix_devices
    elif len(cuda_devices) > 0:
        devices = cuda_devices
    else:
        raise RuntimeError("Unsupported device type")

    activated_gpus = []

    for device in devices:
        if device.type == "CPU":
            device.use = False
        else:
            device.use = True
            activated_gpus.append(device.name)

    cycles_preferences.compute_device_type = device_type
    bpy.context.scene.cycles.device = "GPU"

    return activated_gpus


# FIXME: Figure out which compute_device_type gives the most repeatable results
# across alternate hardware
def set_cycles_renderer(scene: bpy.types.Scene):
    scene.render.engine = 'CYCLES'
    enable_gpus('CUDA')

    scene.cycles.feature_set = 'EXPERIMENTAL'
    scene.cycles.tile_order = 'CENTER'


def set_eevee_renderer(scene: bpy.types.Scene,
                       camera_object: bpy.types.Object,
                       num_samples: int,
                       use_denoising: bool = False,
                       use_motion_blur: bool = False,
                       use_transparent_bg: bool = False) -> None:
    scene.camera = camera_object

    scene.render.image_settings.file_format = 'PNG'
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.use_motion_blur = use_motion_blur

    scene.render.film_transparent = use_transparent_bg
    scene.view_layers[0].cycles.use_denoising = use_denoising

    # disable adaptive samples to help (maybe) with consistency
    scene.cycles.use_adaptive_sampling = False
    scene.cycles.samples = num_samples


def build_background(world: bpy.types.World,
                     bg_rgb: Tuple[float, float, float, float],
                     light_rgb: Tuple[float, float, float, float] = (
                         0.0, 0.0, 0.0, 1.0),
                     light_strength: float = 1.0) -> None:

    world.use_nodes = True
    node_tree = world.node_tree

    light_node = node_tree.nodes["Background"]
    light_node.inputs["Color"].default_value = light_rgb
    light_node.inputs["Strength"].default_value = light_strength

    bg_node = node_tree.nodes.new(type="ShaderNodeBackground")
    bg_node.inputs["Color"].default_value = bg_rgb
    bg_node.inputs["Strength"].default_value = 0.0

    lp_node = node_tree.nodes.new(type="ShaderNodeLightPath")
    mix_node = node_tree.nodes.new(type="ShaderNodeMixShader")

    node_tree.links.new(lp_node.outputs["Is Camera Ray"], mix_node.inputs[0])
    node_tree.links.new(light_node.outputs["Background"], mix_node.inputs[1])
    node_tree.links.new(bg_node.outputs["Background"], mix_node.inputs[2])

    node_tree.links.new(
        mix_node.outputs["Shader"], node_tree.nodes["World Output"].inputs["Surface"])

    # rgb_node = node_tree.nodes.new(type="ShaderNodeRGB")
    # rgb_node.outputs["Color"].default_value = rgba

    # node_tree.nodes["Background"].inputs["Strength"].default_value = strength

    # node_tree.links.new(
    #     rgb_node.outputs["Color"], node_tree.nodes["Background"].inputs["Color"])

    arrange_nodes(node_tree)


# FIXME: Do we really need this much code to arrange node trees nicely for
# something that'sn ot really even intended for a human to look at?
def arrange_nodes(node_tree: bpy.types.NodeTree, verbose: bool = False) -> None:
    max_num_iters = 2000
    epsilon = 1e-05
    target_space = 50.0

    second_stage = False

    fix_horizontal_location = True
    fix_vertical_location = True
    fix_overlaps = True

    if verbose:
        print("-----------------")
        print("Target nodes:")
        for node in node_tree.nodes:
            print("- " + node.name)

    # In the first stage, expand nodes overly
    target_space *= 2.0

    # Gauss-Seidel-style iterations
    previous_squared_deltas_sum = sys.float_info.max
    for i in range(max_num_iters):
        squared_deltas_sum = 0.0

        if fix_horizontal_location:
            for link in node_tree.links:
                k = 0.9 if not second_stage else 0.5
                threshold_factor = 2.0

                x_from = link.from_node.location[0]
                x_to = link.to_node.location[0]
                w_from = link.from_node.width
                signed_space = x_to - x_from - w_from
                C = signed_space - target_space
                grad_C_x_from = -1.0
                grad_C_x_to = 1.0

                # Skip if the distance is sufficiently large
                if C >= target_space * threshold_factor:
                    continue

                lagrange = C / (grad_C_x_from * grad_C_x_from +
                                grad_C_x_to * grad_C_x_to)
                delta_x_from = -lagrange * grad_C_x_from
                delta_x_to = -lagrange * grad_C_x_to

                link.from_node.location[0] += k * delta_x_from
                link.to_node.location[0] += k * delta_x_to

                squared_deltas_sum += k * k * \
                    (delta_x_from * delta_x_from + delta_x_to * delta_x_to)

        if fix_vertical_location:
            k = 0.5 if not second_stage else 0.05
            socket_offset = 20.0

            def get_from_socket_index(node: bpy.types.Node, node_socket: bpy.types
                                      .NodeSocket) -> int:
                for i in range(len(node.outputs)):
                    if node.outputs[i] == node_socket:
                        return i
                assert False

            def get_to_socket_index(node: bpy.types.Node, node_socket: bpy.types.NodeSocket) -> int:
                for i in range(len(node.inputs)):
                    if node.inputs[i] == node_socket:
                        return i
                assert False

            for link in node_tree.links:
                from_socket_index = get_from_socket_index(
                    link.from_node, link.from_socket)
                to_socket_index = get_to_socket_index(link.to_node, link.to_socket
                                                      )
                y_from = link.from_node.location[1] - \
                    socket_offset * from_socket_index
                y_to = link.to_node.location[1] - \
                    socket_offset * to_socket_index
                C = y_from - y_to
                grad_C_y_from = 1.0
                grad_C_y_to = -1.0
                lagrange = C / (grad_C_y_from * grad_C_y_from +
                                grad_C_y_to * grad_C_y_to)
                delta_y_from = -lagrange * grad_C_y_from
                delta_y_to = -lagrange * grad_C_y_to

                link.from_node.location[1] += k * delta_y_from
                link.to_node.location[1] += k * delta_y_to

                squared_deltas_sum += k * k * \
                    (delta_y_from * delta_y_from + delta_y_to * delta_y_to)

        if fix_overlaps and second_stage:
            k = 0.9
            margin = 0.5 * target_space

            # Examine all node pairs
            for node_1 in node_tree.nodes:
                for node_2 in node_tree.nodes:
                    if node_1 == node_2:
                        continue
                    x_1 = node_1.location[0]
                    x_2 = node_2.location[0]
                    w_1 = node_1.width
                    w_2 = node_2.width
                    cx_1 = x_1 + 0.5 * w_1
                    cx_2 = x_2 + 0.5 * w_2
                    rx_1 = 0.5 * w_1 + margin
                    rx_2 = 0.5 * w_2 + margin

                    # Note: "dimensions" and "height" may not be correct depending on the situation
                    def get_height(node: bpy.types.Node) -> float:
                        if node.dimensions.y > epsilon:
                            return node.dimensions.y
                        elif math.fabs(node.height - 100.0) > epsilon:
                            return node.height
                        else:
                            return 200.0

                    y_1 = node_1.location[1]
                    y_2 = node_2.location[1]
                    h_1 = get_height(node_1)
                    h_2 = get_height(node_2)
                    cy_1 = y_1 - 0.5 * h_1
                    cy_2 = y_2 - 0.5 * h_2
                    ry_1 = 0.5 * h_1 + margin
                    ry_2 = 0.5 * h_2 + margin

                    C_x = math.fabs(cx_1 - cx_2) - (rx_1 + rx_2)
                    C_y = math.fabs(cy_1 - cy_2) - (ry_1 + ry_2)

                    # If no collision, just skip
                    if C_x >= 0.0 or C_y >= 0.0:
                        continue

                    # Solve collision for the "easier" direction
                    if C_x > C_y:
                        grad_C_x_1 = 1.0 if cx_1 - cx_2 >= 0.0 else -1.0
                        grad_C_x_2 = -1.0 if cx_1 - cx_2 >= 0.0 else 1.0
                        lagrange = C_x / \
                            (grad_C_x_1 * grad_C_x_1 + grad_C_x_2 * grad_C_x_2)
                        delta_x_1 = -lagrange * grad_C_x_1
                        delta_x_2 = -lagrange * grad_C_x_2

                        node_1.location[0] += k * delta_x_1
                        node_2.location[0] += k * delta_x_2

                        squared_deltas_sum += k * k * \
                            (delta_x_1 * delta_x_1 + delta_x_2 * delta_x_2)
                    else:
                        grad_C_y_1 = 1.0 if cy_1 - cy_2 >= 0.0 else -1.0
                        grad_C_y_2 = -1.0 if cy_1 - cy_2 >= 0.0 else 1.0
                        lagrange = C_y / \
                            (grad_C_y_1 * grad_C_y_1 + grad_C_y_2 * grad_C_y_2)
                        delta_y_1 = -lagrange * grad_C_y_1
                        delta_y_2 = -lagrange * grad_C_y_2

                        node_1.location[1] += k * delta_y_1
                        node_2.location[1] += k * delta_y_2

                        squared_deltas_sum += k * k * \
                            (delta_y_1 * delta_y_1 + delta_y_2 * delta_y_2)

        if verbose:
            print("Iteration #" + str(i) + ": " + str(previous_squared_deltas_sum
                                                      - squared_deltas_sum))

        # Check the termination conditiion
        if math.fabs(previous_squared_deltas_sum - squared_deltas_sum) < epsilon:
            if second_stage:
                break
            else:
                target_space = 0.5 * target_space
                second_stage = True

        previous_squared_deltas_sum = squared_deltas_sum
