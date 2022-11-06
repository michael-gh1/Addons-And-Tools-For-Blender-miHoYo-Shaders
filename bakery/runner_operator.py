import bpy

from bpy.types import Operator

class B_OT_Bakery(Operator):
    """Execute batch job"""
    bl_idname = "b.bakery"
    bl_label = "Bakery: Execute Batch Job"

    def exec(self, context):
        pass

