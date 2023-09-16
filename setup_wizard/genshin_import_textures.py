# Author: michael-gh1
# Originally contributed by Zekium and Modder4869 from Discord

import bpy

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
from setup_wizard.material_import_setup.material_default_value_setters import MaterialDefaultValueSetterFactory

from setup_wizard.setup_wizard_operator_base_classes import CustomOperatorProperties
from setup_wizard.texture_import_setup.game_texture_importers import GameTextureImporter, GameTextureImporterFactory
from setup_wizard.texture_import_setup.texture_importer_service import TextureImporterService


class GI_OT_GenshinImportTextures(Operator, ImportHelper, CustomOperatorProperties):
    """Select the folder with the model's textures to import"""
    bl_idname = "genshin.import_textures"  # important since its how we chain file dialogs
    bl_label = "Select Character Folder"

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
        game_texture_importer: GameTextureImporter = \
            GameTextureImporterFactory.create(self.game_type, self, context)
        material_default_value_setter = MaterialDefaultValueSetterFactory.create(self.game_type, self, context)

        texture_importer_service = TextureImporterService(game_texture_importer, material_default_value_setter)
        status = texture_importer_service.import_textures()

        if status == {'FINISHED'}:
            texture_importer_service.set_default_values()

        super().clear_custom_properties()
        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory(GI_OT_GenshinImportTextures)
