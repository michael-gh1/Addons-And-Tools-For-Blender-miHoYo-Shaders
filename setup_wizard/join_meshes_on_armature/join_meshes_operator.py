# Author: michael-gh1

import bpy
from bpy.types import Operator

from setup_wizard.domain.game_types import GameType
from setup_wizard.import_order import NextStepInvoker
from setup_wizard.setup_wizard_operator_base_classes import CustomOperatorProperties


class GI_OT_JoinMeshesOnArmature(Operator, CustomOperatorProperties):
    '''Joins Meshes on Armature'''
    bl_idname = 'hoyoverse.join_meshes_on_armature'
    bl_label = 'HoYoverse: Join Meshes on Armature'

    def execute(self, context):
        is_advanced_setup = self.high_level_step_name != 'GENSHIN_OT_setup_wizard_ui' and \
            self.high_level_step_name != 'GENSHIN_OT_setup_wizard_ui_no_outlines' and \
            self.high_level_step_name != 'GENSHIN_OT_finish_setup'
        join_meshes_enabled = self.game_type == GameType.GENSHIN_IMPACT.name and \
            (bpy.context.window_manager.setup_wizard_join_meshes_enabled or is_advanced_setup)

        if join_meshes_enabled:
            character_model = None
            for object in bpy.context.scene.objects:
                if object.type == 'ARMATURE':
                    character_model = object
                    continue

            character_model_body = [body_part for body_part in character_model.children if body_part.name == 'Body'][0]
            character_model_children = [body_part for body_part in character_model.children if body_part]

            for character_model_child in character_model_children:
                print(f'Selecting {character_model_child} to join')
                character_model_child.select_set(True)
            bpy.context.view_layer.objects.active = character_model_body
            print(f'Joining children body parts to {character_model_body}')
            bpy.ops.object.join()

        if self.next_step_idx:
            NextStepInvoker().invoke(
                self.next_step_idx, 
                self.invoker_type, 
                high_level_step_name=self.high_level_step_name,
                game_type=self.game_type,
            )
        return {'FINISHED'}
