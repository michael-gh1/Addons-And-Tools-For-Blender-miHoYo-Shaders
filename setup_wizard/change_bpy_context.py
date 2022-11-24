# Author: michael-gh1

import functools

import bpy
from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator

from setup_wizard.models import CustomOperatorProperties

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
        self.rsetattr(  
            bpy.context, 
            self.bpy_context_attr, 
            (self.bpy_context_value_str or self.bpy_context_value_bool)
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
        self.bpy_context_value_bool = ''
        super().clear_custom_properties()
