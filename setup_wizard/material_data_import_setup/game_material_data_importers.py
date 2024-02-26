
from abc import ABC, abstractmethod
import json
import os
from pathlib import PurePosixPath
from typing import List
import bpy
from bpy.types import Operator, Context, Material

from setup_wizard.domain.shader_identifier_service import GenshinImpactShaders, ShaderIdentifierService, \
    ShaderIdentifierServiceFactory
from setup_wizard.domain.shader_material_names import JaredNytsPunishingGrayRavenShaderMaterialNames, V3_BonnyFestivityGenshinImpactMaterialNames, V2_FestivityGenshinImpactMaterialNames, \
    Nya222HonkaiStarRailShaderMaterialNames
from setup_wizard.domain.character_types import CharacterType

from setup_wizard.domain.game_types import GameType
from setup_wizard.domain.outline_material_data import OutlineMaterialGroup
from setup_wizard.exceptions import UnsupportedMaterialDataJsonFormatException, UserInputException
from setup_wizard.import_order import CHARACTER_MODEL_FOLDER_FILE_PATH, get_cache
from setup_wizard.material_data_import_setup.material_data_applier import MaterialDataApplier, MaterialDataAppliersFactory
from setup_wizard.parsers.material_data_json_parsers import MaterialDataJsonParser, HoyoStudioMaterialDataJsonParser, \
    UABEMaterialDataJsonParser, UnknownHoyoStudioMaterialDataJsonParser
from setup_wizard.utils.genshin_body_part_deducer import get_monster_body_part_name, get_npc_mesh_body_part_name


class MaterialDataFile:
    def __init__(self, filename):
        self.name = filename


class MaterialDataFileFinder:
    def __init__(self, material_data_directory_exists, directory_file_path, material_data_files):
        self.material_data_directory_exists = material_data_directory_exists
        self.directory_file_path = directory_file_path
        self.material_data_files = material_data_files


class GameMaterialDataImporter(ABC):
    @abstractmethod
    def import_material_data(self):
        raise NotImplementedError

    def apply_material_data(self, body_part: str, material_data_appliers: List[MaterialDataApplier]):
        for material_data_applier in material_data_appliers:
            try:
                material_data_applier.set_up_mesh_material_data()
                material_data_applier.set_up_outline_colors()
                break  # Important! If a MaterialDataApplier runs successfully, we don't need to try the next version
            except AttributeError as err:
                print(err)
                print('WARNING: Falling back and trying next version')
                continue # fallback and try next version
            except KeyError as err:
                print(err)
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

    def open_and_load_json_data(self, directory_file_path, file):
        with open(f'{directory_file_path}/{file.name}') as fp:
            try:
                json_material_data = json.load(fp)
                return json_material_data
            except UnicodeDecodeError:
                raise Exception(f'Failed to load JSON. Did you select a different type of file? \nFile Selected: "{file.name}"')

    def find_material_and_outline_material_for_body_part(self, body_part) -> (Material, Material):
        # Order of Selection
        # 1. Target Material selected.
        # 2. Shader Materials not renamed (regular setup).
        # 3. Shader Materials renamed. Search for material.
        searched_materials = [material for material in bpy.data.materials.values() if f' {body_part}' in material.name and 'Outlines' not in material.name]
        searched_material = searched_materials[0] if searched_materials else None
        material: Material = self.material or bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}{body_part}') or searched_material

        # Order of Selection
        # 1. Outline Material selected.
        # 2. Shader Materials not renamed (regular setup).
        # 3. Shader Materials renamed. Search for material.
        searched_outlines_materials = [material for material in bpy.data.materials.values() if f' {body_part} Outlines' in material.name]
        searched_outlines_material = searched_outlines_materials[0] if searched_outlines_materials else None
        outlines_material: Material = self.outlines_material or bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}{body_part} Outlines') or searched_outlines_material

        return (material, outlines_material)

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

        material_data_file_finder = MaterialDataFileFinder(
            material_data_directory_exists=material_data_directory_exists,
            directory_file_path=directory_file_path,
            material_data_files=material_data_files,
        )
        return material_data_file_finder

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

        # Because we inject the GameType via StringProperty, we need to compare using the Enum's name (a string)
        if game_type == GameType.GENSHIN_IMPACT.name:
            if shader_identifier_service.identify_shader(bpy.data.materials, bpy.data.node_groups) is GenshinImpactShaders.V3_GENSHIN_IMPACT_SHADER:
                material_names = V3_BonnyFestivityGenshinImpactMaterialNames
            else:
                material_names = V2_FestivityGenshinImpactMaterialNames
            return GenshinImpactMaterialDataImporter(blender_operator, context, outline_material_group, material_names)
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            material_names = Nya222HonkaiStarRailShaderMaterialNames
            return HonkaiStarRailMaterialDataImporter(blender_operator, context, outline_material_group, material_names)
        elif game_type == GameType.PUNISHING_GRAY_RAVEN.name:
            material_names = JaredNytsPunishingGrayRavenShaderMaterialNames
            return PunishingGrayRavenMaterialDataImporter(blender_operator, context, outline_material_group, material_names)
        else:
            raise Exception(f'Unknown {GameType}: {game_type}')


class GenshinImpactMaterialDataImporter(GameMaterialDataImporter):
    WEAPON_NAME_IDENTIFIER = 'Mat'

    def __init__(self, blender_operator, context, outline_material_group: OutlineMaterialGroup, material_names):
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

    def import_material_data(self):
        self.validate_UI_inputs_for_targeted_material_data_import()
        material_data_file_finder: MaterialDataFileFinder = self.get_material_data_files()

        caller_is_advanced_setup = self.blender_operator.setup_mode == 'ADVANCED'
        no_material_data_files = not material_data_file_finder.material_data_directory_exists and \
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

        self.validate_num_of_file_inputs_for_targeted_material_data_import(material_data_file_finder.material_data_files)

        for file in material_data_file_finder.material_data_files:
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
            else:
                body_part = PurePosixPath(file.name).stem.split('_')[-1]
                character_type = CharacterType.UNKNOWN  # catch-all, tries default material applying behavior

            json_material_data = self.open_and_load_json_data(material_data_file_finder.directory_file_path, file)

            material, outlines_material = self.find_material_and_outline_material_for_body_part(body_part)
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
            self.apply_material_data(body_part, material_data_appliers)
        return {'FINISHED'}


class HonkaiStarRailMaterialDataImporter(GameMaterialDataImporter):
    def __init__(self, blender_operator, context, outline_material_group: OutlineMaterialGroup, material_names):
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

    def import_material_data(self):
        self.validate_UI_inputs_for_targeted_material_data_import()
        material_data_file_finder: MaterialDataFileFinder = self.get_material_data_files()

        caller_is_advanced_setup = self.blender_operator.setup_mode == 'ADVANCED'
        no_material_data_files = not material_data_file_finder.material_data_directory_exists and \
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

        self.validate_num_of_file_inputs_for_targeted_material_data_import(material_data_file_finder.material_data_files)

        for file in material_data_file_finder.material_data_files:
            is_firefly = PurePosixPath(file.name).stem.split('_')[-1] == 'D' or PurePosixPath(file.name).stem.split('_')[-1] == 'S'

            body_part = 'Body_Trans' if PurePosixPath(file.name).stem.split('_')[-1] == 'Trans' \
                else PurePosixPath(file.name).stem.split('_')[-2] if is_firefly \
                else PurePosixPath(file.name).stem.split('_')[-1]
            character_type = CharacterType.HSR_AVATAR

            json_material_data = self.open_and_load_json_data(material_data_file_finder.directory_file_path, file)

            material, outlines_material = self.find_material_and_outline_material_for_body_part(body_part)
            outline_material_group: OutlineMaterialGroup = OutlineMaterialGroup(material, outlines_material)

            if not material or not outlines_material:
                self.blender_operator.report({'WARNING'}, \
                    f'Continuing to apply other material data, but: \n'
                    f'* Type: {character_type}\n'
                    f'* Material Data JSON "{file.name}" was selected, but unable to determine material to apply this to.\n'
                    f'* Expected Materials "{Nya222HonkaiStarRailShaderMaterialNames.MATERIAL_PREFIX}{body_part}" and "{Nya222HonkaiStarRailShaderMaterialNames.MATERIAL_PREFIX}{body_part} Outlines"')
                continue

            material_data_parser = self.get_material_data_json_parser(json_material_data)
            material_data_appliers = MaterialDataAppliersFactory.create(
                self.blender_operator.game_type,
                material_data_parser,
                outline_material_group,
                character_type
            )
            self.apply_material_data(body_part, material_data_appliers)
        return {'FINISHED'}


# Unused.
class PunishingGrayRavenMaterialDataImporter(GameMaterialDataImporter):
    def __init__(self, blender_operator, context, outline_material_group: OutlineMaterialGroup, material_names):
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

    def import_material_data(self):
        return {'FINISHED'}
