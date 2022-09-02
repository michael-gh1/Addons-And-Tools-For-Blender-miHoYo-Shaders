import bpy

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
import os

from setup_wizard.import_order import FESTIVITY_ROOT_FOLDER_FILE_PATH, NextStepInvoker, cache_using_cache_key, get_cache
from setup_wizard.models import BasicSetupUIOperator, CustomOperatorProperties

BLEND_FILE_WITH_GENSHIN_MATERIALS = 'miHoYo - Genshin Impact.blend'
MATERIAL_PATH_INSIDE_BLEND_FILE = 'Material'

NAMES_OF_GENSHIN_MATERIALS = [
    {'name': 'miHoYo - Genshin Body'},
    {'name': 'miHoYo - Genshin Face'},
    {'name': 'miHoYo - Genshin Hair'},
    {'name': 'miHoYo - Genshin Outlines'}
]


class GI_OT_SetUpMaterials(Operator, BasicSetupUIOperator):
    '''Sets Up Materials'''
    bl_idname = 'genshin.set_up_materials'
    bl_label = 'Genshin: Set Up Materials (UI)'


class GI_OT_GenshinImportMaterials(Operator, ImportHelper, CustomOperatorProperties):
    """Select Festivity's Shaders folder to import materials"""
    bl_idname = "genshin.import_materials"  # important since its how we chain file dialogs
    bl_label = "Genshin: Import Materials - Select Festivity's Shaders Folder"

    # ImportHelper mixin class uses this
    filename_ext = "*.*"

    import_path: StringProperty(
        name="Path",
        description="Path to the folder of Festivity's Shaders project",
        default="",
        subtype='DIR_PATH'
    )

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        cache_enabled = context.window_manager.cache_enabled
        project_root_directory_file_path = self.file_directory \
            or get_cache(cache_enabled).get(FESTIVITY_ROOT_FOLDER_FILE_PATH) \
            or os.path.dirname(self.filepath)

        if not project_root_directory_file_path:
            bpy.ops.genshin.import_materials(
                'INVOKE_DEFAULT',
                next_step_idx=self.next_step_idx, 
                file_directory=self.file_directory,
                invoker_type=self.invoker_type,
                high_level_step_name=self.high_level_step_name
            )
            return {'FINISHED'}

        directory_with_blend_file_path = os.path.join(
            project_root_directory_file_path,
            BLEND_FILE_WITH_GENSHIN_MATERIALS,
            MATERIAL_PATH_INSIDE_BLEND_FILE
        )

        bpy.ops.wm.append(
            directory=directory_with_blend_file_path,
            files=NAMES_OF_GENSHIN_MATERIALS
        )

        self.report({'INFO'}, 'Imported Shader/Genshin Materials...')
        if cache_enabled and project_root_directory_file_path:
            cache_using_cache_key(get_cache(cache_enabled), FESTIVITY_ROOT_FOLDER_FILE_PATH, project_root_directory_file_path)

        self.filepath = ''  # Important! UI saves previous choices to the Operator instance
        NextStepInvoker().invoke(
            self.next_step_idx, 
            self.invoker_type, 
            file_path_to_cache=project_root_directory_file_path,
            high_level_step_name=self.high_level_step_name
        )
        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory(GI_OT_GenshinImportMaterials)
