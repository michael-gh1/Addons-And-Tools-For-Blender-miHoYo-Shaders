import bpy
from bpy.types import Material, ShaderNodeGroup
from setup_wizard.domain.shader_node_names import ShaderNodeNames

class ShaderMaterial:
    def __init__(self, material: Material, shader_node_names: ShaderNodeNames):
        self.material = material
        self.shader_node_names = shader_node_names or ShaderNodeNames

    '''
    Gets the shader material's accompanying outlines material
    Only use if this is a shader material and not an outlines material
    '''
    def get_outlines_material(self):
        outline_materials = [material for material in bpy.data.materials.values() if
                            self.material.name in material.name and
                            ShaderMaterial(material, self.shader_node_names).is_outlines_material()
        ]
        return outline_materials[0] if outline_materials else None

    def is_outlines_material(self):
        if self.material.node_tree and self.material.node_tree.nodes:
            outlines_nodes = [node for node in self.material.node_tree.nodes.values() if 
                            type(node) is ShaderNodeGroup and 
                            len(node.outputs) == 2 and
                            node.outputs.get(self.shader_node_names.OUTLINES_OUTPUT) and
                            node.outputs.get(self.shader_node_names.OUTLINES_OUTPUT).is_linked
            ]
            if outlines_nodes:
                return True
        return False

    '''
    Gets the shader material's accompanying Night Soul outlines material
    Only use if this is a shader material and not a Night Soul outlines or an outlines material
    '''
    def get_night_soul_outlines_material(self):
        outline_materials = [material for material in bpy.data.materials.values() if
                            self.material.name in material.name and
                            ShaderMaterial(material, self.shader_node_names).is_night_soul_outlines_material()
        ]
        return outline_materials[0] if outline_materials else None

    def is_night_soul_outlines_material(self):
        if self.material.node_tree and self.material.node_tree.nodes:
            outlines_nodes = [node for node in self.material.node_tree.nodes.values() if 
                            type(node) is ShaderNodeGroup and 
                            len(node.outputs) == 2 and
                            node.outputs.get(self.shader_node_names.NIGHT_SOUL_OUTPUT) and
                            node.outputs.get(self.shader_node_names.NIGHT_SOUL_OUTPUT).is_linked
            ]
            if outlines_nodes:
                return True
        return False

