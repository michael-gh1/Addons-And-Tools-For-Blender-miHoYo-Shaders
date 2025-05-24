
from abc import ABC, abstractmethod
import json
import os
from pathlib import PurePosixPath
from typing import List, Union
import bpy
from bpy.types import Operator, Context, Material

from setup_wizard.domain.body_hair_ramp_switch_values import BodyHairRampSwitchValues
from setup_wizard.logger import log_function
from setup_wizard.domain.material_data_body_part_to_version_map import body_part_based_on_version_map
from setup_wizard.domain.shader_node_names import ShaderNodeNames, V2_GenshinShaderNodeNames, V3_GenshinShaderNodeNames
from setup_wizard.domain.shader_material import ShaderMaterial
from setup_wizard.domain.shader_identifier_service import GenshinImpactShaders, HonkaiStarRailShaders, ShaderIdentifierService, \
    ShaderIdentifierServiceFactory
from setup_wizard.domain.shader_material_names import JaredNytsPunishingGrayRavenShaderMaterialNames, ShaderMaterialNames, StellarToonShaderMaterialNames, V3_BonnyFestivityGenshinImpactMaterialNames, V2_FestivityGenshinImpactMaterialNames, \
    Nya222HonkaiStarRailShaderMaterialNames
from setup_wizard.domain.character_types import CharacterType
from setup_wizard.domain.shader_material_name_keywords import ShaderMaterialNameKeywords

from setup_wizard.domain.game_types import GameType
from setup_wizard.domain.outline_material_data import OutlineMaterialGroup
from setup_wizard.exceptions import UnsupportedMaterialDataJsonFormatException, UserInputException
from setup_wizard.import_order import CHARACTER_MODEL_FOLDER_FILE_PATH, get_cache
from setup_wizard.material_data_import_setup.material_data_applier import MaterialDataApplier, MaterialDataAppliersFactory
from setup_wizard.parsers.material_data_json_parsers import MaterialDataJsonParser, HoyoStudioMaterialDataJsonParser, \
    UABEMaterialDataJsonParser, UnknownHoyoStudioMaterialDataJsonParser
from setup_wizard.utils.genshin_body_part_deducer import get_monster_body_part_name, get_npc_mesh_body_part_name, \
    get_body_part


class MaterialDataFile:
    def __init__(self, filename):
        self.name = filename


class MaterialDataDirectory:
    def __init__(self, exists, file_path, files):
        self.exists = exists
        self.file_path = file_path
        self.files = files


class GameMaterialDataImporter(ABC):
    shader_node_names: ShaderNodeNames
    material_names: ShaderMaterialNames

    @abstractmethod
    def import_material_data(self):
        raise NotImplementedError

    def apply_material_data(self, body_part: str, material_data_appliers: List[MaterialDataApplier], file):
        for material_data_applier in material_data_appliers:
            try:
                material_data_applier.set_up_mesh_material_data()
                material_data_applier.set_up_outline_material_data(body_part, file)
                material_data_applier.set_up_outline_colors()
                print(f'INFO: Successfully applied material data on {material_data_applier.__class__}')
                break  # Important! If a MaterialDataApplier runs successfully, we don't need to try the next version
            except AttributeError as err:
                print(f'WARNING: {err} on {material_data_applier.__class__}')
                print('WARNING: Falling back and trying next version')
                continue # fallback and try next version
            except KeyError as err:
                print(f'WARNING: {err} on {material_data_applier.__class__}')
                print('WARNING: Falling back and trying next version')
                continue # fallback and try next version

    # Originally a "private" method, but moved to public due to inheriting classes
    def get_material_data_json_parser(self, json_material_data):
        for index, parser_class in enumerate(self.parsers):
            try:
                parser: MaterialDataJsonParser  = parser_class(json_material_data)
                parser.parse()
                return parser
            except AttributeError:
                if index == len(self.parsers) - 1:
                    raise UnsupportedMaterialDataJsonFormatException(self.parsers)

    # TOOD: Refactor into own class?
    @staticmethod
    def open_and_load_json_data(directory_file_path, file):
        with open(f'{directory_file_path}/{file.name}') as fp:
            try:
                json_material_data = json.load(fp)
                return json_material_data
            except UnicodeDecodeError:
                raise Exception(f'Failed to load JSON. Did you select a different type of file? \nFile Selected: "{file.name}"')

    @log_function()
    def find_material_and_outline_material_for_body_part(self, body_part) -> Union[Material, Material, Material]:
        # Order of Selection
        # 1. Target Material selected.
        # 2. Shader Materials not renamed (regular setup).
        # 3. Shader Materials renamed. Search for material.
        searched_materials = [material for material in bpy.data.materials.values() if 
                              body_part in material.name and 
                              self.material_names.MATERIAL_PREFIX_AFTER_RENAME in material.name and
                              'Outlines' not in material.name
        ] if body_part else []
        is_not_outlines_material = lambda material: not ShaderMaterial(material, self.shader_node_names).is_outlines_material()
        searched_material = next((material for material in searched_materials if is_not_outlines_material(material)), None)
        material: Material = self.material or bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}{body_part}') or searched_material

        # Order of Selection
        # 1. Outline Material selected.
        # 2. Shader Materials not renamed (regular setup).
        # 3. Shader Materials renamed. Search for material.
        searched_outlines_materials = [material for material in bpy.data.materials.values() if 
                                       body_part in material.name and 
                                       self.material_names.MATERIAL_PREFIX_AFTER_RENAME in material.name and
                                       ' Outlines' in material.name and
                                       not self.material_names.NIGHT_SOUL_OUTLINES_SUFFIX in material.name
        ] if body_part else []
        searched_night_soul_outlines_materials = [material for material in bpy.data.materials.values() if 
                                       body_part in material.name and 
                                       self.material_names.MATERIAL_PREFIX_AFTER_RENAME in material.name and
                                       self.material_names.NIGHT_SOUL_OUTLINES_SUFFIX in material.name
        ] if body_part else []

        # If outlines could not be found, the material name may be too long.
        # Try searching for the outlines material by specific settings in it.
        is_outlines_material = lambda material: ShaderMaterial(material, self.shader_node_names).is_outlines_material()
        if not searched_outlines_materials:
            searched_outlines_materials = [material for material in searched_materials if is_outlines_material(material)] or []
        searched_outlines_material = next(
            (material for material in searched_outlines_materials if is_outlines_material(material)), None
        )
        is_night_soul_outlines_material = lambda material: ShaderMaterial(material, self.shader_node_names).is_outlines_material()
        if not searched_night_soul_outlines_materials:
            searched_night_soul_outlines_materials = [material for material in searched_materials if is_outlines_material(material)] or []
            searched_night_soul_outlines_material = next(
                (material for material in searched_outlines_materials if is_night_soul_outlines_material(material)), None
            )

        outlines_material: Material = self.outlines_material or \
            bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}{body_part} Outlines') or \
            searched_outlines_material
        night_soul_outlines_material: Material = self.outlines_material or \
            bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}{body_part} {self.material_names.NIGHT_SOUL_OUTLINES_SUFFIX}') or \
            searched_night_soul_outlines_material

        return (material, outlines_material, night_soul_outlines_material)

    def get_material_data_files(self):
        # Attempt to use the Material or Materials folder in the cached character folder to import material data json
        # It's possible these folders are in the parent folder for characters with skins, however, it's not possible to
        # easily determine which material data json to apply to the character, so in that scenario,
        # pop-up the File Explorer window and ask the user to select material data json files (old flow)
        cache_enabled = self.context.window_manager.cache_enabled
        character_directory = self.blender_operator.file_directory \
            or get_cache(cache_enabled).get(CHARACTER_MODEL_FOLDER_FILE_PATH) \
            or os.path.dirname(self.blender_operator.filepath)
        character_material_data_directory = os.path.join(character_directory, 'Material')
        character_materials_data_directory = os.path.join(character_directory, 'Materials')
        material_data_directory_exists = os.path.isdir(character_material_data_directory) or \
            os.path.isdir(character_materials_data_directory)
        material_data_directory = character_material_data_directory if os.path.isdir(character_material_data_directory) else \
            character_materials_data_directory if os.path.isdir(character_materials_data_directory) else None

        directory_file_path = os.path.dirname(self.blender_operator.filepath) or material_data_directory

        material_data_files = []
        if material_data_directory:
            for filename in os.listdir(material_data_directory):
                material_data_file = MaterialDataFile(filename)
                material_data_files.append(material_data_file)

        is_targeted_material_data_import = self.material and self.outlines_material
        material_data_files = self.blender_operator.files or (material_data_files if not is_targeted_material_data_import else None)

        material_data_directory = MaterialDataDirectory(
            exists=material_data_directory_exists,
            file_path=directory_file_path,
            files=material_data_files,
        )
        return material_data_directory

    def validate_UI_inputs_for_targeted_material_data_import(self):
        if self.material and not self.outlines_material:
            raise UserInputException(f'\n\n>>> Targeted Material Data Import: Missing "Outlines Material" input')
        elif not self.material and self.outlines_material:
            raise UserInputException(f'\n\n>>> Targeted Material Data Import: Missing "Target Material" input')

    def validate_num_of_file_inputs_for_targeted_material_data_import(self, material_data_files):
        num_of_files = len(material_data_files)
        if self.material and self.outlines_material and num_of_files != 1:
            raise UserInputException(f'\n\n>>> Select only 1 material data file to apply to the material. You selected {num_of_files} material data files to apply on 1 material.')


class GameMaterialDataImporterFactory:
    def create(game_type: GameType, blender_operator: Operator, context: Context, outline_material_group: OutlineMaterialGroup):
        shader_identifier_service: ShaderIdentifierService = ShaderIdentifierServiceFactory.create(game_type)
        shader = shader_identifier_service.identify_shader(bpy.data.materials, bpy.data.node_groups)
        material_names = shader_identifier_service.get_shader_material_names(game_type, bpy.data.materials, bpy.data.node_groups)
        shader_node_names = shader_identifier_service.get_shader_node_names(shader)

        # Because we inject the GameType via StringProperty, we need to compare using the Enum's name (a string)
        if game_type == GameType.GENSHIN_IMPACT.name:
            return GenshinImpactMaterialDataImporter(blender_operator, context, outline_material_group, material_names, shader_node_names)
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            return HonkaiStarRailMaterialDataImporter(blender_operator, context, outline_material_group, material_names, shader_node_names)
        elif game_type == GameType.PUNISHING_GRAY_RAVEN.name:
            return PunishingGrayRavenMaterialDataImporter(blender_operator, context, outline_material_group, material_names, shader_node_names)
        else:
            raise Exception(f'Unknown {GameType}: {game_type}')


class GenshinImpactMaterialDataImporter(GameMaterialDataImporter):
    WEAPON_NAME_IDENTIFIER = 'Mat'

    def __init__(self, blender_operator, context, outline_material_group: OutlineMaterialGroup, material_names, shader_node_names):
        self.blender_operator: Operator = blender_operator
        self.context: Context = context
        self.parsers = [
            HoyoStudioMaterialDataJsonParser,
            UnknownHoyoStudioMaterialDataJsonParser,
            UABEMaterialDataJsonParser,
        ]
        self.material = outline_material_group.material
        self.outlines_material = outline_material_group.outlines_material
        self.material_names = material_names
        self.shader_node_names: ShaderNodeNames = shader_node_names

    def import_material_data(self):
        self.validate_UI_inputs_for_targeted_material_data_import()
        material_data_directory: MaterialDataDirectory = self.get_material_data_files()

        caller_is_advanced_setup = self.blender_operator.setup_mode == 'ADVANCED'
        no_material_data_files = not material_data_directory.exists and \
            (not self.blender_operator.filepath or not self.blender_operator.files)
        if caller_is_advanced_setup or no_material_data_files:
            bpy.ops.genshin.import_material_data(
                'INVOKE_DEFAULT',
                next_step_idx=self.blender_operator.next_step_idx, 
                file_directory=self.blender_operator.file_directory,
                invoker_type=self.blender_operator.invoker_type,
                high_level_step_name=self.blender_operator.high_level_step_name,
                game_type=self.blender_operator.game_type,
            )
            return {'SKIP'}

        self.validate_num_of_file_inputs_for_targeted_material_data_import(material_data_directory.files)

        for file in material_data_directory.files:
            body_part = None

            if 'Monster' in file.name:
                expected_body_part_name = PurePosixPath(file.name).stem.split('_')[-2]
                body_part = get_monster_body_part_name(PurePosixPath(file.name).stem.split('_')[-2]) if expected_body_part_name != 'Mat' else get_monster_body_part_name(PurePosixPath(file.name).stem.split('_')[-1])
                character_type = CharacterType.MONSTER
            elif 'NPC' in file.name:
                body_part = get_npc_mesh_body_part_name(PurePosixPath(file.name).stem)
                character_type = CharacterType.NPC
            elif 'Equip' in file.name:
                body_part = 'Body'
                character_type = CharacterType.GI_EQUIPMENT
            elif file.name.endswith('Glass_Mat.json'):
                body_part = 'Glass'
                character_type = CharacterType.UNKNOWN
            elif file.name.endswith('Glass_Eff_Mat.json'):
                body_part = 'Glass_Eff'
                character_type = CharacterType.UNKNOWN
            elif file.name.startswith(ShaderMaterialNameKeywords.SKILLOBJ):
                skillobj_identifier = file.name.split('_')[2]  # WARNING: This is a brittle way to get the identifier
                body_part = f'{ShaderMaterialNameKeywords.SKILLOBJ} {skillobj_identifier}'
                character_type = CharacterType.UNKNOWN
            else:
                body_part = PurePosixPath(file.name).stem.split('_')[-1]
                character_type = CharacterType.UNKNOWN  # catch-all, tries default material applying behavior

            json_material_data = self.open_and_load_json_data(material_data_directory.file_path, file)
            material_data_parser = self.get_material_data_json_parser(json_material_data)

            material, outlines_material, night_soul_outlines_material = self.find_material_and_outline_material_for_body_part(body_part)
            outline_material_group: OutlineMaterialGroup = OutlineMaterialGroup(material, outlines_material, night_soul_outlines_material)

            # Skirk's Dress2 material data JSON is for her StarCloak
            if body_part == 'Dress2' and 'Skirk' in file.name:
                body_part_based_on_version = body_part_based_on_version_map.get(self.material_names, 'StarCloak')
                self.__customized_skirk_starcloak_material_data_setup(material_data_parser, character_type, file, body_part_based_on_version)

            if not material or not outlines_material:
                self.blender_operator.report({'WARNING'}, \
                    f'Continuing to apply other material data, but: \n'
                    f'* Type: {character_type}\n'
                    f'* Material Data JSON "{file.name}" was selected, but unable to determine material to apply this to.\n'
                    f'* Expected Materials "{self.material_names.MATERIAL_PREFIX}{body_part}" and "{self.material_names.MATERIAL_PREFIX}{body_part} Outlines"')
                continue

            shadow_ramp_type_setter = ShadowRampTypeSetter(file, material_data_directory, self.shader_node_names)
            shadow_ramp_type_setter.set_shadow_ramp_type(material)

            material_data_appliers = MaterialDataAppliersFactory.create(
                self.blender_operator.game_type,
                material_data_parser,
                outline_material_group,
                character_type
            )
            self.apply_material_data(body_part, material_data_appliers, file)
        return {'FINISHED'}

    def __customized_skirk_starcloak_material_data_setup(self, material_data_parser, character_type, file, body_part):
        material, outlines_material, night_soul_outlines_material = self.find_material_and_outline_material_for_body_part(body_part)
        outline_material_group: OutlineMaterialGroup = OutlineMaterialGroup(material, outlines_material, night_soul_outlines_material)

        material_data_appliers = MaterialDataAppliersFactory.create(
            self.blender_operator.game_type,
            material_data_parser,
            outline_material_group,
            character_type
        )
        self.apply_material_data(body_part, material_data_appliers, file)

class ShadowRampTypeSetter:
    def __init__(self, target_file, material_data_directory: MaterialDataDirectory, shader_node_names: ShaderNodeNames):
        self.target_file = target_file
        self.material_data_directory = material_data_directory
        self.shader_node_names = shader_node_names

    def set_shadow_ramp_type(self, shader_material):
        shadow_ramp_type = self.__get_shadow_ramp_type_by_PackedShadowRampTex()
        self.__set_shadow_ramp_type_on_shader_material(shader_material, shadow_ramp_type)

    def __get_shadow_ramp_type_by_PackedShadowRampTex(self):
        material_data_files = [mat_file for mat_file in self.material_data_directory.files if mat_file.name.lower() != self.target_file.name.lower()]

        target_file_json = GenshinImpactMaterialDataImporter.open_and_load_json_data(
            self.material_data_directory.file_path, 
            self.target_file
        )
        target_file_shadow_ramp_pathID = self.__get_shadow_ramp_pathID(target_file_json)

        for material_data_file in material_data_files:
            material_data_json = GenshinImpactMaterialDataImporter.open_and_load_json_data(
                self.material_data_directory.file_path, 
                material_data_file
            )
            shadow_ramp_pathID = self.__get_shadow_ramp_pathID(material_data_json)

            if shadow_ramp_pathID and target_file_shadow_ramp_pathID and shadow_ramp_pathID == target_file_shadow_ramp_pathID:
                return get_body_part(material_data_file)

    def __get_shadow_ramp_pathID(self, material_data_json):
        try:
            return material_data_json.get('m_SavedProperties').get('m_TexEnvs').get('_PackedShadowRampTex').get('m_Texture').get('m_PathID')
        except AttributeError:
            return None

    def __set_shadow_ramp_type_on_shader_material(self, shader_material, shadow_ramp_type):
        body_shader_node = shader_material.node_tree.nodes.get(self.shader_node_names.BODY_SHADER)
        body_hair_ramp_switch_input = body_shader_node.inputs.get(self.shader_node_names.BODY_HAIR_RAMP_SWITCH) if body_shader_node else None

        if body_hair_ramp_switch_input:
            body_hair_ramp_switch_values: BodyHairRampSwitchValues = BodyHairRampSwitchValues(self.shader_node_names)
            self.__set_up_body_hair_ramp_switch_value(body_hair_ramp_switch_input, shadow_ramp_type, body_hair_ramp_switch_values)

    def __set_up_body_hair_ramp_switch_value(self, switch_input, shadow_ramp_type, switch_values: BodyHairRampSwitchValues):
        if shadow_ramp_type == 'Hair':  # TODO: Refactor into Enum along side genshin_body_part_deducer.py
            switch_input.default_value = switch_values.HAIR
        elif shadow_ramp_type == 'Body':  # TODO: Refactor into Enum along side genshin_body_part_deducer.py
            switch_input.default_value = switch_values.BODY


class HonkaiStarRailMaterialDataImporter(GameMaterialDataImporter):
    def __init__(self, blender_operator, context, outline_material_group: OutlineMaterialGroup, material_names, shader_node_names: ShaderNodeNames):
        self.blender_operator: Operator = blender_operator
        self.context: Context = context
        self.parsers = [
            HoyoStudioMaterialDataJsonParser,
            UnknownHoyoStudioMaterialDataJsonParser,
            UABEMaterialDataJsonParser,
        ]
        self.material = outline_material_group.material
        self.outlines_material = outline_material_group.outlines_material
        self.material_names = material_names
        self.shader_node_names = shader_node_names

    def import_material_data(self):
        self.validate_UI_inputs_for_targeted_material_data_import()
        material_data_directory: MaterialDataDirectory = self.get_material_data_files()

        caller_is_advanced_setup = self.blender_operator.setup_mode == 'ADVANCED'
        no_material_data_files = not material_data_directory.exists and \
            (not self.blender_operator.filepath or not self.blender_operator.files)
        if caller_is_advanced_setup or no_material_data_files:
            bpy.ops.genshin.import_material_data(
                'INVOKE_DEFAULT',
                next_step_idx=self.blender_operator.next_step_idx, 
                file_directory=self.blender_operator.file_directory,
                invoker_type=self.blender_operator.invoker_type,
                high_level_step_name=self.blender_operator.high_level_step_name,
                game_type=self.blender_operator.game_type,
            )
            return {'SKIP'}

        self.validate_num_of_file_inputs_for_targeted_material_data_import(material_data_directory.files)

        for file in material_data_directory.files:
            is_firefly = PurePosixPath(file.name).stem.split('_')[-1] == 'D' or PurePosixPath(file.name).stem.split('_')[-1] == 'S'

            body_part = PurePosixPath(file.name).stem.split('_Mat_')[1] if PurePosixPath(file.name).stem.split('_')[-1] == 'Trans' \
                else PurePosixPath(file.name).stem.split('_')[-2] if is_firefly \
                else PurePosixPath(file.name).stem.split('_')[-1]
            character_type = CharacterType.HSR_AVATAR

            json_material_data = self.open_and_load_json_data(material_data_directory.file_path, file)

            material, outlines_material, __ = self.find_material_and_outline_material_for_body_part(body_part)
            outline_material_group: OutlineMaterialGroup = OutlineMaterialGroup(material, outlines_material)

            if not material or not outlines_material:
                self.blender_operator.report({'WARNING'}, \
                    f'Continuing to apply other material data, but: \n'
                    f'* Type: {character_type}\n'
                    f'* Material Data JSON "{file.name}" was selected, but unable to determine material to apply this to.\n'
                    f'* Expected Materials "{self.material_names.MATERIAL_PREFIX}{body_part}" and "{self.material_names.MATERIAL_PREFIX}{body_part} Outlines"')
                continue

            material_data_parser = self.get_material_data_json_parser(json_material_data)
            material_data_appliers = MaterialDataAppliersFactory.create(
                self.blender_operator.game_type,
                material_data_parser,
                outline_material_group,
                character_type
            )
            self.apply_material_data(body_part, material_data_appliers, file)
        return {'FINISHED'}


# Unused.
class PunishingGrayRavenMaterialDataImporter(GameMaterialDataImporter):
    def __init__(self, blender_operator, context, outline_material_group: OutlineMaterialGroup, material_names, shader_node_names: ShaderNodeNames):
        self.blender_operator: Operator = blender_operator
        self.context: Context = context
        self.parsers = [
            HoyoStudioMaterialDataJsonParser,
            UnknownHoyoStudioMaterialDataJsonParser,
            UABEMaterialDataJsonParser,
        ]
        self.material = outline_material_group.material
        self.outlines_material = outline_material_group.outlines_material
        self.material_names = material_names
        self.shader_node_names = shader_node_names

    def import_material_data(self):
        return {'FINISHED'}
