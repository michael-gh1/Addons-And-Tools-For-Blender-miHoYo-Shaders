# Written by Mken from Discord

import bpy

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, IntProperty
from bpy.types import Operator

try:
    from setup_wizard.import_order import invoke_next_step
except Exception:
    print('Error! Run the first step of setup_wizard! Need to set up python script paths')


class GI_OT_SetColorManagementToStandard(Operator):
    '''Sets Color Management to Standard'''
    bl_idname = 'file.set_color_management_to_standard'
    bl_label = 'Set Color Management to Standard'

    next_step_idx: IntProperty()
    file_directory: StringProperty()

    def execute(self, context):
        bpy.context.scene.view_settings.view_transform = 'Standard'

        if self.next_step_idx:
            invoke_next_step(self.next_step_idx)
        return {'FINISHED'}


class GI_OT_DeleteSpecificObjects(Operator):
    '''Deletes EffectMesh'''
    bl_idname = 'file.delete_specific_objects'
    bl_label = 'Delete EffectMesh'

    next_step_idx: IntProperty()
    file_directory: StringProperty()

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
