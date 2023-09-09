# Author: michael-gh1

import bpy
import os

from abc import ABC, abstractmethod
from bpy.types import Operator, Context
from setup_wizard.domain.game_types import GameType

from setup_wizard.domain.shader_configurator import ShaderConfigurator
from setup_wizard.import_order import CHARACTER_MODEL_FOLDER_FILE_PATH, NextStepInvoker, cache_using_cache_key, get_cache
from setup_wizard.texture_import_setup.texture_importer_types import GenshinTextureImporter, TextureImporterFactory, TextureImporterType


class GameTextureImporter(ABC):
    @abstractmethod
    def import_textures(self):
        raise NotImplementedError()


class GameTextureImporterFactory:
    def create(game_type: GameType, blender_operator: Operator, context: Context):
        # Because we inject the GameType via StringProperty, we need to compare using the Enum's name (a string)
        if game_type == GameType.GENSHIN_IMPACT.name:
            return GenshinImpactTextureImporterFacade(blender_operator, context)
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            return HonkaiStarRailTextureImporterFacade(blender_operator, context)
        else:
            raise Exception(f'Unknown {GameType}: {game_type}')


'''
GI Texture Importer Abstraction Layer
Facade class intended to help abstract the Blender Operator layer from the Texture Importing layer.
Also named as a Facade in order to differentiate from the actual Texture Importers.
'''
class GenshinImpactTextureImporterFacade(GameTextureImporter):
    def __init__(self, blender_operator, context):
        self.blender_operator: Operator = blender_operator
        self.context: Context = context

    '''
    This does look odd, but is intended to help with troubleshooting errors that users may encounter.
    The stacktrace will contain the method name (game name).
    '''
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
                game_type=GameType.GENSHIN_IMPACT.name,
            )
            return {'FINISHED'}

        texture_importer_type = ''
        
        if [material_name for material_name, material in bpy.data.materials.items() if 'Avatar'.lower() in material_name.lower() and 'Avatar_Default_Mat'.lower() not in material_name.lower()]:
            texture_importer_type = TextureImporterType.AVATAR
        elif [material_name for material_name, material in bpy.data.materials.items() if 'Monster'.lower() in material_name.lower()]:
            texture_importer_type = TextureImporterType.MONSTER
        else:
            texture_importer_type = TextureImporterType.NPC

        texture_importer: GenshinTextureImporter = TextureImporterFactory.create(texture_importer_type, GameType.GENSHIN_IMPACT)
        texture_importer.import_textures(directory)

        '''
            NPCs and Monsters don't typically have shadow ramps. Turn off using shadow ramp if there are no assets for it.
            If an asset does exist, leave it as the default value (1.0).
        '''
        if (texture_importer_type is TextureImporterType.NPC or texture_importer_type is TextureImporterType.MONSTER) and \
            not [file for file in [file for name, folder, file in os.walk(directory)][0] if 'Shadow_Ramp' in file]:
            ShaderConfigurator().update_shader_value(
                materials = [
                    bpy.data.materials.get('miHoYo - Genshin Hair'),
                    bpy.data.materials.get('miHoYo - Genshin Face'),
                    bpy.data.materials.get('miHoYo - Genshin Body'),
                    bpy.data.materials.get('miHoYo - Genshin Dress'),
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
            high_level_step_name=self.blender_operator.high_level_step_name,
            game_type=GameType.GENSHIN_IMPACT.name,
        )
        return {'FINISHED'}


'''
HSR Texture Importer Abstraction Layer
Facade class intended to help abstract the Blender Operator layer from the Texture Importing layer.
Also named as a Facade in order to differentiate from the actual Texture Importers.
'''
class HonkaiStarRailTextureImporterFacade(GameTextureImporter):
    def __init__(self, blender_operator, context):
        self.blender_operator: Operator = blender_operator
        self.context: Context = context

    '''
    This does look odd, but is intended to help with troubleshooting errors that users may encounter.
    The stacktrace will contain the method name (game name).
    '''
    def import_textures(self):
        self.__import_honkai_star_rail_textures()

    def __import_honkai_star_rail_textures(self):
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
                game_type=GameType.HONKAI_STAR_RAIL.name,
            )
            return {'FINISHED'}

        texture_importer_type = TextureImporterType.HSR_AVATAR
        texture_importer: GenshinTextureImporter = TextureImporterFactory.create(texture_importer_type, GameType.HONKAI_STAR_RAIL)
        texture_importer.import_textures(directory)

        self.blender_operator.report({'INFO'}, 'Imported textures')
        if cache_enabled and directory:
            cache_using_cache_key(get_cache(cache_enabled), CHARACTER_MODEL_FOLDER_FILE_PATH, directory)

        NextStepInvoker().invoke(
            self.blender_operator.next_step_idx,
            self.blender_operator.invoker_type,
            file_path_to_cache=directory,
            high_level_step_name=self.blender_operator.high_level_step_name,
            game_type=GameType.HONKAI_STAR_RAIL.name
        )
