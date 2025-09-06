# Author: michael-gh1

import os
import bpy

from abc import ABC, abstractmethod
from bpy.types import Operator, Context

from setup_wizard.domain.shader_identifier_service import GenshinImpactShaders, HonkaiStarRailShaders, ShaderIdentifierService, ShaderIdentifierServiceFactory
from setup_wizard.outline_import_setup.outline_node_groups import OutlineNodeGroupNames
from setup_wizard.import_order import GENSHIN_IMPACT_OUTLINES_FILE_PATH, PUNISHING_GRAY_RAVEN_OUTLINES_FILE_PATH, HONKAI_STAR_RAIL_OUTLINES_FILE_PATH, \
    NextStepInvoker, cache_using_cache_key, get_cache
from setup_wizard.domain.game_types import GameType


class GameOutlineImporterFactory:
    def create(game_type: str, blender_operator: Operator, context: Context):
        shader_identifier_service: ShaderIdentifierService = ShaderIdentifierServiceFactory.create(game_type)
        shader = shader_identifier_service.identify_shader(bpy.data.materials, bpy.data.node_groups)

        if game_type == GameType.GENSHIN_IMPACT.name:
            if shader is GenshinImpactShaders.V1_GENSHIN_IMPACT_SHADER or shader is GenshinImpactShaders.V2_GENSHIN_IMPACT_SHADER:
                outlines_node_group_name = OutlineNodeGroupNames.FESTIVITY_GENSHIN_OUTLINES
            elif shader is GenshinImpactShaders.V3_GENSHIN_IMPACT_SHADER:
                outlines_node_group_name = OutlineNodeGroupNames.V3_BONNY_FESTIVITY_GENSHIN_OUTLINES
            else:
                outlines_node_group_name = OutlineNodeGroupNames.V3_BONNY_FESTIVITY_GENSHIN_OUTLINES
            return GenshinImpactOutlineNodeGroupImporter(blender_operator, context, outlines_node_group_name)
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            if shader is HonkaiStarRailShaders.NYA222_HONKAI_STAR_RAIL_SHADER:
                return HonkaiStarRailOutlineNodeGroupImporter(blender_operator, context, OutlineNodeGroupNames.NYA222_HSR_OUTLINES)
            else:  # is HonkaiStarRailShaders.STELLARTOON_HONKAI_STAR_RAIL_SHADER
                return HonkaiStarRailOutlineNodeGroupImporter(blender_operator, context, OutlineNodeGroupNames.STELLARTOON_HSR_OUTLINES)
                
        elif game_type == GameType.PUNISHING_GRAY_RAVEN.name:
            return PunishingGrayRavenOutlineNodeGroupImporter(blender_operator, context)
        else:
            raise Exception(f'Unknown {GameType}: {game_type}')


class GameOutlineNodeGroupImporter(ABC):
    @abstractmethod
    def import_outline_node_group(self):
        raise NotImplementedError


class GenshinImpactOutlineNodeGroupImporter(GameOutlineNodeGroupImporter):
    def __init__(self, blender_operator, context, outlines_node_group_name):
        self.blender_operator = blender_operator
        self.context = context
        self.outlines_file_path = GENSHIN_IMPACT_OUTLINES_FILE_PATH  # Keep same filepath for all Genshin Impact
        self.outlines_node_group_names = outlines_node_group_name

    def import_outline_node_group(self):
        cache_enabled = self.context.window_manager.cache_enabled
        filepath = get_cache(cache_enabled).get(self.outlines_file_path) or self.blender_operator.filepath

        if not filepath:
            bpy.ops.genshin.import_outlines(
                'INVOKE_DEFAULT',
                next_step_idx=self.blender_operator.next_step_idx, 
                file_directory=self.blender_operator.file_directory,
                invoker_type=self.blender_operator.invoker_type,
                high_level_step_name=self.blender_operator.high_level_step_name,
                game_type=self.blender_operator.game_type,
            )
            return {'FINISHED'}

        for outline_node_group_name in self.outlines_node_group_names:
            if not bpy.data.node_groups.get(outline_node_group_name):
                inner_path = 'NodeTree'
                bpy.ops.wm.append(
                    filepath=os.path.join(filepath, inner_path, outline_node_group_name),
                    directory=os.path.join(filepath, inner_path),
                    filename=outline_node_group_name
                )
                if cache_enabled and filepath:
                    cache_using_cache_key(get_cache(cache_enabled), self.outlines_file_path, filepath)

        NextStepInvoker().invoke(
            self.blender_operator.next_step_idx, 
            self.blender_operator.invoker_type,
            high_level_step_name=self.blender_operator.high_level_step_name,
            game_type=self.blender_operator.game_type,
        )

class HonkaiStarRailOutlineNodeGroupImporter(GameOutlineNodeGroupImporter):
    def __init__(self, blender_operator, context, outlines_node_group_names):
        self.blender_operator = blender_operator
        self.context = context
        self.outlines_file_path = HONKAI_STAR_RAIL_OUTLINES_FILE_PATH  # Keep same filepath for all HSR
        self.outlines_node_group_names = outlines_node_group_names

    def import_outline_node_group(self):
        cache_enabled = self.context.window_manager.cache_enabled
        filepath = get_cache(cache_enabled).get(self.outlines_file_path) or self.blender_operator.filepath

        if not filepath:
            bpy.ops.genshin.import_outlines(
                'INVOKE_DEFAULT',
                next_step_idx=self.blender_operator.next_step_idx, 
                file_directory=self.blender_operator.file_directory,
                invoker_type=self.blender_operator.invoker_type,
                high_level_step_name=self.blender_operator.high_level_step_name,
                game_type=self.blender_operator.game_type,
            )
            return {'FINISHED'}

        for outline_node_group_name in self.outlines_node_group_names:
            if not bpy.data.node_groups.get(outline_node_group_name):
                inner_path = 'NodeTree'

                bpy.ops.wm.append(
                    filepath=os.path.join(filepath, inner_path, outline_node_group_name),
                    directory=os.path.join(filepath, inner_path),
                    filename=outline_node_group_name
                )
                if cache_enabled and filepath:
                    cache_using_cache_key(get_cache(cache_enabled), self.outlines_file_path, filepath)

        NextStepInvoker().invoke(
            self.blender_operator.next_step_idx, 
            self.blender_operator.invoker_type,
            high_level_step_name=self.blender_operator.high_level_step_name,
            game_type=self.blender_operator.game_type,
        )


class PunishingGrayRavenOutlineNodeGroupImporter(GameOutlineNodeGroupImporter):
    def __init__(self, blender_operator, context):
        self.blender_operator = blender_operator
        self.context = context
        self.outlines_file_path = PUNISHING_GRAY_RAVEN_OUTLINES_FILE_PATH
        self.outlines_node_group_names = \
            OutlineNodeGroupNames.V2_JAREDNYTS_PGR_OUTLINES + OutlineNodeGroupNames.V3_JAREDNYTS_PGR_OUTLINES

    def import_outline_node_group(self):
        cache_enabled = self.context.window_manager.cache_enabled
        filepath = get_cache(cache_enabled).get(self.outlines_file_path) or self.blender_operator.filepath

        if not filepath:
            bpy.ops.genshin.import_outlines(
                'INVOKE_DEFAULT',
                next_step_idx=self.blender_operator.next_step_idx, 
                file_directory=self.blender_operator.file_directory,
                invoker_type=self.blender_operator.invoker_type,
                high_level_step_name=self.blender_operator.high_level_step_name,
                game_type=self.blender_operator.game_type,
            )
            return {'FINISHED'}

        for outline_node_group_name in self.outlines_node_group_names:
            if not bpy.data.node_groups.get(outline_node_group_name):
                inner_path = 'NodeTree'

                bpy.ops.wm.append(
                    filepath=os.path.join(filepath, inner_path, outline_node_group_name),
                    directory=os.path.join(filepath, inner_path),
                    filename=outline_node_group_name
                )
                if cache_enabled and filepath:
                    cache_using_cache_key(get_cache(cache_enabled), self.outlines_file_path, filepath)

        NextStepInvoker().invoke(
            self.blender_operator.next_step_idx, 
            self.blender_operator.invoker_type,
            high_level_step_name=self.blender_operator.high_level_step_name,
            game_type=self.blender_operator.game_type,
        )
