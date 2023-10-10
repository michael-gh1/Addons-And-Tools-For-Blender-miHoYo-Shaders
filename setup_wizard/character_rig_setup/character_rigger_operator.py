# Author: michael-gh1

import bpy

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator

from setup_wizard.character_rig_setup.rigify_character_service import RigifyCharacterService
from setup_wizard.setup_wizard_operator_base_classes import BasicSetupUIOperator, CustomOperatorProperties


class GI_OT_RigCharacter(Operator, BasicSetupUIOperator):
    '''Sets Up Rig for Character'''
    bl_idname = 'hoyoverse.set_up_character_rig'
    bl_label = 'HoYoverse: Set Up Character Rig (UI)'


class GI_OT_CharacterRiggerOperator(Operator, ImportHelper, CustomOperatorProperties):
    """Sets Up Rig for Character"""
    bl_idname = "hoyoverse.rig_character"  # important since its how we chain file dialogs
    bl_label = "Rigs Character"

    # ImportHelper mixin class uses this
    filename_ext = "*.*"

    # DEPRECATED, replaced by GI_OT_RootShape_FilePath_Setter_Operator 
    import_path: StringProperty(
        name="Path",
        description="Root_Shape .blend File",
        default="",
        subtype='DIR_PATH'
    )

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        betterfbx_installed = bpy.context.preferences.addons.get('better_fbx')
        expy_kit_installed = bpy.context.preferences.addons.get('Expy-Kit-main')
        rigify_installed = bpy.context.preferences.addons.get('rigify')

        if not betterfbx_installed or not expy_kit_installed or not rigify_installed:
            self.report(
                {'WARNING'},
                'Rigging skipped. BetterFBX, ExpyKit and Rigify are required.\n'
                f'BetterFBX: {"Installed" if betterfbx_installed else "Missing"}\n'
                f'ExpyKit: {"Installed" if expy_kit_installed else "Missing"}\n'
                f'Rigify: {"Installed" if rigify_installed else "Missing"}'
            )
            return {'FINISHED'}

        try:
            rigify_character_service = RigifyCharacterService(self.game_type, self, context)
            rigify_character_service.rig_character()
        except Exception as ex:
            raise ex
        finally:
            super().clear_custom_properties()
        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory(GI_OT_CharacterRiggerOperator)
