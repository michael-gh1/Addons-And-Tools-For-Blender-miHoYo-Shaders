

class OriginalTextureLocatorUtils:
    def get_monster_original_texture_part(original_material):
        original_texture_name = OriginalTextureLocatorUtils.get_monster_original_texture(original_material)
        if original_texture_name:  # Some materials don't have a texture hooked up
            original_texture_name_split = original_texture_name.split('_')
            # ex. 'Fire' in 'Monster_Fatuus_Agent_01_Fire_Tex_Diffuse.png'
            if len(original_texture_name_split) > 2:  # Safety check, ensure we have at least 3 parts
                return original_texture_name_split[-3]
        return ''

    def get_monster_original_texture(original_material):
        try:
            return original_material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node.image.name_full
        except:
            print(f'WARNING: "{original_material.name}" does not exist in bpy.data.materials')
