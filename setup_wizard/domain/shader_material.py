import bpy
from bpy.types import Material, ShaderNodeGroup
from setup_wizard.domain.shader_node_names import ShaderNodeNames

class ShaderMaterial:
    def __init__(self, material: Material):
        self.material = material

    '''
    Gets the shader material's accompanying outlines material
    Only use if this is a shader material and not an outlines material
    '''
    def get_outlines_material(self):
        outline_materials = [material for material in bpy.data.materials.values() if
                            self.material.name in material.name and
                            ShaderMaterial(material).is_outlines_material()
        ]
        return outline_materials[0] if outline_materials else None

    def is_outlines_material(self):
        if self.material.node_tree and self.material.node_tree.nodes:
            outlines_nodes = [node for node in self.material.node_tree.nodes.values() if 
                            type(node) is ShaderNodeGroup and 
                            node.outputs.get(ShaderNodeNames.OUTLINES)
            ]
            if outlines_nodes:
                return True
        return False
