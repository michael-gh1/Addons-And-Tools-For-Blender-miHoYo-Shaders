# Author: michael-gh1

# Kudos to M4urlcl0 for bringing up adding the UV map (UV1) and 
# the armature bone settings when importing the FBX model

import bpy
import pathlib

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
import os

from setup_wizard.import_order import NextStepInvoker, cache_using_cache_key
from setup_wizard.import_order import get_cache, CHARACTER_MODEL_FOLDER_FILE_PATH
from setup_wizard.models import BasicSetupUIOperator, CustomOperatorProperties


class GI_OT_SetUpCharacter(Operator, BasicSetupUIOperator):
    '''Sets Up Character'''
    bl_idname = 'genshin.set_up_character'
    bl_label = 'Genshin: Set Up Character (UI)'


class GI_OT_GenshinImportModel(Operator, ImportHelper, CustomOperatorProperties):
    """Select the folder with the desired model to import"""
    bl_idname = "genshin.import_model"  # important since its how we chain file dialogs
    bl_label = "Genshin: Import Character Model - Select Character Model Folder"

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
        character_model_folder_file_path = self.file_directory or os.path.dirname(self.filepath)

        if not character_model_folder_file_path:
            bpy.ops.genshin.import_model(
                'INVOKE_DEFAULT',
                next_step_idx=self.next_step_idx, 
                file_directory=self.file_directory,
                invoker_type=self.invoker_type,
                high_level_step_name=self.high_level_step_name
                )
            return {'FINISHED'}

        self.import_character_model(character_model_folder_file_path)
        self.reset_pose_location_and_rotation()

        if context.window_manager.cache_enabled and character_model_folder_file_path:
            cache_using_cache_key(get_cache(), CHARACTER_MODEL_FOLDER_FILE_PATH, character_model_folder_file_path)

        NextStepInvoker().invoke(
            self.next_step_idx, 
            self.invoker_type, 
            file_path_to_cache=character_model_folder_file_path,
            high_level_step_name=self.high_level_step_name
        )
        super().clear_custom_properties()
        return {'FINISHED'}

    def import_character_model(self, character_model_file_path_directory):
        character_model_file_path = self.__find_fbx_file(character_model_file_path_directory)
        betterfbx_installed = bpy.context.preferences.addons.get('better_fbx')
        betterfbx_enabled = bpy.context.window_manager.setup_wizard_betterfbx_enabled if betterfbx_installed else False

        if betterfbx_installed and betterfbx_enabled:
            bpy.ops.better_import.fbx(
                'EXEC_DEFAULT',
                filepath=character_model_file_path,
            )
            self.report({'INFO'}, 'Imported character model using BetterFBX')
        else:
            bpy.ops.import_scene.fbx(
                filepath=character_model_file_path,
                force_connect_children=True,
                automatic_bone_orientation=True
            )
            self.report({'INFO'}, 'Imported character model')

            for object in bpy.data.objects:
                if object.type == 'MESH':  # I think this only matters for Body? But adding to all anyways
                    # Important: This is actually not correct, but it looks better than not having a UV Map
                    # The outer part will show up as the inner part (ex. inner skirt will be same as outer skirt )
                    # TODO: Get feedback on whether this is desired or not...
                    object.data.uv_layers.new(name='UV1')
        # Quick-fix, just want to shove this in here for now...
        # Hide EffectMesh (gets deleted later on) and EyeStar
        for object in bpy.data.objects:
            if 'EffectMesh' in object.name or 'EyeStar' in object.name:
                bpy.data.objects[object.name].hide_set(True)
                bpy.data.objects[object.name].hide_render = True

    def reset_pose_location_and_rotation(self):
        armature = [object for object in bpy.data.objects if object.type == 'ARMATURE'][0]  # expecting 1 armature
        bpy.context.view_layer.objects.active = armature

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.loc_clear()
        bpy.ops.pose.rot_clear()
        bpy.ops.object.mode_set(mode='OBJECT')

    def __find_fbx_file(self, directory):
        for root, folder, files in os.walk(directory):
            for file_name in files:
                if '.fbx' in pathlib.Path(file_name).suffix:
                    return os.path.join(root, file_name)


'''
    This Operator should be executed AFTER importing the character model and 
    BEFORE importing Genshin materials.
    That way there is no chance of deleting empties used by Festivity's shaders.
'''
class GI_OT_DeleteEmpties(Operator, CustomOperatorProperties):
    '''Deletes Empties (except Head Driver's empties)'''
    bl_idname = 'genshin.delete_empties'
    bl_label = "Genshin: Delete empties (except Head Driver's empties)"

    def execute(self, context):
        scene = bpy.context.scene
        empties_to_not_delete = [
            'Head Forward',
            'Head Up'
        ]
        for object in scene.objects:
            if object.type == 'EMPTY' and object.name not in empties_to_not_delete:
                bpy.data.objects.remove(object)

        self.report({'INFO'}, 'Deleted Empties')
        if self.next_step_idx:
            NextStepInvoker().invoke(
                self.next_step_idx, 
                self.invoker_type, 
                high_level_step_name=self.high_level_step_name
            )
        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory([
    GI_OT_GenshinImportModel,
    GI_OT_DeleteEmpties,
])
