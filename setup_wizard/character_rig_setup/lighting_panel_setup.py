import bpy
import os

from setup_wizard.geometry_nodes_setup.lighting_panel_names import LightingPanelNames


# Genshin Shader >= v3.4
class LightingPanel:
    def __init__(self):
        pass

    def set_up_lighting_panel(self, light_vectors_modifier):
        if LightingPanelNames.LIGHT_VECTORS_MODIFIER_INPUT_NAME_TO_OBJECT_NAME[0][0] in light_vectors_modifier:
            if not bpy.data.objects.get(LightingPanelNames.Objects.LIGHTING_PANEL):
                self.import_lighting_panel()
            self.connect_lighting_panel_nodes_to_global_material_properties()

            for modifier_input_name, object_name in LightingPanelNames.LIGHT_VECTORS_MODIFIER_INPUT_NAME_TO_OBJECT_NAME:
                light_vectors_modifier[modifier_input_name] = light_vectors_modifier[modifier_input_name] or bpy.data.objects.get(object_name)

    def import_lighting_panel(self):
        lighting_panel_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), LightingPanelNames.FILENAME)
        inner_path = 'Collection'
        bpy.ops.wm.append(
            filepath=os.path.join(lighting_panel_filepath, inner_path, LightingPanelNames.Collections.LIGHTING_PANEL),
            directory=os.path.join(lighting_panel_filepath, inner_path),
            files=[
                {'name': LightingPanelNames.Collections.LIGHTING_PANEL},
            ],
        )

    def connect_lighting_panel_nodes_to_global_material_properties(self):
        EXTERNAL_GLOBAL_PROPERTIES_NODE_NAME = 'Global Properties'  # At shader level
        INTERNAL_GLOBAL_PROPERTIES_NODE_NAME = 'Global Properties'  # Inside node group
        materials_with_global_properties = [material for material in bpy.data.materials.values() if 
                                            material.node_tree and material.node_tree.nodes and 
                                            material.node_tree.nodes.get(EXTERNAL_GLOBAL_PROPERTIES_NODE_NAME)]
        if materials_with_global_properties:
            global_properties_external_node = materials_with_global_properties[0].node_tree.nodes.get(EXTERNAL_GLOBAL_PROPERTIES_NODE_NAME)
            global_properties_internal_nodes = global_properties_external_node.node_tree.nodes

            for node_name, input_output_names in GlobalPropertiesNames.NODES_TO_GLOBAL_PROPERTIES.items():
                output = global_properties_internal_nodes[node_name].outputs.get(input_output_names['output'])
                input = global_properties_internal_nodes[INTERNAL_GLOBAL_PROPERTIES_NODE_NAME].inputs.get(input_output_names['input'])
                global_properties_external_node.node_tree.links.new(output, input)


class GlobalPropertiesNames:
    class LightingPanelNodeNames:
        COMBINE_COLOR = 'Combine Color'
        SEPARATE_COLOR = 'Separate Color'
        ATTR_AMBIENT_COLOUR = 'Attribute.001'
        ATTR_SHARP_LIT_COLOUR = 'Attribute.002'
        ATTR_SOFT_LIFT_COLOUR = 'Attribute.003'
        ATTR_SHARP_SHADOW_COLOUR = 'Attribute.004'
        ATTR_SOFT_SHADOW_COLOUR = 'Attribute.005'
        MULTIPLY_RIMLIT = 'Mix'
        MULTIPLY_RIM_SHADOW = 'Mix.001'


    FRESNEL_COLOR = 'Fresnel Color'
    FRESNEL_SCALER = 'Fresnel Scaler'
    AMBIENT_COLOUR = 'Ambient Colour'
    SHARP_LIT_COLOUR = 'Sharp Lit Colour'
    SOFT_LIT_COLOUR = 'Soft Lit Colour'
    SHARP_SHADOW_COLOUR = 'Sharp Shadow Colour'
    SOFT_SHADOW_COLOUR = 'Soft Shadow Colour'
    RIM_LIT = 'Rim Lit'
    RIM_SHADOW = 'Rim Shadow'

    NODES_TO_GLOBAL_PROPERTIES = {
        LightingPanelNodeNames.COMBINE_COLOR: {
            'input': FRESNEL_COLOR,
            'output': 'Color',
        },
        LightingPanelNodeNames.SEPARATE_COLOR: {
            'input': FRESNEL_SCALER,
            'output': 'Blue',  # 'Value'
        },
        LightingPanelNodeNames.ATTR_AMBIENT_COLOUR: {
            'input': AMBIENT_COLOUR,
            'output': 'Color',
        },
        LightingPanelNodeNames.ATTR_SHARP_LIT_COLOUR: {
            'input': SHARP_LIT_COLOUR,
            'output': 'Color',
        },
        LightingPanelNodeNames.ATTR_SOFT_LIFT_COLOUR: {
            'input': SOFT_LIT_COLOUR,
            'output': 'Color',
        },
        LightingPanelNodeNames.ATTR_SHARP_SHADOW_COLOUR: {
            'input': SHARP_SHADOW_COLOUR,
            'output': 'Color',
        },
        LightingPanelNodeNames.ATTR_SOFT_SHADOW_COLOUR: {
            'input': SOFT_SHADOW_COLOUR,
            'output': 'Color',
        },
        LightingPanelNodeNames.MULTIPLY_RIMLIT: {
            'input': RIM_LIT,
            'output': 'Result',
        },
        LightingPanelNodeNames.MULTIPLY_RIM_SHADOW: {
            'input': RIM_SHADOW,
            'output': 'Result',
        },
    }
