from enum import Enum, auto
from typing import List
import bpy

import os
from setup_wizard.domain.material_identifier_service import PunishingGrayRavenMaterialIdentifierService
from setup_wizard.domain.game_types import GameType
from setup_wizard.domain.shader_identifier_service import GenshinImpactShaders, HonkaiStarRailShaders, ShaderIdentifierService, \
    ShaderIdentifierServiceFactory
from setup_wizard.domain.shader_material_names import JaredNytsPunishingGrayRavenShaderMaterialNames, StellarToonShaderMaterialNames, V3_BonnyFestivityGenshinImpactMaterialNames, V2_FestivityGenshinImpactMaterialNames, \
    ShaderMaterialNames, Nya222HonkaiStarRailShaderMaterialNames, V4_PrimoToonGenshinImpactMaterialNames
from setup_wizard.domain.shader_node_names import JaredNyts_PunishingGrayRavenNodeNames, ShaderNodeNames, StellarToonShaderNodeNames
from setup_wizard.domain.shader_material_name_keywords import ShaderMaterialNameKeywords

from setup_wizard.import_order import get_actual_material_name_for_dress
from setup_wizard.texture_import_setup.texture_node_names import JaredNytsPunishingGrayRavenTextureNodeNames, Nya222HonkaiStarRailTextureNodeNames, StellarToonTextureNodeNames, TextureNodeNames, V4_GenshinImpactTextureNodeNames
from setup_wizard.texture_import_setup.original_texture_locator_utils import OriginalTextureLocatorUtils


class TextureImporterType(Enum):
    AVATAR = auto()
    MONSTER = auto()
    NPC = auto()
    HSR_AVATAR = auto()
    PGR_AVATAR = auto()
    PGR_CHIBI = auto()


class TextureType(Enum):
    HAIR = 'Hair'
    BODY = 'Body'
    BODY2 = 'Body2'
    FACE = 'Face'
    WEAPON = 'Weapon'


class TextureImporterFactory:
    def create(texture_importer_type, game_type: GameType):
        shader_identifier_service: ShaderIdentifierService = ShaderIdentifierServiceFactory.create(game_type.name)

        if game_type is GameType.GENSHIN_IMPACT:
            shader: GenshinImpactShaders = shader_identifier_service.identify_shader(bpy.data.materials, bpy.data.node_groups)

            if shader is GenshinImpactShaders.V1_GENSHIN_IMPACT_SHADER or shader is GenshinImpactShaders.V2_GENSHIN_IMPACT_SHADER:
                # Not sure why IDE says code is unreachable, it is used
                material_names = V2_FestivityGenshinImpactMaterialNames  # V1/V2 have the same material names
            elif shader is GenshinImpactShaders.V3_GENSHIN_IMPACT_SHADER:
                # Not sure why IDE says code is unreachable, it is used
                material_names = V3_BonnyFestivityGenshinImpactMaterialNames
            else:
                material_names = V4_PrimoToonGenshinImpactMaterialNames  

            if texture_importer_type == TextureImporterType.AVATAR:
                return GenshinAvatarTextureImporter(material_names)
            elif texture_importer_type == TextureImporterType.NPC:
                return GenshinNPCTextureImporter(material_names)
            elif texture_importer_type == TextureImporterType.MONSTER:
                return GenshinMonsterTextureImporter(material_names)
            else:
                print(f'Unknown TextureImporterType: {texture_importer_type}')
        elif game_type is GameType.HONKAI_STAR_RAIL:
            shader: HonkaiStarRailShaders = shader_identifier_service.identify_shader(bpy.data.materials, bpy.data.node_groups)

            if shader is HonkaiStarRailShaders.NYA222_HONKAI_STAR_RAIL_SHADER:
                material_names = Nya222HonkaiStarRailShaderMaterialNames
                texture_names = Nya222HonkaiStarRailTextureNodeNames
            else:  # shader is HonkaiStarRailShaders.STELLARTOON_HONKAI_STAR_RAIL_SHADER
                material_names = StellarToonShaderMaterialNames
                texture_names = StellarToonTextureNodeNames

            if texture_importer_type == TextureImporterType.HSR_AVATAR:
                return HonkaiStarRailAvatarTextureImporter(material_names, texture_names)
            else:
                print(f'Unknown TextureImporterType: {texture_importer_type}')
        elif game_type is GameType.PUNISHING_GRAY_RAVEN:
            if texture_importer_type == TextureImporterType.PGR_AVATAR:
                return PunishingGrayRavenAvatarTextureImporter(JaredNytsPunishingGrayRavenShaderMaterialNames, 
                                                               JaredNytsPunishingGrayRavenTextureNodeNames)
            else:
                print(f'Unknown TextureImporterType: {texture_importer_type}')
        else:
            print(f'Unknown game_type: {game_type}')


class GenshinTextureImporter:
    SUPPORTED_TEXTURE_FILE_EXTENSIONS: tuple[str, ...] = ('.jpg', '.jpeg', '.png','.tga')

    def __init__(self, game_type: GameType, character_type: TextureImporterType):
        self.game_type = game_type
        self.character_type = character_type
        self.shader_identifier_service: ShaderIdentifierService
        self.genshin_shader_version: GenshinImpactShaders

    def import_textures(self, directory):
        raise NotImplementedError()


    def is_supported_texture(self, file: str):
        return file.endswith(self.SUPPORTED_TEXTURE_FILE_EXTENSIONS)

    '''
    Checks if all texture identifiers are in the texture name
    Use Case: I want to check if a texture has [X, Y, Z] in it.
    '''
    def is_texture_identifiers_in_texture_name(self, texture_identifiers: List[str], texture_name: str):
        assert(type(texture_identifiers) is list)  # TODO: Write unit test, programming error, input is wrong type!
        texture_identifier: str

        for texture_identifier in texture_identifiers:
            if texture_identifier.lower() not in texture_name.lower():
                return False
        return True

    def is_one_texture_identifier_in_texture_name(self, texture_identifiers: List[str], texture_name: str, normalize=False):
        for texture_identifier in texture_identifiers:
            if normalize:
                if texture_identifier.lower() in texture_name.lower():
                    return True
            else:
                if texture_identifier in texture_name:
                    return True
        return False

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

    def set_diffuse_texture(self, texture_type: TextureType, material, img, override=True):
        possible_texture_node_names = [
            f'{texture_type.value}_Diffuse_UV0',
            f'{texture_type.value}_Diffuse_UV1',
            V4_GenshinImpactTextureNodeNames.DIFFUSE,
            V4_GenshinImpactTextureNodeNames.VFX_DIFFUSE,
        ]
        
        for texture_node_name in possible_texture_node_names:
            if material.node_tree.nodes.get(texture_node_name):
                if override or not material.node_tree.nodes[texture_node_name].image:
                    material.node_tree.nodes[texture_node_name].image = img

                if self.game_type == GameType.GENSHIN_IMPACT:
                    if not self.does_dress_texture_exist_in_directory_files() or \
                        type(self) is GenshinMonsterTextureImporter or \
                        type(self) is GenshinNPCTextureImporter:
                        self.setup_dress_textures(texture_node_name, img, self.character_type)

    def set_lightmap_texture(self, texture_type: TextureType, material, img):
        img.colorspace_settings.name='Non-Color'
        possible_texture_node_names = [
            f'{texture_type.value}_Lightmap_UV0',
            f'{texture_type.value}_Lightmap_UV1',
            V4_GenshinImpactTextureNodeNames.LIGHTMAP,
        ]
        for texture_node_name in possible_texture_node_names:
            if material.node_tree.nodes.get(texture_node_name):
                material.node_tree.nodes[texture_node_name].image = img
        
                if self.game_type == GameType.GENSHIN_IMPACT:
                    if not self.does_dress_texture_exist_in_directory_files() or \
                        type(self) is GenshinMonsterTextureImporter or \
                        type(self) is GenshinNPCTextureImporter:
                        self.setup_dress_textures(texture_node_name, img, self.character_type)

    def set_normalmap_texture(self, type: TextureType, material, img):
        img.colorspace_settings.name='Non-Color'
        possible_texture_node_names = [
            f'{type.value}_Normalmap_UV0',
            f'{type.value}_Normalmap_UV1',
            V4_GenshinImpactTextureNodeNames.NORMALMAP,
        ]
        for texture_node_name in possible_texture_node_names:
            if material.node_tree.nodes.get(texture_node_name):
                material.node_tree.nodes[texture_node_name].image = img
        
            if self.game_type == GameType.GENSHIN_IMPACT:
                self.setup_dress_textures(texture_node_name, img, self.character_type)

        # Deprecated. Tries only if it exists. Only for V1 Shader
        self.plug_normal_map(f'miHoYo - Genshin {type.value}', 'MUTE IF ONLY 1 UV MAP EXISTS')
        self.plug_normal_map('miHoYo - Genshin Dress', 'MUTE IF ONLY 1 UV MAP EXISTS')
        self.plug_normal_map('miHoYo - Genshin Dress1', 'MUTE IF ONLY 1 UV MAP EXISTS')
        self.plug_normal_map('miHoYo - Genshin Dress2', 'MUTE IF ONLY 1 UV MAP EXISTS')

    def set_shadow_ramp_texture(self, type: TextureType, img):
        possible_shadow_ramp_node_group_names = [
            f'{type.value} Shadow Ramp',
            V4_GenshinImpactTextureNodeNames.SHADER_TEXTURES_NODE_GROUP,
        ]
        for shadow_ramp_node_name in possible_shadow_ramp_node_group_names:
            shadow_ramp_node_group = bpy.data.node_groups.get(shadow_ramp_node_name)
            if shadow_ramp_node_group:
                shadow_ramp_node_group.nodes[f'{type.value}_Shadow_Ramp'].image = img

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
            global_properties = face_material.node_tree.nodes.get(ShaderNodeNames.EXTERNAL_GLOBAL_PROPERTIES)

            if not face_lightmap_input and global_properties:
                face_lightmap_input = global_properties.node_tree.nodes.get(
                    ShaderNodeNames.INTERNAL_GLOBAL_PROPERTIES).inputs.get('[Loli/Boy/Girl/Male/Lady]')

            if face_lightmap_input:
                if 'Loli' in img.name:
                    face_lightmap_input.default_value = 1.0
                elif 'Boy' in img.name:
                    face_lightmap_input.default_value = 2.0
                elif 'Girl' in img.name or 'Female' in img.name:
                    face_lightmap_input.default_value = 3.0
                elif 'Male' in img.name:
                    face_lightmap_input.default_value = 4.0
                elif 'Lady' in img.name:
                    face_lightmap_input.default_value = 5.0

    def set_face_shadow_texture(self, face_material, img):
        # V1/V2 - Node
        face_shadow_node = face_material.node_tree.nodes.get('Face_Shadow')
        if face_shadow_node:
            img.colorspace_settings.name='Non-Color'
            face_material.node_tree.nodes['Face_Shadow'].image = img

        # V4 - Node Group
        texture_node_names = self.shader_identifier_service.get_shader_texture_node_names(self.genshin_shader_version)
        face_shadow_map_node_group = bpy.data.node_groups.get(texture_node_names.FACE_SHADOW_MAP_NODE_GROUP)

        if face_shadow_map_node_group:
            img.colorspace_settings.name='Non-Color'
            face_shadow_map_node_group.nodes[texture_node_names.FACE_SHADOW_MAP].image = img


    def set_face_lightmap_texture(self, img):
        # Genshin Impact Shader V1/V2/V4
        texture_node_names = self.shader_identifier_service.get_shader_texture_node_names(self.genshin_shader_version)
        face_lightmap_node_group = bpy.data.node_groups.get(texture_node_names.FACE_LIGHTMAP_NODE_GROUP)

        if face_lightmap_node_group:
            img.colorspace_settings.name='Non-Color'
            face_lightmap_node_group.nodes[texture_node_names.FACE_LIGHTMAP].image = img

    def set_metalmap_texture(self, img):
        metallic_matcap_node_exists = bpy.data.node_groups.get('Metallic Matcap')

        if metallic_matcap_node_exists:
            bpy.data.node_groups['Metallic Matcap'].nodes['MetalMap'].image = img

    def set_glass_diffuse_texture(self, material, img):
        diffuse_node = material.node_tree.nodes.get('Main_Diffuse') 
        vfx_node = material.node_tree.nodes.get(V4_GenshinImpactTextureNodeNames.VFX_DIFFUSE)

        nodes = [diffuse_node, vfx_node]
        for node in nodes:
            if material and node:
                node.image = img

    def set_nyx_color_ramp_texture(self, img):
        possible_nyx_color_ramp_node_group_names = [
            V4_GenshinImpactTextureNodeNames.SHADER_TEXTURES_NODE_GROUP,
        ]
        for nyx_color_ramp_node_group_name in possible_nyx_color_ramp_node_group_names:
            nyx_color_ramp_node_group = bpy.data.node_groups.get(nyx_color_ramp_node_group_name)
            if nyx_color_ramp_node_group:
                nyx_color_ramp_node = nyx_color_ramp_node_group.nodes.get(V4_GenshinImpactTextureNodeNames.NYX_COLOR_RAMP)
                if nyx_color_ramp_node:
                    nyx_color_ramp_node.image = img

    def set_up_night_soul_mask_texture(self, material, img):
        if material and material.node_tree and material.node_tree.nodes:
            texture_node_names = self.shader_identifier_service.get_shader_texture_node_names(self.genshin_shader_version)
            night_soul_mask_texture_node = material.node_tree.nodes.get(texture_node_names.NIGHT_SOUL_MASK) or \
                material.node_tree.nodes.get(texture_node_names.FACE_NIGHT_SOUL_MASK)

            if night_soul_mask_texture_node:
                night_soul_mask_texture_node.image = img

    def set_up_night_soul_outlines_material(self):
        night_soul_outline_material = self.create_night_soul_outlines()
        if not night_soul_outline_material:
            return None
        shader_node_names: ShaderNodeNames = self.shader_identifier_service.get_shader_node_names(self.genshin_shader_version)

        body_shader = night_soul_outline_material.node_tree.nodes[shader_node_names.BODY_SHADER]
        output = body_shader.outputs.get(shader_node_names.NIGHT_SOUL_OUTPUT)
        input = night_soul_outline_material.node_tree.nodes.get(shader_node_names.MATERIAL_OUTPUT_NODE).inputs.get(shader_node_names.MATERIAL_OUTPUT_SHADER_INPUT)
        night_soul_outline_material.node_tree.links.new(output, input)
        night_soul_outline_material.use_screen_refraction = True

    def create_night_soul_outlines(self):
        shader_material_names: ShaderMaterialNames = self.shader_identifier_service.get_shader_material_names_using_shader(self.genshin_shader_version)
        outline_material = bpy.data.materials.get(shader_material_names.OUTLINES)
        if not shader_material_names.NIGHT_SOUL_OUTLINES:
            return None
        night_soul_outlines_material = bpy.data.materials.get(shader_material_names.NIGHT_SOUL_OUTLINES)
        if not night_soul_outlines_material:
            night_soul_outlines_material = outline_material.copy()
            night_soul_outlines_material.name = shader_material_names.NIGHT_SOUL_OUTLINES
            night_soul_outlines_material.use_fake_user = True
        return night_soul_outlines_material

    def setup_dress_textures(self, texture_name, texture_img, character_type: TextureImporterType):
        shader_dress_materials = [material for material in bpy.data.materials if 
                                  'Genshin Dress' in material.name and 'Outlines' not in material.name]
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
            if actual_cloak_material in texture_img.name:
                material_shader_nodes = bpy.data.materials.get(shader_cloak_materials[0].name).node_tree.nodes
                if material_shader_nodes.get(texture_name):
                    material_shader_nodes.get(texture_name).image = texture_img

        for shader_dress_material in shader_dress_materials:
            original_dress_material = self.get_original_dress_material(shader_dress_material)
            if not original_dress_material:
                print(f'ERROR: Could not find original dress material for "{shader_dress_material.name}", skipping texture import')
                return

            if character_type == TextureImporterType.MONSTER:
                actual_material = OriginalTextureLocatorUtils.get_monster_original_texture_part(original_dress_material)
            else:
                actual_material = get_actual_material_name_for_dress(original_dress_material.name, character_type.name)
            if actual_material in texture_img.name:
                print(f'Importing texture "{texture_name}" onto material "{shader_dress_material.name}"')
                material_shader_nodes = bpy.data.materials.get(shader_dress_material.name).node_tree.nodes
                if material_shader_nodes.get(texture_name):
                    material_shader_nodes.get(texture_name).image = texture_img
                return

    def get_original_dress_material(self, shader_dress_material):
        for material in bpy.data.materials:
            is_not_original_material = material.name.startswith(self.material_names.MATERIAL_PREFIX)
            if is_not_original_material:
                continue

            is_playable_character_original_material = material.name.endswith(shader_dress_material.name.split(' ')[-1])
            # ex. 'Monster_Fatuus_Agent_01_Fire_Dress_Mat' and 'HoYoverse - Genshin Dress'
            # ex. 'Monster_Eremite_Male_Strong_Katar_01_Rock_Dress_Mat' and 'HoYoverse - Genshin Dress'
            is_npc_original_material = len(material.name.split('_')) > 2 and material.name.split('_')[-2].endswith(shader_dress_material.name.split(' ')[-1])

            if is_playable_character_original_material or is_npc_original_material:
                return material  # material that ends with 'Dress', 'Dress1', 'Dress2'

    def does_dress_texture_exist_in_directory_files(self):
        dress_texture_detected = False
        for file in self.files:
            if 'Dress' in file and '.png' in file:
                dress_texture_detected = True
        return dress_texture_detected

    def set_face_material_id(self, face_material, image):
        character_to_face_material_id_map = {
            'Collei': 5,
            'Cyno': 3,
            'DilucCostumeFlamme': 3,
            'Faruzan': 3,
            'AyakaCostumeFruhling': 5,
            'Ayato': 3,
            'KleeCostumeWitch': 3,
            'Linette': 3,  # Lynette
            'Liney': 3,  # Lyney
            'Nilou': 3,
            'Kokomi': 3,
            'Tighnari': 3,
            'Yelan': 3,
        }

        shader_has_face_material_id = self.genshin_shader_version is GenshinImpactShaders.V2_GENSHIN_IMPACT_SHADER

        # No longer a field in V3 shader
        if shader_has_face_material_id:
            for character_name in character_to_face_material_id_map.keys():
                if character_name in image.name:
                    shader_node_names = self.shader_identifier_service.get_shader_node_names(self.genshin_shader_version)
                    if face_material.node_tree.nodes.get(shader_node_names.FACE_SHADER):
                        face_shader_node = face_material.node_tree.nodes[shader_node_names.FACE_SHADER]
                        face_shader_node.inputs[shader_node_names.FACE_MATERIAL_ID].default_value = \
                            character_to_face_material_id_map[character_name]

    def set_body_hair_output_on_face_shader(self, face_material, image):
        characters_needing_hair_output = [
            'Funingna',  # Furina
        ]

        shader_has_body_hair_output = self.genshin_shader_version is GenshinImpactShaders.V2_GENSHIN_IMPACT_SHADER

        if shader_has_body_hair_output:
            for character_name in characters_needing_hair_output:
                shader_node_names = self.shader_identifier_service.get_shader_node_names(self.genshin_shader_version)
                if character_name in image.name and face_material.node_tree.nodes.get(shader_node_names.FACE_SHADER):
                    face_shader_node = face_material.node_tree.nodes[shader_node_names.FACE_SHADER]
                    face_shader_node_hair_output = face_shader_node.outputs.get('Hair')

                    depth_based_rim_node = face_material.node_tree.nodes.get(shader_node_names.DEPTH_BASED_RIM)
                    is_depth_based_rim_node = depth_based_rim_node and depth_based_rim_node.inputs.get('Lit Factor')

                    if is_depth_based_rim_node:
                        depth_based_rim_node_input = depth_based_rim_node.inputs.get('Input')
                        face_material.node_tree.links.new(
                            face_shader_node_hair_output,
                            depth_based_rim_node_input
                        )
                    else:
                        material_output_node = face_material.node_tree.nodes.get('Material Output')
                        material_output_node_surface_input = material_output_node.inputs.get('Surface')
                        face_material.node_tree.links.new(
                            face_shader_node_hair_output,
                            material_output_node_surface_input
                        )

    def star_cloak_uses_body_texture(self, file):
        texture_name_identifiers = [
            'Dainslaif',
        ]
        for identifier in texture_name_identifiers:
            if identifier in file:
                return True
        return False

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

    def set_stocking_texture(self, img):
        possible_shadow_ramp_node_group_names = [
            V4_GenshinImpactTextureNodeNames.SHADER_TEXTURES_NODE_GROUP,
        ]
        for shadow_ramp_node_name in possible_shadow_ramp_node_group_names:
            shadow_ramp_node_group = bpy.data.node_groups.get(shadow_ramp_node_name)
            if shadow_ramp_node_group:
                shader_node_names = self.shader_identifier_service.get_shader_node_names(self.genshin_shader_version)
                img.colorspace_settings.name='Non-Color'
                shadow_ramp_node_group.nodes[shader_node_names.STOCKINGS_DETAIL].image = img


class GenshinAvatarTextureImporter(GenshinTextureImporter):
    def __init__(self, material_names: ShaderMaterialNames):
        super().__init__(GameType.GENSHIN_IMPACT, TextureImporterType.AVATAR)
        self.material_names = material_names

        self.shader_identifier_service = ShaderIdentifierServiceFactory.create(GameType.GENSHIN_IMPACT.name)
        self.genshin_shader_version = self.shader_identifier_service.identify_shader(bpy.data.materials, bpy.data.node_groups)

    def import_textures(self, directory):
        for folder_name, folder, files in os.walk(directory):
            self.files = files
            for file in files:
                if not self.is_supported_texture(file):
                    continue
                # load the file with the correct alpha mode
                img_path = folder_name + "/" + file
                img = bpy.data.images.load(filepath = img_path, check_existing=True)
                img.alpha_mode = 'CHANNEL_PACKED'

                effect_hair_material = bpy.data.materials.get(f'{self.material_names.EFFECT_HAIR}') or \
                    bpy.data.materials.get(f'{self.material_names.EFFECT}')
                hair_material = bpy.data.materials.get(f'{self.material_names.HAIR}')
                helmet_material = bpy.data.materials.get(f'{self.material_names.HELMET}')
                helmet_emotion_material = bpy.data.materials.get(f'{self.material_names.HELMET_EMO}')
                face_material = bpy.data.materials.get(f'{self.material_names.FACE}')
                body_material = bpy.data.materials.get(f'{self.material_names.BODY}')
                body1_material = bpy.data.materials.get(f'{self.material_names.BODY1}')
                body2_material = bpy.data.materials.get(f'{self.material_names.BODY2}')
                dress_material = bpy.data.materials.get(f'{self.material_names.DRESS}')
                dress2_material = bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}Dress2')
                gauntlet_material = bpy.data.materials.get(f'{self.material_names.GAUNTLET}')
                glass_material = bpy.data.materials.get(f'{self.material_names.GLASS}')
                glass_eff_material = bpy.data.materials.get(f'{self.material_names.GLASS_EFF}')
                leather_material = bpy.data.materials.get(f'{self.material_names.LEATHER}')
                pupil_material = bpy.data.materials.get(f'{self.material_names.PUPIL}')
                skirt_material = bpy.data.materials.get(f'{self.material_names.SKIRT}')
                star_cloak_material = bpy.data.materials.get(f'{self.material_names.STAR_CLOAK}')

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
                elif self.is_texture_identifiers_in_texture_name([ShaderMaterialNameKeywords.HAIR, ShaderMaterialNameKeywords.NORMAL_MAP], file):
                    self.set_normalmap_texture(TextureType.HAIR, hair_material, img)
                elif "Hair_Shadow_Ramp" in file:
                    self.set_shadow_ramp_texture(TextureType.HAIR, img)
                elif self.is_one_texture_identifier_in_texture_name(
                    [
                        ShaderMaterialNameKeywords.BODY_DIFFUSE, 
                        ShaderMaterialNameKeywords.BODY1_DIFFUSE, 
                        ShaderMaterialNameKeywords.BODY2_DIFFUSE, 
                    ], file):
                    selected_body_material = \
                        body_material if ShaderMaterialNameKeywords.BODY_DIFFUSE in file else \
                        body1_material if ShaderMaterialNameKeywords.BODY1_DIFFUSE in file else \
                        body2_material if ShaderMaterialNameKeywords.BODY2_DIFFUSE in file else body_material
                    self.set_diffuse_texture(TextureType.BODY, selected_body_material, img)
                    # Set Face Id in Body_Diffuse because not all Face Diffuse filenames have the full costume name
                    # Ex. Diluc's costume does not have DilucCostumeFlamme, but just Diluc
                    self.set_face_material_id(face_material, img)
                    self.set_body_hair_output_on_face_shader(face_material, img)
                    self.set_diffuse_texture(TextureType.BODY, leather_material, img) if leather_material else None
                    self.set_diffuse_texture(TextureType.BODY, pupil_material, img) if pupil_material and selected_body_material is body1_material else None
                    if star_cloak_material and self.star_cloak_uses_body_texture(file):
                        self.set_diffuse_texture(TextureType.BODY, star_cloak_material, img)
                elif self.is_one_texture_identifier_in_texture_name(
                    [
                        ShaderMaterialNameKeywords.BODY_LIGHTMAP, 
                        ShaderMaterialNameKeywords.BODY1_LIGHTMAP, 
                        ShaderMaterialNameKeywords.BODY2_LIGHTMAP, 
                    ], file):
                    selected_body_material = \
                        body_material if ShaderMaterialNameKeywords.BODY_LIGHTMAP in file else \
                        body1_material if ShaderMaterialNameKeywords.BODY1_LIGHTMAP in file else \
                        body2_material if ShaderMaterialNameKeywords.BODY2_LIGHTMAP in file else body_material
                    self.set_lightmap_texture(TextureType.BODY, selected_body_material, img)
                    self.set_lightmap_texture(TextureType.BODY, leather_material, img) if leather_material else None
                    self.set_lightmap_texture(TextureType.BODY, pupil_material, img) if pupil_material and selected_body_material is body1_material else None
                elif self.is_texture_identifiers_in_texture_name([ShaderMaterialNameKeywords.BODY, ShaderMaterialNameKeywords.NORMAL_MAP], file):
                    self.set_normalmap_texture(TextureType.BODY, body_material, img)
                    self.set_normalmap_texture(TextureType.BODY, leather_material, img) if leather_material else None
                elif self.is_one_texture_identifier_in_texture_name(
                    [
                        ShaderMaterialNameKeywords.BODY_SHADOW_RAMP,
                        ShaderMaterialNameKeywords.BODY1_SHADOW_RAMP,
                        ShaderMaterialNameKeywords.BODY2_SHADOW_RAMP,
                    ], file):
                    if ShaderMaterialNameKeywords.BODY2_SHADOW_RAMP in file:
                        self.set_shadow_ramp_texture(TextureType.BODY2, img)
                    else:  # Body/Body1
                        self.set_shadow_ramp_texture(TextureType.BODY, img)
                elif "Body_Specular_Ramp" in file or "Tex_Specular_Ramp" in file:
                    self.set_specular_ramp_texture(TextureType.BODY, img)
                elif "Face_Diffuse" in file:
                    self.set_face_diffuse_texture(face_material, img)
                elif self.is_texture_identifiers_in_texture_name(['Face', 'Shadow'], file):
                    self.set_face_shadow_texture(face_material, img)
                elif self.is_texture_identifiers_in_texture_name(['Face', 'Lightmap'], file):
                    self.set_face_lightmap_texture(img)
                elif "MetalMap" in file:
                    self.set_metalmap_texture(img)
                elif self.is_texture_identifiers_in_texture_name(['Glass', 'Diffuse'], file):
                    if glass_material:
                        self.set_glass_diffuse_texture(glass_material, img)
                    if glass_eff_material:
                        self.set_glass_diffuse_texture(glass_eff_material, img)
                elif self.is_texture_identifiers_in_texture_name(['Glass', 'Lightmap'], file):
                    if glass_material:
                        self.set_lightmap_texture(TextureType.BODY, glass_material, img)
                    if glass_eff_material:
                        self.set_lightmap_texture(TextureType.BODY, glass_eff_material, img)
                elif "Gauntlet_Diffuse" in file:
                    self.set_diffuse_texture(TextureType.BODY, gauntlet_material, img)
                elif "Gauntlet_Ligntmap" in file:
                    self.set_lightmap_texture(TextureType.BODY, gauntlet_material, img)
                elif "Gauntlet_Normalmap" in file:
                    self.set_normalmap_texture(TextureType.BODY, gauntlet_material, img)
                elif self.is_texture_identifiers_in_texture_name([ShaderMaterialNameKeywords.TAIL, 'Diffuse'], file):
                    if skirt_material:
                        self.set_diffuse_texture(TextureType.BODY, skirt_material, img)
                elif self.is_texture_identifiers_in_texture_name([ShaderMaterialNameKeywords.SKILLOBJ, 'Diffuse'], file):
                    expected_skillobj_identifier = file.split('_')[2]
                    skillobj_material = bpy.data.materials.get(f'{self.material_names.SKILLOBJ} {expected_skillobj_identifier}')
                    if skillobj_material:
                        self.set_diffuse_texture(TextureType.BODY, skillobj_material, img)
                elif self.is_texture_identifiers_in_texture_name([ShaderMaterialNameKeywords.SKILLOBJ, 'Lightmap'], file):
                    expected_skillobj_identifier = file.split('_')[2]
                    skillobj_material = bpy.data.materials.get(f'{self.material_names.SKILLOBJ} {expected_skillobj_identifier}')
                    if skillobj_material:
                        self.set_lightmap_texture(TextureType.BODY, skillobj_material, img)
                elif "Effect_Diffuse" in file:  # keep at bottom as a last resort check (Skirk support)
                    if star_cloak_material:
                        self.set_diffuse_texture(TextureType.HAIR, star_cloak_material, img)
                    else:  # backwards compatible before VFX shader existed, pre-v4.0
                        self.set_diffuse_texture(TextureType.HAIR, dress2_material, img)
                elif "Effect_Lightmap" in file:  # keep at bottom as a last resort check (Skirk support)
                    if star_cloak_material:  # No lightmap texture node as of this commit
                        self.set_lightmap_texture(TextureType.HAIR, star_cloak_material, img)
                    else:  # backwards compatible before VFX shader existed, pre-v4.0
                        self.set_lightmap_texture(TextureType.HAIR, dress2_material, img)
                elif "Dress_Diffuse" in file:
                    if dress_material:
                        self.set_diffuse_texture(TextureType.BODY, dress_material, img)
                elif "Dress_Lightmap" in file:
                    if dress_material:
                        self.set_lightmap_texture(TextureType.BODY, dress_material, img)
                elif self.is_one_texture_identifier_in_texture_name([  # Nyx Color Ramp
                    "NyxState_Ramp",
                    "Nyx_Ramp",
                    "Tex_Ramp"
                ], file):
                    self.set_nyx_color_ramp_texture(img)
                    self.set_up_night_soul_outlines_material()
                elif self.is_texture_identifiers_in_texture_name(ShaderMaterialNameKeywords.NIGHT_SOUL_MASK_IDENTIFIERS, file):
                    for material in bpy.data.materials.values():
                        self.set_up_night_soul_mask_texture(material, img)
                elif self.is_texture_identifiers_in_texture_name([ShaderMaterialNameKeywords.STOCKINGS_DETAILMAP], file):
                    self.set_stocking_texture(img)
                else:
                    print(f'WARN: Ignoring texture {file}')
            # TODO: Investiate this some more and see if we can implement this across all TexureImporters
            # Walk through all folders as textures could exist in a separate Textures folder
            # break  # IMPORTANT: We os.walk which also traverses through folders...we just want the files


class GenshinNPCTextureImporter(GenshinTextureImporter):
    def __init__(self, material_names: ShaderMaterialNames):
        super().__init__(GameType.GENSHIN_IMPACT, TextureImporterType.NPC)
        self.material_names = material_names

        self.shader_identifier_service = ShaderIdentifierServiceFactory.create(GameType.GENSHIN_IMPACT.name)
        self.genshin_shader_version = self.shader_identifier_service.identify_shader(bpy.data.materials, bpy.data.node_groups)
        self.shader_material_names = self.shader_identifier_service.get_shader_material_names_using_shader(self.genshin_shader_version)

    def import_textures(self, directory):
        for name, folder, files in os.walk(directory):
            self.files = files
            for file in files:
                if not self.is_supported_texture(file):
                    continue
                # load the file with the correct alpha mode
                img_path = directory + "/" + file
                img = bpy.data.images.load(filepath = img_path, check_existing=True)
                img.alpha_mode = 'CHANNEL_PACKED'

                hair_material = bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}Hair')
                face_material = bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}Face')
                body_material = bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}Body')
                star_cloak_material = bpy.data.materials.get(f'{self.material_names.STAR_CLOAK}')

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

                elif self.is_texture_identifiers_in_texture_name(['Cloak', 'Diffuse'], file):  # Paimon - VFX support
                    if star_cloak_material:
                        self.set_diffuse_texture(TextureType.HAIR, star_cloak_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Item', 'Diffuse'], file):
                    # Remove the '_Mat' suffix on materials and the MATERIAL_PREFIX, then search if it matches the texture filename
                    item_materials = [material for material in bpy.data.materials if 
                                      material.name.split('_Mat')[0].replace(self.shader_material_names.MATERIAL_PREFIX, '') in file]
                    if item_materials:
                        item_material = item_materials[0]
                        self.set_diffuse_texture(TextureType.BODY, item_material, img)
                elif self.is_texture_identifiers_in_texture_name(['Item', 'Lightmap'], file):
                    # Remove the '_Mat' suffix on materials and the MATERIAL_PREFIX, then search if it matches the texture filename
                    item_materials = [material for material in bpy.data.materials if 
                                      material.name.split('_Mat')[0].replace(self.shader_material_names.MATERIAL_PREFIX, '') in file]
                    if item_materials:
                        item_material = item_materials[0]
                        self.set_lightmap_texture(TextureType.BODY, item_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Hat', 'Diffuse'], file):
                    hat_materials = [material for material in bpy.data.materials if 'Hat' in material.name and 
                                     self.shader_material_names.MATERIAL_PREFIX in material.name]
                    if hat_materials:
                        hat_material = hat_materials[0]
                        self.set_diffuse_texture(TextureType.BODY, hat_material, img)
                elif self.is_texture_identifiers_in_texture_name(['Hat', 'Lightmap'], file):
                    hat_materials = [material for material in bpy.data.materials if 'Hat' in material.name and 
                                     self.shader_material_names.MATERIAL_PREFIX in material.name]
                    if hat_materials:
                        hat_material = hat_materials[0]
                        self.set_lightmap_texture(TextureType.BODY, hat_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Screw', 'Diffuse'], file):
                    screw_materials = [material for material in bpy.data.materials if 'Screw' in material.name and 
                                     self.shader_material_names.MATERIAL_PREFIX in material.name]
                    if screw_materials:
                        screw_material = screw_materials[0]
                        self.set_diffuse_texture(TextureType.BODY, screw_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Screw', 'Lightmap'], file):
                    screw_materials = [material for material in bpy.data.materials if 'Screw' in material.name and 
                                     self.shader_material_names.MATERIAL_PREFIX in material.name]
                    if screw_materials:
                        screw_material = screw_materials[0]
                        self.set_lightmap_texture(TextureType.BODY, screw_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Others', 'Diffuse'], file):
                    others_materials = [material for material in bpy.data.materials if 'Others' in material.name and 
                                     self.shader_material_names.MATERIAL_PREFIX in material.name]
                    if others_materials:
                        others_material = others_materials[0]
                        self.set_diffuse_texture(TextureType.BODY, others_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Others', 'Lightmap'], file):
                    others_materials = [material for material in bpy.data.materials if 'Others' in material.name and 
                                     self.shader_material_names.MATERIAL_PREFIX in material.name]
                    if others_materials:
                        others_material = others_materials[0]
                        self.set_lightmap_texture(TextureType.BODY, others_material, img)

                else:
                    print(f'WARN: Ignoring texture {file}')
            # break  # IMPORTANT: We os.walk which also traverses through folders...we just want the files


class GenshinMonsterTextureImporter(GenshinTextureImporter):
    def __init__(self, material_names: ShaderMaterialNames):
        super().__init__(GameType.GENSHIN_IMPACT, TextureImporterType.MONSTER)
        self.material_names = material_names

        self.shader_identifier_service = ShaderIdentifierServiceFactory.create(GameType.GENSHIN_IMPACT.name)
        self.genshin_shader_version = self.shader_identifier_service.identify_shader(bpy.data.materials, bpy.data.node_groups)

    def import_textures(self, directory):
        for name, folder, files in os.walk(directory):
            self.files = files
            for file in files:
                if not self.is_supported_texture(file):
                    continue
                # load the file with the correct alpha mode
                img_path = directory + "/" + file
                img = bpy.data.images.load(filepath = img_path, check_existing=True)
                img.alpha_mode = 'CHANNEL_PACKED'

                hair_material = bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}Hair')
                face_material = bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}Face')
                body_material = bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}Body')
                star_cloak_material = bpy.data.materials.get(f'{self.material_names.STAR_CLOAK}')

                # Implement the texture in the correct node
                print(f'Importing texture {file} using {self.__class__.__name__}')

                if self.is_texture_identifiers_in_texture_name(['Body', 'Tex', 'Diffuse'], file) or \
                    (self.is_texture_identifiers_in_texture_name(['Tex', 'Diffuse'], file) and \
                    not self.is_texture_identifiers_in_files(['Hair'], files)):
                    self.set_diffuse_texture(TextureType.BODY, body_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Body', 'Tex', 'Lightmap'], file) or \
                    (self.is_texture_identifiers_in_texture_name(['Tex', 'Lightmap'], file) and \
                    not self.is_texture_identifiers_in_files(['Hair'], files)):
                    self.set_lightmap_texture(TextureType.BODY, body_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Hair', 'Tex', 'Diffuse'], file) or \
                    (self.is_texture_identifiers_in_texture_name(['Tex', 'Diffuse'], file) and \
                    not self.is_texture_identifiers_in_files(['Body'], files)):
                    self.set_diffuse_texture(TextureType.HAIR, hair_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Hair', 'Tex', 'Lightmap'], file) or \
                    (self.is_texture_identifiers_in_texture_name(['Tex', 'Lightmap'], file) and \
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

                elif self.is_texture_identifiers_in_texture_name(['Hand', 'Tex', 'Eff'], file):  # Asmoday - VFX Support
                    self.set_diffuse_texture(TextureType.BODY, star_cloak_material, img)

                else:
                    print(f'WARN: Ignoring texture {file}')
            # break  # IMPORTANT: We os.walk which also traverses through folders...we just want the files


class HonkaiStarRailTextureImporter(GenshinTextureImporter):
    def __init__(self, game_type: GameType, character_type: TextureImporterType, material_names: ShaderMaterialNames, texture_node_names: TextureNodeNames):
        super().__init__(game_type, character_type)
        self.material_names = material_names
        self.texture_node_names: TextureNodeNames = texture_node_names

    '''
    Lazy attempt at setting all known diffuses across Nya222 HSR Shader and StellarToon
    If the material has the texture node, set it.
    '''
    def set_diffuse_texture(self, type: TextureType, material, img):
        nya222_or_outline_diffuse_node = material.node_tree.nodes.get(self.texture_node_names.DIFFUSE)
        diffuse_uv0_node = material.node_tree.nodes.get(f'{type.value}{self.texture_node_names.DIFFUSE_UV0_SUFFIX}')
        diffuse_uv1_node = material.node_tree.nodes.get(f'{type.value}{self.texture_node_names.DIFFUSE_UV1_SUFFIX}')
        face_color_node = material.node_tree.nodes.get(f'{type.value}{self.texture_node_names.FACE_COLOR_SUFFIX}')
        
        for diffuse_node in [nya222_or_outline_diffuse_node, diffuse_uv0_node, diffuse_uv1_node, face_color_node]:
            if diffuse_node:
                diffuse_node.image = img

    '''
    Lazy attempt at setting all known lightmaps across Nya222 HSR Shader and StellarToon.
    If the material has the texture node, set it.
    '''
    def set_lightmap_texture(self, type: TextureType, material, img):
        img.colorspace_settings.name='Non-Color'
        lightmap_nya222_node = material.node_tree.nodes.get(self.texture_node_names.LIGHTMAP)
        lightmap_uv0_node = material.node_tree.nodes.get(f'{type.value}{self.texture_node_names.LIGHTMAP_UV0_SUFFIX}')
        lightmap_uv1_node = material.node_tree.nodes.get(f'{type.value}{self.texture_node_names.LIGHTMAP_UV1_SUFFIX}')

        for lightmap_node in [lightmap_nya222_node, lightmap_uv0_node, lightmap_uv1_node]:
            if lightmap_node:
                lightmap_node.image = img

    def set_warm_shadow_ramp_texture(self, type: TextureType, img):
        ramp_node_name = \
            self.texture_node_names.BODY_WARM_RAMP if type is TextureType.BODY else \
            self.texture_node_names.HAIR_WARM_RAMP

        ramp_texture_node = bpy.data.node_groups.get(self.texture_node_names.BODY_WARM_RAMP_NODE_GROUP).nodes[ramp_node_name] if \
            type is TextureType.BODY else bpy.data.node_groups.get(self.texture_node_names.HAIR_WARM_RAMP_NODE_GROUP).nodes[ramp_node_name]
        ramp_texture_node.image = img

    def set_cool_shadow_ramp_texture(self, type: TextureType, img):
        if not bpy.data.node_groups.get(self.texture_node_names.BODY_COOL_RAMP_NODE_GROUP) or \
            not bpy.data.node_groups.get(self.texture_node_names.HAIR_COOL_RAMP_NODE_GROUP):
            return

        ramp_node_name = \
            self.texture_node_names.BODY_COOL_RAMP if type is TextureType.BODY else \
            self.texture_node_names.HAIR_COOL_RAMP

        ramp_texture_node = bpy.data.node_groups.get(self.texture_node_names.BODY_COOL_RAMP_NODE_GROUP).nodes[ramp_node_name] if \
            type is TextureType.BODY else bpy.data.node_groups.get(self.texture_node_names.HAIR_COOL_RAMP_NODE_GROUP).nodes[ramp_node_name]
        ramp_texture_node.image = img

    def set_weapon_ramp_texture(self, img, override=False):
        weapon_ramp_node = bpy.data.node_groups[f'{self.texture_node_names.WEAPON_RAMP_NODE_GROUP}'].nodes[
            self.texture_node_names.WEAPON_RAMP
        ]
        
        if override or not weapon_ramp_node.image:
            weapon_ramp_node.image = img

    def set_facemap_texture(self, img):
        img.colorspace_settings.name='Non-Color'
        bpy.data.node_groups[self.texture_node_names.FACE_LIGHTMAP_NODE_GROUP].nodes[
            self.texture_node_names.FACE_LIGHTMAP].image = img

    def set_face_expression_texture(self, face_material, img):
        img.colorspace_settings.name='Non-Color'

        # Nya222 Shader has it inside a node group
        face_expression_node_group = bpy.data.node_groups.get(self.texture_node_names.FACE_EXPRESSION_NODE_GROUP)
        if face_expression_node_group:
            face_expression_node_group.nodes[self.texture_node_names.FACE_EXPRESSION_MAP].image = img
        
        # Stellartoon
        face_expression_node = face_material.node_tree.nodes.get(self.texture_node_names.FACE_EXPRESSION_MAP)
        if face_expression_node:
            face_expression_node.image = img

    def set_stocking_texture(self, type: TextureType, material, img):
        body_material = bpy.data.materials.get(self.material_names.BODY)
        body1_material = bpy.data.materials.get(self.material_names.BODY1)
        body2_material = bpy.data.materials.get(self.material_names.BODY2)
        img.colorspace_settings.name='Non-Color'

        # If Body material or Body1 material apply to Body1 Stockings
        # Else Body2 material or Body Stockings texture with Body1/Body2 materials apply to Body2 Stockings
        if (body_material and material is body_material) or (body1_material and material is body1_material):
            stockings_body1_node_group = bpy.data.node_groups.get(self.texture_node_names.STOCKINGS_BODY1_NODE_GROUP)

            if stockings_body1_node_group:  # Nya222
                stockings_body1_node_group.nodes[self.texture_node_names.STOCKINGS].image = img

            # StellarToon Shader
            self.set_up_stellartoon_stocking_texture(material, img)  # Body or Body1 material
        else:
            stockings_body2_node_group = bpy.data.node_groups.get(self.texture_node_names.STOCKINGS_BODY2_NODE_GROUP)
            if stockings_body2_node_group:  # Nya222
                stockings_body2_node_group.nodes[self.texture_node_names.STOCKINGS].image = img

            # StellarToon Shader
            self.set_up_stellartoon_stocking_texture(body2_material, img)

    def set_up_stellartoon_stocking_texture(self, material, img):
        body_stockings_node = material.node_tree.nodes.get(self.texture_node_names.STOCKINGS)
        body_stockings_node_group = bpy.data.node_groups.get(self.texture_node_names.STOCKINGS_NODE_GROUP)

        if body_stockings_node:
            body_stockings_node.image = img
            material.node_tree.nodes.get(StellarToonShaderNodeNames.BODY_SHADER).inputs.get(
                StellarToonShaderNodeNames.ENABLE_STOCKINGS).default_value = 1.0
        if body_stockings_node_group:
            body_stockings_node_group.nodes[self.texture_node_names.STOCKINGS].image = img

class HonkaiStarRailAvatarTextureImporter(HonkaiStarRailTextureImporter):
    def __init__(self, material_names: ShaderMaterialNames, texture_node_names: TextureNodeNames):
        super().__init__(
            GameType.HONKAI_STAR_RAIL, 
            TextureImporterType.HSR_AVATAR, 
            material_names, 
            texture_node_names
        )
        self.material_names = material_names

    def import_textures(self, directory):
        for name, folder, files in os.walk(directory):
            for file in files:
                if not self.is_supported_texture(file):
                    continue
                # load the file with the correct alpha mode
                img_path = directory + "/" + file
                img = bpy.data.images.load(filepath = img_path, check_existing=True)
                img.alpha_mode = 'CHANNEL_PACKED'

                hair_material = bpy.data.materials.get(self.material_names.HAIR)
                face_material = bpy.data.materials.get(self.material_names.FACE)
                body_material = bpy.data.materials.get(self.material_names.BODY)
                body1_material = bpy.data.materials.get(self.material_names.BODY1)
                body2_material = bpy.data.materials.get(self.material_names.BODY2)
                body3_material = bpy.data.materials.get(self.material_names.BODY3)
                body_trans_material = bpy.data.materials.get(self.material_names.BODY_TRANS)
                body2_trans_material = bpy.data.materials.get(self.material_names.BODY2_TRANS)
                coat_material = bpy.data.materials.get(self.material_names.COAT)
                weapon_material = bpy.data.materials.get(self.material_names.WEAPON)
                weapon1_material = bpy.data.materials.get(self.material_names.WEAPON1)
                weapon01_material = bpy.data.materials.get(self.material_names.WEAPON01)
                weapon02_material = bpy.data.materials.get(self.material_names.WEAPON02)
                weapon_trans_material = bpy.data.materials.get(self.material_names.WEAPON_TRANS)
                weapon_materials = [weapon_material, weapon1_material, weapon01_material, weapon02_material, weapon_trans_material]
                handbag_material = bpy.data.materials.get(self.material_names.HANDBAG)
                kendama_material = bpy.data.materials.get(self.material_names.KENDAMA)

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
                    self.set_cool_shadow_ramp_texture(TextureType.HAIR, img)
                
                # Character has Body and no Body1 or Body2?
                elif self.is_texture_identifiers_in_texture_name(['Body_', 'Color'], file):
                    if body_material:
                        self.set_diffuse_texture(TextureType.BODY, body_material, img)

                    # If NOT Body material, but Body texture, check for Body1/Body2 (Firefly)
                    if not body_material:
                        if body1_material:
                            self.set_diffuse_texture(TextureType.BODY, body1_material, img)
                        if body2_material:
                            self.set_diffuse_texture(TextureType.BODY, body2_material, img)
                        if body2_trans_material:
                            self.set_diffuse_texture(TextureType.BODY, body2_trans_material, img)

                    if body_trans_material:
                        self.set_diffuse_texture(TextureType.BODY, body_trans_material, img)

                # Character has Body and no Body1 or Body2?
                elif self.is_texture_identifiers_in_texture_name(['Body_', 'LightMap'], file):
                    if body_material:
                        self.set_lightmap_texture(TextureType.BODY, body_material, img)

                    # If NOT Body material, but Body texture, check for Body1/Body2 (Firefly)
                    if not body_material:
                        if body1_material:
                            self.set_lightmap_texture(TextureType.BODY, body1_material, img)
                        if body2_material:
                            self.set_lightmap_texture(TextureType.BODY, body2_material, img)
                        if body2_trans_material:
                            self.set_lightmap_texture(TextureType.BODY, body2_trans_material, img)

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

                elif (self.is_texture_identifiers_in_texture_name(['Warm_Ramp'], file) or \
                    self.is_texture_identifiers_in_texture_name(['Body_Ramp'], file)) and \
                        not self.is_texture_identifiers_in_texture_name(['Weapon'], file):  # Not Hair, so ramp must be Body
                    self.set_warm_shadow_ramp_texture(TextureType.BODY, img)
                    self.set_weapon_ramp_texture(img)

                # Not Hair, so ramp must be Body
                elif self.is_texture_identifiers_in_texture_name(['Cool_Ramp'], file):
                    self.set_cool_shadow_ramp_texture(TextureType.BODY, img)

                # Not Hair, so ramp must be Body. Only one ramp texture exists (no specific Warm or Cool ramp)
                # TODO: Unknown uses, previously this was to handle Svarog, but was updated)
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

                elif self.is_texture_identifiers_in_texture_name(['Coat', 'Color'], file):
                    self.set_diffuse_texture(TextureType.BODY, coat_material, img)
                elif self.is_texture_identifiers_in_texture_name(['Coat', 'LightMap'], file):
                    self.set_lightmap_texture(TextureType.BODY, coat_material, img)

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

                elif self.is_texture_identifiers_in_texture_name(['Weapon', 'Color'], file) and \
                    not self.is_texture_identifiers_in_texture_name(['Screen'], file):  # Pela, Silverwolf
                    for weapon_material in weapon_materials:
                        if weapon_material:
                            self.set_diffuse_texture(TextureType.WEAPON, weapon_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Weapon', 'LightMap'], file) or \
                    self.is_texture_identifiers_in_texture_name(['Weapon', 'LigthMap'], file):  # Yes, intentional typo (Asta)

                    for weapon_material in weapon_materials:
                        if weapon_material:
                            self.set_lightmap_texture(TextureType.WEAPON, weapon_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Weapon', 'Ramp'], file):
                    # Set Weapon Ramp, if none exists use Body Ramp
                    self.set_weapon_ramp_texture(img, override=True)

                elif self.is_texture_identifiers_in_texture_name(['Handbag', 'Color'], file):
                    self.set_diffuse_texture(TextureType.WEAPON, handbag_material, img)
                
                elif self.is_texture_identifiers_in_texture_name(['Handbag', 'Lightmap'], file):
                    self.set_lightmap_texture(TextureType.WEAPON, handbag_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Kendama', 'Color'], file):
                    self.set_diffuse_texture(TextureType.WEAPON, kendama_material, img)

                elif self.is_texture_identifiers_in_texture_name(['Kendama', 'Lightmap'], file):
                    self.set_lightmap_texture(TextureType.WEAPON, kendama_material, img)

                # Fallback, best guess attempt by assigning the texture to materials containing the texture name
                elif self.is_texture_identifiers_in_texture_name(['Color'], file):
                    try:
                        body_part = file.split('_')[3]
                        body_part_materials = [material for material in bpy.data.materials if body_part in material.name]
                        for body_part_material in body_part_materials:
                            self.set_diffuse_texture(TextureType.BODY, body_part_material, img)
                    except IndexError:
                        print(f'WARN: Unexpected format when trying fallback texture assignment on: {file}')
                elif self.is_texture_identifiers_in_texture_name(['LightMap'], file):
                    try:
                        body_part = file.split('_')[3]
                        body_part_materials = [material for material in bpy.data.materials if body_part in material.name]
                        for body_part_material in body_part_materials:
                            self.set_lightmap_texture(TextureType.BODY, body_part_material, img)
                    except IndexError:
                        print(f'WARN: Unexpected format when trying fallback texture assignment on: {file}')

                else:
                    print(f'WARN: Ignoring texture {file}')
            # break  # IMPORTANT: We os.walk which also traverses through folders...we just want the files


class PunishingGrayRavenTextureImporter(GenshinTextureImporter):
    def __init__(self, game_type: GameType, character_type: TextureImporterType, texture_node_names: TextureNodeNames):
        super().__init__(game_type, character_type)
        self.texture_node_names: TextureNodeNames = texture_node_names

    def set_diffuse_texture(self, type: TextureType, material, img, override=False):
        img.colorspace_settings.name = 'sRGB'

        if type is TextureType.FACE:
            texture_image = material.node_tree.nodes[self.texture_node_names.FACE_DIFFUSE].image
            if texture_image and not override:
                return
            material.node_tree.nodes[self.texture_node_names.FACE_DIFFUSE].image = img
        else:
            texture_image = material.node_tree.nodes[self.texture_node_names.DIFFUSE].image
            if texture_image and not override:
                return
            material.node_tree.nodes[self.texture_node_names.DIFFUSE].image = img

    def set_lightmap_texture(self, type: TextureType, material, img):
        img.colorspace_settings.name = 'Non-Color'
        lightmap_node = material.node_tree.nodes.get(self.texture_node_names.LIGHTMAP)

        if lightmap_node:
            lightmap_node.image = img

    def set_pbr_texture(self, type: TextureType, material, img):
        img.colorspace_settings.name = 'Non-Color'
        material.node_tree.nodes.get(self.texture_node_names.PBR).image = img

    def set_normalmap_texture(self, type: TextureType, material, img):
        img.colorspace_settings.name = 'Non-Color'
        normal_map_node = material.node_tree.nodes.get(self.texture_node_names.NORMALMAP)

        if normal_map_node:
            normal_map_node.image = img

    def set_lut_texture(self, type: TextureType, material, img):
        if type is TextureType.FACE:
            lut_node = material.node_tree.nodes.get(self.texture_node_names.FACE_LUT)
        else:
            lut_node = material.node_tree.nodes.get(self.texture_node_names.LUT)

        if lut_node:
            lut_node.image = img
            shader_node_name = JaredNyts_PunishingGrayRavenNodeNames.FACE_SHADER if type is TextureType.FACE else \
                JaredNyts_PunishingGrayRavenNodeNames.MAIN_SHADER
            if type is not TextureType.FACE:  # TODO: Something is wrong when LUT enabled on face
                self.set_lut_value(material, shader_node_name, True)

    def set_lut_value(self, material, shader_node_name, enabled):
        lut_value = 1.0 if enabled else 0.0

        material.node_tree.nodes.get(shader_node_name) \
            .inputs.get(JaredNyts_PunishingGrayRavenNodeNames.USE_LUT).default_value = lut_value

    def set_eye_diffuse_texture(self, material, img):
        eye_node = material.node_tree.nodes.get(self.texture_node_names.EYE)

        if eye_node:
            eye_node.image = img

    def set_face_heao_texture(self, img):
        face_heao_node = bpy.data.node_groups.get(self.texture_node_names.FACE_HEAO_NODE_GROUP)

        if face_heao_node:
            img.colorspace_settings.name = 'Non-Color'
            face_heao_node.nodes.get(self.texture_node_names.FACE_HEAO).image = img

    def set_metalmap_texture(self, img):
        metallic_matcap_node = bpy.data.node_groups.get(self.texture_node_names.METALLIC_MATCAP_NODE_GROUP)

        if metallic_matcap_node:
            metallic_matcap_node.nodes[self.texture_node_names.METALLIC_MATCAP].image = img


class PunishingGrayRavenAvatarTextureImporter(PunishingGrayRavenTextureImporter):
    def __init__(self, material_names: ShaderMaterialNames, texture_node_names: TextureNodeNames):
        super().__init__(GameType.PUNISHING_GRAY_RAVEN, TextureImporterType.PGR_AVATAR, texture_node_names)
        self.material_names = material_names

        shader_identifier_service = ShaderIdentifierServiceFactory.create(GameType.PUNISHING_GRAY_RAVEN.name)
        self.genshin_shader_version = shader_identifier_service.identify_shader(bpy.data.materials, bpy.data.node_groups)

    def import_textures(self, directory):
        for name, folder, files in os.walk(directory):
            self.files = files
            for file in files:
                if not self.is_supported_texture(file):
                    continue
                # load the file with the correct alpha mode
                img_path = directory + "/" + file
                img = bpy.data.images.load(filepath = img_path, check_existing=True)
                img.alpha_mode = 'CHANNEL_PACKED'

                alpha_material = bpy.data.materials.get(f'{self.material_names.ALPHA}') 
                eye_material = bpy.data.materials.get(f'{self.material_names.EYE}')

                # Implement the texture in the correct node
                print(f'Importing texture {file} using {self.__class__.__name__}')

                # Eyes
                if self.is_texture_identifiers_in_texture_name(['Eye'], file) and \
                    not self.is_one_texture_identifier_in_texture_name(['HET'], file):
                    self.set_eye_diffuse_texture(eye_material, img)

                else:
                    material_identifer_service = PunishingGrayRavenMaterialIdentifierService()
                    texture_body_part_name = material_identifer_service.get_body_part_name(file)

                    if not texture_body_part_name or '.fbx' in file or 'Mt4Ejector' in file or 'Mb1Motor' in file or \
                        'Mt2Machinehand' in file:
                        continue

                    materials = [material for material in bpy.data.materials if material.name.replace(JaredNytsPunishingGrayRavenShaderMaterialNames.MATERIAL_PREFIX, '') in texture_body_part_name]

                    # Check cases where textures are not prefixed with body part names
                    if not materials:
                        texture_body_part_name = material_identifer_service.search_original_material_user_for_body_part_name(file)
                        if not texture_body_part_name:
                            continue
                        materials = [material for material in bpy.data.materials if material.name.replace(JaredNytsPunishingGrayRavenShaderMaterialNames.MATERIAL_PREFIX, '') in texture_body_part_name]

                    if materials:
                        material = bpy.data.materials.get(max([material.name for material in materials], key=len))
                        body_part_name = material.name.replace(JaredNytsPunishingGrayRavenShaderMaterialNames.MATERIAL_PREFIX, '')
                        img = self.reload_texture(img, img_path)  # reloads only if the texture already exists

                        if 'AO' in file and \
                            not self.is_one_texture_identifier_in_texture_name(['HEAO'], file):
                            if 'Face' in file:
                                self.set_face_heao_texture(img)
                            elif 'Cloth' in body_part_name and 'UV' not in file:
                                cloth_materials = [material for material in bpy.data.materials if 'Cloth' in material.name]
                                for material in cloth_materials:
                                    self.set_lightmap_texture(TextureType.BODY, material, img)
                            else:
                                self.set_lightmap_texture(TextureType.BODY, material, img)
                        elif 'HEAO' in file:
                            if 'Face' in file:
                                self.set_face_heao_texture(img)
                            else:
                                self.set_lightmap_texture(TextureType.BODY, material, img)
                        elif 'NM' in file:
                            self.set_normalmap_texture(TextureType.BODY, material, img)
                        elif 'PBR' in file:
                            self.set_pbr_texture(TextureType.BODY, material, img)
                        elif 'Skin' in file:
                            if 'Face' in file:
                                self.set_lut_texture(TextureType.FACE, material, img)
                            else:
                                self.set_lut_texture(TextureType.BODY, material, img)
                        elif file.endswith(f'{body_part_name}.png'):
                            if 'Face' in file:
                                self.set_diffuse_texture(TextureType.FACE, material, img)
                            else:
                                self.set_diffuse_texture(TextureType.BODY, material, img)
                        else:
                            print(f'WARN: Unexpected texture {file}')
                            if file.endswith(f'{body_part_name}.png') or \
                                material.name == JaredNytsPunishingGrayRavenShaderMaterialNames.XDEFAULTMATERIAL:
                                print(f'WARN: Default setting Diffuse to {material.name}')
                                try:
                                    self.set_diffuse_texture(TextureType.BODY, material, img)
                                except:
                                    pass  # Unexpected or unused textures hit here!
                            elif ('Body' in body_part_name or 'Cloth' in body_part_name) and \
                                not self.is_one_texture_identifier_in_texture_name(['UV', 'MC'], file):
                                print(f'WARN: Default setting Diffuse to {material.name}')
                                try:
                                    fallback_materials = [material for material in bpy.data.materials if
                                                       JaredNytsPunishingGrayRavenShaderMaterialNames.MATERIAL_PREFIX and
                                                       ('Body' in material.name or 'Cloth' in material.name)]
                                    for material in fallback_materials:
                                        self.set_diffuse_texture(TextureType.BODY, material, img)
                                except:
                                    pass  # Unexpected or unused textures hit here!

            # break  # IMPORTANT: We os.walk which also traverses through folders...we just want the files

    # Fix characters with blank textures in their original material texture
    # We do this by deleting the original texture and loading the new texture
    # This happens on characters with textures named the same as their model
    # MUST BE DONE AFTER search_original_material_user_for_body_part_name() is called
    # Ex. Sophia_Silverfang
    def reload_texture(self, img, img_path):
        image_exists = [image for image in bpy.data.images.values() if image.name == img.name]
        if image_exists:
            print(f'Reloading texture! {img}')
            bpy.data.images.remove(image_exists[0])
            img = bpy.data.images.load(filepath = img_path, check_existing=True)
            img.alpha_mode = 'CHANNEL_PACKED'
        return img

class PunishingGrayRavenChibiTextureImporter(PunishingGrayRavenTextureImporter):
    def __init__(self, material_names: ShaderMaterialNames, texture_node_names: TextureNodeNames):
        super().__init__(GameType.PUNISHING_GRAY_RAVEN, TextureImporterType.PGR_CHIBI, texture_node_names)
        self.material_names = material_names

        shader_identifier_service = ShaderIdentifierServiceFactory.create(GameType.PUNISHING_GRAY_RAVEN.name)
        self.genshin_shader_version = shader_identifier_service.identify_shader(bpy.data.materials, bpy.data.node_groups)

    def import_textures(self, directory):
        pass