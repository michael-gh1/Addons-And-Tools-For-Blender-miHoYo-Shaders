# Author: michael-gh1

# Kudos to M4urlcl0 for bringing up adding the UV map (UV1) and 
# the armature bone settings when importing the FBX model

import bpy
import pathlib

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator
import os

from setup_wizard.domain.game_types import GameType
from setup_wizard.import_order import NextStepInvoker, cache_using_cache_key
from setup_wizard.import_order import get_cache, CHARACTER_MODEL_FOLDER_FILE_PATH
from setup_wizard.setup_wizard_operator_base_classes import BasicSetupUIOperator, CustomOperatorProperties
from setup_wizard.utils import material_utils


SHADER_COLOR_ATTRIBUTE_NAME = 'Col'


class GI_OT_SetUpCharacter(Operator, BasicSetupUIOperator):
    '''Sets Up Character'''
    bl_idname = 'genshin.set_up_character'
    bl_label = 'Genshin: Set Up Character (UI)'


class HSR_OT_SetUpCharacter(Operator, BasicSetupUIOperator):
    '''Sets Up Character'''
    bl_idname = 'honkai_star_rail.set_up_character'
    bl_label = 'Honkai Star Rail: Set Up Character (UI)'


class GI_OT_GenshinImportModel(Operator, ImportHelper, CustomOperatorProperties):
    """Select the folder with the desired model to import"""
    bl_idname = "genshin.import_model"  # important since its how we chain file dialogs
    bl_label = "Select Character Folder"

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

    use_auto_bone_orientation: BoolProperty(
        name="Automatic Bone Orientation",
        description="Automatically sort bones orientations, if you want to preserve the original armature, please disable the option",
        default=True,
    )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="BetterFBX Bone Options:")
        box.prop(self, 'use_auto_bone_orientation')

    def execute(self, context):
        self.clean_up_scene()

        is_character_model_file = not os.path.isdir(self.filepath) and self.filepath
        character_model_directory = os.path.dirname(self.filepath) or self.file_directory
        character_model_file_path_or_directory = self.filepath if is_character_model_file else \
            (self.file_directory or character_model_directory)

        if not character_model_file_path_or_directory:
            bpy.ops.genshin.import_model(
                'INVOKE_DEFAULT',
                next_step_idx=self.next_step_idx, 
                file_directory=self.file_directory,
                invoker_type=self.invoker_type,
                high_level_step_name=self.high_level_step_name,
                game_type=self.game_type,
                )
            return {'FINISHED'}

        existing_materials = bpy.data.materials.values()  # used to track materials before and after importing character model
        original_language = bpy.context.preferences.view.language
        try:
            # Blender's FBX import has some silent issue when importing in different languages. Unsure why.
            # TODO: Confirm if this issue is due to the Color Attribute name being named differently in each language
            # TODO: rename_mesh_color_attribute_name() should address this issue and not require us to set language
            bpy.context.preferences.view.language = 'en_US'
            self.import_character_model(character_model_file_path_or_directory, is_character_model_file)
            self.reset_pose_location_and_rotation()
            self.rename_mesh_color_attribute_name(SHADER_COLOR_ATTRIBUTE_NAME)  # Blender 3.4 changed default name to 'Attribute', revert it

            if context.window_manager.cache_enabled and character_model_directory:
                cache_using_cache_key(get_cache(), CHARACTER_MODEL_FOLDER_FILE_PATH, character_model_directory)

            # Add fake user to all materials that were added when importing character model (to prevent unused materials from being cleaned up)
            materials_imported_from_character_model = [material for material in bpy.data.materials.values() if material not in existing_materials]
            material_utils.add_fake_user_to_materials(materials_imported_from_character_model)

            NextStepInvoker().invoke(
                self.next_step_idx, 
                self.invoker_type, 
                file_path_to_cache=character_model_directory,
                high_level_step_name=self.high_level_step_name,
                game_type=self.game_type,
            )
        finally:
            bpy.context.preferences.view.language = original_language
            super().clear_custom_properties()
        return {'FINISHED'}

    '''
        We need to clean up the scene to ensure no other objects will interfere the setup.
        Flins has a Light mesh which creates a Light.001 on character import and causes issues later in the setup.
    '''
    def clean_up_scene(self):
        OBJECTS_TO_CLEAN_UP = [
            'Cube',
            'Light',
        ]
        for obj in bpy.data.objects:
            if obj.name in OBJECTS_TO_CLEAN_UP:
                bpy.data.objects.remove(obj)

    def import_character_model(self, character_model_file_path_or_directory, is_character_model_file):
        character_model_file_path = character_model_file_path_or_directory if is_character_model_file else \
            self.__find_fbx_file(character_model_file_path_or_directory)
        betterfbx_installed = bpy.context.preferences.addons.get('better_fbx')
        # Honkai Star Rail requires BetterFBX. We should always use it for HSR Character Import
        betterfbx_enabled = True if self.game_type == GameType.HONKAI_STAR_RAIL.name else \
            bpy.context.window_manager.setup_wizard_betterfbx_enabled if betterfbx_installed else False

        if betterfbx_installed and betterfbx_enabled:
            bpy.ops.better_import.fbx(
                'EXEC_DEFAULT',
                filepath=character_model_file_path,
                use_auto_bone_orientation=self.use_auto_bone_orientation,
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
            if object.type == 'MESH' and not object.data.uv_layers.get('UV1'):
                object.data.uv_layers.new(name='UV1')
        # Quick-fix, just want to shove this in here for now...
        # Hide EffectMesh (gets deleted later on) and EyeStar
        for object in bpy.data.objects:
            if 'EffectMesh' in object.name or 'EyeStar' in object.name:
                bpy.data.objects[object.name].hide_set(True)
                bpy.data.objects[object.name].hide_render = True

    def reset_pose_location_and_rotation(self):
        try:
            armature = [object for object in bpy.data.objects if object.type == 'ARMATURE'][0]  # expecting 1 armature
        except IndexError as err:
            self.report(
                {'ERROR'}, 
                'Attempted to import model, but no armature found after import. Likely failed to import from FBX file.\n'
                '- Try again with BetterFBX disabled.\n'
                "- Try renaming and removing any special characters (like star symbols) from any folders in the filepath"
            )
            raise err
        bpy.context.view_layer.objects.active = armature

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.loc_clear()
        bpy.ops.pose.rot_clear()
        bpy.ops.object.mode_set(mode='OBJECT')

    '''
        NOTE: This will rename the Color Attributes for ALL meshes
        Currently expecting character setup to be performed in a fresh (new) file
    '''
    def rename_mesh_color_attribute_name(self, name):
        meshes = [mesh for mesh_name, mesh in bpy.data.meshes.items()]

        for mesh in meshes:
            if len(mesh.color_attributes) == 1:
                mesh.color_attributes[0].name = name  # PGR: Named "VertexColors" and may not be the active color
            else:
                if mesh.color_attributes.active_color:
                    mesh.color_attributes.active_color.name = name

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
                high_level_step_name=self.high_level_step_name,
                game_type=self.game_type,
            )
        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory([
    GI_OT_GenshinImportModel,
    GI_OT_DeleteEmpties,
])
