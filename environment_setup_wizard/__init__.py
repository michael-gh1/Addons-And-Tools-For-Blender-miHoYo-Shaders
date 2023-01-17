import bpy

from environment_setup_wizard.ui.ui_environment_setup_wizard import B_PT_EnvironmentSetupWizard_UI_Layout
from environment_setup_wizard.operators.genshin_environment_import_textures import B_OT_GenshinEnvironmentImportTextures
from environment_setup_wizard.operators.genshin_environment_import_environment_materials import B_OT_GenshinEnvironmentImportEnvironmentMaterials

bl_info = {
    "name": "Environment Setup Wizard",
    "author": "Mken",
    "version": (1, 0, 0),
    "blender": (3, 3, 1),
    "location": "3D View > Sidebar > Environment Setup Wizard",
    "description": "Environment Setup Wizard",
    "warning": "",
    "doc_url": "",
    "support": 'COMMUNITY',
    "category": "HoYoverse",
    "tracker_url": "",
    "doc_url": ""
}

classes = [
    B_PT_EnvironmentSetupWizard_UI_Layout,
    B_OT_GenshinEnvironmentImportTextures,
    B_OT_GenshinEnvironmentImportEnvironmentMaterials,
]

register, unregister = bpy.utils.register_classes_factory(classes)
