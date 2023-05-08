# Author: michael-gh1

import bpy

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator

from setup_wizard.material_import_setup.game_material_importers import GameMaterialImporterFactory
from setup_wizard.material_import_setup.material_importer_service import MaterialImporterService
from setup_wizard.models import BasicSetupUIOperator, CustomOperatorProperties


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
        try:
            game_material_importer = GameMaterialImporterFactory.create(self.game_type, self, context)

            material_importer_service = MaterialImporterService(game_material_importer)
            material_importer_service.import_materials()
        except RuntimeError as ex:
            # Catch error when running bpy.ops.wm.append()
            super().clear_custom_properties()
            self.report({'ERROR'}, \
                f"ERROR: Error when trying to append materials. \n\
                Did not find `{game_material_importer.game_default_blend_file_with_materials}` in the directory you selected. \n\
                Try selecting the exact blend file you want to use.")
            raise ex
        finally:
            super().clear_custom_properties()
        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory(GI_OT_GenshinImportMaterials)
