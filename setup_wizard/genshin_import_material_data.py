# Author: michael-gh1

import bpy

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, CollectionProperty, PointerProperty
from bpy.types import Operator, PropertyGroup
from setup_wizard.domain.outline_material_data import OutlineMaterialGroup

from setup_wizard.import_order import NextStepInvoker
from setup_wizard.material_data_import_setup.game_material_data_importers import GameMaterialDataImporterFactory
from setup_wizard.setup_wizard_operator_base_classes import CustomOperatorProperties
from setup_wizard.parsers.material_data_json_parsers import HoyoStudioMaterialDataJsonParser, UABEMaterialDataJsonParser

WEAPON_NAME_IDENTIFIER = 'Mat'


class GI_OT_GenshinImportMaterialData(Operator, ImportHelper, CustomOperatorProperties):
    """Select the Character Material Data Json Files for Outlines"""
    bl_idname = "genshin.import_material_data"  # important since its how we chain file dialogs
    bl_label = "Genshin: Select Material Json Data Files"

    bpy.types.Scene.setup_wizard_material_for_material_data_import = PointerProperty(
        name='Target Material',
        type=bpy.types.Material
    )

    bpy.types.Scene.setup_wizard_outlines_material_for_material_data_import = PointerProperty(
        name='Outlines Material',
        type=bpy.types.Material
    )

    # ImportHelper mixin class uses this
    filename_ext = "*.*"

    import_path: StringProperty(
        name="Path",
        description="Path to the material json data files",
        default="",
        subtype='DIR_PATH'
    )

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    files: CollectionProperty(type=PropertyGroup)

    parsers = [
        HoyoStudioMaterialDataJsonParser,
        UABEMaterialDataJsonParser,
    ]

    def execute(self, context):
        selected_material = context.scene.setup_wizard_material_for_material_data_import
        outlines_material = context.scene.setup_wizard_outlines_material_for_material_data_import

        outline_material_group: OutlineMaterialGroup = OutlineMaterialGroup(selected_material, outlines_material)

        game_material_data_importer = GameMaterialDataImporterFactory.create(self.game_type, self, context, outline_material_group)
        game_material_data_importer.import_material_data()

        self.report({'INFO'}, 'Imported material data')
        if self.filepath or self.files:
            NextStepInvoker().invoke(
                self.next_step_idx, 
                self.invoker_type, 
                high_level_step_name=self.high_level_step_name,
                game_type=self.game_type,
            )
        super().clear_custom_properties()
        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory(GI_OT_GenshinImportMaterialData)
