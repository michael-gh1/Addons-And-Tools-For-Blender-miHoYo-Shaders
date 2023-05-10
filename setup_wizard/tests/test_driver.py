from datetime import datetime
import bpy
import json
import subprocess
import os
from pathlib import Path, PurePath
from setup_wizard.services.config_service import ConfigService
from setup_wizard.tests.constants import BLENDER_EXECUTION_FILE_PATH, CHARACTERS_FOLDER_FILE_PATH

IGNORE_LIST = [
    'Asmoday',
    'Barbara',  # Missing face textures
    'Dvalin',
    'La Signora',
]  # Broken characters

class TestDriver:
    def __init__(self):
        self.config_service = ConfigService('setup_wizard/tests/config.json')

        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H%M%SZ')
        self.logs_directory_path = f'setup_wizard/tests/logs/{timestamp}'
        Path(self.logs_directory_path).mkdir(parents=True, exist_ok=True)

    def execute(self):
        environment_configs = self.config_service.get('environments')

        for environment_config in environment_configs:
            if not environment_config.get('metadata').get('enabled'):
                continue

            test_file = environment_config.get('test_file')
            characters_folder_file_path = environment_config.get(CHARACTERS_FOLDER_FILE_PATH)  # root level
            character_folders = os.listdir(characters_folder_file_path)  # all folders inside
            environment_config_str = json.dumps(environment_config)

            for character_folder_file_path in character_folders:  # for each character folder
                if character_folder_file_path in IGNORE_LIST:
                    continue

                is_not_nested = True
                character_folder_items = os.listdir(
                    str(PurePath(characters_folder_file_path, character_folder_file_path))
                )  # all items inside character folder

                for nested_character_folder_item in character_folder_items:  # is the item a directory?
                    if nested_character_folder_item.lower() == 'material' or \
                        nested_character_folder_item.lower() == 'materials':  # is a material data folder
                        continue
                    absolute_character_folder_file_path = str(PurePath(characters_folder_file_path, character_folder_file_path,  nested_character_folder_item))

                    if os.path.isdir(absolute_character_folder_file_path):
                        subprocess.run([
                            environment_config.get(BLENDER_EXECUTION_FILE_PATH),
                            '-b',
                            '--python',
                            test_file,
                            '--',
                            f'{self.logs_directory_path}',
                            f'{environment_config_str}',
                            f'{character_folder_file_path}{nested_character_folder_item}',
                            f'{absolute_character_folder_file_path}',
                            str(PurePath(characters_folder_file_path, character_folder_file_path, 'materials'))
                        ])
                        is_not_nested = False
                if is_not_nested:
                    absolute_character_folder_file_path = str(PurePath(characters_folder_file_path, character_folder_file_path))

                    subprocess.run([
                        environment_config.get(BLENDER_EXECUTION_FILE_PATH),
                        '-b',
                        '--python',
                        test_file,
                        '--',
                        f'{self.logs_directory_path}',
                        f'{environment_config_str}',
                        f'{character_folder_file_path}',
                        f'{absolute_character_folder_file_path}',
                        str(PurePath(characters_folder_file_path, character_folder_file_path, 'materials'))
                    ])


TestDriver().execute()
bpy.ops.wm.quit_blender()
