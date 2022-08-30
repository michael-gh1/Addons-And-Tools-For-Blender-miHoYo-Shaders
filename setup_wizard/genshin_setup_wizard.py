# Structure for class comes from a script initially written by Zekium from Discord
# Written by Mken from Discord

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator

import os


class GI_OT_GenshinSetupWizard(Operator, ImportHelper):
    """Setup Wizard Process"""
    bl_idname = "file.genshin_setup_wizard"
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
        invoke_next_step = setup_dependencies(self.filepath)
        invoke_next_step(
            1, 
            file_path_to_cache = self.filepath, 
            path_to_streamlined_setup=os.path.join(self.filepath, 'setup_wizard/')
        )

        return {'FINISHED'}


def register():
    bpy.utils.register_class(GI_OT_GenshinSetupWizard)


# Specifically done this way because path is dependent on where Blender is started
# We ask for the filepath to Festivity's shaders that way we can set up the scripts in the path
def setup_dependencies(filepath=None):
    if filepath:
        directory = os.path.dirname(filepath)

        import sys
        if filepath not in sys.path:
            sys.path.append(directory)

    # Really ugly in my opinion, but this let's us reload modules when we make changes to them without
    # having to restart Blender.
    import importlib
    import setup_wizard.import_order
    import setup_wizard.genshin_import_character_model
    import setup_wizard.genshin_import_material_data
    import setup_wizard.genshin_import_materials
    import setup_wizard.genshin_setup_geometry_nodes
    import setup_wizard.genshin_import_outline_lightmaps
    import setup_wizard.genshin_import_outlines
    import setup_wizard.genshin_import_textures
    import setup_wizard.genshin_replace_default_materials
    import setup_wizard.fix_mouth_outlines
    import setup_wizard.misc_operations

    importlib.reload(setup_wizard.import_order)
    importlib.reload(setup_wizard.genshin_import_character_model)
    importlib.reload(setup_wizard.genshin_import_material_data)
    importlib.reload(setup_wizard.genshin_import_materials)
    importlib.reload(setup_wizard.genshin_setup_geometry_nodes)
    importlib.reload(setup_wizard.genshin_import_outline_lightmaps)
    importlib.reload(setup_wizard.genshin_import_outlines)
    importlib.reload(setup_wizard.genshin_import_textures)
    importlib.reload(setup_wizard.genshin_replace_default_materials)
    importlib.reload(setup_wizard.fix_mouth_outlines)
    importlib.reload(setup_wizard.misc_operations)

    for class_to_register in [
        setup_wizard.genshin_import_character_model.GI_OT_GenshinImportModel,
        setup_wizard.genshin_import_material_data.GI_OT_GenshinImportMaterialData,
        setup_wizard.genshin_import_materials.GI_OT_GenshinImportMaterials,
        setup_wizard.genshin_setup_geometry_nodes.GI_OT_SetupGeometryNodes,
        setup_wizard.genshin_import_outline_lightmaps.GI_OT_GenshinImportOutlineLightmaps,
        setup_wizard.genshin_import_outlines.GI_OT_GenshinImportOutlines,
        setup_wizard.genshin_import_textures.GI_OT_GenshinImportTextures,
        setup_wizard.genshin_replace_default_materials.GI_OT_GenshinReplaceDefaultMaterials,
        setup_wizard.fix_mouth_outlines.GI_OT_FixMouthOutlines,
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
    from setup_wizard.genshin_import_character_model import GI_OT_GenshinImportModel
    from setup_wizard.genshin_replace_default_materials import GI_OT_GenshinReplaceDefaultMaterials
    from setup_wizard.genshin_import_textures import GI_OT_GenshinImportTextures
    from setup_wizard.genshin_setup_geometry_nodes import GI_OT_SetupGeometryNodes
    from setup_wizard.genshin_import_outlines import GI_OT_GenshinImportOutlines
    from setup_wizard.genshin_import_outline_lightmaps import GI_OT_GenshinImportOutlineLightmaps
    from setup_wizard.genshin_import_material_data import GI_OT_GenshinImportMaterialData
    from setup_wizard.misc_operations import GI_OT_SetColorManagementToStandard, GI_OT_DeleteSpecificObjects

    for class_to_unregister in [
        GI_OT_GenshinImportModel,
        GI_OT_GenshinImportMaterials,
        GI_OT_GenshinReplaceDefaultMaterials,
        GI_OT_GenshinImportTextures,
        GI_OT_SetupGeometryNodes,
        GI_OT_GenshinImportOutlines,
        GI_OT_GenshinImportOutlineLightmaps,
        GI_OT_GenshinImportMaterialData,
        GI_OT_SetColorManagementToStandard,
        GI_OT_DeleteSpecificObjects,
    ]:
        try:
            bpy.utils.unregister_class(class_to_unregister)
        except ValueError:
            pass  # expected if class is already registered


if __name__ == "__main__":
    register()
