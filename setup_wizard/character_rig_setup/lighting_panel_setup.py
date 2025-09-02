import bpy
import os

from setup_wizard.domain.shader_material_names import ShaderMaterialNames, V4_PrimoToonGenshinImpactMaterialNames
from setup_wizard.geometry_nodes_setup.lighting_panel_names import LightingPanelNames


# Genshin Shader >= v3.4
class LightingPanel:
    def __init__(self, material_names: ShaderMaterialNames):
        if material_names is V4_PrimoToonGenshinImpactMaterialNames:
            self.lighting_panel_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), LightingPanelNames.FILENAME)
        else:  # for backwards compatibility
            self.lighting_panel_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'LightingPanel_Shader_v3_4.blend')

    def set_up_lighting_panel(self, light_vectors_modifier):
        lighting_panel_attributes_exist = LightingPanelNames.LIGHT_VECTORS_MODIFIER_INPUT_NAME_TO_OBJECT_NAME[0][0] in light_vectors_modifier
        if lighting_panel_attributes_exist:
            if not bpy.data.objects.get(LightingPanelNames.Objects.LIGHTING_PANEL):
                self.import_lighting_panel()
            self.connect_lighting_panel_nodes_to_global_material_properties()

            for modifier_input_name, object_name in LightingPanelNames.LIGHT_VECTORS_MODIFIER_INPUT_NAME_TO_OBJECT_NAME:
                try:
                    light_vectors_modifier[modifier_input_name] = light_vectors_modifier[modifier_input_name] or bpy.data.objects.get(object_name)
                except KeyError:
                    pass  # Skip if modifier input name does not exist, must do try-except because it may not have a value yet

    def import_lighting_panel(self):
        inner_path = 'Collection'
        bpy.ops.wm.append(
            filepath=os.path.join(self.lighting_panel_filepath, inner_path, LightingPanelNames.Collections.LIGHTING_PANEL),
            directory=os.path.join(self.lighting_panel_filepath, inner_path),
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
                output = global_properties_internal_nodes[node_name].outputs.get(input_output_names['output']) or \
                    global_properties_internal_nodes[node_name].outputs.get(input_output_names['old_output_name'])
                input = global_properties_internal_nodes[INTERNAL_GLOBAL_PROPERTIES_NODE_NAME].inputs.get(input_output_names['input'])
                global_properties_external_node.node_tree.links.new(output, input)


class GlobalPropertiesNames:
    class LightingPanelNodeNames:
        FRESNEL_COLOR_NODE = 'Fresnel Color'
        FRESNEL_SCALER_NODE = 'Value = Fresnel Scaler'
        AMBIENT_COLOUR_NODE = 'Ambient'
        SHARP_LIT_COLOUR_NODE = 'SharpLit'
        SOFT_LIFT_COLOUR_NODE = 'SoftLit'
        SHARP_SHADOW_COLOUR_NODE = 'SharpShadow'
        SOFT_SHADOW_COLOUR_NODE = 'SoftShadow'
        RIM_LIT_NODE = 'RimLitMult'
        RIM_SHADOW_NODE = 'RimShadowMult'
        RIM_SCALE_NODE = 'Rim Scale'

    class Inputs:
        FRESNEL_COLOR = 'Fresnel Color'
        FRESNEL_SCALER = 'Fresnel Scaler'
        AMBIENT_COLOUR = 'Ambient Colour'
        SHARP_LIT_COLOUR = 'Sharp Lit Colour'
        SOFT_LIT_COLOUR = 'Soft Lit Colour'
        SHARP_SHADOW_COLOUR = 'Sharp Shadow Colour'
        SOFT_SHADOW_COLOUR = 'Soft Shadow Colour'
        RIM_LIT = 'Rim Lit'
        RIM_SHADOW = 'Rim Shadow'
        RIM_SCALE = 'Rim Scale'

    NODES_TO_GLOBAL_PROPERTIES = {
        LightingPanelNodeNames.FRESNEL_COLOR_NODE: {
            'input': Inputs.FRESNEL_COLOR,
            'output': 'Color',
        },
        LightingPanelNodeNames.FRESNEL_SCALER_NODE: {
            'input': Inputs.FRESNEL_SCALER,
            'output': 'Blue',  # 'Value'
        },
        LightingPanelNodeNames.AMBIENT_COLOUR_NODE: {
            'input': Inputs.AMBIENT_COLOUR,
            'output': 'Output',
            'old_output_name': 'Color',
        },
        LightingPanelNodeNames.SHARP_LIT_COLOUR_NODE: {
            'input': Inputs.SHARP_LIT_COLOUR,
            'output': 'Output',
            'old_output_name': 'Color',
        },
        LightingPanelNodeNames.SOFT_LIFT_COLOUR_NODE: {
            'input': Inputs.SOFT_LIT_COLOUR,
            'output': 'Output',
            'old_output_name': 'Color',
        },
        LightingPanelNodeNames.SHARP_SHADOW_COLOUR_NODE: {
            'input': Inputs.SHARP_SHADOW_COLOUR,
            'output': 'Output',
            'old_output_name': 'Color',
        },
        LightingPanelNodeNames.SOFT_SHADOW_COLOUR_NODE: {
            'input': Inputs.SOFT_SHADOW_COLOUR,
            'output': 'Output',
            'old_output_name': 'Color',
        },
        LightingPanelNodeNames.RIM_LIT_NODE: {
            'input': Inputs.RIM_LIT,
            'output': 'Result',
        },
        LightingPanelNodeNames.RIM_SHADOW_NODE: {
            'input': Inputs.RIM_SHADOW,
            'output': 'Result',
        },
        LightingPanelNodeNames.RIM_SCALE_NODE: {
            'input': Inputs.RIM_SCALE,
            'output': 'Vector',
        },
    }
