from bpy.props import IntProperty, StringProperty

from setup_wizard.import_order import NextStepInvoker

class CustomOperatorProperties:
    next_step_idx: IntProperty()
    file_directory: StringProperty()
    invoker_type: StringProperty()
    high_level_step_name: StringProperty()


class BasicSetupUIOperator:
    def execute(self, context):
        next_step_index = 0

        NextStepInvoker().invoke(
            next_step_index,
            'invoke_next_step_ui', 
            high_level_step_name=self.bl_idname
        )
        return {'FINISHED'}
