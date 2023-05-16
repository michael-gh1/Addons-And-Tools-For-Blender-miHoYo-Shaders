# Author: michael-gh1

import bpy

from bpy.props import StringProperty
from bpy.types import Operator

from setup_wizard.import_order import NextStepInvoker
from setup_wizard.import_order import get_actual_material_name_for_dress
from setup_wizard.setup_wizard_operator_base_classes import CustomOperatorProperties
from setup_wizard.replace_default_materials_setup.default_material_replacer_service import DefaultMaterialReplacerService
from setup_wizard.replace_default_materials_setup.game_default_material_replacers import GameDefaultMaterialReplacerFactory


class GI_OT_GenshinReplaceDefaultMaterials(Operator, CustomOperatorProperties):
    """Swaps out the default character materials with Festivity's Shaders materials"""
    bl_idname = "genshin.replace_default_materials"  # important since its how we chain file dialogs
    bl_label = "Genshin: Replace Default Materials - Select Character Model Folder"

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
        game_default_material_replacer = GameDefaultMaterialReplacerFactory.create(self.game_type, self, context)

        default_material_replacer_service = DefaultMaterialReplacerService(game_default_material_replacer)
        default_material_replacer_service.replace_default_materials()

        NextStepInvoker().invoke(
            self.next_step_idx, 
            self.invoker_type, 
            high_level_step_name=self.high_level_step_name,
            game_type=self.game_type,
        )
        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory(GI_OT_GenshinReplaceDefaultMaterials)
