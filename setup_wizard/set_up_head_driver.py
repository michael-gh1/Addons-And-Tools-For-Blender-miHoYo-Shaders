# Written by Mken from Discord

import bpy
from bpy.props import StringProperty, IntProperty
from bpy.types import Operator

from setup_wizard.import_order import invoke_next_step

HEAD_DRIVER_OBJECT_NAME = 'Head Driver'


class GI_OT_SetUpHeadDriver(Operator):
    '''Sets up Head Driver'''
    bl_idname = 'genshin.setup_head_driver'
    bl_label = 'Genshin: Setup HeadDriver'

    next_step_idx: IntProperty()
    file_directory: StringProperty()  # Unused, but necessary for import_order to execute/invoke

    def execute(self, context):
        head_driver_object = bpy.data.objects.get(HEAD_DRIVER_OBJECT_NAME)
        child_of_constraint = head_driver_object.constraints[0]  # expecting 1 constraint head driver

        armature = [object for object in bpy.data.objects if object.type == 'ARMATURE'][0]  # expecting 1 armature
        armature_bones = armature.data.bones
        head_bone_name = [bone_name for bone_name in armature_bones.keys() if 'Head' in bone_name][0]  # expecting 1 bone with Head in the name

        self.set_contraint_target_and_bone(child_of_constraint, armature, head_bone_name)
        self.set_inverse(head_driver_object)

        if self.next_step_idx:
            invoke_next_step(self.next_step_idx)
        return {'FINISHED'}

    def set_contraint_target_and_bone(self, constraint, armature, bone_name):
        constraint.target = armature
        constraint.subtarget = bone_name

    def set_inverse(self, object):
        bpy.context.view_layer.objects.active = object
        bpy.ops.constraint.childof_set_inverse(constraint="Child Of", owner='OBJECT')


register, unregister = bpy.utils.register_classes_factory(GI_OT_SetUpHeadDriver)
