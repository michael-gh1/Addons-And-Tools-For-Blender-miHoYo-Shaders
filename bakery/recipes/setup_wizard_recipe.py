import os
from pathlib import PurePath

from bakery.operator_executor import OperatorExecutor
from setup_wizard.tests.character_filename_to_material_data_mapper import get_character_material_dictionary


class SetupWizardRecipe:
    def __init__(self, recipe, source_folder, destination_folder, character_name, festivity_root_folder_file_path, material_json_folder_file_path, **kwargs):
        self.source_folder = source_folder
        self.destination_folder = destination_folder
        self.character_name = character_name
        self.festivity_root_folder_file_path = festivity_root_folder_file_path
        self.material_json_folder_file_path = str(PurePath(material_json_folder_file_path, 'placeholder_string_for_import_material_data_operator'))

        self.character_folder_file_path = self.source_folder  # str(PurePath(self.source_folder, self.character_name))
        self.outlines_file_path = str(PurePath(
                self.festivity_root_folder_file_path, 
                'miHoYo - Outlines.blend'
            )
        )
        self.material_json_files = self.__find_material_json_folder_file_path(recipe)

    def generate_recipe(self):
        operators = [
            OperatorExecutor('bpy.ops.genshin.import_model', file_directory=self.character_folder_file_path),
            OperatorExecutor('bpy.ops.genshin.delete_empties'),
            OperatorExecutor('bpy.ops.genshin.import_materials', file_directory=self.festivity_root_folder_file_path),
            OperatorExecutor('bpy.ops.genshin.replace_default_materials'),
            OperatorExecutor('bpy.ops.genshin.import_textures'),
            OperatorExecutor('bpy.ops.genshin.import_outlines', filepath=self.outlines_file_path),
            OperatorExecutor('bpy.ops.genshin.setup_geometry_nodes'),
            OperatorExecutor('bpy.ops.genshin.import_outline_lightmaps', file_directory=self.character_folder_file_path),
            OperatorExecutor('bpy.ops.genshin.import_material_data', files=self.material_json_files, filepath=self.material_json_folder_file_path),
            OperatorExecutor('bpy.ops.genshin.fix_transformations'),
            OperatorExecutor('bpy.ops.genshin.setup_head_driver'),
            OperatorExecutor('bpy.ops.genshin.set_color_management_to_standard'),
            OperatorExecutor('bpy.ops.genshin.delete_specific_objects'),
        ]

        for operator in operators:
            # Important! Running tests in background will hit a RecursionError if no material files
            if operator.operator_name == 'bpy.ops.genshin.import_material_data' and not self.material_json_files:
                operators.remove(operator)
                break
        
        return operators

    def __find_material_json_folder_file_path(self, recipe):
        material_json_files = os.listdir(os.path.dirname(self.material_json_folder_file_path))

        character_name_in_material_data = get_character_material_dictionary(recipe).get(self.character_name)
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

        return material_json_files