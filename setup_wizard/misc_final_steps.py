# Author: michael-gh1

import bpy
from bpy.types import Armature, Operator

from setup_wizard.import_order import NextStepInvoker
from setup_wizard.setup_wizard_operator_base_classes import BasicSetupUIOperator, CustomOperatorProperties


class GI_OT_FinishSetup(Operator, BasicSetupUIOperator):
    '''Finish Setup'''
    bl_idname = 'genshin.finish_setup'
    bl_label = 'Genshin: Finish Setup (UI)'


class HSR_OT_FinishSetup(Operator, BasicSetupUIOperator):
    '''Finish Setup'''
    bl_idname = 'honkai_star_rail.finish_setup'
    bl_label = 'Honkai Star Rail: Finish Setup (UI)'


class GI_OT_FixTransformations(Operator, CustomOperatorProperties):
    '''Makes the Character Upright and Fixes Scale'''
    bl_idname = 'genshin.fix_transformations'
    bl_label = 'Genshin: Makes Character Upright and Fixes Scale'

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        armature: Armature = [object for object in bpy.data.objects if object.type == 'ARMATURE'][0]  # expecting 1 armature
        armature.select_set(True)

        # I don't want to modify any characters unless absolutely necessary
        # So, as Dehya comes with keyframes and is not in an A-Pose by default, let's clean her character
        #   - This must be done before the rigging step, otherwise the rig setup will not be upright!
        if 'Dehya' in armature.name and armature.animation_data:
            self.clean_character(armature)

        bpy.ops.object.scale_clear()
        bpy.ops.object.rotation_clear()
        armature.rotation_euler[0] = 1.5708  # x-axis, 90 degrees
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)  # needed if you rotate using the above

        # clean rotation
        # bpy.ops.transform.rotate(
        #     value=1.5708, 
        #     orient_axis='X', 
        #     orient_type='GLOBAL', 
        #     orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), 
        #     orient_matrix_type='GLOBAL', 
        #     constraint_axis=(True, False, False), 
        #     mirror=False, 
        #     use_proportional_edit=False,
        #     proportional_edit_falloff='SMOOTH', 
        #     proportional_size=0.1, 
        #     use_proportional_connected=False, 
        #     use_proportional_projected=False
        # )  # from @M4urlcl0

        if self.next_step_idx:
            NextStepInvoker().invoke(
                self.next_step_idx, 
                self.invoker_type, 
                high_level_step_name=self.high_level_step_name,
                game_type=self.game_type,
            )
        return {'FINISHED'}

    def clean_character(self, armature):
        armature.animation_data_clear()
        self.reset_pose(armature)

    def reset_pose(self, armature):
        pose = armature.pose

        for bone in pose.bones:
            bone: bpy.types.PoseBone
            bone.matrix_basis.identity()


register, unregister = bpy.utils.register_classes_factory(GI_OT_FixTransformations)
