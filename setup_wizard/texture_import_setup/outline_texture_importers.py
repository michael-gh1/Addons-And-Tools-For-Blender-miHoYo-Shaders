
import bpy
import os

from abc import ABC, abstractmethod
from bpy.types import Context, Operator
from setup_wizard.domain.game_types import GameType

from setup_wizard.import_order import CHARACTER_MODEL_FOLDER_FILE_PATH, cache_using_cache_key, get_actual_material_name_for_dress, get_cache
from setup_wizard.texture_import_setup.texture_importer_types import TextureImporterType


class OutlineTextureImporter(ABC):
    def __init__(self, blender_operator: Operator, context: Context):
        self.blender_operator: Operator = blender_operator
        self.context: Context = context

    @abstractmethod
    def import_textures(self):
        raise NotImplementedError()

    def assign_lightmap_texture(self, character_model_folder_file_path, lightmap_files, body_part_material_name, actual_material_part_name):
        v1_lightmap_node_name = 'Image Texture'
        v2_lightmap_node_name = 'Outline_Lightmap'
        outline_material = bpy.data.materials.get(f'miHoYo - Genshin {body_part_material_name} Outlines')

        lightmap_filename = [file for file in lightmap_files if actual_material_part_name in file][0]
        lightmap_node = outline_material.node_tree.nodes.get(v2_lightmap_node_name) \
            or outline_material.node_tree.nodes.get(v1_lightmap_node_name)
        self.assign_texture_to_node(lightmap_node, character_model_folder_file_path, lightmap_filename)
        self.blender_operator.report({'INFO'}, f'Imported "{actual_material_part_name}" lightmap onto material "{outline_material.name}"')

    def assign_diffuse_texture(self, character_model_folder_file_path, diffuse_files, body_part_material_name, actual_material_part_name):
        difuse_node_name = 'Outline_Diffuse'
        outline_material = bpy.data.materials.get(f'miHoYo - Genshin {body_part_material_name} Outlines')
        diffuse_node = outline_material.node_tree.nodes.get(difuse_node_name) \
            or None  # None for backwards compatibility in v1 where it did not exist

        if diffuse_node:
            diffuse_filename = [file for file in diffuse_files if actual_material_part_name in file][0]
            self.assign_texture_to_node(diffuse_node, character_model_folder_file_path, diffuse_filename)
            self.blender_operator.report({'INFO'}, f'Imported "{actual_material_part_name}" diffuse onto material "{outline_material.name}"')

    def assign_texture_to_node(self, node, character_model_folder_file_path, texture_file_name):
        texture_img_path = character_model_folder_file_path + "/" + texture_file_name
        texture_img = bpy.data.images.load(filepath = texture_img_path, check_existing=True)
        texture_img.alpha_mode = 'CHANNEL_PACKED'
        node.image = texture_img


class OutlineTextureImporterFactory:
    def create(game_type: GameType, blender_operator: Operator, context: Context):
        # Because we inject the GameType via StringProperty, we need to compare using the Enum's name (a string)
        if game_type == GameType.GENSHIN_IMPACT.name:
            return GenshinImpactOutlineTextureImporter(blender_operator, context)
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            return HonkaiStarRailOutlineTextureImporter(blender_operator, context)
        else:
            raise Exception(f'Unknown {GameType}: {game_type}')


class GenshinImpactOutlineTextureImporter(OutlineTextureImporter):
    def __init__(self, blender_operator, context):
        super().__init__(blender_operator, context)

    def import_textures(self):
        cache_enabled = self.context.window_manager.cache_enabled
        character_model_folder_file_path = self.blender_operator.file_directory \
            or get_cache(cache_enabled).get(CHARACTER_MODEL_FOLDER_FILE_PATH) \
            or os.path.dirname(self.blender_operator.filepath)

        if not character_model_folder_file_path:
            bpy.ops.genshin.import_outline_lightmaps(
                'INVOKE_DEFAULT',
                next_step_idx=self.blender_operator.next_step_idx, 
                file_directory=self.blender_operator.file_directory,
                invoker_type=self.blender_operator.invoker_type,
                high_level_step_name=self.blender_operator.high_level_step_name,
                game_type=self.blender_operator.game_type,
            )
            return {'FINISHED'}
        
        for name, folder, files in os.walk(character_model_folder_file_path):
            diffuse_files = [file for file in files if 'Diffuse'.lower() in file.lower()]
            lightmap_files = [file for file in files if 'Lightmap'.lower() in file.lower()]
            outline_materials = [material for material in bpy.data.materials.values() if 'Outlines' in material.name and material.name != 'miHoYo - Genshin Outlines']

            for outline_material in outline_materials:
                body_part_material_name = outline_material.name.split(' ')[-2]  # ex. 'miHoYo - Genshin Hair Outlines'
                character_type = None

                if [material for material in bpy.data.materials if material.name.startswith('NPC')]:
                    original_mesh_material = [material for material in bpy.data.materials if material.name.startswith('NPC') and body_part_material_name in material.name][0]
                    character_type = TextureImporterType.NPC
                elif [material for material in bpy.data.materials if material.name.startswith('Monster')]:
                    if body_part_material_name == 'Body':
                        original_mesh_material = [material for material in bpy.data.materials if material.name.startswith('Monster') and body_part_material_name in material.name][0]
                    character_type = TextureImporterType.MONSTER
                else:
                    original_mesh_material = [material for material in bpy.data.materials if material.name.endswith(f'Mat_{body_part_material_name}')][0]
                    character_type = TextureImporterType.AVATAR
                actual_material_part_name = get_actual_material_name_for_dress(original_mesh_material.name, character_type.name)

                if 'Face' not in actual_material_part_name and 'Face' not in body_part_material_name:
                    if character_type is TextureImporterType.MONSTER:
                        actual_material_part_name = 'Tex'
                    self.assign_lightmap_texture(character_model_folder_file_path, lightmap_files, body_part_material_name, actual_material_part_name)
                    self.assign_diffuse_texture(character_model_folder_file_path, diffuse_files, body_part_material_name, actual_material_part_name)
            break  # IMPORTANT: We os.walk which also traverses through folders...we just want the files

        if cache_enabled and character_model_folder_file_path:
            cache_using_cache_key(get_cache(cache_enabled), CHARACTER_MODEL_FOLDER_FILE_PATH, character_model_folder_file_path)


class HonkaiStarRailOutlineTextureImporter(OutlineTextureImporter):
    def __init__(self, blender_operator, context):
        super().__init__(blender_operator, context)

    def import_textures(self):
        cache_enabled = self.context.window_manager.cache_enabled
        character_model_folder_file_path = self.blender_operator.file_directory \
            or get_cache(cache_enabled).get(CHARACTER_MODEL_FOLDER_FILE_PATH) \
            or os.path.dirname(self.blender_operator.filepath)

        if not character_model_folder_file_path:
            bpy.ops.genshin.import_outline_lightmaps(
                'INVOKE_DEFAULT',
                next_step_idx=self.blender_operator.next_step_idx, 
                file_directory=self.blender_operator.file_directory,
                invoker_type=self.blender_operator.invoker_type,
                high_level_step_name=self.blender_operator.high_level_step_name,
                game_type=self.blender_operator.game_type,
            )
            return {'FINISHED'}

        for name, folder, files in os.walk(character_model_folder_file_path):
            color_files = [file for file in files if 'Color'.lower() in file.lower()]
            lightmap_files = [file for file in files if 'LightMap'.lower() in file.lower() or 'FaceMap' in file.lower() or 'LigthMap'.lower() in file.lower()]  # that Lightmap typo is on purpose
            outline_materials = [material for material in bpy.data.materials.values() if 'outlines' in material.name.lower() and material.name.lower() != 'mihoyo - genshin outlines']

            for outline_material in outline_materials:
                body_part_material_name = outline_material.name.split(' ')[-2]  # ex. 'miHoYo - Genshin Hair Outlines'
                original_mesh_material = [material for material in bpy.data.materials if material.name.endswith(f'Mat_{body_part_material_name}')]

                if original_mesh_material and 'Face' not in original_mesh_material and 'Face' not in body_part_material_name:
                    actual_material_part_name = 'Weapon' if 'Weapon' in body_part_material_name else body_part_material_name
                    self.assign_lightmap_texture(character_model_folder_file_path, lightmap_files, body_part_material_name, actual_material_part_name)
                    self.assign_diffuse_texture(character_model_folder_file_path, color_files, body_part_material_name, actual_material_part_name)
            break  # IMPORTANT: We os.walk which also traverses through folders...we just want the files

        if cache_enabled and character_model_folder_file_path:
            cache_using_cache_key(get_cache(cache_enabled), CHARACTER_MODEL_FOLDER_FILE_PATH, character_model_folder_file_path)
