import json
import subprocess
import os
from pathlib import PurePath
from setup_wizard.services.config_service import ConfigService

BLENDER_EXECUTION_FILE_PATH = 'blender_execution_file_path'
CHARACTERS_FOLDER_FILE_PATH = 'characters_folder_file_path'
IGNORE_LIST = [
    'Asmoday'
]

class TestDriver:
    def __init__(self):
        self.config_service = ConfigService('setup_wizard/tests/config.json')

    def execute(self):
        characters_folder_file_path = self.config_service.get(CHARACTERS_FOLDER_FILE_PATH)  # root level
        character_folders = os.listdir(characters_folder_file_path)  # all folders inside

        for character_folder_file_path in character_folders:  # for each character folder
            if character_folder_file_path in IGNORE_LIST:
                continue

            is_not_nested = True
            character_folder_items = os.listdir(
                str(PurePath(characters_folder_file_path, character_folder_file_path))
            )  # all items inside character folder

            for nested_character_folder_item in character_folder_items:  # is the item a directory?
                if os.path.isdir(nested_character_folder_item):
                    subprocess.run([
                        self.config_service.get(BLENDER_EXECUTION_FILE_PATH),
                        '--python',
                        'setup_wizard/tests/test_setup_character.py',
                        '--',
                        f'{json.dumps(self.config_service.get_config())}',
                        f'{character_folder_file_path}',
                        f'{str(PurePath(characters_folder_file_path, character_folder_file_path))}'
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
                subprocess.run([
                    self.config_service.get(BLENDER_EXECUTION_FILE_PATH),
                    '--python',
                    'setup_wizard/tests/test_setup_character.py',
                    '--',
                    f'{json.dumps(self.config_service.get_config())}',
                    f'{character_folder_file_path}',
                    f'{str(PurePath(characters_folder_file_path, character_folder_file_path))}'
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
