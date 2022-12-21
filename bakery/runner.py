import json
import os
import subprocess

from datetime import datetime
from pathlib import Path


IGNORE_LIST = [
    'Asmoday',
    'Barbara',  # Missing face textures
    'Dvalin',
    'La Signora',
]  # Broken characters


class Runner:
    def __init__(self):
        recipe_file = open('bakery/recipes/setup_wizard_recipe.json')
        self.recipe_json = json.load(recipe_file)
        self.recipe = self.recipe_json.get('recipe')

        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H%M%SZ')
        self.logs_directory_path = f'bakery/logs/'
        Path(self.logs_directory_path).mkdir(parents=True, exist_ok=True)
        self.recipe['timestamp'] = timestamp

    def execute(self):
        blender_executable_path = self.recipe.get('blender_executable_path')
        source_folder = self.recipe.get('characters_folder_file_path')
        destination_folder = self.recipe.get('destination_folder')
        file_extension_search = self.recipe.get('file_extension_search')

        character_names = [character_name for character_name in os.listdir(source_folder) if character_name not in IGNORE_LIST]

        for root, dirs, files in os.walk(source_folder):
            skip = False
            if 'Material' in root:
                skip = True
            for ignored_character in IGNORE_LIST:
                if ignored_character in root:
                    skip = True
                    break
            if skip:
                print(f'Skipping: {root}')
                continue
            if root[root.rindex('\\') + 1:] in character_names:
                character_name = root[root.rindex('\\') + 1:]
                print(f'character_name: {character_name}')
                self.recipe['character_name'] = character_name

            print(f'root: {root}')
            print(f'dirs: {dirs}')
            print(f'files: {files}')

            for file in files:
                if file_extension_search in file:
                    self.recipe['source_folder'] = root  # TODO: We shouldn't modify existing values
                    subprocess.run([
                        blender_executable_path,
                        '-b',
                        '--python',
                        'bakery/recipe_runner.py',
                        '--',
                        f'{json.dumps(self.recipe)}',
                    ])


def main():
    runner = Runner()
    runner.execute()


if __name__ == '__main__':
    main()
