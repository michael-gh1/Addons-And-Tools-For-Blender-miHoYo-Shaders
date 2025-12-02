
import bpy
import os

from bpy.types import Operator, Context

from setup_wizard.domain.shader_identifier_service import GenshinImpactShaders, ShaderIdentifierService, \
    ShaderIdentifierServiceFactory
from setup_wizard.domain.game_types import GameType
from setup_wizard.domain.node_group_names import ShaderNodeGroupNames
from setup_wizard.domain.shader_material_names import StellarToonShaderMaterialNames, V3_BonnyFestivityGenshinImpactMaterialNames, \
    V2_FestivityGenshinImpactMaterialNames, Nya222HonkaiStarRailShaderMaterialNames, \
    JaredNytsPunishingGrayRavenShaderMaterialNames, V1_HoYoToonGenshinImpactMaterialNames
from setup_wizard.import_order import GENSHIN_IMPACT_OUTLINES_FILE_PATH, NextStepInvoker, cache_using_cache_key, get_cache, \
    GENSHIN_IMPACT_ROOT_FOLDER_FILE_PATH, GENSHIN_IMPACT_SHADER_FILE_PATH, HONKAI_STAR_RAIL_ROOT_FOLDER_FILE_PATH, \
    HONKAI_STAR_RAIL_SHADER_FILE_PATH, PUNISHING_GRAY_RAVEN_ROOT_FOLDER_FILE_PATH, PUNISHING_GRAY_RAVEN_SHADER_FILE_PATH
from setup_wizard.material_import_setup.empty_names import LightDirectionEmptyNames
from setup_wizard.outline_import_setup.outline_node_groups import OutlineNodeGroupNames
from setup_wizard.texture_import_setup.material_default_value_setters import MaterialDefaultValueSetter, MaterialDefaultValueSetterFactory
from setup_wizard.utils.scene_utils import move_objects_between_scenes


class GameMaterialImporterFactory:
    def create(game_type: GameType, blender_operator: Operator, context: Context):
        if game_type == GameType.GENSHIN_IMPACT.name:
            return GenshinImpactMaterialImporterFacade(blender_operator, context)
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            return HonkaiStarRailMaterialImporterFacade(blender_operator, context)
        elif game_type == GameType.PUNISHING_GRAY_RAVEN.name:
            return PunishingGrayRavenMaterialImporterFacade(blender_operator, context)
        else:
            raise Exception(f'Unknown {GameType}: {game_type}')


class GameMaterialImporter:
    MATERIAL_PATH_INSIDE_BLEND_FILE = 'Material'
    NODE_TREE_PATH_INSIDE_BLEND_FILE = 'NodeTree'
    OBJECT_PATH_INSIDE_BLEND_FILE = 'Object'
    OUTLINES_FILE_PATH = None

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

        blend_file_with_genshin_node_tree = os.path.join(
            user_selected_shader_blend_file_path,
            self.NODE_TREE_PATH_INSIDE_BLEND_FILE
        ) if user_selected_shader_blend_file_path else None

        default_blend_file_path_node_tree = os.path.join(
            project_root_directory_file_path,
            self.game_default_blend_file_with_materials,
            self.NODE_TREE_PATH_INSIDE_BLEND_FILE
        )

        blend_file_with_light_direction_empties = os.path.join(
            user_selected_shader_blend_file_path,
            self.OBJECT_PATH_INSIDE_BLEND_FILE
        ) if user_selected_shader_blend_file_path else None

        default_blend_file_with_light_direction_empties = os.path.join(
            project_root_directory_file_path,
            self.game_default_blend_file_with_materials,
            self.OBJECT_PATH_INSIDE_BLEND_FILE
        )

        try:
            # Use the exact file the user selected, otherwise fallback to the non-Goo blender file in the directory
            shader_blend_file_path = blend_file_with_genshin_materials or default_blend_file_path
            bpy.ops.wm.append(
                directory=shader_blend_file_path,
                files=self.names_of_game_materials,
                set_fake=True
            )
            shader_blend_node_tree_file_path = blend_file_with_genshin_node_tree or default_blend_file_path_node_tree
            light_direction_empties_file_path = blend_file_with_light_direction_empties or default_blend_file_with_light_direction_empties
            self.import_light_vectors_geometry_node(shader_blend_node_tree_file_path, light_direction_empties_file_path)
        except RuntimeError as ex:
            self.blender_operator.report({'ERROR'}, \
                f"ERROR: Error when trying to append materials and Light Vector geometry node. \n\
                Did not find `{self.game_default_blend_file_with_materials}` in the directory you selected. \n\
                Try selecting the exact blend file you want to use.")
            raise ex

        self.blender_operator.report({'INFO'}, 'Imported Shader/Genshin Materials...')
        if cache_enabled and (user_selected_shader_blend_file_path or project_root_directory_file_path):
            if user_selected_shader_blend_file_path:
                cache_using_cache_key(get_cache(cache_enabled), self.game_shader_file_path, user_selected_shader_blend_file_path)

                outlines_in_shader_blend_file = self.__get_outlines_node_group_from_shader_blend_file(
                    user_selected_shader_blend_file_path)
                if outlines_in_shader_blend_file:
                    self.__set_outlines_cache(cache_enabled, user_selected_shader_blend_file_path)
            else:
                cache_using_cache_key(get_cache(cache_enabled), self.game_shader_folder_path, project_root_directory_file_path)


    def import_light_vectors_geometry_node(self, node_tree_filepath, object_file_path):
        for outline_node_group_name in OutlineNodeGroupNames.V3_LIGHT_VECTORS_GEOMETRY_NODES:
            if not bpy.data.node_groups.get(outline_node_group_name):
                bpy.ops.wm.append(
                    filepath=os.path.join(node_tree_filepath, outline_node_group_name),
                    directory=os.path.join(node_tree_filepath),
                    filename=outline_node_group_name
                )

        light_direction_empties_to_append = \
            [empty_object for empty_object in LightDirectionEmptyNames.LIGHT_DIRECTION_EMPTIES_FILE_IMPORT 
             if not bpy.data.objects.get(empty_object.get('name'))]
        bpy.ops.wm.append(
            directory=os.path.join(object_file_path),
            files=light_direction_empties_to_append
        )

    def __get_outlines_node_group_from_shader_blend_file(self, shader_blend_file_path):
        with bpy.data.libraries.load(shader_blend_file_path) as (data_from, data_to):
            outlines_in_shader_blend_file = [node_group for node_group in data_from.node_groups if
                                                node_group in [
                                                    node_group_name for node_group_name in OutlineNodeGroupNames.V3_BONNY_FESTIVITY_GENSHIN_OUTLINES
                                                ]
                                            ]
        return outlines_in_shader_blend_file

    def __set_outlines_cache(self, cache_enabled, shader_file_path):
        if self.OUTLINES_FILE_PATH and cache_enabled and shader_file_path:
            cache_using_cache_key(get_cache(cache_enabled), self.OUTLINES_FILE_PATH, shader_file_path)

class GenshinImpactMaterialImporterFacade(GameMaterialImporter):
    DEFAULT_BLEND_FILE_WITH_GENSHIN_MATERIALS = 'HoYoverse - Genshin Impact - Goo Engine v3.blend'
    NAMES_OF_GENSHIN_MATERIALS = [
        {'name': V2_FestivityGenshinImpactMaterialNames.BODY},
        {'name': V2_FestivityGenshinImpactMaterialNames.FACE},
        {'name': V2_FestivityGenshinImpactMaterialNames.HAIR},
        {'name': V2_FestivityGenshinImpactMaterialNames.OUTLINES},
        {'name': V3_BonnyFestivityGenshinImpactMaterialNames.BODY},
        {'name': V3_BonnyFestivityGenshinImpactMaterialNames.FACE},
        {'name': V3_BonnyFestivityGenshinImpactMaterialNames.HAIR},
        {'name': V3_BonnyFestivityGenshinImpactMaterialNames.OUTLINES},
        {'name': V1_HoYoToonGenshinImpactMaterialNames.VFX},
    ]
    OUTLINES_FILE_PATH = GENSHIN_IMPACT_OUTLINES_FILE_PATH

    def __init__(self, blender_operator, context):
        super().__init__(
            blender_operator,
            context,
            GENSHIN_IMPACT_SHADER_FILE_PATH,
            GENSHIN_IMPACT_ROOT_FOLDER_FILE_PATH,
            self.DEFAULT_BLEND_FILE_WITH_GENSHIN_MATERIALS,
            self.NAMES_OF_GENSHIN_MATERIALS
        )

    def import_materials(self):
        starting_scene_names = bpy.data.scenes.keys()
        active_scene_name = bpy.context.scene.name if bpy.context.scene else starting_scene_names[0]
        status = super().import_materials()  # Genshin Impact Material Importer

        if status == {'FINISHED'}:
            return status

        # Identify shader here instead of in factory or earlier because we haven't imported materials yet
        shader_identifier_service: ShaderIdentifierService = ShaderIdentifierServiceFactory.create(GameType.GENSHIN_IMPACT.name)
        self.shader: GenshinImpactShaders = shader_identifier_service.identify_shader(bpy.data.materials, bpy.data.node_groups)

        if self.shader in [GenshinImpactShaders.V1_HOYOTOON_GENSHIN_IMPACT_SHADER]:
            self.move_required_scene_objects(starting_scene_names, active_scene_name)
            self.update_vfx_shader_scene_dependency(active_scene_name)
            self.clean_up_unused_objects()

        if self.is_create_hair_material_from_body():  # Genshin Shader >= v4.0
            self.create_hair_material()

        cache_enabled = self.context.window_manager.cache_enabled
        project_root_directory_file_path = self.blender_operator.file_directory \
            or get_cache(cache_enabled).get(self.game_shader_folder_path) \
            or os.path.dirname(self.blender_operator.filepath)

        NextStepInvoker().invoke(
            self.blender_operator.next_step_idx, 
            self.blender_operator.invoker_type, 
            file_path_to_cache=project_root_directory_file_path,
            high_level_step_name=self.blender_operator.high_level_step_name,
            game_type=self.blender_operator.game_type,
        )

    """
        Starting in V1 HoYoToon GEnshin Impact Shader, Light Direction empties get imported into a new scene due to
        the VFX shader having drivers that are connected to a scene.

        Because of this, we need to move the empties to the active scene and then delete the new scene that was created.

        Args:
            starting_scene_names: List of scene names before import
            active_scene_name: Name of the active scene
    """
    def move_required_scene_objects(self, starting_scene_names, active_scene_name):
        new_scenes = list(set(bpy.data.scenes.keys()) - set(starting_scene_names))
        if new_scenes:  # expected length 1
            DEFAULT_COLLECTION_NAME = 'Collection'
            move_objects_between_scenes(new_scenes[0], active_scene_name, LightDirectionEmptyNames.LIGHT_DIRECTION_EMPTIES, DEFAULT_COLLECTION_NAME)
            bpy.data.scenes.remove(bpy.data.scenes[new_scenes[0]])

    """
        VFX Shader > Star Cloak node group has drivers that reference the active scene and need to be updated
        to the current active scene after import

        Args:
            active_scene_name: Name of the active scene
    """
    def update_vfx_shader_scene_dependency(self, active_scene_name):
        DRIVER_VARIABLE_TARGET_DATA_PATHS = ['render.resolution_x', 'render.resolution_y']
        for animation_driver in bpy.data.node_groups[ShaderNodeGroupNames.VFX_SHADER_STAR_CLOAK].animation_data.drivers.values():
            for driver_variable in animation_driver.driver.variables.values():
                for driver_variable_target in driver_variable.targets.values():
                    if driver_variable_target.data_path in DRIVER_VARIABLE_TARGET_DATA_PATHS:
                        driver_variable_target.id = bpy.data.scenes[active_scene_name]

    def clean_up_unused_objects(self):
        OBJECTS_TO_CLEAN_UP = [
            'Preview',
        ]
        for obj in bpy.data.objects:
            if obj.name in OBJECTS_TO_CLEAN_UP:
                obj_data = obj.data
                bpy.data.objects.remove(obj)
                bpy.data.meshes.remove(obj_data)

    def is_create_hair_material_from_body(self):
        body_material_exists = bpy.data.materials.get(V1_HoYoToonGenshinImpactMaterialNames.BODY)
        hair_material_missing = not bpy.data.materials.get(V1_HoYoToonGenshinImpactMaterialNames.HAIR)
        return body_material_exists and hair_material_missing

    def create_hair_material(self):
        body_material = bpy.data.materials.get(V1_HoYoToonGenshinImpactMaterialNames.BODY)
        hair_material = body_material.copy()
        material_default_value_setter: MaterialDefaultValueSetter = MaterialDefaultValueSetterFactory.create(self.blender_operator.game_type)
        material_default_value_setter.set_up_hair_material(hair_material)


class HonkaiStarRailMaterialImporterFacade(GameMaterialImporter):
    DEFAULT_BLEND_FILE_WITH_HSR_MATERIALS = 'StellarToon.blend'
    NAMES_OF_HONKAI_STAR_RAIL_MATERIALS = [
        {'name': Nya222HonkaiStarRailShaderMaterialNames.BODY1},
        {'name': Nya222HonkaiStarRailShaderMaterialNames.BODY2},
        {'name': Nya222HonkaiStarRailShaderMaterialNames.BODY_TRANS},
        {'name': Nya222HonkaiStarRailShaderMaterialNames.HAIR},
        {'name': Nya222HonkaiStarRailShaderMaterialNames.FACE},
        {'name': Nya222HonkaiStarRailShaderMaterialNames.EYESHADOW},
        {'name': Nya222HonkaiStarRailShaderMaterialNames.OUTLINES},
        {'name': Nya222HonkaiStarRailShaderMaterialNames.WEAPON},
        {'name': StellarToonShaderMaterialNames.BASE},
        {'name': StellarToonShaderMaterialNames.HAIR},
        {'name': StellarToonShaderMaterialNames.FACE},
        {'name': StellarToonShaderMaterialNames.WEAPON},
        {'name': StellarToonShaderMaterialNames.BASE_OUTLINES},
        {'name': StellarToonShaderMaterialNames.HAIR_OUTLINES},
        {'name': StellarToonShaderMaterialNames.FACE_OUTLINES},
        {'name': StellarToonShaderMaterialNames.WEAPON_OUTLINES},
    ]

    def __init__(self, blender_operator, context):
        super().__init__(
            blender_operator,
            context,
            HONKAI_STAR_RAIL_SHADER_FILE_PATH,
            HONKAI_STAR_RAIL_ROOT_FOLDER_FILE_PATH,
            self.DEFAULT_BLEND_FILE_WITH_HSR_MATERIALS,
            self.NAMES_OF_HONKAI_STAR_RAIL_MATERIALS
        )

    def import_materials(self):
        status = super().import_materials()  # Honkai Star Rail Material Importer

        # EXEC_DEFAULT hits this if INVOKE_DEFAULT is executed above.
        # Ensure it ends here otherwise it will error below due to the materia
        if status == {'FINISHED'}:
            return status

        # Set 'Use Nodes' because shader does not have that by default
        # It's important this runs BEFORE the next step is invoked because Replace Default Materials clones materials
        for material_dictionary in self.NAMES_OF_HONKAI_STAR_RAIL_MATERIALS:
            material: bpy.types.Material = bpy.data.materials.get(material_dictionary.get('name'))
            if material:
                material.use_nodes = True


        cache_enabled = self.context.window_manager.cache_enabled
        project_root_directory_file_path = self.blender_operator.file_directory \
            or get_cache(cache_enabled).get(self.game_shader_folder_path) \
            or os.path.dirname(self.blender_operator.filepath)

        # Important that this is called here so that 'Use Nodes' is set on all original materials before Replace Default Materials
        NextStepInvoker().invoke(
            self.blender_operator.next_step_idx, 
            self.blender_operator.invoker_type, 
            file_path_to_cache=project_root_directory_file_path,
            high_level_step_name=self.blender_operator.high_level_step_name,
            game_type=self.blender_operator.game_type,
        )


class PunishingGrayRavenMaterialImporterFacade(GameMaterialImporter):
    DEFAULT_BLEND_FILE_WITH_PGR_MATERIALS = 'PGR_Shader.blend'
    NAMES_OF_PUNISHING_GRAY_RAVEN_MATERIALS = [
        {'name': JaredNytsPunishingGrayRavenShaderMaterialNames.ALPHA},
        {'name': JaredNytsPunishingGrayRavenShaderMaterialNames.EYE},
        {'name': JaredNytsPunishingGrayRavenShaderMaterialNames.FACE},
        {'name': JaredNytsPunishingGrayRavenShaderMaterialNames.HAIR},
        {'name': JaredNytsPunishingGrayRavenShaderMaterialNames.MAIN},
        {'name': JaredNytsPunishingGrayRavenShaderMaterialNames.OUTLINES},
    ]

    def __init__(self, blender_operator, context):
        super().__init__(
            blender_operator,
            context,
            PUNISHING_GRAY_RAVEN_SHADER_FILE_PATH,
            PUNISHING_GRAY_RAVEN_ROOT_FOLDER_FILE_PATH,
            self.DEFAULT_BLEND_FILE_WITH_PGR_MATERIALS,
            self.NAMES_OF_PUNISHING_GRAY_RAVEN_MATERIALS
        )

    def import_materials(self):
        status = super().import_materials()  # Punishing Gray Raven Material Importer

        # EXEC_DEFAULT hits this if INVOKE_DEFAULT is executed above.
        # Ensure it ends here otherwise it will error below due to the materia
        if status == {'FINISHED'}:
            return status

        cache_enabled = self.context.window_manager.cache_enabled
        project_root_directory_file_path = self.blender_operator.file_directory \
            or get_cache(cache_enabled).get(self.game_shader_folder_path) \
            or os.path.dirname(self.blender_operator.filepath)

        NextStepInvoker().invoke(
            self.blender_operator.next_step_idx, 
            self.blender_operator.invoker_type, 
            file_path_to_cache=project_root_directory_file_path,
            high_level_step_name=self.blender_operator.high_level_step_name,
            game_type=self.blender_operator.game_type,
        )
