
from abc import ABC, abstractmethod
import json
import os
from pathlib import PurePosixPath
from typing import List
import bpy
from bpy.types import Operator, Context, Material

from setup_wizard.domain.shader_identifier_service import GenshinImpactShaders, ShaderIdentifierService, \
    ShaderIdentifierServiceFactory
from setup_wizard.domain.shader_materials import V3_BonnyFestivityGenshinImpactMaterialNames, FestivityGenshinImpactMaterialNames, \
    Nya222HonkaiStarRailShaderMaterialNames
from setup_wizard.domain.character_types import CharacterType

from setup_wizard.domain.game_types import GameType
from setup_wizard.domain.outline_material_data import OutlineMaterialGroup
from setup_wizard.exceptions import UnsupportedMaterialDataJsonFormatException, UserInputException
from setup_wizard.material_data_import_setup.material_data_applier import MaterialDataApplier, MaterialDataAppliersFactory
from setup_wizard.parsers.material_data_json_parsers import MaterialDataJsonParser, HoyoStudioMaterialDataJsonParser, \
    UABEMaterialDataJsonParser, UnknownHoyoStudioMaterialDataJsonParser
from setup_wizard.utils.genshin_body_part_deducer import get_monster_body_part_name, get_npc_mesh_body_part_name

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
                print('Falling back and trying next version')
                continue # fallback and try next version
            except KeyError as err:
                print(err)

                if 'Shader" not found' in str(err):
                    print('Falling back and trying next version')
                    continue
                self.blender_operator.report({'WARNING'}, \
                    f'Continuing to apply other material data, but: \n'
                    f'* Material Data JSON "{body_part}" was selected, but there is no material named "{self.material_names.MATERIAL_PREFIX}{body_part}"')
                break

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


class GameMaterialDataImporterFactory:
    def create(game_type: GameType, blender_operator: Operator, context: Context, outline_material_group: OutlineMaterialGroup):
        shader_identifier_service: ShaderIdentifierService = ShaderIdentifierServiceFactory.create(game_type)

        # Because we inject the GameType via StringProperty, we need to compare using the Enum's name (a string)
        if game_type == GameType.GENSHIN_IMPACT.name:
            if shader_identifier_service.identify_shader(bpy.data.materials) is GenshinImpactShaders.V3_GENSHIN_IMPACT_SHADER:
                material_names = V3_BonnyFestivityGenshinImpactMaterialNames
            else:
                material_names = FestivityGenshinImpactMaterialNames
            return GenshinImpactMaterialDataImporter(blender_operator, context, outline_material_group, material_names)
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            return HonkaiStarRailMaterialDataImporter(blender_operator, context, outline_material_group)
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
        self.__validate_UI_inputs_for_targeted_material_data_import()

        directory_file_path = os.path.dirname(self.blender_operator.filepath)

        if not self.blender_operator.filepath or not self.blender_operator.files:
            bpy.ops.genshin.import_material_data(
                'INVOKE_DEFAULT',
                next_step_idx=self.blender_operator.next_step_idx, 
                file_directory=self.blender_operator.file_directory,
                invoker_type=self.blender_operator.invoker_type,
                high_level_step_name=self.blender_operator.high_level_step_name,
                game_type=self.blender_operator.game_type,
            )
            return {'FINISHED'}

        self.__validate_num_of_file_inputs_for_targeted_material_data_import()

        for file in self.blender_operator.files:
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

            json_material_data = self.open_and_load_json_data(directory_file_path, file)

            material: Material = self.material or bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}{body_part}')
            outlines_material: Material = self.outlines_material or bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}{body_part} Outlines')
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

    def __validate_UI_inputs_for_targeted_material_data_import(self):
        if self.material and not self.outlines_material:
            raise UserInputException(f'\n\n>>> Targeted Material Data Import: Missing "Outlines Material" input')
        elif not self.material and self.outlines_material:
            raise UserInputException(f'\n\n>>> Targeted Material Data Import: Missing "Target Material" input')

    def __validate_num_of_file_inputs_for_targeted_material_data_import(self):
        num_of_files = len(self.blender_operator.files)
        if self.material and self.outlines_material and num_of_files != 1:
            raise UserInputException(f'\n\n>>> Select only 1 material data file to apply to the material. You selected {num_of_files} material data files to apply on 1 material.')


class HonkaiStarRailMaterialDataImporter(GameMaterialDataImporter):
    def __init__(self, blender_operator, context, outline_material_group: OutlineMaterialGroup):
        self.blender_operator: Operator = blender_operator
        self.context: Context = context
        self.parsers = [
            HoyoStudioMaterialDataJsonParser,
            UnknownHoyoStudioMaterialDataJsonParser,
            UABEMaterialDataJsonParser,
        ]
        self.material = outline_material_group.material
        self.outlines_material = outline_material_group.outlines_material

    def import_material_data(self):
        directory_file_path = os.path.dirname(self.blender_operator.filepath)

        if not self.blender_operator.filepath or not self.blender_operator.files:
            bpy.ops.genshin.import_material_data(
                'INVOKE_DEFAULT',
                next_step_idx=self.blender_operator.next_step_idx, 
                file_directory=self.blender_operator.file_directory,
                invoker_type=self.blender_operator.invoker_type,
                high_level_step_name=self.blender_operator.high_level_step_name,
                game_type=self.blender_operator.game_type,
            )
            return {'FINISHED'}

        for file in self.blender_operator.files:
            body_part = 'Body_Trans' if PurePosixPath(file.name).stem.split('_')[-1] == 'Trans' \
                else PurePosixPath(file.name).stem.split('_')[-1]
            character_type = CharacterType.HSR_AVATAR

            json_material_data = self.open_and_load_json_data(directory_file_path, file)

            material: Material = self.material or bpy.data.materials.get(f'{Nya222HonkaiStarRailShaderMaterialNames.MATERIAL_PREFIX}{body_part}')
            outlines_material: Material = self.outlines_material or bpy.data.materials.get(f'{Nya222HonkaiStarRailShaderMaterialNames.MATERIAL_PREFIX}{body_part} Outlines')
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
