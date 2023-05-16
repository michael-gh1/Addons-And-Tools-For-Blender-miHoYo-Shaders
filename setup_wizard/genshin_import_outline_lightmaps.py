# Author: michael-gh1

import bpy

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
from setup_wizard.import_order import NextStepInvoker
from setup_wizard.setup_wizard_operator_base_classes import CustomOperatorProperties
from setup_wizard.texture_import_setup.outline_texture_importers import OutlineTextureImporter, OutlineTextureImporterFactory


class GI_OT_GenshinImportOutlineLightmaps(Operator, ImportHelper, CustomOperatorProperties):
    """Select the folder with the character's lightmaps to import"""
    bl_idname = "genshin.import_outline_lightmaps"  # important since its how we chain file dialogs
    bl_label = "Genshin: Import Lightmaps - Select Character Model Folder"

    # ImportHelper mixin class uses this
    filename_ext = "*.*"

    import_path: StringProperty(
        name="Path",
        description="Path to the folder of the Model",
        default="",
        subtype='DIR_PATH'
    )

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        outline_texture_importer: OutlineTextureImporter = OutlineTextureImporterFactory.create(self.game_type, self, context)
        outline_texture_importer.import_textures()

        NextStepInvoker().invoke(
            self.next_step_idx, 
            self.invoker_type, 
            high_level_step_name=self.high_level_step_name,
            game_type=self.game_type,
        )
        super().clear_custom_properties()
        return {'FINISHED'}

register, unregister = bpy.utils.register_classes_factory(GI_OT_GenshinImportOutlineLightmaps)
