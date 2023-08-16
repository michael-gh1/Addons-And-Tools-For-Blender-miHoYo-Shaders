class ShaderConfigurator:
    v1_node_name_mapping = {}

    v2_node_name_mapping = {
        'miHoYo - Genshin Impact': 'Group.006',
    }

    def update_shader_value(self, materials, node_name, input_name, value):
        for material in materials:
            if not material:
                continue
            internal_node_name = self.v2_node_name_mapping.get(node_name) if \
                self.v2_node_name_mapping.get(node_name) else self.v1_node_name_mapping.get(node_name)

            shader_node = material.node_tree.nodes.get(internal_node_name)
            shader_node_inputs = shader_node.inputs if shader_node else None

            if shader_node_inputs:
                shader_node_input = shader_node_inputs.get(input_name)

                if shader_node_input:
                    shader_node_input.default_value = value
