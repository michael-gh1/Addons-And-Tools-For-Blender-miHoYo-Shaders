# Structure for class comes from a script initially written by Zekium from Discord
# Written by Mken from Discord

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator

import os


class GI_OT_GenshinSetupWizard(Operator):
    """Setup Wizard Process"""
    bl_idname = "genshin.setup_wizard"
    bl_label = "Genshin: Setup Wizard - Select Festivity's Shaders Folder"

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
        invoke_next_step = setup_dependencies()
        invoke_next_step(1)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(GI_OT_GenshinSetupWizard)

# Legacy import system before this became an Addon. Refactoring necessary.
def setup_dependencies():
    # Really ugly in my opinion, but this let's us reload modules when we make changes to them without
    # having to restart Blender.
    import importlib
    import setup_wizard.import_order
    import setup_wizard.genshin_import_character_model
    import setup_wizard.genshin_import_material_data
    import setup_wizard.genshin_import_materials
    import setup_wizard.genshin_set_up_geometry_nodes
    import setup_wizard.genshin_import_outline_lightmaps
    import setup_wizard.genshin_import_outlines
    import setup_wizard.genshin_import_textures
    import setup_wizard.genshin_replace_default_materials
    import setup_wizard.misc_final_steps
    import setup_wizard.set_up_head_driver
    import setup_wizard.fix_mouth_outlines
    import setup_wizard.misc_operations

    importlib.reload(setup_wizard.import_order)
    importlib.reload(setup_wizard.genshin_import_character_model)
    importlib.reload(setup_wizard.genshin_import_material_data)
    importlib.reload(setup_wizard.genshin_import_materials)
    importlib.reload(setup_wizard.genshin_set_up_geometry_nodes)
    importlib.reload(setup_wizard.genshin_import_outline_lightmaps)
    importlib.reload(setup_wizard.genshin_import_outlines)
    importlib.reload(setup_wizard.genshin_import_textures)
    importlib.reload(setup_wizard.genshin_replace_default_materials)
    importlib.reload(setup_wizard.misc_final_steps)
    importlib.reload(setup_wizard.set_up_head_driver)
    importlib.reload(setup_wizard.fix_mouth_outlines)
    importlib.reload(setup_wizard.misc_operations)

    for class_to_register in [
        setup_wizard.genshin_import_character_model.GI_OT_GenshinImportModel,
        setup_wizard.genshin_import_character_model.GI_OT_DeleteEmpties,
        setup_wizard.genshin_import_material_data.GI_OT_GenshinImportMaterialData,
        setup_wizard.genshin_import_materials.GI_OT_GenshinImportMaterials,
        setup_wizard.genshin_set_up_geometry_nodes.GI_OT_SetUpGeometryNodes,
        setup_wizard.genshin_import_outline_lightmaps.GI_OT_GenshinImportOutlineLightmaps,
        setup_wizard.genshin_import_outlines.GI_OT_GenshinImportOutlines,
        setup_wizard.genshin_import_textures.GI_OT_GenshinImportTextures,
        setup_wizard.genshin_replace_default_materials.GI_OT_GenshinReplaceDefaultMaterials,
        setup_wizard.fix_mouth_outlines.GI_OT_FixMouthOutlines,
        setup_wizard.misc_final_steps.GI_OT_MakeCharacterUpright,
        setup_wizard.set_up_head_driver.GI_OT_SetUpHeadDriver,
        setup_wizard.misc_operations.GI_OT_SetColorManagementToStandard,
        setup_wizard.misc_operations.GI_OT_DeleteSpecificObjects,
    ]:
        try:
            bpy.utils.register_class(class_to_register)
        except ValueError:
            pass  # expected if class is already registered
    return setup_wizard.import_order.invoke_next_step


# Need to have run setup_dependencies in order to unregister, otherwise sys.path 
# will be missing the filepath to the scripts folder
def unregister():
    from setup_wizard.genshin_import_materials import GI_OT_GenshinImportMaterials
    from setup_wizard.genshin_import_character_model import GI_OT_GenshinImportModel, GI_OT_DeleteEmpties
    from setup_wizard.genshin_replace_default_materials import GI_OT_GenshinReplaceDefaultMaterials
    from setup_wizard.genshin_import_textures import GI_OT_GenshinImportTextures
    from setup_wizard.genshin_set_up_geometry_nodes import GI_OT_SetUpGeometryNodes
    from setup_wizard.genshin_import_outlines import GI_OT_GenshinImportOutlines
    from setup_wizard.genshin_import_outline_lightmaps import GI_OT_GenshinImportOutlineLightmaps
    from setup_wizard.genshin_import_material_data import GI_OT_GenshinImportMaterialData
    from setup_wizard.misc_final_steps import GI_OT_MakeCharacterUpright
    from setup_wizard.set_up_head_driver import GI_OT_SetUpHeadDriver
    from setup_wizard.misc_operations import GI_OT_SetColorManagementToStandard, GI_OT_DeleteSpecificObjects

    for class_to_unregister in [
        GI_OT_GenshinImportModel,
        GI_OT_DeleteEmpties,
        GI_OT_GenshinImportMaterials,
        GI_OT_GenshinReplaceDefaultMaterials,
        GI_OT_GenshinImportTextures,
        GI_OT_SetUpGeometryNodes,
        GI_OT_GenshinImportOutlines,
        GI_OT_GenshinImportOutlineLightmaps,
        GI_OT_GenshinImportMaterialData,
        GI_OT_MakeCharacterUpright,
        GI_OT_SetUpHeadDriver,
        GI_OT_SetColorManagementToStandard,
        GI_OT_DeleteSpecificObjects,
    ]:
        try:
            bpy.utils.unregister_class(class_to_unregister)
        except ValueError:
            pass  # expected if class is already registered


if __name__ == "__main__":
    register()
