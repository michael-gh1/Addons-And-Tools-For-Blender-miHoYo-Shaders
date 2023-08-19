
import bpy
import os

from bpy.types import Operator, Context

from setup_wizard.domain.game_types import GameType
from setup_wizard.import_order import NextStepInvoker, cache_using_cache_key, get_cache, \
    FESTIVITY_ROOT_FOLDER_FILE_PATH, FESTIVITY_SHADER_FILE_PATH, NYA222_HONKAI_STAR_RAIL_ROOT_FOLDER_FILE_PATH, \
    NYA222_HONKAI_STAR_RAIL_SHADER_FILE_PATH


class GameMaterialImporterFactory:
    def create(game_type: GameType, blender_operator: Operator, context: Context):
        if game_type == GameType.GENSHIN_IMPACT.name:
            return GenshinImpactMaterialImporterFacade(blender_operator, context)
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            return HonkaiStarRailMaterialImporterFacade(blender_operator, context)
        else:
            raise Exception(f'Unknown {GameType}: {game_type}')


class GameMaterialImporter:
    MATERIAL_PATH_INSIDE_BLEND_FILE = 'Material'

    def __init__(self, 
                 blender_operator: Operator, 
                 context: Context,
                 game_shader_cache_file_path: str,
                 game_shader_cache_folder_path: str,
                 game_default_blend_file_with_materials: str,
                 names_of_game_materials: list):
        self.blender_operator = blender_operator
        self.context = context
        self.game_shader_file_path = game_shader_cache_file_path
        self.game_shader_folder_path = game_shader_cache_folder_path
        self.game_default_blend_file_with_materials = game_default_blend_file_with_materials
        self.names_of_game_materials = names_of_game_materials

    def import_materials(self):
        cache_enabled = self.context.window_manager.cache_enabled
        user_selected_shader_blend_file_path = self.blender_operator.filepath if \
            self.blender_operator.filepath and not os.path.isdir(self.blender_operator.filepath) else \
            get_cache(cache_enabled).get(self.game_shader_file_path)
        project_root_directory_file_path = self.blender_operator.file_directory \
            or get_cache(cache_enabled).get(self.game_shader_folder_path) \
            or os.path.dirname(self.blender_operator.filepath)

        if not user_selected_shader_blend_file_path and not project_root_directory_file_path:
            # Use Case: Advanced Setup
            # The Operator is Executed directly with no cached files and so we need to Invoke to prompt the user
            bpy.ops.genshin.import_materials(
                'INVOKE_DEFAULT',
                next_step_idx=self.blender_operator.next_step_idx, 
                file_directory=self.blender_operator.file_directory,
                invoker_type=self.blender_operator.invoker_type,
                high_level_step_name=self.blender_operator.high_level_step_name,
                game_type=self.blender_operator.game_type,
            )
            return {'FINISHED'}

        blend_file_with_genshin_materials = os.path.join(
            user_selected_shader_blend_file_path,
            self.MATERIAL_PATH_INSIDE_BLEND_FILE
        ) if user_selected_shader_blend_file_path else None

        default_blend_file_path = os.path.join(
            project_root_directory_file_path,
            self.game_default_blend_file_with_materials,
            self.MATERIAL_PATH_INSIDE_BLEND_FILE
        )

        try:
            # Use the exact file the user selected, otherwise fallback to the non-Goo blender file in the directory
            shader_blend_file_path = blend_file_with_genshin_materials or default_blend_file_path
            bpy.ops.wm.append(
                directory=shader_blend_file_path,
                files=self.names_of_game_materials,
                set_fake=True
            )
        except RuntimeError as ex:
            self.blender_operator.report({'ERROR'}, \
                f"ERROR: Error when trying to append materials. \n\
                Did not find `{self.game_default_blend_file_with_materials}` in the directory you selected. \n\
                Try selecting the exact blend file you want to use.")
            raise ex

        self.blender_operator.report({'INFO'}, 'Imported Shader/Genshin Materials...')
        if cache_enabled and (user_selected_shader_blend_file_path or project_root_directory_file_path):
            if user_selected_shader_blend_file_path:
                cache_using_cache_key(get_cache(cache_enabled), self.game_shader_file_path, user_selected_shader_blend_file_path)
            else:
                cache_using_cache_key(get_cache(cache_enabled), self.game_shader_folder_path, project_root_directory_file_path)

        NextStepInvoker().invoke(
            self.blender_operator.next_step_idx, 
            self.blender_operator.invoker_type, 
            file_path_to_cache=project_root_directory_file_path,
            high_level_step_name=self.blender_operator.high_level_step_name,
            game_type=self.blender_operator.game_type,
        )


class GenshinImpactMaterialImporterFacade(GameMaterialImporter):
    DEFAULT_BLEND_FILE_WITH_GENSHIN_MATERIALS = 'miHoYo - Genshin Impact.blend'
    NAMES_OF_GENSHIN_MATERIALS = [
        {'name': 'miHoYo - Genshin Body'},
        {'name': 'miHoYo - Genshin Face'},
        {'name': 'miHoYo - Genshin Hair'},
        {'name': 'miHoYo - Genshin Outlines'}
    ]

    def __init__(self, blender_operator, context):
        super().__init__(
            blender_operator,
            context,
            FESTIVITY_SHADER_FILE_PATH,
            FESTIVITY_ROOT_FOLDER_FILE_PATH,
            self.DEFAULT_BLEND_FILE_WITH_GENSHIN_MATERIALS,
            self.NAMES_OF_GENSHIN_MATERIALS
        )

    def import_materials(self):
        return super().import_materials()  # Genshin Impact Material Importer


class HonkaiStarRailMaterialImporterFacade(GameMaterialImporter):
    DEFAULT_BLEND_FILE_WITH_HSR_MATERIALS = 'miHoYo_-_Star_Rail.blend'
    NAMES_OF_HONKAI_STAR_RAIL_MATERIALS = [
        {'name': 'HSR - Body1'},
        {'name': 'HSR - Body2'},
        {'name': 'HSR - Body_Trans'},
        {'name': 'HSR - Hair'},
        {'name': 'HSR - Face'},
        {'name': 'HSR - EyeShadow'},
        {'name': 'HSR - Outlines'},
        {'name': 'HSR - Weapon'},
    ]

    def __init__(self, blender_operator, context):
        super().__init__(
            blender_operator,
            context,
            NYA222_HONKAI_STAR_RAIL_SHADER_FILE_PATH,
            NYA222_HONKAI_STAR_RAIL_ROOT_FOLDER_FILE_PATH,
            self.DEFAULT_BLEND_FILE_WITH_HSR_MATERIALS,
            self.NAMES_OF_HONKAI_STAR_RAIL_MATERIALS
        )

    def import_materials(self):
        super().import_materials()  # Honkai Star Rail Material Importer

        # Set 'Use Nodes' because shader does not have that by default
        for material_dictionary in self.NAMES_OF_HONKAI_STAR_RAIL_MATERIALS + [{'name': 'HSR - Body'}]:
            material: bpy.types.Material = bpy.data.materials.get(material_dictionary.get('name'))
            material.use_nodes = True
