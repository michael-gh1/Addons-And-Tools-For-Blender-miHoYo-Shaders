# Author: michael-gh1

import bpy

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator

from setup_wizard.outline_import_setup.game_outline_importer_service import GameOutlineImporterService
from setup_wizard.outline_import_setup.outline_importers import GameOutlineImporterFactory

from setup_wizard.import_order import NextStepInvoker
from setup_wizard.setup_wizard_operator_base_classes import BasicSetupUIOperator, CustomOperatorProperties


class GI_OT_SetUpOutlines(Operator, BasicSetupUIOperator):
    '''Sets Up Outlines'''
    bl_idname = 'genshin.set_up_outlines'
    bl_label = 'Genshin: Set Up Outlines (UI)'


class GI_OT_GenshinImportOutlines(Operator, ImportHelper, CustomOperatorProperties):
    """Select the .blend file with the outlines node group to import"""
    bl_idname = "genshin.import_outlines"  # important since its how we chain file dialogs
    bl_label = "Select Outlines File"

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
        try:
            game_outline_importer = GameOutlineImporterFactory.create(self.game_type, self, context)

            outline_importer_service = GameOutlineImporterService(game_outline_importer)
            outline_importer_service.import_outlines()
        except Exception as ex:
            raise ex
        finally:
            super().clear_custom_properties()

        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory(GI_OT_GenshinImportOutlines)
