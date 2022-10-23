from datetime import datetime
import bpy
import json
import subprocess
import os
from pathlib import Path, PurePath
from setup_wizard.services.config_service import ConfigService

BLENDER_EXECUTION_FILE_PATH = 'blender_execution_file_path'
CHARACTERS_FOLDER_FILE_PATH = 'characters_folder_file_path'
IGNORE_LIST = [
    'Asmoday',
    'Barbara',
    'Childe',  # Body_CloakEffecTMesh. Maybe make us check 'BodyPart.' and not just 'BodyPart'
    'Dainsleif',  # Cloak Outlines not found...we didn't replace material
    'Dvalin',
    'Eula', # Body_CloakEffectMesh
    'La Signora',
    'Ningguang',  # Floral issue?
    'Xiao',  # Mat_Arm not found...didn't replace material,
]  # TODO: Fix these characters, latest changes in v1.1.0 likely broke them

class TestDriver:
    def __init__(self):
        self.config_service = ConfigService('setup_wizard/tests/config.json')

        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H%M%SZ')
        self.logs_directory_path = f'setup_wizard/tests/logs/{timestamp}'
        Path(self.logs_directory_path).mkdir(parents=True, exist_ok=True)

    def execute(self):
        characters_folder_file_path = self.config_service.get(CHARACTERS_FOLDER_FILE_PATH)  # root level
        character_folders = os.listdir(characters_folder_file_path)  # all folders inside
        config = json.dumps(self.config_service.get_config())

        for character_folder_file_path in character_folders:  # for each character folder
            if character_folder_file_path in IGNORE_LIST:
                continue

            is_not_nested = True
            character_folder_items = os.listdir(
                str(PurePath(characters_folder_file_path, character_folder_file_path))
            )  # all items inside character folder

            for nested_character_folder_item in character_folder_items:  # is the item a directory?
                if nested_character_folder_item == 'Material' or \
                    nested_character_folder_item == 'Materials':  # is a material data folder
                    continue
                absolute_character_folder_file_path = str(PurePath(characters_folder_file_path, character_folder_file_path,  nested_character_folder_item))

                if os.path.isdir(absolute_character_folder_file_path):
                    subprocess.run([
                        self.config_service.get(BLENDER_EXECUTION_FILE_PATH),
                        '-b',
                        '--python',
                        'setup_wizard/tests/test_setup_character.py',
                        '--',
                        f'{self.logs_directory_path}',
                        f'{config}',
                        f'{character_folder_file_path}{nested_character_folder_item}',
                        f'{absolute_character_folder_file_path}'
                    ])
                    # setup_character(
                    #     self.config_service.get_config(),
                    #     f'{nested_character_folder_item}', 
                    #     str(
                    #         PurePath(
                    #             characters_folder_file_path, 
                    #             character_folder_file_path, 
                    #             nested_character_folder_item
                    #         )
                    #     )
                    # )
                    is_not_nested = False
            if is_not_nested:
                absolute_character_folder_file_path = str(PurePath(characters_folder_file_path, character_folder_file_path))

                subprocess.run([
                    self.config_service.get(BLENDER_EXECUTION_FILE_PATH),
                    '-b',
                    '--python',
                    'setup_wizard/tests/test_setup_character.py',
                    '--',
                    f'{self.logs_directory_path}',
                    f'{config}',
                    f'{character_folder_file_path}',
                    f'{absolute_character_folder_file_path}'
                ])
                # setup_character(
                #     self.config_service.get_config(),
                #     character_folder_file_path,
                #     str(
                #         PurePath(
                #             characters_folder_file_path,
                #             character_folder_file_path
                #         )
                #     )
                # )


TestDriver().execute()
bpy.ops.wm.quit_blender()
