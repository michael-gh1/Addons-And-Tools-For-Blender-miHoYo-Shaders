# Author: michael-gh1

import bpy

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
import os

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator

DEFAULT_BLEND_FILE_WITH_ENVIRONMENT_MATERIALS = ''  # TODO: name
MATERIAL_PATH_INSIDE_BLEND_FILE = 'Material'

NAMES_OF_ENVIRONMENT_MATERIALS = [
    {'name': 'TODO'},  # TODO: name
]


class B_OT_GenshinEnvironmentImportEnvironmentMaterials(Operator, ImportHelper):
    """Import Environment Material (Shader)"""
    bl_idname = "genshin_environment.import_materials"
    bl_label = "Import Environ. Materials"

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
        user_selected_shader_blend_file_path = self.filepath if self.filepath and not os.path.isdir(self.filepath) else None
        project_root_directory_file_path = self.file_directory or os.path.dirname(self.filepath)

        blend_file_with_genshin_materials = os.path.join(
            user_selected_shader_blend_file_path,
            MATERIAL_PATH_INSIDE_BLEND_FILE
        ) if user_selected_shader_blend_file_path else None

        default_blend_file_path = os.path.join(
            project_root_directory_file_path,
            DEFAULT_BLEND_FILE_WITH_ENVIRONMENT_MATERIALS,
            MATERIAL_PATH_INSIDE_BLEND_FILE
        )

        try:
            # Use the exact file the user selected, otherwise fallback to the non-Goo blender file in the directory
            shader_blend_file_path = blend_file_with_genshin_materials or default_blend_file_path
            bpy.ops.wm.append(
                directory=shader_blend_file_path,
                files=NAMES_OF_ENVIRONMENT_MATERIALS
            )
        except RuntimeError as ex:
            super().clear_custom_properties()
            self.report({'ERROR'}, \
                f"ERROR: Error when trying to append materials. \n\
                Did not find `{DEFAULT_BLEND_FILE_WITH_ENVIRONMENT_MATERIALS}` in the directory you selected. \n\
                Try selecting the exact blend file you want to use.")
            raise ex

        self.report({'INFO'}, 'Imported Shader/Environment Materials...')
        return {'FINISHED'}
