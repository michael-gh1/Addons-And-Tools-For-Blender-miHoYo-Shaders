# Structure for file comes from a script initially written by Zekium from Discord
# Written by Mken from Discord
# Kudos to M4urlcl0 for bringing up adding the UV map (UV1) and 
# the armature bone settings when importing the FBX model

import bpy
import pathlib

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, IntProperty
from bpy.types import Operator
import os

from setup_wizard.import_order import cache_using_cache_key, invoke_next_step
from setup_wizard.import_order import get_cache, CHARACTER_MODEL_FOLDER_FILE_PATH


class GI_OT_GenshinImportModel(Operator, ImportHelper):
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

    next_step_idx: IntProperty()
    file_directory: StringProperty()

    def execute(self, context):
        character_model_folder_file_path = self.file_directory or os.path.dirname(self.filepath)

        if not character_model_folder_file_path:
            bpy.ops.genshin.import_model('INVOKE_DEFAULT')
            return {'FINISHED'}

        self.import_character_model(character_model_folder_file_path)
        self.reset_pose_location_and_rotation()

        # Quick-fix, just want to shove this in here for now...
        # Hide EffectMesh (gets deleted later on) and EyeStar
        # Now shoving in adding UV1 map too...
        for object in bpy.data.objects:
            if object.name == 'EffectMesh' or object.name == 'EyeStar':
                bpy.data.objects[object.name].hide_set(True)
            if object.type == 'MESH':  # I think this only matters for Body? But adding to all anyways
                object.data.uv_layers.new(name='UV1')

        if not self.next_step_idx and context.window_manager.cache_enabled:  # executed from UI
            cache_using_cache_key(get_cache(), CHARACTER_MODEL_FOLDER_FILE_PATH, character_model_folder_file_path)
        invoke_next_step(self.next_step_idx, character_model_folder_file_path)
        return {'FINISHED'}

    def import_character_model(self, character_model_file_path_directory):
        character_model_file_path = self.__find_fbx_file(character_model_file_path_directory)
        bpy.ops.import_scene.fbx(
            filepath=character_model_file_path,
            force_connect_children=True,
            automatic_bone_orientation=True
        )
        self.report({'INFO'}, 'Imported character model...')
    
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
class GI_OT_DeleteEmpties(Operator):
    '''Deletes Empties (except Head Driver's empties)'''
    bl_idname = 'genshin.delete_empties'
    bl_label = "Genshin: Delete empties (except Head Driver's empties)"

    next_step_idx: IntProperty()
    file_directory: StringProperty()  # Unused, but ncessary for import_order to execute/invoke
    
    def execute(self, context):
        scene = bpy.context.scene
        empties_to_not_delete = [
            'Head Forward',
            'Head Up'
        ]
        for object in scene.objects:
            if object.type == 'EMPTY' and object.name not in empties_to_not_delete:
                bpy.data.objects.remove(object)

        if self.next_step_idx:
            invoke_next_step(self.next_step_idx)
        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory([
    GI_OT_GenshinImportModel,
    GI_OT_DeleteEmpties,
])
