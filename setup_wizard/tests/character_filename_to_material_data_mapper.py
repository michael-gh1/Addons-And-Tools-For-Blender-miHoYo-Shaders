import json
import os
from pathlib import PurePath


def main():
    config = json.load(open('setup_wizard/tests/config.json')).get('environments')[0]
    character_material_dictionary = get_character_material_dictionary(config)
    return character_material_dictionary


def get_character_material_dictionary(config):
    character_material_dictionary = {}
    characters_folder_file_path = config.get('characters_folder_file_path')

    for character_folder in os.listdir(characters_folder_file_path):
        for root, dirs, files in os.walk(PurePath(characters_folder_file_path, character_folder)):
            for file in files:
                if file.endswith('.fbx'):
                    try:
                        material_data_name = parse_fbx_filename_to_material_data_name(file)
                        character_name_key = parse_character_name_key(root)

                        character_material_dictionary[character_name_key] = material_data_name
                    except ValueError:
                        continue
    return character_material_dictionary


# Parse the character name out of the fbx file name
# Handle different name formats (space, underscore, period) after character name
def parse_fbx_filename_to_material_data_name(filename):
    index_of_character_name = 3

    material_data_name = filename[filename.index('Avatar'):].split('_')[index_of_character_name]
    material_data_name = material_data_name.split(' ')[0]
    material_data_name = material_data_name.split('_')[0]
    material_data_name = material_data_name.split('.')[0]
    return material_data_name

# Character name key is used by tests, format: {character_name}{skin_name}
def parse_character_name_key(file_path):
    character_name_key = file_path[file_path.index('Characters') + len('Characters') + 1:]
    character_name_key = character_name_key.replace('\\', '')  # Windows
    character_name_key = character_name_key.replace('/', '')  # Linux/OSX filesytsem?
    return character_name_key


if __name__ == '__main__':
    main()
