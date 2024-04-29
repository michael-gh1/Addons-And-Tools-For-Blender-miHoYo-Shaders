# Author: michael-gh1

import bpy
import os

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
from setup_wizard.import_order import cache_using_cache_key, get_cache, HOYOVERSE_COMPOSITING_NODE_FILE_PATH

from setup_wizard.setup_wizard_operator_base_classes import CustomOperatorProperties
from setup_wizard.setup_wizard_operator_base_classes import NextStepInvoker
from setup_wizard.setup_wizard_operator_base_classes import BasicSetupUIOperator

NAME_OF_DEFAULT_SCENE = 'Scene'

NAME_OF_COMPOSITE_NODE = 'Group'
NAME_OF_GRAN_TURISMO_NODE_TREE = 'GranTurismoWrapper [APPEND]'
NAME_OF_HOYOVERSE_POST_PROCESSING_NODE_TREE = 'HoYoverse - Post Processing'

NAME_OF_COMPOSITOR_INPUT_NODE = 'Render Layers'
NAME_OF_COMPOSITOR_OUTPUT_NODE = 'Composite'

NAME_OF_VIEWER_NODE = 'Viewer'
NAME_OF_VIEWER_NODE_TYPE = 'CompositorNodeViewer'

NAME_OF_IMAGE_IO = 'Image'
NAME_OF_GT_COMPOSITE_NODE_OUTPUT = 'Result'
NAME_OF_HYV_PP_COMPOSITE_NODE_OUTPUT = 'Image'


class GI_OT_PostProcessingCompositingSetup(Operator, BasicSetupUIOperator):
    '''Sets Up Post Processing Compositing'''
    bl_idname = 'hoyoverse.post_processing_compositing_setup'
    bl_label = 'HoYoverse: Set Up Post Processing Compositing (UI)'


class PostProcessingFeatureFlag:
    # self is CustomOperatorProperties only for IDE syntax highlighting purposes
    def feature_disabled(self: CustomOperatorProperties, context):
        post_processing_setup_enabled = context.window_manager.post_processing_setup_enabled

        is_advanced_setup = self.high_level_step_name != 'GENSHIN_OT_setup_wizard_ui' and \
            self.high_level_step_name != 'GENSHIN_OT_setup_wizard_ui_no_outlines' and \
            self.high_level_step_name != 'HONKAI_STAR_RAIL_OT_setup_wizard_ui' and \
            self.high_level_step_name != 'HONKAI_STAR_RAIL_OT_setup_wizard_ui_no_outlines'
        
        return not post_processing_setup_enabled and not is_advanced_setup


class GI_OT_GenshinGranTurismoTonemapperSetup(Operator, ImportHelper, CustomOperatorProperties, PostProcessingFeatureFlag):
    """Select the Custom Compositing .blend File to import NodeTree"""
    bl_idname = 'hoyoverse.custom_composite_node_setup'
    bl_label = 'Hoyoverse: Custom Composite Node Setup - Select Custom Compositing .blend File'

    # ImportHelper mixin class uses this
    filename_ext = "*.*"

    import_path: StringProperty(
        name="Path",
        description="Custom Composite Node .blend File",
        default="",
        subtype='DIR_PATH'
    )

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    logs = 'Custom Composite Node Setup:\n'
    names_of_node_groups = [
        NAME_OF_GRAN_TURISMO_NODE_TREE,
        NAME_OF_HOYOVERSE_POST_PROCESSING_NODE_TREE,
    ]
    names_of_composite_node_outputs = [
        NAME_OF_GT_COMPOSITE_NODE_OUTPUT,
        NAME_OF_HYV_PP_COMPOSITE_NODE_OUTPUT,
    ]

    def execute(self, context):
        if self.feature_disabled(context):
            if self.next_step_idx:
                NextStepInvoker().invoke(
                    self.next_step_idx, 
                    self.invoker_type, 
                    high_level_step_name=self.high_level_step_name,
                    game_type=self.game_type,
                )
            self.clear_custom_properties()
            return {'FINISHED'}

        cache_enabled = context.window_manager.cache_enabled
        composite_blend_file_path = self.filepath or get_cache(cache_enabled).get(HOYOVERSE_COMPOSITING_NODE_FILE_PATH)

        context.scene.use_nodes = True

        # Technically works if only running this Operator, but this cannot be chained because we need to be 
        # out of the script (or in another Operator) to update ctx before the import modal appears
        # Solution would be to create a separate Operator that handles context switches
        # TODO: This does not work unless INVOKE_DEFAULT with a modal or some window appears to update the Blender UI
        # self.switch_to_compositor()

        composite_node_group = None
        for composite_node_group_name in self.names_of_node_groups:
            composite_node_group = bpy.data.node_groups.get(composite_node_group_name)
            if composite_node_group:
                break

        if not composite_node_group:
            if not composite_blend_file_path:
                bpy.ops.hoyoverse.custom_composite_node_setup(
                    'INVOKE_DEFAULT',
                    next_step_idx=self.next_step_idx, 
                    file_directory=self.file_directory,
                    invoker_type=self.invoker_type,
                    high_level_step_name=self.high_level_step_name
                )
                return {'FINISHED'}
            name_of_composite_node_group = self.append_composite_node_group(composite_blend_file_path)
            composite_node_group = bpy.data.node_groups.get(name_of_composite_node_group)
        else:
            self.logs += f'{composite_node_group.name} already appended, skipping.\n'

        composite_node = bpy.data.scenes.get(NAME_OF_DEFAULT_SCENE).node_tree.nodes.get(NAME_OF_COMPOSITE_NODE)
        if not composite_node or \
            (composite_node and (composite_node.node_tree.name not in self.names_of_node_groups)):
            self.create_compositor_node_group(composite_node_group.name)
        else:
            self.logs += f'{composite_node_group.name} node already created, skipping and not creating new node.\n'

        viewer_node = bpy.data.scenes.get(NAME_OF_DEFAULT_SCENE).node_tree.nodes.get(NAME_OF_VIEWER_NODE)
        if not viewer_node:
            self.create_compositor_node(NAME_OF_VIEWER_NODE_TYPE)
        else:
            self.logs += f'Viewer node already exists, skipping.\n'

        self.connect_starting_nodes()
        self.set_node_locations()

        if cache_enabled and composite_blend_file_path:
            cache_using_cache_key(
                get_cache(cache_enabled), 
                HOYOVERSE_COMPOSITING_NODE_FILE_PATH, 
                composite_blend_file_path
            )

        self.report({'INFO'}, f'{self.logs}')
        if self.next_step_idx:
            NextStepInvoker().invoke(
                self.next_step_idx, 
                self.invoker_type, 
                high_level_step_name=self.high_level_step_name,
                game_type=self.game_type,
            )
        self.clear_custom_properties()
        return {'FINISHED'}

    '''
    def switch_to_compositor(self):
        bpy.ops.genshin.change_bpy_context(
            'EXEC_DEFAULT',
            bpy_context_attr='area.type',
            bpy_context_value_str='NODE_EDITOR'
        )
        bpy.ops.genshin.change_bpy_context(
            'EXEC_DEFAULT',
            bpy_context_attr='scene.use_nodes',
            bpy_context_value_bool=True
        )
    '''

    def append_composite_node_group(self, composite_node_group_blend_file_path):
        inner_path = 'NodeTree'

        for node_group_name in self.names_of_node_groups:
            bpy.ops.wm.append(
                filepath=os.path.join(composite_node_group_blend_file_path, inner_path, node_group_name),
                directory=os.path.join(composite_node_group_blend_file_path, inner_path),
                filename=node_group_name
            )
            
            if bpy.data.node_groups.get(node_group_name):
                self.logs += f'Appended {node_group_name}\n'
                return node_group_name

    # Important to create using node_tree.nodes.new() instead of bpy.ops.node.add_node()
    def create_compositor_node_group(self, node_name):
        node_tree = bpy.context.scene.node_tree
        node = node_tree.nodes.new(
            type='CompositorNodeGroup'
        )
        node.node_tree = bpy.data.node_groups.get(node_name)
        self.logs += f'Created {node_name} node tree\n'

    # Important to create using node_tree.nodes.new() instead of bpy.ops.node.add_node()
    def create_compositor_node(self, node_type):
        node_tree = bpy.context.scene.node_tree
        node_tree.nodes.new(
            type=node_type
        )
        self.logs += f'Created {node_type} node tree\n'

    def connect_starting_nodes(self):
        default_scene = bpy.data.scenes.get(NAME_OF_DEFAULT_SCENE)

        render_layers_node = default_scene.node_tree.nodes.get(NAME_OF_COMPOSITOR_INPUT_NODE)
        render_layers_output = render_layers_node.outputs.get(NAME_OF_IMAGE_IO)

        composite_wrapper_node = default_scene.node_tree.nodes.get(NAME_OF_COMPOSITE_NODE)
        composite_wrapper_node_input = composite_wrapper_node.inputs.get(NAME_OF_IMAGE_IO)
        composite_wrapper_node_output = None

        for composite_node_output_name in self.names_of_composite_node_outputs:
            composite_wrapper_node_output = composite_wrapper_node.outputs.get(composite_node_output_name)
            if composite_wrapper_node_output:
                break

        composite_node = default_scene.node_tree.nodes.get(NAME_OF_COMPOSITOR_OUTPUT_NODE)
        composite_node_input = composite_node.inputs.get(NAME_OF_IMAGE_IO)

        viewer_node = default_scene.node_tree.nodes.get(NAME_OF_VIEWER_NODE)
        viewer_node_input = viewer_node.inputs.get(NAME_OF_IMAGE_IO)

        self.connect_nodes_in_scene(default_scene, render_layers_output, composite_wrapper_node_input)
        self.connect_nodes_in_scene(default_scene, composite_wrapper_node_output, composite_node_input)
        self.connect_nodes_in_scene(default_scene, composite_wrapper_node_output, viewer_node_input)

    def connect_nodes_in_scene(self, scene, input, output):
        # This is very important! The links are at the scene.node_tree level
        # It makes sense after you spend some time thinking about it because you're linking the nodes in the scene.
        # I spent way too much time troubleshooting at the scene.node_tree.nodes level
        # At that point you're trying to link things inside nodes, which is wrong!
        scene_node_tree_links = scene.node_tree.links
        scene_node_tree_links.new(
            input, 
            output
        )

        input_node_name = input.node.node_tree.name_full if hasattr(input.node, 'node_tree') else input.node.name
        output_node_name = output.node.node_tree.name_full if hasattr(output.node, 'node_tree') else output.node.name

        self.logs += f"Connected '{input_node_name}' ({input.name}) to '{output_node_name}' ({output.name}) in scene: {scene.name}\n"

    def set_node_locations(self):
        default_scene = bpy.data.scenes.get(NAME_OF_DEFAULT_SCENE)
        render_layers_node = default_scene.node_tree.nodes.get(NAME_OF_COMPOSITOR_INPUT_NODE)
        composite_wrapper_node = default_scene.node_tree.nodes.get(NAME_OF_COMPOSITE_NODE)
        composite_node = default_scene.node_tree.nodes.get(NAME_OF_COMPOSITOR_OUTPUT_NODE)
        viewer_node = default_scene.node_tree.nodes.get(NAME_OF_VIEWER_NODE)

        render_layers_node.location = (-200, 400)
        composite_wrapper_node.location = (250, 400)
        composite_node.location = (500, 400)
        viewer_node.location = (500, 200)
        self.logs += f'Set default locations for nodes in Compositing\n'


class HYV_OT_HoyoversePostProcessingDefaultSettings(Operator, ImportHelper, CustomOperatorProperties, PostProcessingFeatureFlag):
    """Sets default settings when using Hoyoverse - Post Processing"""
    bl_idname = 'hoyoverse.post_processing_default_settings'
    bl_label = 'Hoyoverse: Post Processing - Default Settings'

    # ImportHelper mixin class uses this
    filename_ext = "*.*"

    def execute(self, context):
        if self.feature_disabled(context):
            if self.next_step_idx:
                NextStepInvoker().invoke(
                    self.next_step_idx, 
                    self.invoker_type, 
                    high_level_step_name=self.high_level_step_name,
                    game_type=self.game_type,
                )
            self.clear_custom_properties()
            return {'FINISHED'}

        bpy.context.scene.node_tree.use_opencl = False
        bpy.context.scene.node_tree.use_two_pass = True
        bpy.context.scene.eevee.use_bloom = False
        bpy.context.scene.render.film_transparent = False

        if self.next_step_idx:
            NextStepInvoker().invoke(
                self.next_step_idx, 
                self.invoker_type, 
                high_level_step_name=self.high_level_step_name,
                game_type=self.game_type,
            )
        self.clear_custom_properties()

        return {'FINISHED'}
