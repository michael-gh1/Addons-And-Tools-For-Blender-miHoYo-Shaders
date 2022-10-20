import bpy
import json
import os
import sys
from pathlib import PurePath
from setup_wizard.import_order import FESTIVITY_ROOT_FOLDER_FILE_PATH, ComponentFunctionFactory
from setup_wizard.tests.gi_assets_material_data_mapper import get_character_material_dictionary

MATERIAL_JSON_FOLDER_FILE_PATH = 'material_json_folder_file_path_with_placeholder_at_end'

argv = sys.argv
argv = argv[argv.index('--') + 1:]

print('argv')
print(argv)

arg_config = json.loads(argv[0])
arg_character_name = argv[1]
arg_character_folder_file_path = argv[2]


def setup_character(config, character_name, character_folder_file_path):
    try:
        material_json_folder_file_path = config.get(MATERIAL_JSON_FOLDER_FILE_PATH)
        material_json_files = os.listdir(os.path.dirname(material_json_folder_file_path))

        character_name = get_character_material_dictionary().get(character_name)
        material_json_files = [
            { 'name': material_json_file } for material_json_file in material_json_files
            if f'_{character_name}_' in material_json_file and 
            (
                material_json_file[material_json_file.rindex('_'):material_json_file.rindex('.json')] == '_Body' or
                material_json_file[material_json_file.rindex('_'):material_json_file.rindex('.json')] == '_Dress' or
                material_json_file[material_json_file.rindex('_'):material_json_file.rindex('.json')] == '_Face' or
                material_json_file[material_json_file.rindex('_'):material_json_file.rindex('.json')] == '_Hair'
            )
        ]

        execute_ops(
            'import_character_model',
            file_directory=character_folder_file_path
        )

        execute_ops(
            'delete_empties'
        )

        execute_ops(
            'import_materials',
            file_directory=config.get(FESTIVITY_ROOT_FOLDER_FILE_PATH)
        )

        execute_ops(
            'replace_default_materials'
        )

        execute_ops(
            'import_character_textures'
        )

        execute_ops(
            'import_outlines',
            filepath=str(PurePath(
                config.get(FESTIVITY_ROOT_FOLDER_FILE_PATH), 
                'miHoYo - Outlines.blend'
            ))
        )

        execute_ops(
            'setup_geometry_nodes'
        )

        execute_ops(
            'import_outline_lightmaps',
            file_directory=character_folder_file_path
        )

        if material_json_files:  # Important! Running tests in background will hit a RecursionError if no material files
            execute_ops(
                'import_material_data',
                files=material_json_files,
                config=config
            )

        execute_ops(
            'fix_transformations'
        )

        execute_ops(
            'setup_head_driver'
        )

        execute_ops(
            'set_color_management_to_standard'
        )

        execute_ops(
            'delete_specific_objects'
        )
    except Exception as ex:
        print(ex)
        pass  # Unexpected exception! Catch any exception and quit
    bpy.ops.wm.quit_blender()


def execute_ops(component_name, file_directory='', filepath='', files=[], config={}):
    operator_to_execute = ComponentFunctionFactory.create_component_function(component_name)

    if files:
        operator_to_execute(
            'EXEC_DEFAULT',
            files=files,
            filepath=config.get(MATERIAL_JSON_FOLDER_FILE_PATH),
        )
    elif file_directory or filepath:
        operator_to_execute(
            'EXEC_DEFAULT',
            file_directory=file_directory,
            filepath=filepath
        )
    else:
        operator_to_execute(
            'EXEC_DEFAULT'
        )


setup_character(arg_config, arg_character_name, arg_character_folder_file_path)
