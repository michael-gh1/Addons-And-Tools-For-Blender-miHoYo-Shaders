# Author: michael-gh1

import bpy
import os

from setup_wizard.character_rig_setup.rig_script import rig_character
from setup_wizard.character_rig_setup.npc_rig_script import rig_character as rig_npc
from setup_wizard.character_rig_setup.hsr_rig_script import rig_character as hsr_rig_character

from abc import ABC, abstractmethod
from bpy.types import Armature, Operator, Context

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
        elif game_type == GameType.PUNISHING_GRAY_RAVEN.name:
            return PunishingGrayRavenCharacterRigger(blender_operator, context)
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
            filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'RootShape.blend')

        armature = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE'][0]
        hand_bones = [bone for bone in armature.pose.bones.values() if 'Hand' in bone.name]
        number_of_hand_bone_children = max([len(hand_bone.children) for hand_bone in hand_bones])
        is_player_hand = number_of_hand_bone_children >= 5

        character_rigger_props: CharacterRiggerPropertyGroup = self.context.scene.character_rigger_props

        # Important that the Armature is selected before performing rigging operations
        bpy.ops.object.select_all(action='DESELECT')
        armature: Armature = [object for object in bpy.data.objects if object.type == 'ARMATURE'][0]  # expecting 1 armature
        bpy.context.view_layer.objects.active = armature
        armature.select_set(True)

        meshes_joined = not (bpy.data.objects.get('Body') and bpy.data.objects.get('Face'))
        if [material for material in bpy.data.materials.values() if 'Paimon' in material.name]:
            rig_npc(
                filepath,
                not character_rigger_props.allow_arm_ik_stretch,
                not character_rigger_props.allow_leg_ik_stretch,
                character_rigger_props.use_arm_ik_poles,
                character_rigger_props.use_leg_ik_poles,
                character_rigger_props.add_children_of_constraints,
                character_rigger_props.use_head_tracker,
            )
        elif not is_player_hand:
            rig_npc(
                filepath,
                not character_rigger_props.allow_arm_ik_stretch,
                not character_rigger_props.allow_leg_ik_stretch,
                character_rigger_props.use_arm_ik_poles,
                character_rigger_props.use_leg_ik_poles,
                character_rigger_props.add_children_of_constraints,
                character_rigger_props.use_head_tracker,
            )                                 
        else:
            rig_character(
                filepath,
                not character_rigger_props.allow_arm_ik_stretch,
                not character_rigger_props.allow_leg_ik_stretch,
                character_rigger_props.use_arm_ik_poles,
                character_rigger_props.use_leg_ik_poles,
                character_rigger_props.add_children_of_constraints,
                character_rigger_props.use_head_tracker,
                meshes_joined=meshes_joined
            )

        # head_tracker_constraint_influence = 1.0 if character_rigger_props.use_head_tracker else 0.0
        # self.__set_head_tracker_constraint_influence(head_tracker_constraint_influence)

        self.blender_operator.report({'INFO'}, 'Successfully rigged character')

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
        armature = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE'][0]

        # Important that the Armature is selected before performing rigging operations
        bpy.ops.object.select_all(action='DESELECT')
        armature: Armature = [object for object in bpy.data.objects if object.type == 'ARMATURE'][0]  # expecting 1 armature
        bpy.context.view_layer.objects.active = armature
        armature.select_set(True)

        hsr_rig_character()


class PunishingGrayRavenCharacterRigger(CharacterRigger):
    def __init__(self, blender_operator, context):
        self.blender_operator = blender_operator
        self.context = context
        self.rigify_bone_shapes_file_path = 'PLACEHOLDER'

    def rig_character(self):
        return
