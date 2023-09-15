from enum import Enum, auto
from typing import List
import bpy

import os
from setup_wizard.domain.game_types import GameType
from setup_wizard.domain.shader_identifier_service import GenshinImpactShaders, ShaderIdentifierService, \
    ShaderIdentifierServiceFactory
from setup_wizard.domain.shader_materials import V3_BonnyFestivityGenshinImpactMaterialNames, FestivityGenshinImpactMaterialNames, \
    GameMaterialNames, Nya222HonkaiStarRailShaderMaterialNames
from setup_wizard.domain.shader_node_names import V3_GenshinShaderNodeNames

from setup_wizard.import_order import get_actual_material_name_for_dress
from setup_wizard.texture_import_setup.texture_node_names import TextureNodeNames
from setup_wizard.texture_import_setup.texture_node_names import Nya222HonkaiStarRailTextureNodeNames


class TextureImporterType(Enum):
    AVATAR = auto()
    MONSTER = auto()
    NPC = auto()
    HSR_AVATAR = auto()


class TextureType(Enum):
    HAIR = 'Hair'
    BODY = 'Body'
    FACE = 'Face'


class TextureImporterFactory:
    def create(texture_importer_type, game_type: GameType):
        shader_identifier_service: ShaderIdentifierService = ShaderIdentifierServiceFactory.create(game_type.name)

        if texture_importer_type == TextureImporterType.AVATAR:
            if shader_identifier_service.identify_shader(bpy.data.materials) is GenshinImpactShaders.V3_GENSHIN_IMPACT_SHADER:
                material_names = V3_BonnyFestivityGenshinImpactMaterialNames
            else:
                material_names = FestivityGenshinImpactMaterialNames
            return GenshinAvatarTextureImporter(material_names)
        elif texture_importer_type == TextureImporterType.NPC:
            if shader_identifier_service.identify_shader(bpy.data.materials) is GenshinImpactShaders.V3_GENSHIN_IMPACT_SHADER:
                material_names = V3_BonnyFestivityGenshinImpactMaterialNames
            else:
                material_names = FestivityGenshinImpactMaterialNames
            return GenshinNPCTextureImporter(material_names)
        elif texture_importer_type == TextureImporterType.MONSTER:
            if shader_identifier_service.identify_shader(bpy.data.materials) is GenshinImpactShaders.V3_GENSHIN_IMPACT_SHADER:
                material_names = V3_BonnyFestivityGenshinImpactMaterialNames
            else:
                material_names = FestivityGenshinImpactMaterialNames
            return GenshinMonsterTextureImporter(material_names)
        elif texture_importer_type == TextureImporterType.HSR_AVATAR:
            return HonkaiStarRailAvatarTextureImporter(Nya222HonkaiStarRailTextureNodeNames)
        else:
            print(f'Unknown TextureImporterType: {texture_importer_type}')


class GenshinTextureImporter:
    def __init__(self, game_type: GameType, character_type: TextureImporterType):
        self.game_type = game_type
        self.character_type = character_type

    def import_textures(self, directory):
        raise NotImplementedError()

    '''
    Checks if all texture identifiers are in the texture name
    Use Case: I want to check if a texture has [X, Y, Z] in it.
    '''
    def is_texture_identifiers_in_texture_name(self, texture_identifiers, texture_name: str):
        texture_identifier: str

        for texture_identifier in texture_identifiers:
            if texture_identifier.lower() not in texture_name.lower():
                return False
        return True

    '''
    Checks a groups of files to see if there is a file that has all texture identifiers in the filename
    Use Case: I want to check if there is a file with [X, Y, Z] in a group of files
    '''
    def is_texture_identifiers_in_files(self, texture_identifiers, files):
        file: str

        for file in files:
            if self.is_texture_identifiers_in_texture_name(texture_identifiers, file.lower()):
                return True
        return False

    '''
    Checks if no texture identifiers exist in each file
    Use Case: I want to check if a group of files does not have [X, Y, Z] in each filename
    '''
    def is_no_texture_identifiers_in_files(self, texture_identifiers: List[str], files: List[str]):
        for file in files:
            for texture_identifier in texture_identifiers:
                if texture_identifier.lower() in file.lower():
                    return False
        return True

    def set_diffuse_texture(self, texture_type: TextureType, material, img):
        material.node_tree.nodes[f'{texture_type.value}_Diffuse_UV0'].image = img
        material.node_tree.nodes[f'{texture_type.value}_Diffuse_UV1'].image = img

        if self.game_type == GameType.GENSHIN_IMPACT:
            if not self.does_dress_texture_exist_in_directory_files() or \
                type(self) is GenshinMonsterTextureImporter or \
                type(self) is GenshinNPCTextureImporter:
                self.setup_dress_textures(f'{texture_type.value}_Diffuse', img, self.character_type)

    def set_lightmap_texture(self, texture_type: TextureType, material, img):
        img.colorspace_settings.name='Non-Color'
        material.node_tree.nodes[f'{texture_type.value}_Lightmap_UV0'].image = img
        material.node_tree.nodes[f'{texture_type.value}_Lightmap_UV1'].image = img
        
        if self.game_type == GameType.GENSHIN_IMPACT:
            if not self.does_dress_texture_exist_in_directory_files() or \
                type(self) is GenshinMonsterTextureImporter or \
                type(self) is GenshinNPCTextureImporter:
                self.setup_dress_textures(f'{texture_type.value}_Lightmap', img, self.character_type)

    def set_normalmap_texture(self, type: TextureType, material, img):
        img.colorspace_settings.name='Non-Color'
        material.node_tree.nodes[f'{type.value}_Normalmap_UV0'].image = img
        material.node_tree.nodes[f'{type.value}_Normalmap_UV1'].image = img
        
        if self.game_type == GameType.GENSHIN_IMPACT:
            self.setup_dress_textures(f'{type.value}_Normalmap', img, self.character_type)

        # Deprecated. Tries only if it exists. Only for V1 Shader
        self.plug_normal_map(f'miHoYo - Genshin {type.value}', 'MUTE IF ONLY 1 UV MAP EXISTS')
        self.plug_normal_map('miHoYo - Genshin Dress', 'MUTE IF ONLY 1 UV MAP EXISTS')
        self.plug_normal_map('miHoYo - Genshin Dress1', 'MUTE IF ONLY 1 UV MAP EXISTS')
        self.plug_normal_map('miHoYo - Genshin Dress2', 'MUTE IF ONLY 1 UV MAP EXISTS')

    def set_shadow_ramp_texture(self, type: TextureType, img):
        bpy.data.node_groups[f'{type.value} Shadow Ramp'].nodes[f'{type.value}_Shadow_Ramp'].image = img

    def set_specular_ramp_texture(self, type: TextureType, img):
        specular_ramp_node_exists = bpy.data.node_groups.get(f'{type.value} Specular Ramp')

        if specular_ramp_node_exists:
            img.colorspace_settings.name='Non-Color'
            bpy.data.node_groups[f'{type.value} Specular Ramp'].nodes[f'{type.value}_Specular_Ramp'].image = img        

    def set_face_diffuse_texture(self, face_material, img):
        face_material.node_tree.nodes['Face_Diffuse'].image = img

        # Set Built-In Face Lightmap Value for the V3 Shader
        face_shader_node = face_material.node_tree.nodes.get('Face Shader')
        if face_shader_node:
            face_lightmap_input = face_shader_node.inputs.get('[Loli/Boy/Girl/Male/Lady]')
            if face_lightmap_input:
                if 'Loli' in img.name:
                    face_lightmap_input.default_value = 1.0
                elif 'Boy' in img.name:
                    face_lightmap_input.default_value = 2.0
                elif 'Girl' in img.name:
                    face_lightmap_input.default_value = 3.0
                elif 'Male' in img.name:
                    face_lightmap_input.default_value = 4.0
                elif 'Lady' in img.name:
                    face_lightmap_input.default_value = 5.0


    def set_face_shadow_texture(self, face_material, img):
        face_shadow_node_exists = face_material.node_tree.nodes.get('Face_Shadow')

        if face_shadow_node_exists:
            img.colorspace_settings.name='Non-Color'
            face_material.node_tree.nodes['Face_Shadow'].image = img        

    def set_face_lightmap_texture(self, img):
        face_lightmap_node_exist = bpy.data.node_groups.get('Face Lightmap')

        if face_lightmap_node_exist:
            img.colorspace_settings.name='Non-Color'
            bpy.data.node_groups['Face Lightmap'].nodes['Face_Lightmap'].image = img

    def set_metalmap_texture(self, img):
        metallic_matcap_node_exists = bpy.data.node_groups.get('Metallic Matcap')

        if metallic_matcap_node_exists:
            bpy.data.node_groups['Metallic Matcap'].nodes['MetalMap'].image = img

    def setup_dress_textures(self, texture_name, texture_img, character_type: TextureImporterType):
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
            actual_cloak_material = get_actual_material_name_for_dress(original_cloak_material.name, character_type.name)
            if actual_cloak_material in texture_name:
                material_shader_nodes = bpy.data.materials.get(shader_cloak_materials[0].name).node_tree.nodes
                material_shader_nodes.get(f'{texture_name}_UV0').image = texture_img
                material_shader_nodes.get(f'{texture_name}_UV1').image = texture_img

        for shader_dress_material in shader_dress_materials:
            original_dress_material = [material for material in bpy.data.materials if material.name.endswith(
                shader_dress_material.name.split(' ')[-1]
            )][0]  # the material that ends with 'Dress', 'Dress1', 'Dress2'

            actual_material = get_actual_material_name_for_dress(original_dress_material.name, character_type.name)
            if actual_material in texture_name:
                print(f'Importing texture "{texture_name}" onto material "{shader_dress_material.name}"')
                material_shader_nodes = bpy.data.materials.get(shader_dress_material.name).node_tree.nodes
                material_shader_nodes.get(f'{texture_name}_UV0').image = texture_img
                material_shader_nodes.get(f'{texture_name}_UV1').image = texture_img
                return

    def does_dress_texture_exist_in_directory_files(self):
        dress_texture_detected = False
        for file in self.files:
            if 'Dress' in file:
                dress_texture_detected = True
        return dress_texture_detected

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

    def set_face_material_id(self, face_material, image):
        character_to_face_material_id_map = {
            'Collei': 5,
            'Cyno': 3,
            'DilucCostumeFlamme': 3,
            'Faruzan': 3,
            'AyakaCostumeFruhling': 5,
            'Ayato': 3,
            'Linette': 3,  # Lynette
            'Nilou': 3,
            'Kokomi': 3,
            'Tighnari': 3,
            'Yelan': 3,
        }

        for character_name in character_to_face_material_id_map.keys():
            if character_name in image.name:
                if face_material.node_tree.nodes.get(V3_GenshinShaderNodeNames.FACE_SHADER):
                    face_shader_node = face_material.node_tree.nodes[V3_GenshinShaderNodeNames.FACE_SHADER]
                    face_shader_node.inputs[V3_GenshinShaderNodeNames.FACE_MATERIAL_ID].default_value = \
                        character_to_face_material_id_map[character_name]


class GenshinAvatarTextureImporter(GenshinTextureImporter):
    def __init__(self, material_names: GameMaterialNames):
        super().__init__(GameType.GENSHIN_IMPACT, TextureImporterType.AVATAR)
        self.material_names = material_names

    def import_textures(self, directory):
        for name, folder, files in os.walk(directory):
            self.files = files
            for file in files:
                # load the file with the correct alpha mode
                img_path = directory + "/" + file
                img = bpy.data.images.load(filepath = img_path, check_existing=True)
                img.alpha_mode = 'CHANNEL_PACKED'

                effect_hair_material = bpy.data.materials.get(f'{self.material_names.EFFECT_HAIR}')
                hair_material = bpy.data.materials.get(f'{self.material_names.HAIR}')
                helmet_material = bpy.data.materials.get(f'{self.material_names.HELMET}')
                helmet_emotion_material = bpy.data.materials.get(f'{self.material_names.HELMET_EMO}')
                face_material = bpy.data.materials.get(f'{self.material_names.FACE}')
                body_material = bpy.data.materials.get(f'{self.material_names.BODY}')
                dress_material = bpy.data.materials.get(f'{self.material_names.DRESS}')
                gauntlet_material = bpy.data.materials.get(f'{self.material_names.GAUNTLET}')

                # Implement the texture in the correct node
                print(f'Importing texture {file} using {self.__class__.__name__}')
                if "Hair_Diffuse" in file and "Eff" not in file:
                    self.set_diffuse_texture(TextureType.HAIR, hair_material, img)
                elif "EffectHair_Diffuse" in file:
                    self.set_diffuse_texture(TextureType.HAIR, effect_hair_material, img)
                elif 'Helmet_Tex_Diffuse' in file:
                    self.set_diffuse_texture(TextureType.HAIR, helmet_material, img)
                elif 'HelmetEmo_Tex_Diffuse' in file:
                    self.set_diffuse_texture(TextureType.HAIR, helmet_emotion_material, img)
                elif "Hair_Lightmap" in file and "Eff" not in file:
                    self.set_lightmap_texture(TextureType.HAIR, hair_material, img)
                elif "EffectHair_Lightmap" in file:
                    self.set_lightmap_texture(TextureType.HAIR, effect_hair_material, img)
                elif 'Helmet_Tex_Lightmap' in file:
                    self.set_lightmap_texture(TextureType.HAIR, helmet_material, img)
                elif "Hair_Normalmap" in file:
                    self.set_normalmap_texture(TextureType.HAIR, hair_material, img)
                elif "Hair_Shadow_Ramp" in file:
                    self.set_shadow_ramp_texture(TextureType.HAIR, img)
                elif "Body_Diffuse" in file:
                    self.set_diffuse_texture(TextureType.BODY, body_material, img)
                    # Set Face Id in Body_Diffuse because not all Face Diffuse filenames have the full costume name
                    # Ex. Diluc's costume does not have DilucCostumeFlamme, but just Diluc
                    self.set_face_material_id(face_material, img)
                elif "Body_Lightmap" in file:
                    self.set_lightmap_texture(TextureType.BODY, body_material, img)
                elif "Body_Normalmap" in file:
                    self.set_normalmap_texture(TextureType.BODY, body_material, img)
                elif "Body_Shadow_Ramp" in file:
                    self.set_shadow_ramp_texture(TextureType.BODY, img)
                elif "Body_Specular_Ramp" in file or "Tex_Specular_Ramp" in file:
                    self.set_specular_ramp_texture(TextureType.BODY, img)
                elif "Dress" in file:
                    self.set_diffuse_texture(TextureType.BODY, dress_material, img)
                elif "Face_Diffuse" in file:
                    self.set_face_diffuse_texture(face_material, img)
                elif "Face_Shadow" in file:
                    self.set_face_shadow_texture(face_material, img)
                elif "FaceLightmap" in file:
                    self.set_face_lightmap_texture(img)
                elif "MetalMap" in file:
                    self.set_metalmap_texture(img)
                elif "Gauntlet_Diffuse" in file:
                    self.set_diffuse_texture(TextureType.BODY, gauntlet_material, img)
                elif "Gauntlet_Lightmap" in file:
                    self.set_lightmap_texture(TextureType.BODY, gauntlet_material, img)
                elif "Gauntlet_Normalmap" in file:
                    self.set_normalmap_texture(TextureType.BODY, gauntlet_material, img)
                else:
                    print(f'WARN: Ignoring texture {file}')
            break  # IMPORTANT: We os.walk which also traverses through folders...we just want the files


class GenshinNPCTextureImporter(GenshinTextureImporter):
    def __init__(self, material_names: GameMaterialNames):
        super().__init__(GameType.GENSHIN_IMPACT, TextureImporterType.NPC)
        self.material_names = material_names

    def import_textures(self, directory):
        for name, folder, files in os.walk(directory):
            self.files = files
            for file in files:
                # load the file with the correct alpha mode
                img_path = directory + "/" + file
                img = bpy.data.images.load(filepath = img_path, check_existing=True)
                img.alpha_mode = 'CHANNEL_PACKED'

                hair_material = bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}Hair')
                face_material = bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}Face')
                body_material = bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}Body')

                # Implement the texture in the correct node
                print(f'Importing texture {file} using {self.__class__.__name__}')
                if self.is_texture_identifiers_in_texture_name(['Hair', 'Diffuse'], file) and \
                    not self.is_texture_identifiers_in_texture_name(['Eff'], file):
                    self.set_diffuse_texture(TextureType.HAIR, hair_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Hair', 'Lightmap'], file):
                    self.set_lightmap_texture(TextureType.HAIR, hair_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Hair', 'Normalmap'], file):
                    self.set_normalmap_texture(TextureType.HAIR, hair_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Hair', 'Shadow_Ramp'], file):
                    self.set_shadow_ramp_texture(TextureType.HAIR, img)

                elif self.is_texture_identifiers_in_texture_name(['Body', 'Diffuse'], file):
                    self.set_diffuse_texture(TextureType.BODY, body_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Body', 'Lightmap'], file):
                    self.set_lightmap_texture(TextureType.BODY, body_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Body', 'Normalmap'], file):
                    self.set_normalmap_texture(TextureType.BODY, body_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Body', 'Shadow_Ramp'], file):
                    self.set_shadow_ramp_texture(TextureType.BODY, img)

                elif self.is_texture_identifiers_in_texture_name(['Body', 'Specular_Ramp'], file) or \
                    self.is_texture_identifiers_in_texture_name(['Tex', 'Specular_Ramp'], file):
                    self.set_specular_ramp_texture(TextureType.BODY, img)

                elif self.is_texture_identifiers_in_texture_name(['Face', 'Diffuse'], file):
                    self.set_face_diffuse_texture(face_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Face', 'Shadow'], file) or \
                    (self.is_texture_identifiers_in_texture_name(['NPC', 'Face', 'Lightmap'], file) and
                        not self.is_texture_identifiers_in_files(['Face', 'Shadow'], files)):
                    # If Face Shadow exists, use that texture
                    # If Face Shadow does not exist in this folder, use "Face Lightmap" (actually an NPC Face Shadow texture)
                    self.set_face_shadow_texture(face_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Face', 'Lightmap'], file):
                    self.set_face_lightmap_texture(img)

                elif self.is_texture_identifiers_in_texture_name(['MetalMap'], file):
                    self.set_metalmap_texture(img)

                else:
                    print(f'WARN: Ignoring texture {file}')
            break  # IMPORTANT: We os.walk which also traverses through folders...we just want the files


class GenshinMonsterTextureImporter(GenshinTextureImporter):
    def __init__(self, material_names: GameMaterialNames):
        super().__init__(GameType.GENSHIN_IMPACT, TextureImporterType.MONSTER)
        self.material_names = material_names

    def import_textures(self, directory):
        for name, folder, files in os.walk(directory):
            self.files = files
            for file in files:
                # load the file with the correct alpha mode
                img_path = directory + "/" + file
                img = bpy.data.images.load(filepath = img_path, check_existing=True)
                img.alpha_mode = 'CHANNEL_PACKED'

                hair_material = bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}Hair')
                face_material = bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}Face')
                body_material = bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}Body')

                # Implement the texture in the correct node
                print(f'Importing texture {file} using {self.__class__.__name__}')

                if self.is_texture_identifiers_in_texture_name(['Body', 'Tex', 'Diffuse'], file) or \
                    (self.is_texture_identifiers_in_texture_name(['Tex', 'Diffuse'], file) and \
                    not self.is_texture_identifiers_in_files(['Hair'], files)):
                    self.set_diffuse_texture(TextureType.BODY, body_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Body', 'Tex', 'Lightmap'], file) or \
                    (self.is_texture_identifiers_in_texture_name(['Tex', 'Diffuse'], file) and \
                    not self.is_texture_identifiers_in_files(['Hair'], files)):
                    self.set_lightmap_texture(TextureType.BODY, body_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Hair', 'Tex', 'Diffuse'], file) or \
                    (self.is_texture_identifiers_in_texture_name(['Tex', 'Diffuse'], file) and \
                    not self.is_texture_identifiers_in_files(['Body'], files)):
                    self.set_diffuse_texture(TextureType.HAIR, hair_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Hair', 'Tex', 'Lightmap'], file) or \
                    (self.is_texture_identifiers_in_texture_name(['Tex', 'Diffuse'], file) and \
                    not self.is_texture_identifiers_in_files(['Body'], files)):
                    self.set_lightmap_texture(TextureType.HAIR, hair_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Body_Shadow_Ramp'], file):
                    self.set_shadow_ramp_texture(TextureType.BODY, img)
                elif self.is_texture_identifiers_in_texture_name(['Hair_Shadow_Ramp'], file):
                    self.set_shadow_ramp_texture(TextureType.HAIR, img)
                elif self.is_texture_identifiers_in_texture_name(['Tex', 'Specular_Ramp'], file):
                    self.set_specular_ramp_texture(TextureType.BODY, img)

                elif self.is_texture_identifiers_in_texture_name(['Face', 'Diffuse'], file):
                    self.set_face_diffuse_texture(face_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Face', 'Shadow'], file) or \
                    (self.is_texture_identifiers_in_texture_name(['NPC', 'Face', 'Lightmap'], file) and
                        not self.is_texture_identifiers_in_files(['Face', 'Shadow'], files)):
                    # If Face Shadow exists, use that texture
                    # If Face Shadow does not exist in this folder, use "Face Lightmap" (actually an NPC Face Shadow texture)
                    self.set_face_shadow_texture(face_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Face', 'Lightmap'], file):
                    self.set_face_lightmap_texture(img)

                elif self.is_texture_identifiers_in_texture_name(['MetalMap'], file):
                    self.set_metalmap_texture(img)

                else:
                    print(f'WARN: Ignoring texture {file}')
            break  # IMPORTANT: We os.walk which also traverses through folders...we just want the files


class HonkaiStarRailTextureImporter(GenshinTextureImporter):
    def __init__(self, game_type: GameType, character_type: TextureImporterType, texture_node_names: TextureNodeNames):
        super().__init__(game_type, character_type)
        self.texture_node_names: TextureNodeNames = texture_node_names

    def set_diffuse_texture(self, type: TextureType, material, img):
        material.node_tree.nodes[self.texture_node_names.DIFFUSE].image = img

    def set_lightmap_texture(self, type: TextureType, material, img):
        img.colorspace_settings.name='Non-Color'
        material.node_tree.nodes[self.texture_node_names.LIGHTMAP].image = img

    def set_warm_shadow_ramp_texture(self, type: TextureType, img):
        ramp_node_name = \
            self.texture_node_names.BODY_RAMP if type is TextureType.BODY else \
            self.texture_node_names.HAIR_RAMP

        ramp_texture_node = bpy.data.node_groups.get('Body_Ramp').nodes[ramp_node_name] if \
            type is TextureType.BODY else bpy.data.node_groups.get('Hair_Ramp').nodes[ramp_node_name]
        ramp_texture_node.image = img

    # TODO: Not currently called, but should be supported in the future
    def set_cool_shadow_ramp_texture(self, type: TextureType, img):
        # Yes, the Hair_Shadow_Ramp Cool Ramp is also named Body_Shadow_Ramp.001
        bpy.data.node_groups[f'{type.value} Shadow Ramp'].nodes[f'Body_Shadow_Ramp.001'].image = img

    def set_weapon_ramp_texture(self, img, override=False):
        weapon_ramp_node = bpy.data.node_groups[f'{Nya222HonkaiStarRailTextureNodeNames.WEAPON_RAMP_NODE_GROUP}'].nodes[
            Nya222HonkaiStarRailTextureNodeNames.WEAPON_RAMP
        ]
        
        if override or not weapon_ramp_node.image:
            weapon_ramp_node.image = img

    def set_facemap_texture(self, img):
        img.colorspace_settings.name='Non-Color'
        bpy.data.node_groups[self.texture_node_names.FACE_MAP_NODE_GROUP].nodes[
            self.texture_node_names.FACE_MAP].image = img

    def set_face_expression_texture(self, face_material, img):
        img.colorspace_settings.name='Non-Color'
        bpy.data.node_groups[self.texture_node_names.FACE_EXPRESSION_NODE_GROUP].nodes[
            self.texture_node_names.FACE_EXPRESSION_MAP].image = img

    def set_stocking_texture(self, type: TextureType, material, img):
        body_material = bpy.data.materials.get(Nya222HonkaiStarRailShaderMaterialNames.BODY)
        body1_material = bpy.data.materials.get(Nya222HonkaiStarRailShaderMaterialNames.BODY1)
        img.colorspace_settings.name='Non-Color'

        # If Body material or Body1 material apply to Body1 Stockings
        # Else Body2 material or Body Stockings texture with Body1/Body2 materials apply to Body2 Stockings
        if (body_material and material is body_material) or (body1_material and material is body1_material):
            bpy.data.node_groups[self.texture_node_names.STOCKINGS_BODY1_NODE_GROUP].nodes[
                self.texture_node_names.STOCKINGS].image = img
        else:
            bpy.data.node_groups[self.texture_node_names.STOCKINGS_BODY2_NODE_GROUP].nodes[
                self.texture_node_names.STOCKINGS].image = img


class HonkaiStarRailAvatarTextureImporter(HonkaiStarRailTextureImporter):
    def __init__(self, texture_node_names: TextureNodeNames):
        super().__init__(GameType.HONKAI_STAR_RAIL, TextureImporterType.HSR_AVATAR, texture_node_names)

    def import_textures(self, directory):
        for name, folder, files in os.walk(directory):
            for file in files:
                # load the file with the correct alpha mode
                img_path = directory + "/" + file
                img = bpy.data.images.load(filepath = img_path, check_existing=True)
                img.alpha_mode = 'CHANNEL_PACKED'

                hair_material = bpy.data.materials.get(Nya222HonkaiStarRailShaderMaterialNames.HAIR)
                face_material = bpy.data.materials.get(Nya222HonkaiStarRailShaderMaterialNames.FACE)
                body_material = bpy.data.materials.get(Nya222HonkaiStarRailShaderMaterialNames.BODY)
                body1_material = bpy.data.materials.get(Nya222HonkaiStarRailShaderMaterialNames.BODY1)
                body2_material = bpy.data.materials.get(Nya222HonkaiStarRailShaderMaterialNames.BODY2)
                body3_material = bpy.data.materials.get(Nya222HonkaiStarRailShaderMaterialNames.BODY3)
                body_trans_material = bpy.data.materials.get(Nya222HonkaiStarRailShaderMaterialNames.BODY_TRANS)
                body2_trans_material = bpy.data.materials.get(Nya222HonkaiStarRailShaderMaterialNames.BODY2_TRANS)
                weapon_material = bpy.data.materials.get(Nya222HonkaiStarRailShaderMaterialNames.WEAPON)
                weapon01_material = bpy.data.materials.get(Nya222HonkaiStarRailShaderMaterialNames.WEAPON01)
                weapon02_material = bpy.data.materials.get(Nya222HonkaiStarRailShaderMaterialNames.WEAPON02)
                weapon_materials = [weapon_material, weapon01_material, weapon02_material]

                # Implement the texture in the correct node
                print(f'INFO: Importing texture {file} using {self.__class__.__name__}')

                if self.is_texture_identifiers_in_texture_name(['Hair', 'Color'], file) and \
                    not self.is_texture_identifiers_in_texture_name(['Eff'], file):  # TODO: Review this line
                    self.set_diffuse_texture(TextureType.HAIR, hair_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Hair', 'LightMap'], file):
                    self.set_lightmap_texture(TextureType.HAIR, hair_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Hair', 'Warm_Ramp'], file):
                    self.set_warm_shadow_ramp_texture(TextureType.HAIR, img)

                elif self.is_texture_identifiers_in_texture_name(['Hair', 'Cool_Ramp'], file):
                    pass
                #     self.set_cool_shadow_ramp_texture(TextureType.HAIR, img)
                
                # Character has Body and no Body1 or Body2?
                elif self.is_texture_identifiers_in_texture_name(['Body_', 'Color'], file):
                    self.set_diffuse_texture(TextureType.BODY, body_material, img)

                    if body_trans_material:
                        self.set_diffuse_texture(TextureType.BODY, body_trans_material, img)

                # Character has Body and no Body1 or Body2?
                elif self.is_texture_identifiers_in_texture_name(['Body_', 'LightMap'], file):
                    self.set_lightmap_texture(TextureType.BODY, body_material, img)

                    if body_trans_material:
                        self.set_lightmap_texture(TextureType.BODY, body_trans_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Body1', 'Color'], file):
                    self.set_diffuse_texture(TextureType.BODY, body1_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Body1', 'LightMap'], file):
                    self.set_lightmap_texture(TextureType.BODY, body1_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Body2', 'Color'], file):
                    self.set_diffuse_texture(TextureType.BODY, body2_material, img)

                    if body2_trans_material:
                        self.set_diffuse_texture(TextureType.BODY, body2_trans_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Body2', 'LightMap'], file):
                    self.set_lightmap_texture(TextureType.BODY, body2_material, img)

                    if body2_trans_material:
                        self.set_lightmap_texture(TextureType.BODY, body2_trans_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Body3', 'Color'], file):
                    self.set_diffuse_texture(TextureType.BODY, body3_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Body3', 'LightMap'], file):
                    self.set_lightmap_texture(TextureType.BODY, body3_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Warm_Ramp'], file) or \
                    self.is_texture_identifiers_in_texture_name(['Body_Ramp'], file):  # Not Hair, so ramp must be Body
                    self.set_warm_shadow_ramp_texture(TextureType.BODY, img)
                    self.set_weapon_ramp_texture(img)

                # TODO: RAMPS? Only supporting Warm Ramps for now
                elif self.is_texture_identifiers_in_texture_name(['Cool_Ramp'], file):  # Not Hair, so ramp must be Body
                    pass
                #     self.set_cool_shadow_ramp_texture(TextureType.BODY, img)

                # Not Hair, so ramp must be Body. Only one ramp texture exists (no specific Warm or Cool ramp)
                elif self.is_texture_identifiers_in_texture_name(['Ramp'], file) and \
                    not self.is_texture_identifiers_in_texture_name(['Weapon'], file):

                    if self.is_texture_identifiers_in_texture_name(['Warm_Ramp'], file):
                        self.set_warm_shadow_ramp_texture(TextureType.BODY, img)
                    # TODO: RAMPS? Only supporting Warm Ramps for now
                    # self.set_cool_shadow_ramp_texture(TextureType.BODY, img)

                elif self.is_texture_identifiers_in_texture_name(['Stockings'], file):
                    if self.is_texture_identifiers_in_texture_name(['Body1'], file):
                        self.set_stocking_texture(TextureType.BODY, body1_material, img)
                    elif self.is_texture_identifiers_in_texture_name(['Body2'], file):
                        self.set_stocking_texture(TextureType.BODY, body2_material, img)
                    elif self.is_texture_identifiers_in_texture_name(['Body'], file):  # Must be AFTER Body1/Body2
                        self.set_stocking_texture(TextureType.BODY, body_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Face', 'Color'], file):
                    self.set_diffuse_texture(TextureType.FACE, face_material, img)

                # TODO: Review this whole block, NPC support is borrowed code from GI
                elif self.is_texture_identifiers_in_texture_name(['FaceMap'], file) or \
                    (self.is_texture_identifiers_in_texture_name(['NPC', 'Face', 'LightMap'], file) and
                        not self.is_texture_identifiers_in_files(['FaceMap'], files)):
                    # If Face Shadow exists, use that texture
                    # If Face Shadow does not exist in this folder, use "Face Lightmap" (actually an NPC Face Shadow texture)
                    self.set_facemap_texture(img)

                elif self.is_texture_identifiers_in_texture_name(['Face_ExpressionMap'], file):
                    self.set_face_expression_texture(face_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Weapon', 'Color'], file):
                    for weapon_material in weapon_materials:
                        if weapon_material:
                            self.set_diffuse_texture(TextureType.BODY, weapon_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Weapon', 'LightMap'], file) or \
                    self.is_texture_identifiers_in_texture_name(['Weapon', 'LigthMap'], file):  # Yes, intentional typo

                    for weapon_material in weapon_materials:
                        if weapon_material:
                            self.set_lightmap_texture(TextureType.BODY, weapon_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Weapon', 'Ramp'], file):
                    # Set Weapon Ramp, if none exists use Body Ramp
                    self.set_weapon_ramp_texture(img, override=True)

                else:
                    print(f'WARN: Ignoring texture {file}')
            break  # IMPORTANT: We os.walk which also traverses through folders...we just want the files

