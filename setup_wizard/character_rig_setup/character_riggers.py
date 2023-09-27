# Author: michael-gh1

import bpy
from setup_wizard.character_rig_setup.rig_script import rig_character

from abc import ABC, abstractmethod
from bpy.types import Operator, Context

from setup_wizard.domain.game_types import GameType
from setup_wizard.import_order import GENSHIN_RIGIFY_BONE_SHAPES_FILE_PATH, NextStepInvoker, cache_using_cache_key, \
    get_cache

from setup_wizard.character_rig_setup.character_rigger_props import CharacterRiggerPropertyGroup


class CharacterRiggerFactory:
    def create(game_type: GameType, blender_operator: Operator, context: Context):
        if game_type == GameType.GENSHIN_IMPACT.name:
            return GenshinImpactCharacterRigger(blender_operator, context)
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            return HonkaiStarRailCharacterRigger(blender_operator, context)
        else:
            raise Exception(f'Unexpected input GameType "{game_type}" for CharacterRiggerFactory')


class CharacterRigger(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def rig_character(self):
        raise NotImplementedError


class GenshinImpactCharacterRigger(CharacterRigger):
    def __init__(self, blender_operator, context):
        self.blender_operator: Operator = blender_operator
        self.context: Context = context
        self.rigify_bone_shapes_file_path = GENSHIN_RIGIFY_BONE_SHAPES_FILE_PATH

    def rig_character(self):
        cache_enabled = self.context.window_manager.cache_enabled
        filepath = get_cache(cache_enabled).get(self.rigify_bone_shapes_file_path) or self.blender_operator.filepath

        if not filepath:
            bpy.ops.hoyoverse.rig_character(
                'INVOKE_DEFAULT',
                next_step_idx=self.blender_operator.next_step_idx, 
                file_directory=self.blender_operator.file_directory,
                invoker_type=self.blender_operator.invoker_type,
                high_level_step_name=self.blender_operator.high_level_step_name,
                game_type=self.blender_operator.game_type,
            )
            return {'FINISHED'}

        armature = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE'][0]
        hand_bones = [bone for bone in armature.pose.bones.values() if 'Hand' in bone.name]
        number_of_hand_bone_children = max([len(hand_bone.children) for hand_bone in hand_bones])
        is_player_hand = number_of_hand_bone_children >= 5

        if not is_player_hand:
            self.blender_operator.report(
                {'ERROR'}, \
                '\n\n[INFO] Setup Wizard has finished setup and stopped before attempting to rig character.\n'
                'Only Playable characters are supported.\n'
                'If you are rigging a playable character and you see this, please report which character you are using.\n'
            )
            return

        character_rigger_props: CharacterRiggerPropertyGroup = self.context.scene.character_rigger_props
        rig_character(
            filepath,
            not character_rigger_props.allow_arm_ik_stretch,
            not character_rigger_props.allow_leg_ik_stretch,
            character_rigger_props.use_arm_ik_poles,
            character_rigger_props.use_leg_ik_poles,
            character_rigger_props.add_children_of_constraints,
            character_rigger_props.use_head_tracker
        )

        # head_tracker_constraint_influence = 1.0 if character_rigger_props.use_head_tracker else 0.0
        # self.__set_head_tracker_constraint_influence(head_tracker_constraint_influence)

        self.blender_operator.report({'INFO'}, 'Successfully rigged character')
        if cache_enabled and filepath:
            cache_using_cache_key(get_cache(cache_enabled), self.rigify_bone_shapes_file_path, filepath)

        NextStepInvoker().invoke(
            self.blender_operator.next_step_idx,
            self.blender_operator.invoker_type,
            file_path_to_cache=filepath,
            high_level_step_name=self.blender_operator.high_level_step_name,
            game_type=GameType.GENSHIN_IMPACT.name
        )

    # @staticmethod
    # def __set_head_tracker_constraint_influence(influence_value):
    #     character_rig = [data_obj for data_obj in bpy.data.objects if data_obj.type == 'ARMATURE' and 'Rig' in data_obj.name][0]

    #     bpy.data.objects[character_rig.name].pose.bones['head'].constraints['Damped Track'].influence = influence_value
    #     bpy.data.objects[character_rig.name].pose.bones['head-controller'].constraints['Damped Track'].influence = influence_value

class HonkaiStarRailCharacterRigger(CharacterRigger):
    def __init__(self, blender_operator, context):
        self.blender_operator = blender_operator
        self.context = context
        self.rigify_bone_shapes_file_path = 'PLACEHOLDER'

    def rig_character(self):
        return
