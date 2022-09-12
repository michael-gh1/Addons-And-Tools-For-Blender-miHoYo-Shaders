# Author: michael-gh1

from bpy.props import IntProperty, StringProperty

from setup_wizard.import_order import NextStepInvoker

class CustomOperatorProperties:
    next_step_idx: IntProperty()
    file_directory: StringProperty()
    invoker_type: StringProperty()
    high_level_step_name: StringProperty()

    '''
    Modules will be registered and store previous choices within the same Blender file instance/session.
    This method will reset all values in the module in order for previous state to persist.
    
    Scenario: After running Setup Wizard, Import Material Data would run the next steps in the Setup Wizard.
    This would occur despite running the individual component in Advanced Setup.
    '''
    def clear_custom_properties(self):
        self.filepath = ''  # Important! UI saves previous choices to the Operator instance
        self.next_step_idx = -1
        self.file_directory = ''
        self.invoker_type = ''
        self.high_level_step_name = ''


class BasicSetupUIOperator:
    def execute(self, context):
        next_step_index = 0

        NextStepInvoker().invoke(
            next_step_index,
            'invoke_next_step_ui', 
            high_level_step_name=self.bl_idname
        )
        return {'FINISHED'}
