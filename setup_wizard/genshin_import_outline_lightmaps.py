# Author: michael-gh1

import bpy

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
import os

from setup_wizard.import_order import CHARACTER_MODEL_FOLDER_FILE_PATH, NextStepInvoker, cache_using_cache_key, get_cache
from setup_wizard.import_order import get_actual_material_name_for_dress
from setup_wizard.models import CustomOperatorProperties


class GI_OT_GenshinImportOutlineLightmaps(Operator, ImportHelper, CustomOperatorProperties):
    """Select the folder with the character's lightmaps to import"""
    bl_idname = "genshin.import_outline_lightmaps"  # important since its how we chain file dialogs
    bl_label = "Genshin: Import Lightmaps - Select Character Model Folder"

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
        cache_enabled = context.window_manager.cache_enabled
        character_model_folder_file_path = self.file_directory \
            or get_cache(cache_enabled).get(CHARACTER_MODEL_FOLDER_FILE_PATH) \
            or os.path.dirname(self.filepath)

        if not character_model_folder_file_path:
            bpy.ops.genshin.import_outline_lightmaps(
                'INVOKE_DEFAULT',
                next_step_idx=self.next_step_idx, 
                file_directory=self.file_directory,
                invoker_type=self.invoker_type,
                high_level_step_name=self.high_level_step_name
            )
            return {'FINISHED'}
        
        for name, folder, files in os.walk(character_model_folder_file_path):
            diffuse_files = [file for file in files if 'Diffuse' in file]
            lightmap_files = [file for file in files if 'Lightmap' in file]
            outline_materials = [material for material in bpy.data.materials.values() if 'Outlines' in material.name and material.name != 'miHoYo - Genshin Outlines']

            for outline_material in outline_materials:
                body_part_material_name = outline_material.name.split(' ')[-2]  # ex. 'miHoYo - Genshin Hair Outlines'
                original_material_name = [material for material in bpy.data.materials if material.name.endswith(f'Mat_{body_part_material_name}')][0]  # from original model
                actual_material_part_name = get_actual_material_name_for_dress(original_material_name.name)

                if 'Face' not in actual_material_part_name and 'Face' not in body_part_material_name:
                    self.assign_lightmap_texture(character_model_folder_file_path, lightmap_files, body_part_material_name, actual_material_part_name)
                    self.assign_diffuse_texture(character_model_folder_file_path, diffuse_files, body_part_material_name, actual_material_part_name)
                    self.report({'INFO'}, f'Imported outline textures (diffuse and lightmap) onto material "{outline_material.name}"')
            break  # IMPORTANT: We os.walk which also traverses through folders...we just want the files

        if cache_enabled and character_model_folder_file_path:
            cache_using_cache_key(get_cache(cache_enabled), CHARACTER_MODEL_FOLDER_FILE_PATH, character_model_folder_file_path)

        NextStepInvoker().invoke(
            self.next_step_idx, 
            self.invoker_type, 
            file_path_to_cache=character_model_folder_file_path,
            high_level_step_name=self.high_level_step_name
        )
        super().clear_custom_properties()
        return {'FINISHED'}

    def assign_lightmap_texture(self, character_model_folder_file_path, lightmap_files, body_part_material_name, actual_material_part_name):
        v1_lightmap_node_name = 'Image Texture'
        v2_lightmap_node_name = 'Outline_Lightmap'
        outline_material = bpy.data.materials.get(f'miHoYo - Genshin {body_part_material_name} Outlines')

        lightmap_filename = [file for file in lightmap_files if actual_material_part_name in file][0]
        lightmap_node = outline_material.node_tree.nodes.get(v2_lightmap_node_name) \
            or outline_material.node_tree.nodes.get(v1_lightmap_node_name)
        self.assign_texture_to_node(lightmap_node, character_model_folder_file_path, lightmap_filename)

    def assign_diffuse_texture(self, character_model_folder_file_path, diffuse_files, body_part_material_name, actual_material_part_name):
        difuse_node_name = 'Outline_Diffuse'
        outline_material = bpy.data.materials.get(f'miHoYo - Genshin {body_part_material_name} Outlines')
        diffuse_node = outline_material.node_tree.nodes.get(difuse_node_name) \
            or None  # None for backwards compatibility in v1 where it did not exist

        if diffuse_node:
            diffuse_filename = [file for file in diffuse_files if actual_material_part_name in file][0]
            self.assign_texture_to_node(diffuse_node, character_model_folder_file_path, diffuse_filename)

    def assign_texture_to_node(self, node, character_model_folder_file_path, texture_file_name):
        texture_img_path = character_model_folder_file_path + "/" + texture_file_name
        texture_img = bpy.data.images.load(filepath = texture_img_path, check_existing=True)
        texture_img.alpha_mode = 'CHANNEL_PACKED'
        node.image = texture_img

register, unregister = bpy.utils.register_classes_factory(GI_OT_GenshinImportOutlineLightmaps)
