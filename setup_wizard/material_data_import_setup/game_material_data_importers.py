
from abc import ABC, abstractmethod
import json
import os
from pathlib import PurePosixPath
import bpy
from bpy.types import Operator, Context

from setup_wizard.domain.game_types import GameType
from setup_wizard.exceptions import UnsupportedMaterialDataJsonFormatException
from setup_wizard.material_data_applier import MaterialDataApplier, V1_MaterialDataApplier, V2_HSR_MaterialDataApplier, V2_WeaponMaterialDataApplier, V2_MaterialDataApplier
from setup_wizard.parsers.material_data_json_parsers import HoyoStudioMaterialDataJsonParser, MaterialDataJsonParser, UABEMaterialDataJsonParser

class GameMaterialDataImporter(ABC):
    @abstractmethod
    def import_material_data(self):
        raise NotImplementedError


class GameMaterialDataImporterFactory:
    def create(game_type: GameType, blender_operator: Operator, context: Context):
        # Because we inject the GameType via StringProperty, we need to compare using the Enum's name (a string)
        if game_type == GameType.GENSHIN_IMPACT.name:
            return GenshinImpactMaterialDataImporter(blender_operator, context)
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            return HonkaiStarRailMaterialDataImporter(blender_operator, context)
        else:
            raise Exception(f'Unknown {GameType}: {game_type}')


class GenshinImpactMaterialDataImporter(GameMaterialDataImporter):
    WEAPON_NAME_IDENTIFIER = 'Mat'

    def __init__(self, blender_operator, context):
        self.blender_operator: Operator = blender_operator
        self.context: Context = context
        self.parsers = [
            HoyoStudioMaterialDataJsonParser,
            UABEMaterialDataJsonParser,
        ]

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
            body_part = PurePosixPath(file.name).stem.split('_')[-1]

            fp = open(f'{directory_file_path}/{file.name}')
            json_material_data = json.load(fp)
            material_data_parser = self.__get_material_data_json_parser(json_material_data)

            # V2_WeaponMaterialDataApplier is technically unnecessary for now, does same logic as V2_MaterialDataApplier
            weapon_material_data_appliers = [
                V2_WeaponMaterialDataApplier(material_data_parser, 'Body'),  
                V1_MaterialDataApplier(material_data_parser, 'Body'),
            ]
            character_model_material_data_appliers = [
                V2_MaterialDataApplier(material_data_parser, body_part), 
                V1_MaterialDataApplier(material_data_parser, body_part),
            ]
            # Was tempted to add another check, but holding off for now: file.name.startswith('Equip')
            is_weapon = body_part == self.WEAPON_NAME_IDENTIFIER

            material_data_appliers  = weapon_material_data_appliers if is_weapon else character_model_material_data_appliers

            material_data_applier: MaterialDataApplier  # annotate type
            for material_data_applier in material_data_appliers:
                try:
                    material_data_applier.set_up_mesh_material_data()
                    material_data_applier.set_up_outline_colors()
                    break  # Important! If a MaterialDataApplier runs successfully, we don't need to try the next version
                except AttributeError as err:
                    print(err)
                    continue # fallback and try next version
                except KeyError:
                    self.blender_operator.report({'WARNING'}, \
                        f'Continuing to apply other material data, but: \n'
                        f'* Material Data JSON "{body_part}" was selected, but there is no material named "miHoYo - Genshin {body_part}"')
                    break

    def __get_material_data_json_parser(self, json_material_data):
        for index, parser_class in enumerate(self.parsers):
            try:
                parser: MaterialDataJsonParser  = parser_class(json_material_data)
                parser.parse()
                return parser
            except AttributeError:
                if index == len(self.parsers) - 1:
                    raise UnsupportedMaterialDataJsonFormatException(self.parsers)

class HonkaiStarRailMaterialDataImporter(GameMaterialDataImporter):
    def __init__(self, blender_operator, context):
        self.blender_operator: Operator = blender_operator
        self.context: Context = context
        self.parsers = [
            HoyoStudioMaterialDataJsonParser,
            UABEMaterialDataJsonParser,
        ]

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
            body_part = PurePosixPath(file.name).stem.split('_')[-1]

            fp = open(f'{directory_file_path}/{file.name}')
            json_material_data = json.load(fp)
            material_data_parser = self.__get_material_data_json_parser(json_material_data)

            character_model_material_data_appliers = [
                V2_HSR_MaterialDataApplier(material_data_parser, body_part), 
            ]

            material_data_appliers = character_model_material_data_appliers

            material_data_applier: MaterialDataApplier  # annotate type
            for material_data_applier in material_data_appliers:
                try:
                    material_data_applier.set_up_mesh_material_data()
                    material_data_applier.set_up_outline_colors()
                    break  # Important! If a MaterialDataApplier runs successfully, we don't need to try the next version
                except AttributeError as err:
                    print(err)
                    continue # fallback and try next version
                except KeyError:
                    self.blender_operator.report({'WARNING'}, \
                        f'Continuing to apply other material data, but: \n'
                        f'* Material Data JSON "{body_part}" was selected, but there is no material named "miHoYo - Genshin {body_part}"')
                    break

    def __get_material_data_json_parser(self, json_material_data):
        for index, parser_class in enumerate(self.parsers):
            try:
                parser: MaterialDataJsonParser  = parser_class(json_material_data)
                parser.parse()
                return parser
            except AttributeError:
                if index == len(self.parsers) - 1:
                    raise UnsupportedMaterialDataJsonFormatException(self.parsers)
