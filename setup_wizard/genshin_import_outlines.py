# Structure for class comes from a script initially written by Zekium from Discord
# Written by Mken from Discord

import bpy

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, IntProperty
from bpy.types import Operator
import os

from setup_wizard.import_order import FESTIVITY_OUTLINES_FILE_PATH, cache_using_cache_key, get_cache, invoke_next_step


class GI_OT_GenshinImportOutlines(Operator, ImportHelper):
    """Select the `miHoYo - Outlines` to import Outlines"""
    bl_idname = "genshin.import_outlines"  # important since its how we chain file dialogs
    bl_label = "Genshin: Select with `miHoYo - Outlines`"

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

    next_step_idx: IntProperty()
    file_directory: StringProperty()

    def execute(self, context):
        if not bpy.data.node_groups.get('miHoYo - Outlines'):
            inner_path = 'NodeTree'
            object_name = 'miHoYo - Outlines'
            filepath = get_cache().get(FESTIVITY_OUTLINES_FILE_PATH) or self.filepath

            if not filepath:
                bpy.ops.genshin.import_outlines('INVOKE_DEFAULT')
                return {'FINISHED'}
            bpy.ops.wm.append(
                filepath=os.path.join(filepath, inner_path, object_name),
                directory=os.path.join(filepath, inner_path),
                filename=object_name
            )
            cache_using_cache_key(get_cache(), FESTIVITY_OUTLINES_FILE_PATH, filepath)
        invoke_next_step(self.next_step_idx)
        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory(GI_OT_GenshinImportOutlines)
