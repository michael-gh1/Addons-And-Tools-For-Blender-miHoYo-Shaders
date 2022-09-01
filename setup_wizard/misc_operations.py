# Written by Mken from Discord

import bpy

from bpy.props import StringProperty, IntProperty
from bpy.types import Operator

from setup_wizard.import_order import invoke_next_step
from setup_wizard.models import CustomOperatorProperties


class GI_OT_SetColorManagementToStandard(Operator, CustomOperatorProperties):
    '''Sets Color Management to Standard'''
    bl_idname = 'genshin.set_color_management_to_standard'
    bl_label = 'Genshin: Set Color Management to Standard'

    def execute(self, context):
        bpy.context.scene.view_settings.view_transform = 'Standard'

        if self.next_step_idx:
            invoke_next_step(self.next_step_idx)
        return {'FINISHED'}


class GI_OT_DeleteSpecificObjects(Operator):
    '''Deletes EffectMesh'''
    bl_idname = 'genshin.delete_specific_objects'
    bl_label = 'Genshin: Delete EffectMesh'

    next_step_idx: IntProperty()
    file_directory: StringProperty()  # Unused, but necessary for import_order to execute/invoke

    def execute(self, context):
        scene = bpy.context.scene
        objects_to_delete = [
            'EffectMesh'
        ]

        for object in scene.objects:
            if object.name in objects_to_delete:
                bpy.data.objects.remove(object)

        if self.next_step_idx:
            invoke_next_step(self.next_step_idx)
        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory([
    GI_OT_SetColorManagementToStandard,
    GI_OT_DeleteSpecificObjects
])
