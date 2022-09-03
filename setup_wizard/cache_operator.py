# Author: michael-gh1

import bpy
from bpy.types import Operator

from setup_wizard.import_order import clear_cache

class ClearCacheOperator(Operator):
    """Clears the cache"""
    bl_idname = "genshin.clear_cache_operator"  # important since its how we chain file dialogs
    bl_label = "Genshin: Clear Cache"

    def execute(self, context):
        clear_cache()
        return {'FINISHED'}

register, unregister = bpy.utils.register_classes_factory(ClearCacheOperator)
