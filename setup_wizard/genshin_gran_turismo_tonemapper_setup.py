# Author: michael-gh1

import bpy
import os

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
from setup_wizard.import_order import cache_using_cache_key, get_cache, FESTIVITY_GRAN_TURISMO_FILE_PATH

from setup_wizard.setup_wizard_operator_base_classes import CustomOperatorProperties

NAME_OF_DEFAULT_SCENE = 'Scene'

NAME_OF_GRAN_TURISMO_NODE = 'Group'
NAME_OF_GRAN_TURISMO_NODE_TREE = 'GranTurismoWrapper [APPEND]'

NAME_OF_COMPOSITOR_INPUT_NODE = 'Render Layers'
NAME_OF_COMPOSITOR_OUTPUT_NODE = 'Composite'

NAME_OF_VIEWER_NODE = 'Viewer'
NAME_OF_VIEWER_NODE_TYPE = 'CompositorNodeViewer'

NAME_OF_IMAGE_IO = 'Image'
NAME_OF_RESULT_IO = 'Result'


class GI_OT_GenshinGranTurismoTonemapperSetup(Operator, ImportHelper, CustomOperatorProperties):
    """Select Festivity's Gran Turismo ToneMapper .blend File to import NodeTree"""
    bl_idname = 'genshin.gran_turismo_tonemapper_setup'
    bl_label = 'Genshin: Gran Turismo Tonemapper Setup - Select Gran Turismo .blend File'

    # ImportHelper mixin class uses this
    filename_ext = "*.*"

    import_path: StringProperty(
        name="Path",
        description="Festivity's Gran Turismo .blend File",
        default="",
        subtype='DIR_PATH'
    )

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    logs = 'Gran Turismo Tonemapper Setup:\n'

    def execute(self, context):
        cache_enabled = context.window_manager.cache_enabled
        gran_turismo_blend_file_path = self.filepath or get_cache(cache_enabled).get(FESTIVITY_GRAN_TURISMO_FILE_PATH)

        if not bpy.data.scenes.get(NAME_OF_DEFAULT_SCENE).node_tree:
            self.logs += 'ERROR: Must enable "Use Nodes" in Compositor view before being able to set up GT Tonemapper\n'
            self.report({'ERROR'}, f'{self.logs}')
            return {'FINISHED'}

        # Technically works if only running this Operator, but this cannot be chained because we need to be 
        # out of the script (or in another Operator) to update ctx before the import modal appears
        # Solution would be to create a separate Operator that handles context switches
        # TODO: This does not work unless INVOKE_DEFAULT with a modal or some window appears to update the Blender UI
        # self.switch_to_compositor()

        if not bpy.data.node_groups.get(NAME_OF_GRAN_TURISMO_NODE_TREE):
            if not gran_turismo_blend_file_path:
                bpy.ops.genshin.gran_turismo_tonemapper_setup(
                    'INVOKE_DEFAULT',
                    next_step_idx=self.next_step_idx, 
                    file_directory=self.file_directory,
                    invoker_type=self.invoker_type,
                    high_level_step_name=self.high_level_step_name
                )
                return {'FINISHED'}
            self.append_gran_turismo_tonemapper(gran_turismo_blend_file_path)
        else:
            self.logs += f'{NAME_OF_GRAN_TURISMO_NODE_TREE} already appended, skipping.\n'

        gran_turismo_node = bpy.data.scenes.get(NAME_OF_DEFAULT_SCENE).node_tree.nodes.get(NAME_OF_GRAN_TURISMO_NODE)
        if not gran_turismo_node or \
            (gran_turismo_node and gran_turismo_node.node_tree.name != NAME_OF_GRAN_TURISMO_NODE_TREE):
            self.create_compositor_node_group(NAME_OF_GRAN_TURISMO_NODE_TREE)
        else:
            self.logs += f'{NAME_OF_GRAN_TURISMO_NODE_TREE} node already created, skipping and not creating new node.\n'

        viewer_node = bpy.data.scenes.get(NAME_OF_DEFAULT_SCENE).node_tree.nodes.get(NAME_OF_VIEWER_NODE)
        if not viewer_node:
            self.create_compositor_node(NAME_OF_VIEWER_NODE_TYPE)
        else:
            self.logs += f'Viewer node already exists, skipping.\n'

        self.connect_starting_nodes()
        self.set_node_locations()

        if cache_enabled and gran_turismo_blend_file_path:
            cache_using_cache_key(
                get_cache(cache_enabled), 
                FESTIVITY_GRAN_TURISMO_FILE_PATH, 
                gran_turismo_blend_file_path
            )

        self.report({'INFO'}, f'{self.logs}')
        super().clear_custom_properties()
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

    def append_gran_turismo_tonemapper(self, gran_turismo_blend_file_path):
        inner_path = 'NodeTree'

        bpy.ops.wm.append(
            filepath=os.path.join(gran_turismo_blend_file_path, inner_path, NAME_OF_GRAN_TURISMO_NODE_TREE),
            directory=os.path.join(gran_turismo_blend_file_path, inner_path),
            filename=NAME_OF_GRAN_TURISMO_NODE_TREE
        )

        self.logs += f'Appended {NAME_OF_GRAN_TURISMO_NODE_TREE}\n'

    def create_compositor_node_group(self, node_name):
        bpy.ops.node.add_node(
            type="CompositorNodeGroup", 
            use_transform=True, 
            settings=[
                {"name":"node_tree", "value":f"bpy.data.node_groups['{node_name}']"}
            ]
        )
        self.logs += f'Created {node_name} node tree\n'

    def create_compositor_node(self, node_type):
        bpy.ops.node.add_node(
            type=node_type, 
            use_transform=True
        )
        self.logs += f'Created {node_type} node tree\n'

    def connect_starting_nodes(self):
        default_scene = bpy.data.scenes.get(NAME_OF_DEFAULT_SCENE)

        render_layers_node = default_scene.node_tree.nodes.get(NAME_OF_COMPOSITOR_INPUT_NODE)
        render_layers_output = render_layers_node.outputs.get(NAME_OF_IMAGE_IO)

        gran_turismo_wrapper_node = default_scene.node_tree.nodes.get(NAME_OF_GRAN_TURISMO_NODE)
        gran_turismo_wrapper_node_input = gran_turismo_wrapper_node.inputs.get(NAME_OF_IMAGE_IO)
        gran_turismo_wrapper_node_output = gran_turismo_wrapper_node.outputs.get(NAME_OF_RESULT_IO)

        composite_node = default_scene.node_tree.nodes.get(NAME_OF_COMPOSITOR_OUTPUT_NODE)
        composite_node_input = composite_node.inputs.get(NAME_OF_IMAGE_IO)

        viewer_node = default_scene.node_tree.nodes.get(NAME_OF_VIEWER_NODE)
        viewer_node_input = viewer_node.inputs.get(NAME_OF_IMAGE_IO)

        self.connect_nodes_in_scene(default_scene, render_layers_output, gran_turismo_wrapper_node_input)
        self.connect_nodes_in_scene(default_scene, gran_turismo_wrapper_node_output, composite_node_input)
        self.connect_nodes_in_scene(default_scene, gran_turismo_wrapper_node_output, viewer_node_input)

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
        gran_turismo_wrapper_node = default_scene.node_tree.nodes.get(NAME_OF_GRAN_TURISMO_NODE)
        composite_node = default_scene.node_tree.nodes.get(NAME_OF_COMPOSITOR_OUTPUT_NODE)
        viewer_node = default_scene.node_tree.nodes.get(NAME_OF_VIEWER_NODE)

        render_layers_node.location = (-200, 400)
        gran_turismo_wrapper_node.location = (250, 400)
        composite_node.location = (500, 400)
        viewer_node.location = (500, 200)
        self.logs += f'Set default locations for nodes in Compositing\n'
