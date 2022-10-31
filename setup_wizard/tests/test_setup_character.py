import bpy
import json
import logging
import os
import sys
from pathlib import PurePath
from setup_wizard.tests.constants import FESTIVITY_ROOT_FOLDER_FILE_PATH, MATERIAL_JSON_FOLDER_FILE_PATH
from setup_wizard.tests.logger import Logger
from setup_wizard.tests.character_filename_to_material_data_mapper import get_character_material_dictionary
from setup_wizard.tests.models.test_operator_executioner import TestOperatorExecutioner

argv = sys.argv
argv = argv[argv.index('--') + 1:]

arg_logs_directory_path = argv[0]
arg_config = json.loads(argv[1])
arg_character_name = argv[2]
arg_character_folder_file_path = argv[3]

Logger(f'{arg_logs_directory_path}/tests.log')
logger = logging.getLogger(__name__)


def setup_character(config, character_name, character_folder_file_path):
    logger.info(f'Starting test for {character_name}')
    try:
        material_json_folder_file_path = str(
            PurePath(config.get(MATERIAL_JSON_FOLDER_FILE_PATH), 
                'placeholder_string_for_import_material_data_operator'
            )
        )
        material_json_files = os.listdir(os.path.dirname(material_json_folder_file_path))

        character_name_in_material_data = get_character_material_dictionary().get(character_name)
        material_json_files = [
            { 'name': material_json_file } for material_json_file in material_json_files
            if f'_{character_name_in_material_data}_' in material_json_file and 
            (
                material_json_file[material_json_file.rindex('_'):material_json_file.rindex('.json')] == '_Body' or
                material_json_file[material_json_file.rindex('_'):material_json_file.rindex('.json')] == '_Dress' or
                material_json_file[material_json_file.rindex('_'):material_json_file.rindex('.json')] == '_Face' or
                material_json_file[material_json_file.rindex('_'):material_json_file.rindex('.json')] == '_Hair'
            )
        ]

        operators = [
            TestOperatorExecutioner('import_character_model', file_directory=character_folder_file_path),
            TestOperatorExecutioner('delete_empties'),
            TestOperatorExecutioner('import_materials', file_directory=config.get(FESTIVITY_ROOT_FOLDER_FILE_PATH)),
            TestOperatorExecutioner('replace_default_materials'),
            TestOperatorExecutioner('import_character_textures'),
            TestOperatorExecutioner('import_outlines', filepath=str(
                PurePath(
                    config.get(FESTIVITY_ROOT_FOLDER_FILE_PATH), 
                    'miHoYo - Outlines.blend'
                )
            )),
            TestOperatorExecutioner('setup_geometry_nodes'),
            TestOperatorExecutioner('import_outline_lightmaps', file_directory=character_folder_file_path),
            TestOperatorExecutioner('import_material_data', files=material_json_files, config=config),
            TestOperatorExecutioner('fix_transformations'),
            TestOperatorExecutioner('setup_head_driver'),
            TestOperatorExecutioner('set_color_management_to_standard'),
            TestOperatorExecutioner('delete_specific_objects'),
        ]

        for operator in operators:
            # Important! Running tests in background will hit a RecursionError if no material files
            if operator.operator_name == 'import_material_data' and not material_json_files:
                continue

            operator.execute()
        logger.info(f'Completed test for {character_name}')
    except Exception as ex:
        logger.error(ex)
        logger.error(f'Failed test for {arg_character_name}')
        pass  # Unexpected exception! Catch any exception and quit
    bpy.ops.wm.quit_blender()


setup_character(arg_config, arg_character_name, arg_character_folder_file_path)
