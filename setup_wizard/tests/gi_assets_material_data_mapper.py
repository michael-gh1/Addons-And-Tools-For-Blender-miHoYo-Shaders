import json
import os
from pathlib import PurePath


config = json.load(open('setup_wizard/tests/config.json'))
characters_folder_file_path = config.get('characters_folder_file_path')

material_json_folder_file_path = config.get('material_json_folder_file_path')
material_json_files = os.listdir(material_json_folder_file_path)

def main():
    character_material_dictionary = get_character_material_dictionary()
    return character_material_dictionary


def get_character_material_dictionary():
    index_of_character_name = 3
    character_material_dictionary = {}

    for character_folder in os.listdir(characters_folder_file_path):
        for root, dirs, files in os.walk(PurePath(characters_folder_file_path, character_folder)):
            for file in files:
                if file.endswith('.fbx'):
                    try:
                        # find the character name via the fbx file name
                        # handle different name formats (space, underscore, period) after character name
                        material_name = file[file.index('Avatar'):].split('_')[index_of_character_name]
                        material_name = material_name.split(' ')[0]
                        material_name = material_name.split('_')[0]
                        material_name = material_name.split('.')[0]
                        
                        # key name is used by tests, format: {character_name}{skin_name}
                        character_name_key = root[root.index('Characters\\') + len('Characters\\'):].replace('\\', '')
                        character_material_dictionary[character_name_key] = material_name
                    except ValueError:
                        continue
    return character_material_dictionary


if __name__ == '__main__':
    main()
