from enum import Enum, auto
import bpy

import os

from setup_wizard.import_order import get_actual_material_name_for_dress


class TextureImporterType(Enum):
    AVATAR = auto()
    NPC = auto()


class TextureType(Enum):
    HAIR = 'Hair'
    BODY = 'Body'


class TextureImporterFactory:
    def create(texture_importer_type):
        if texture_importer_type == TextureImporterType.AVATAR:
            return GenshinAvatarTextureImporter()
        elif texture_importer_type == TextureImporterType.NPC:
            return GenshinNPCTextureImporter()
        else:
            print(f'Unknown TextureImporterType: {texture_importer_type}')


class GenshinTextureImporter:
    def import_textures(self, directory):
        raise NotImplementedError()

    def is_texture_identifiers_in_texture_name(self, texture_identifiers, texture_name):
        for texture_identifier in texture_identifiers:
            if texture_identifier not in texture_name:
                return False
        return True

    def set_diffuse_texture(self, type: TextureType, material, img):
        material.node_tree.nodes[f'{type.value}_Diffuse_UV0'].image = img
        material.node_tree.nodes[f'{type.value}_Diffuse_UV1'].image = img
        self.setup_dress_textures(f'{type.value}_Diffuse', img)

    def set_lightmap_texture(self, type: TextureType, material, img):
        img.colorspace_settings.name='Non-Color'
        material.node_tree.nodes[f'{type.value}_Lightmap_UV0'].image = img
        material.node_tree.nodes[f'{type.value}_Lightmap_UV1'].image = img
        self.setup_dress_textures(f'{type.value}_Lightmap', img)

    def set_normalmap_texture(self, type:TextureType, material, img):
        img.colorspace_settings.name='Non-Color'
        material.node_tree.nodes[f'{type.value}_Normalmap_UV0'].image = img
        material.node_tree.nodes[f'{type.value}_Normalmap_UV1'].image = img
        self.setup_dress_textures(f'{type.value}_Normalmap', img)

        # Deprecated. Tries only if it exists. Only for V1 Shader
        self.plug_normal_map(f'miHoYo - Genshin {type.value}', 'MUTE IF ONLY 1 UV MAP EXISTS')
        self.plug_normal_map('miHoYo - Genshin Dress', 'MUTE IF ONLY 1 UV MAP EXISTS')
        self.plug_normal_map('miHoYo - Genshin Dress1', 'MUTE IF ONLY 1 UV MAP EXISTS')
        self.plug_normal_map('miHoYo - Genshin Dress2', 'MUTE IF ONLY 1 UV MAP EXISTS')

    def set_hair_shadow_ramp_texture(self, img):
        bpy.data.node_groups['Hair Shadow Ramp'].nodes['Hair_Shadow_Ramp'].image = img

    def set_body_shadow_ramp_texture(self, img):
        bpy.data.node_groups['Body Shadow Ramp'].nodes['Body_Shadow_Ramp'].image = img

    def set_body_specular_ramp_texture(self, img):
        img.colorspace_settings.name='Non-Color'
        bpy.data.node_groups['Body Specular Ramp'].nodes['Body_Specular_Ramp'].image = img        

    def set_face_diffuse_texture(self, face_material, img):
        face_material.node_tree.nodes['Face_Diffuse'].image = img        

    def set_face_shadow_texture(self, face_material, img):
        img.colorspace_settings.name='Non-Color'
        face_material.node_tree.nodes['Face_Shadow'].image = img        

    def set_face_lightmap_texture(self, img):
        img.colorspace_settings.name='Non-Color'
        bpy.data.node_groups['Face Lightmap'].nodes['Face_Lightmap'].image = img

    def set_metalmap_texture(self, img):
        bpy.data.node_groups['Metallic Matcap'].nodes['MetalMap'].image = img

    def setup_dress_textures(self, texture_name, texture_img):
        shader_dress_materials = [material for material in bpy.data.materials if 'Genshin Dress' in material.name]
        shader_cloak_materials = [material for material in bpy.data.materials
                                  if 'Genshin Arm' in material.name or 'Genshin Cloak' in material.name]

        # TODO: Refactor this for sure!
        # Specific case for Xiao (the only character with an Arm material)
        # Specific case for Dainsleif (the only character with a Cloak material)
        # Technically Paimon has one, but we ignore it
        if shader_cloak_materials:
            original_cloak_material = [material for material in bpy.data.materials if material.name.endswith(
                shader_cloak_materials[0].name.split(' ')[-1]
            )][0]  # the material that ends with 'Dress', 'Dress1', 'Dress2'
            actual_cloak_material = get_actual_material_name_for_dress(original_cloak_material.name)
            if actual_cloak_material in texture_name:
                material_shader_nodes = bpy.data.materials.get(shader_cloak_materials[0].name).node_tree.nodes
                material_shader_nodes.get(f'{texture_name}_UV0').image = texture_img
                material_shader_nodes.get(f'{texture_name}_UV1').image = texture_img

        for shader_dress_material in shader_dress_materials:
            original_dress_material = [material for material in bpy.data.materials if material.name.endswith(
                shader_dress_material.name.split(' ')[-1]
            )][0]  # the material that ends with 'Dress', 'Dress1', 'Dress2'

            actual_material = get_actual_material_name_for_dress(original_dress_material.name)
            if actual_material in texture_name:
                print(f'Importing texture "{texture_name}" onto material "{shader_dress_material.name}"')
                material_shader_nodes = bpy.data.materials.get(shader_dress_material.name).node_tree.nodes
                material_shader_nodes.get(f'{texture_name}_UV0').image = texture_img
                material_shader_nodes.get(f'{texture_name}_UV1').image = texture_img
                return

    '''
    Deprecated: No longer needed after shader rewrite because normal map is plugged by default
    Still maintains backward compatibility by only trying this if `label_name` is found in the node tree.
    '''
    def plug_normal_map(self, shader_material_name, label_name):
        shader_group_material_name = 'Group.001'
        shader_material = bpy.data.materials.get(shader_material_name)

        if shader_material:
            normal_map_node_color_outputs = [node.outputs.get('Color') for node in shader_material.node_tree.nodes \
                if node.label == label_name and not node.outputs.get('Color').is_linked]
            
            if normal_map_node_color_outputs:
                normal_map_node_color_output = normal_map_node_color_outputs[0]
                normal_map_input = shader_material.node_tree.nodes.get(shader_group_material_name).inputs.get('Normal Map')

                bpy.data.materials.get(shader_material_name).node_tree.links.new(
                    normal_map_node_color_output,
                    normal_map_input
                )


class GenshinAvatarTextureImporter(GenshinTextureImporter):
    def import_textures(self, directory):
        for name, folder, files in os.walk(directory):
            for file in files:
                # load the file with the correct alpha mode
                img_path = directory + "/" + file
                img = bpy.data.images.load(filepath = img_path, check_existing=True)
                img.alpha_mode = 'CHANNEL_PACKED'

                hair_material = bpy.data.materials.get('miHoYo - Genshin Hair')
                face_material = bpy.data.materials.get('miHoYo - Genshin Face')
                body_material = bpy.data.materials.get('miHoYo - Genshin Body')

                # Implement the texture in the correct node
                print(f'Importing texture {file}')
                if "Hair_Diffuse" in file and "Eff" not in file:
                    self.set_diffuse_texture(TextureType.HAIR, hair_material, img)
                elif "Hair_Lightmap" in file:
                    self.set_lightmap_texture(TextureType.HAIR, hair_material, img)
                elif "Hair_Normalmap" in file:
                    self.set_normalmap_texture(TextureType.HAIR, hair_material, img)
                elif "Hair_Shadow_Ramp" in file:
                    bpy.data.node_groups['Hair Shadow Ramp'].nodes['Hair_Shadow_Ramp'].image = img
                elif "Body_Diffuse" in file:
                    self.set_diffuse_texture(TextureType.BODY, body_material, img)
                elif "Body_Lightmap" in file:
                    self.set_lightmap_texture(TextureType.BODY, body_material, img)
                elif "Body_Normalmap" in file:
                    self.set_normalmap_texture(TextureType.BODY, body_material, img)
                elif "Body_Shadow_Ramp" in file:
                    bpy.data.node_groups['Body Shadow Ramp'].nodes['Body_Shadow_Ramp'].image = img
                elif "Body_Specular_Ramp" in file or "Tex_Specular_Ramp" in file :
                    img.colorspace_settings.name='Non-Color'
                    bpy.data.node_groups['Body Specular Ramp'].nodes['Body_Specular_Ramp'].image = img
                elif "Face_Diffuse" in file:
                    face_material.node_tree.nodes['Face_Diffuse'].image = img
                elif "Face_Shadow" in file:
                    img.colorspace_settings.name='Non-Color'
                    face_material.node_tree.nodes['Face_Shadow'].image = img
                elif "FaceLightmap" in file:
                    img.colorspace_settings.name='Non-Color'
                    bpy.data.node_groups['Face Lightmap'].nodes['Face_Lightmap'].image = img
                elif "MetalMap" in file:
                    bpy.data.node_groups['Metallic Matcap'].nodes['MetalMap'].image = img
                else:
                    pass
            break  # IMPORTANT: We os.walk which also traverses through folders...we just want the files


class GenshinNPCTextureImporter(GenshinTextureImporter):
    def import_textures(self, directory):
        for name, folder, files in os.walk(directory):
            for file in files:
                # load the file with the correct alpha mode
                img_path = directory + "/" + file
                img = bpy.data.images.load(filepath = img_path, check_existing=True)
                img.alpha_mode = 'CHANNEL_PACKED'

                hair_material = bpy.data.materials.get('miHoYo - Genshin Hair')
                face_material = bpy.data.materials.get('miHoYo - Genshin Face')
                body_material = bpy.data.materials.get('miHoYo - Genshin Body')

                # Implement the texture in the correct node
                print(f'Importing texture {file}')
                if self.is_texture_identifiers_in_texture_name(['Hair', 'Diffuse'], file) and \
                    not self.is_texture_identifiers_in_texture_name(['Eff'], file):
                    self.set_diffuse_texture(TextureType.HAIR, hair_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Hair', 'Lightmap'], file):
                    self.set_lightmap_texture(TextureType.HAIR, hair_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Hair', 'Normalmap'], file):
                    self.set_normalmap_texture(TextureType.HAIR, hair_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Hair', 'Shadow_Ramp'], file):
                    bpy.data.node_groups['Hair Shadow Ramp'].nodes['Hair_Shadow_Ramp'].image = img

                elif self.is_texture_identifiers_in_texture_name(['Body', 'Diffuse'], file):
                    self.set_diffuse_texture(TextureType.BODY, body_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Body', 'Lightmap'], file):
                    self.set_lightmap_texture(TextureType.BODY, body_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Body', 'Normalmap'], file):
                    self.set_normalmap_texture(TextureType.BODY, body_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Body', 'Shadow_Ramp'], file):
                    bpy.data.node_groups['Body Shadow Ramp'].nodes['Body_Shadow_Ramp'].image = img

                elif self.is_texture_identifiers_in_texture_name(['Body', 'Specular_Ramp'], file) or \
                    self.is_texture_identifiers_in_texture_name(['Tex', 'Specular_Ramp'], file):
                    img.colorspace_settings.name='Non-Color'
                    bpy.data.node_groups['Body Specular Ramp'].nodes['Body_Specular_Ramp'].image = img

                elif self.is_texture_identifiers_in_texture_name(['Face', 'Diffuse'], file):
                    face_material.node_tree.nodes['Face_Diffuse'].image = img

                elif self.is_texture_identifiers_in_texture_name(['NPC', 'Face', 'Lightmap'], file):
                    img.colorspace_settings.name='Non-Color'
                    face_material.node_tree.nodes['Face_Shadow'].image = img

                elif self.is_texture_identifiers_in_texture_name(['Face', 'Lightmap'], file):
                    img.colorspace_settings.name='Non-Color'
                    bpy.data.node_groups['Face Lightmap'].nodes['Face_Lightmap'].image = img

                elif "MetalMap" in file:
                    bpy.data.node_groups['Metallic Matcap'].nodes['MetalMap'].image = img

                else:
                    pass
            break  # IMPORTANT: We os.walk which also traverses through folders...we just want the files
