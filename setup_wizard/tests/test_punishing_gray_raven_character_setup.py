import bpy
import json
import logging
import os
import sys
from pathlib import PurePath
from setup_wizard.import_order import PUNISHING_GRAY_RAVEN_ROOT_FOLDER_FILE_PATH, PUNISHING_GRAY_RAVEN_SHADER_FILE_PATH, \
    PUNISHING_GRAY_RAVEN_OUTLINES_FILE_PATH, PUNISHING_GRAY_RAVEN_CHIBI_MESH_FILE_PATH
from setup_wizard.tests.constants import RIG_CHARACTER
from setup_wizard.tests.logger import Logger
from setup_wizard.tests.models.test_operator_executioner import PunishingGrayRavenTestOperatorExecutioner

argv = sys.argv
argv = argv[argv.index('--') + 1:]

arg_logs_directory_path = argv[0]
arg_config = json.loads(argv[1])
arg_character_name = argv[2]
arg_character_folder_file_path = argv[3]
arg_material_data_folder = argv[4]

Logger(f'{arg_logs_directory_path}/tests.log')
logger = logging.getLogger(__name__)

def setup_character(config, character_name, character_folder_file_path, arg_material_data_folder):
    logger.info(f'Starting test for {character_name}')
    logger.info(f'Emptying scene...')

    default_objects_to_delete = ['Cube', 'Light', 'Camera']

    for object_to_delete in default_objects_to_delete:
        object = bpy.context.scene.objects.get(object_to_delete)
        if object:
            object_name = object.name  # necessary to create because we lose the reference after deletion
            logger.info(f'Deleting {object_name}')
            bpy.data.objects.remove(object)
            logger.info(f'Deleted {object_name}')

    logger.info(f'Preparing scene...')
    default_collection = bpy.data.collections.get('Collection')
    if default_collection:
        logger.info(f'Renaming {default_collection.name} to {character_name}...')
        default_collection.name = character_name
        logger.info(f'Successfully renamed Collection to: {bpy.data.collections.get(character_name).name}')
    bpy.context.scene.character_setup_wizard_logging_enabled = True

    logger.info(f'{config.get("metadata")}')

    if config.get('metadata').get('betterfbx_enabled'):
        logger.info('Enabling BetterFBX')
        bpy.ops.preferences.addon_enable(module='better_fbx')
        logger.info(f"{bpy.context.preferences.addons.get('better_fbx')}")
    else:
        logger.info('Disabling BetterFBX')
        bpy.ops.preferences.addon_disable(module='better_fbx')
        logger.info(f"{bpy.context.preferences.addons.get('better_fbx')}")

    try:
        material_json_files = []
        try:
            material_json_files = os.listdir(PurePath(arg_material_data_folder))
        except FileNotFoundError as ex:
            pass  # eat the error, NPCs do not have material data

        material_json_files = [
            { 'name': material_json_file } for material_json_file in material_json_files if material_json_file.endswith('.json')
        ]

        logger.info(material_json_files)

        operators = [
            PunishingGrayRavenTestOperatorExecutioner('clear_cache_operator'),
            PunishingGrayRavenTestOperatorExecutioner('import_character_model', file_directory=character_folder_file_path),
            PunishingGrayRavenTestOperatorExecutioner('delete_empties'),
            PunishingGrayRavenTestOperatorExecutioner('import_materials', 
                file_directory=config.get(PUNISHING_GRAY_RAVEN_ROOT_FOLDER_FILE_PATH) or '',
                filepath=config.get(PUNISHING_GRAY_RAVEN_SHADER_FILE_PATH) or '',
            ),
            PunishingGrayRavenTestOperatorExecutioner('replace_default_materials'),
            PunishingGrayRavenTestOperatorExecutioner('import_character_textures'),
            PunishingGrayRavenTestOperatorExecutioner('import_outlines', filepath=config.get(PUNISHING_GRAY_RAVEN_OUTLINES_FILE_PATH)),
            PunishingGrayRavenTestOperatorExecutioner('setup_geometry_nodes'),
            PunishingGrayRavenTestOperatorExecutioner('import_outline_lightmaps', file_directory=character_folder_file_path),
            # PunishingGrayRavenTestOperatorExecutioner('import_material_data', 
            #                                      files=material_json_files, 
            #                                      filepath=str(PurePath(arg_material_data_folder, "placeholder_value")),
            #                                      config=config),
            PunishingGrayRavenTestOperatorExecutioner('fix_transformations'),
            PunishingGrayRavenTestOperatorExecutioner('setup_head_driver'),
            PunishingGrayRavenTestOperatorExecutioner('set_color_management_to_standard'),
            PunishingGrayRavenTestOperatorExecutioner('rename_shader_materials'),
            PunishingGrayRavenTestOperatorExecutioner('delete_specific_objects'),
            PunishingGrayRavenTestOperatorExecutioner('set_up_armtwist_bone_constraints'),
            PunishingGrayRavenTestOperatorExecutioner('join_meshes_on_armature'),
            # PunishingGrayRavenTestOperatorExecutioner('rootshape_filepath_setter', filepath=config.get(GENSHIN_RIGIFY_BONE_SHAPES_FILE_PATH)),
            PunishingGrayRavenTestOperatorExecutioner('rig_character', config=config),
            PunishingGrayRavenTestOperatorExecutioner('paint_vertex_colors'),
        ]

        for operator in operators:
            # Important! Running tests in background will hit a RecursionError if no material files
            if operator.operator_name == 'import_material_data' and not material_json_files:
                continue
            elif operator.operator_name == 'rig_character' and not config.get(RIG_CHARACTER):
                continue

            logger.info(f'Executing Operator: {operator.operator_name}')
            operator.execute()

        chibi_operators = [
            PunishingGrayRavenTestOperatorExecutioner('set_up_chibi_face_mesh', filepath=config.get(PUNISHING_GRAY_RAVEN_CHIBI_MESH_FILE_PATH)),
            PunishingGrayRavenTestOperatorExecutioner('import_chibi_face_texture', file_directory=character_folder_file_path),
        ]
        if [material for material in bpy.data.materials if 'XDefaultMaterial' in material.name]:
            for chibi_operator in chibi_operators:
                logger.info(f'Executing Operator: {chibi_operator.operator_name}')
                chibi_operator.execute()

        logger.info(f'Completed test for {character_name}')
    except Exception as ex:
        logger.error(ex)
        logger.error(f'Failed test for {arg_character_name}')
        raise ex  # If it errors out it will still quit blender
    finally:
        if config.get('metadata').get('save_file'):
            logger.info(f'Preparing file for {character_name}')
            logger.info('Setting Transform Mode to "XYZ Euler"...')
            character_armature = [object for object in bpy.data.objects if object.type == 'ARMATURE'][0]
            character_armature.rotation_mode = 'XYZ'
            character_armature.animation_data_clear()  # some characters have animation data, clear it
            logger.info('Successfully set to "XYZ Euler"')

            logger.info('Packing files...')
            try:
                bpy.ops.file.pack_all()
            except RuntimeError as e:
                logger.warning(e)
            logger.info('Successfully packed files')

            filename = f'{character_name}.blend'
            logger.info(f'Saving file for {character_name} as: {filename}...')
            os.makedirs(f'{os.path.abspath(arg_logs_directory_path)}/PunishingGrayRaven', exist_ok=True)
            bpy.ops.wm.save_as_mainfile(filepath=f'{os.path.abspath(arg_logs_directory_path)}/PunishingGrayRaven/{filename}')
            logger.info(f'Saved file for {character_name} as: {filename}')
        bpy.ops.wm.quit_blender()


setup_character(arg_config, arg_character_name, arg_character_folder_file_path, arg_material_data_folder)
