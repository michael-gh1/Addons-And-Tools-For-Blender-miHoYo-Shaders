# Author: michael-gh1

import bpy

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator

from setup_wizard.setup_wizard_operator_base_classes import CustomOperatorProperties

from setup_wizard.import_order import GENSHIN_RIGIFY_BONE_SHAPES_FILE_PATH, cache_using_cache_key, get_cache


class GI_OT_RootShape_FilePath_Setter_Operator(Operator, ImportHelper, CustomOperatorProperties):
    """Set a different RootShape blend file to use"""
    bl_idname = "hoyoverse.rootshape_filepath_setter"
    bl_label = "Select RootShape File"

    # ImportHelper mixin class uses this
    filename_ext = "*.*"

    import_path: StringProperty(
        name="Path",
        description="Root_Shape .blend File",
        default="",
        subtype='DIR_PATH'
    )

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        try:
            rigify_bone_shapes_file_path = GENSHIN_RIGIFY_BONE_SHAPES_FILE_PATH
            cache_using_cache_key(get_cache(), rigify_bone_shapes_file_path, self.filepath)
        except Exception as ex:
            raise ex
        finally:
            super().clear_custom_properties()
        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory(GI_OT_RootShape_FilePath_Setter_Operator)
