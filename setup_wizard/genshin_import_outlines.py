# Author: michael-gh1

import bpy

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
import os
from setup_wizard.domain.game_types import GameType

from setup_wizard.import_order import FESTIVITY_OUTLINES_FILE_PATH, NYA222_HONKAI_STAR_RAIL_OUTLINES_FILE_PATH, NextStepInvoker, cache_using_cache_key, get_cache
from setup_wizard.models import BasicSetupUIOperator, CustomOperatorProperties


class GI_OT_SetUpOutlines(Operator, BasicSetupUIOperator):
    '''Sets Up Outlines'''
    bl_idname = 'genshin.set_up_outlines'
    bl_label = 'Genshin: Set Up Outlines (UI)'


class GI_OT_GenshinImportOutlines(Operator, ImportHelper, CustomOperatorProperties):
    """Select the `miHoYo - Outlines.blend` file to import Outlines"""
    bl_idname = "genshin.import_outlines"  # important since its how we chain file dialogs
    bl_label = "Genshin: Select `miHoYo - Outlines.blend`"

    # ImportHelper mixin class uses this
    filename_ext = "*.*"
    
    import_path: StringProperty(
        name = "Path",
        description = "Path to the folder containing the files to import",
        default = "",
        subtype = 'DIR_PATH'
        )

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        if not bpy.data.node_groups.get('miHoYo - Outlines'):
            outlines_file_path = FESTIVITY_OUTLINES_FILE_PATH if self.game_type == GameType.GENSHIN_IMPACT.name else \
                NYA222_HONKAI_STAR_RAIL_OUTLINES_FILE_PATH
            cache_enabled = context.window_manager.cache_enabled
            inner_path = 'NodeTree'
            object_name = 'miHoYo - Outlines'
            filepath = get_cache(cache_enabled).get(outlines_file_path) or self.filepath

            if not filepath:
                bpy.ops.genshin.import_outlines(
                    'INVOKE_DEFAULT',
                    next_step_idx=self.next_step_idx, 
                    file_directory=self.file_directory,
                    invoker_type=self.invoker_type,
                    high_level_step_name=self.high_level_step_name,
                    game_type=self.game_type,
                )
                return {'FINISHED'}
            bpy.ops.wm.append(
                filepath=os.path.join(filepath, inner_path, object_name),
                directory=os.path.join(filepath, inner_path),
                filename=object_name
            )
            if cache_enabled and filepath:
                cache_using_cache_key(get_cache(cache_enabled), outlines_file_path, filepath)

        NextStepInvoker().invoke(
            self.next_step_idx, 
            self.invoker_type,
            high_level_step_name=self.high_level_step_name,
            game_type=self.game_type,
        )
        super().clear_custom_properties()
        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory(GI_OT_GenshinImportOutlines)
