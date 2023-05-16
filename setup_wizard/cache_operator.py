# Author: michael-gh1

import bpy
from bpy.types import Operator

from setup_wizard.import_order import clear_cache
from setup_wizard.setup_wizard_operator_base_classes import CustomOperatorProperties

class ClearCacheOperator(Operator, CustomOperatorProperties):
    """Clears the cache"""
    bl_idname = "genshin.clear_cache_operator"  # important since its how we chain file dialogs
    bl_label = "Genshin: Clear Cache"

    def execute(self, context):
        clear_cache(self.game_type)
        return {'FINISHED'}

register, unregister = bpy.utils.register_classes_factory(ClearCacheOperator)
