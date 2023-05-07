# Author: michael-gh1

import bpy
import os

from abc import ABC, abstractmethod
from bpy.types import Operator, Context
from setup_wizard.domain.game_types import GameType

from setup_wizard.domain.shader_configurator import ShaderConfigurator
from setup_wizard.import_order import CHARACTER_MODEL_FOLDER_FILE_PATH, NextStepInvoker, cache_using_cache_key, get_cache
from setup_wizard.texture_setup.texture_importer_types import GenshinTextureImporter, TextureImporterFactory, TextureImporterType


class GameTextureImporter(ABC):
    @abstractmethod
    def import_textures(self):
        raise NotImplementedError()


class GameTextureImporterFactory:
    def create(game_texture_importer_type: GameType, blender_operator: Operator, context):
        if game_texture_importer_type == GameType.GENSHIN_IMPACT.name:
            return GenshinImpactTextureImporter(blender_operator, context)
        elif game_texture_importer_type == GameType.HONKAI_STAR_RAIL.name:
            return HonkaiStarRailTextureImporter(blender_operator, context)
        else:
            raise Exception(f'Unknown {GameType}: {game_texture_importer_type}')


class GenshinImpactTextureImporter(GameTextureImporter):
    def __init__(self, blender_operator, context):
        self.blender_operator: Operator = blender_operator
        self.context: Context = context

    # Acts as a "facade". May help when troubleshooting issues with others (method name appears in stack trace).
    def import_textures(self):
        self.__import_genshin_impact_textures()

    def __import_genshin_impact_textures(self):
        cache_enabled = self.context.window_manager.cache_enabled
        directory = self.blender_operator.file_directory \
            or get_cache(cache_enabled).get(CHARACTER_MODEL_FOLDER_FILE_PATH) \
            or os.path.dirname(self.blender_operator.filepath)

        if not directory:
            bpy.ops.genshin.import_textures(
                'INVOKE_DEFAULT',
                next_step_idx=self.blender_operator.next_step_idx, 
                file_directory=self.blender_operator.file_directory,
                invoker_type=self.blender_operator.invoker_type,
                high_level_step_name=self.blender_operator.high_level_step_name,
                game_type=GameType.GENSHIN_IMPACT,
            )
            return {'FINISHED'}

        texture_importer_type = TextureImporterType.AVATAR if \
            [material_name for material_name, material in bpy.data.materials.items() if 'Avatar' in material_name] else \
                TextureImporterType.NPC
        texture_importer: GenshinTextureImporter = TextureImporterFactory.create(texture_importer_type)
        texture_importer.import_textures(directory)

        '''
            NPCs don't typically have shadow ramps. Turn off using shadow ramp if there are no assets for it.
            If an asset does exist, leave it as the default value (1.0).
        '''
        if texture_importer_type is TextureImporterType.NPC and \
            not [file for file in [file for name, folder, file in os.walk(directory)][0] if 'Shadow_Ramp' in file]:
            ShaderConfigurator().update_shader_value(
                materials = [
                    bpy.data.materials.get('miHoYo - Genshin Hair'),
                    bpy.data.materials.get('miHoYo - Genshin Face'),
                    bpy.data.materials.get('miHoYo - Genshin Body'),
                ],
                node_name = 'miHoYo - Genshin Impact',
                input_name = 'Use Shadow Ramp',
                value = 0
        )

        self.blender_operator.report({'INFO'}, 'Imported textures')
        if cache_enabled and directory:
            cache_using_cache_key(get_cache(cache_enabled), CHARACTER_MODEL_FOLDER_FILE_PATH, directory)

        NextStepInvoker().invoke(
            self.blender_operator.next_step_idx,
            self.blender_operator.invoker_type,
            file_path_to_cache=directory,
            high_level_step_name=self.blender_operator.high_level_step_name
        )


class HonkaiStarRailTextureImporter:
    def __init__(self):
        pass

    # Acts as a "facade". May help when troubleshooting issues with others (method name appears in stack trace).
    def import_textures(self, context):
        self.__import_honkai_star_rail_textures(context)

    def __import_honkai_star_rail_textures(self, context):
        pass
