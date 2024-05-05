# Author: michael-gh1

import functools

import bpy
from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator

from setup_wizard.setup_wizard_operator_base_classes import CustomOperatorProperties
from setup_wizard.setup_wizard_operator_base_classes import NextStepInvoker

'''
While this Operator technically works in changing bpy.context, the Blender UI
does not update if you're only running EXEC_DEFAULTs which don't have the
Blender UI updating between calls.

You would need to have an INVOKE_DEFAULT with a window manager apppearing (such as a
file explorer) in order to switch context (ex. bpy.context.type.area to NODE_EDITOR) and
have a chained Operator have this new context.
'''
class GI_OT_Change_BPY_Context(Operator, CustomOperatorProperties):
    '''Change bpy context'''
    bl_idname = 'genshin.change_bpy_context'
    bl_label = 'Genshin: Change bpy context'

    bpy_context_attr: StringProperty()
    bpy_context_value_str: StringProperty()
    bpy_context_value_bool: BoolProperty()

    def execute(self, context):
        try:
            self.rsetattr(  
                bpy.context, 
                self.bpy_context_attr, 
                (self.bpy_context_value_str or self.bpy_context_value_bool)
            )
            self.invoke_next_step()
        except Exception as ex:
            raise ex
        finally:
            super().clear_custom_properties()
        return {'FINISHED'}

    def invoke_next_step(self):
        if self.next_step_idx:
            NextStepInvoker().invoke(
                self.next_step_idx, 
                self.invoker_type, 
                high_level_step_name=self.high_level_step_name,
                game_type=self.game_type,
            )
        self.clear_custom_properties()
        return {'FINISHED'}

    # This allows us to setattr with nested attributes
    # source: https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-subobjects-chained-properties
    def rsetattr(self, obj, attr, val):
        pre, _, post = attr.rpartition('.')
        return setattr(self.rgetattr(obj, pre) if pre else obj, post, val)

    def rgetattr(self, obj, attr, *args):
        def _getattr(obj, attr):
            return getattr(obj, attr, *args)
        return functools.reduce(_getattr, [obj] + attr.split('.'))

    def clear_custom_properties(self):
        self.bpy_context_attr = ''
        self.bpy_context_value_str = ''
        self.bpy_context_value_bool = False
        super().clear_custom_properties()
