# Author: michael-gh1

import bpy
from bpy.types import Operator

from setup_wizard.import_order import NextStepInvoker
from setup_wizard.models import CustomOperatorProperties


class GI_OT_SetColorManagementToStandard(Operator, CustomOperatorProperties):
    '''Sets Color Management to Standard'''
    bl_idname = 'genshin.set_color_management_to_standard'
    bl_label = 'Genshin: Set Color Management to Standard'

    def execute(self, context):
        bpy.context.scene.view_settings.view_transform = 'Standard'

        if self.next_step_idx:
            NextStepInvoker().invoke(
                self.next_step_idx, 
                self.invoker_type, 
                high_level_step_name=self.high_level_step_name
            )
        return {'FINISHED'}


class GI_OT_DeleteSpecificObjects(Operator, CustomOperatorProperties):
    '''Deletes EffectMesh'''
    bl_idname = 'genshin.delete_specific_objects'
    bl_label = 'Genshin: Delete EffectMesh'

    def execute(self, context):
        scene = bpy.context.scene
        objects_to_delete = [
            'EffectMesh'
        ]  # be extremely careful, we will be deleting anything that contains these object names

        for object in scene.objects:
            for object_to_delete in objects_to_delete:
                if object_to_delete in object.name and object.type == 'MESH':
                    bpy.data.objects.remove(object)

        if self.next_step_idx:
            NextStepInvoker().invoke(
                self.next_step_idx, 
                self.invoker_type, 
                high_level_step_name=self.high_level_step_name
            )
        return {'FINISHED'}


class GI_OT_SetUpArmTwistBoneConstraints(Operator, CustomOperatorProperties):
    '''Sets Up ArmTwist Bone Constraints'''
    bl_idname = 'genshin.set_up_armtwist_bone_constraints'
    bl_label = 'Genshin: Set Up ArmTwist Bone Constraints'

    def execute(self, context):
        armature =  [object for object in bpy.data.objects if object.type == 'ARMATURE'][0]
        armature_bones = armature.pose.bones

        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')

        upper_arm_bone = armature.data.edit_bones.get('Bip001 R Forearm')
        twist_bone = armature.data.edit_bones.get('+UpperArmTwist R A01')
        twist_bone.tail = upper_arm_bone.head

        twist_bone = armature.data.edit_bones.get('+UpperArmTwist R A02')
        twist_bone.tail = upper_arm_bone.head

        bpy.ops.object.mode_set(mode='OBJECT')

        twist_bone = armature_bones.get('+UpperArmTwist R A01')
        copy_rotation_constraint = twist_bone.constraints.new('COPY_ROTATION')
        copy_rotation_constraint.target = armature
        copy_rotation_constraint.subtarget = 'Bip001 R Forearm'

        copy_rotation_constraint.use_x = False
        copy_rotation_constraint.use_z = False

        copy_rotation_constraint.target_space = 'LOCAL'
        copy_rotation_constraint.owner_space = 'LOCAL'

        copy_rotation_constraint.influence = 0.35

        twist_bone = armature_bones.get('+UpperArmTwist R A02')
        copy_rotation_constraint = twist_bone.constraints.new('COPY_ROTATION')
        copy_rotation_constraint.target = armature
        copy_rotation_constraint.subtarget = 'Bip001 R Forearm'

        copy_rotation_constraint.use_x = False
        copy_rotation_constraint.use_z = False

        copy_rotation_constraint.target_space = 'LOCAL'
        copy_rotation_constraint.owner_space = 'LOCAL'

        copy_rotation_constraint.influence = 0.65

        print(twist_bone)

        if self.next_step_idx:
            NextStepInvoker().invoke(
                self.next_step_idx, 
                self.invoker_type, 
                high_level_step_name=self.high_level_step_name
            )
        return {'FINISHED'}


    def reorient_armtwist_bones(self):
        pass

    def set_up_bone_constarint(self):
        pass


register, unregister = bpy.utils.register_classes_factory([
    GI_OT_SetColorManagementToStandard,
    GI_OT_DeleteSpecificObjects,
    GI_OT_SetUpArmTwistBoneConstraints,
])
