# Author: michael-gh1

import bpy

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
import os

from setup_wizard.import_order import NextStepInvoker, cache_using_cache_key, get_cache, \
    FESTIVITY_ROOT_FOLDER_FILE_PATH, FESTIVITY_SHADER_FILE_PATH
from setup_wizard.models import BasicSetupUIOperator, CustomOperatorProperties
from setup_wizard.utils import material_utils

DEFAULT_BLEND_FILE_WITH_GENSHIN_MATERIALS = 'miHoYo - Genshin Impact.blend'
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
    """Select Festivity's Shader .blend File to import materials"""
    bl_idname = "genshin.import_materials"  # important since its how we chain file dialogs
    bl_label = "Genshin: Import Materials - Select Festivity's .blend File"

    # ImportHelper mixin class uses this
    filename_ext = "*.*"

    import_path: StringProperty(
        name="Path",
        description="Festivity's Shader .blend File",
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
        user_selected_shader_blend_file_path = self.filepath if self.filepath and not os.path.isdir(self.filepath) \
            else get_cache(cache_enabled).get(FESTIVITY_SHADER_FILE_PATH)
        project_root_directory_file_path = self.file_directory \
            or get_cache(cache_enabled).get(FESTIVITY_ROOT_FOLDER_FILE_PATH) \
            or os.path.dirname(self.filepath)

        if not user_selected_shader_blend_file_path and not project_root_directory_file_path:
            # Use Case: Advanced Setup
            # The Operator is Executed directly with no cached files and so we need to Invoke to prompt the user
            bpy.ops.genshin.import_materials(
                'INVOKE_DEFAULT',
                next_step_idx=self.next_step_idx, 
                file_directory=self.file_directory,
                invoker_type=self.invoker_type,
                high_level_step_name=self.high_level_step_name
            )
            return {'FINISHED'}

        blend_file_with_genshin_materials = os.path.join(
            user_selected_shader_blend_file_path,
            MATERIAL_PATH_INSIDE_BLEND_FILE
        ) if user_selected_shader_blend_file_path else None

        default_blend_file_path = os.path.join(
            project_root_directory_file_path,
            DEFAULT_BLEND_FILE_WITH_GENSHIN_MATERIALS,
            MATERIAL_PATH_INSIDE_BLEND_FILE
        )

        try:
            # Use the exact file the user selected, otherwise fallback to the non-Goo blender file in the directory
            shader_blend_file_path = blend_file_with_genshin_materials or default_blend_file_path
            bpy.ops.wm.append(
                directory=shader_blend_file_path,
                files=NAMES_OF_GENSHIN_MATERIALS
            )
        except RuntimeError as ex:
            super().clear_custom_properties()
            self.report({'ERROR'}, \
                f"ERROR: Error when trying to append materials. \n\
                Did not find `{DEFAULT_BLEND_FILE_WITH_GENSHIN_MATERIALS}` in the directory you selected. \n\
                Try selecting the exact blend file you want to use.")
            raise ex

        self.report({'INFO'}, 'Imported Shader/Genshin Materials...')
        if cache_enabled and (user_selected_shader_blend_file_path or project_root_directory_file_path):
            if user_selected_shader_blend_file_path:
                cache_using_cache_key(get_cache(cache_enabled), FESTIVITY_SHADER_FILE_PATH, user_selected_shader_blend_file_path)
            else:
                cache_using_cache_key(get_cache(cache_enabled), FESTIVITY_ROOT_FOLDER_FILE_PATH, project_root_directory_file_path)

        # Add fake user to prevent unused materials from being cleaned up
        genshin_materials = [bpy.data.materials.get(genshin_material_name.get('name')) for genshin_material_name in NAMES_OF_GENSHIN_MATERIALS]
        material_utils.add_fake_user_to_materials(genshin_materials)

        NextStepInvoker().invoke(
            self.next_step_idx, 
            self.invoker_type, 
            file_path_to_cache=project_root_directory_file_path,
            high_level_step_name=self.high_level_step_name
        )
        super().clear_custom_properties()
        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory(GI_OT_GenshinImportMaterials)
