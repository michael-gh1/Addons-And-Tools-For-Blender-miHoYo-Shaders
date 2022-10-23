# Author: michael-gh1

# Kudos to Modder4869 for introducing another way to get the real material name for Dress materials

import bpy
import json
import os

# Config Constants
COMPONENT_NAME = 'component_name'
ENABLED = 'enabled'
CACHE_KEY = 'cache_key'
UI_ORDER_CONFIG_KEY = 'ui_order'

# Cache Constants
FESTIVITY_ROOT_FOLDER_FILE_PATH = 'festivity_root_folder_file_path'
FESTIVITY_OUTLINES_FILE_PATH = 'festivity_outlines_file_path'
CHARACTER_MODEL_FOLDER_FILE_PATH = 'character_model_folder_file_path'


class NextStepInvoker:
    def invoke(self, current_step_index, type, file_path_to_cache=None, high_level_step_name=None):
        if type == 'invoke_next_step':
            invoke_next_step(current_step_index, file_path_to_cache)
        elif type == 'invoke_next_step_ui':
            invoke_next_step_ui(high_level_step_name, current_step_index)
        else:
            print(f'Warning: Unknown type found when invoking: {type}')


def invoke_next_step(current_step_idx: int, file_path_to_cache=None):
    path_to_setup_wizard_folder = os.path.dirname(os.path.abspath(__file__))
    file = open(f'{path_to_setup_wizard_folder}/config.json')
    config = json.load(file)

    if current_step_idx == 1:
        clear_cache()
    cache = get_cache()

    if current_step_idx <= 0 or current_step_idx + 1 > len(config):  # +1 because we have a step 0
        return

    # Cache only if running SetupWizard using F3 search menu. It should return before reaching here.
    previous_step = config.get(str(current_step_idx - 1))
    if file_path_to_cache and previous_step and previous_step[CACHE_KEY]:
        cache_previous_step_file_path(cache, previous_step, file_path_to_cache)
    
    if config[str(current_step_idx)][ENABLED]:
        cached_file_directory = cache.get(config[str(current_step_idx)][CACHE_KEY], '')
        execute_or_invoke = 'EXEC' if cached_file_directory else 'INVOKE'
        component_name = config[str(current_step_idx)][COMPONENT_NAME]
        function_to_use = ComponentFunctionFactory.create_component_function(component_name)

        if type(function_to_use) is bpy.ops._BPyOpsSubModOp:
            print(f'Calling {function_to_use} with {execute_or_invoke}_DEFAULT w/ cache: {cached_file_directory}')
            function_to_use(
                    f'{execute_or_invoke}_DEFAULT', 
                    next_step_idx=current_step_idx + 1, 
                    file_directory=cached_file_directory,
                    invoker_type='invoke_next_step'
            )
        else:
            function_to_use(current_step_idx + 1)
    else:
        invoke_next_step(current_step_idx + 1)


def invoke_next_step_ui(high_level_step_name, current_step_index):
    path_to_setup_wizard_folder = os.path.dirname(os.path.abspath(__file__))

    file = open(f'{path_to_setup_wizard_folder}/config_ui.json')
    config = json.load(file)
    ui_order = config.get(UI_ORDER_CONFIG_KEY)
    high_level_step_list = ui_order.get(high_level_step_name)
    if current_step_index == len(high_level_step_list) - 1:
        return
    component_name = high_level_step_list[current_step_index + 1]
    operator_to_execute = ComponentFunctionFactory.create_component_function(component_name)

    operator_to_execute(
        'EXEC_DEFAULT',
        next_step_idx=current_step_index + 1,
        invoker_type='invoke_next_step_ui',
        high_level_step_name=high_level_step_name
    )


def get_cache(cache_enabled=True):
    if not cache_enabled:
        return {}
    path_to_setup_wizard_folder = os.path.dirname(os.path.abspath(__file__))

    cache_file_path = f'{path_to_setup_wizard_folder}/cache.json.tmp'
    if not os.path.exists(cache_file_path):
        return {}
    cache_file = open(cache_file_path)
    cache = json.load(cache_file)
    return cache


def cache_previous_step_file_path(cache, last_step, file_path_to_cache):
    if not file_path_to_cache:
        return
    path_to_setup_wizard_folder = os.path.dirname(os.path.abspath(__file__))
    cache_file_path = f'{path_to_setup_wizard_folder}/cache.json.tmp'
    step_cache_key = last_step.get(CACHE_KEY)

    print(f'Assigning `{step_cache_key}:{file_path_to_cache}` in cache')
    cache[step_cache_key] = file_path_to_cache
    with open(cache_file_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)


def cache_using_cache_key(cache, cache_key, file_path_for_cache):
    if not file_path_for_cache:
        return
    path_to_setup_wizard_folder = os.path.dirname(os.path.abspath(__file__))
    cache_file_path = f'{path_to_setup_wizard_folder}/cache.json.tmp'

    print(f'Assigning `{cache_key}:{file_path_for_cache}` in cache')
    cache[cache_key] = file_path_for_cache
    with open(cache_file_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)


def clear_cache():
    path_to_setup_wizard_folder = os.path.dirname(os.path.abspath(__file__))
    cache_file_path = f'{path_to_setup_wizard_folder}/cache.json.tmp'
    with open(cache_file_path, 'w') as f:
        json.dump({}, f)


def get_actual_material_name_for_dress(material_name):
    for material in bpy.data.materials:
        if material_name in material.name:
            try:
                # ex. 'Avatar_Lady_Pole_Rosaria_Tex_Body_Diffuse.png'
                base_color_texture_image_name = material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node.image.name_full
                actual_material_name = base_color_texture_image_name.split('_')[-2]
                actual_material_name = \
                    actual_material_name if actual_material_name == 'Hair' or actual_material_name == 'Body' \
                        else 'Hair' if 'Hair' in base_color_texture_image_name \
                            else 'Body' if 'Body' in base_color_texture_image_name \
                                else actual_material_name  # fallback method to get mat name
            except IndexError:
                # ex. 'Diffuse Texture.001'
                actual_material_name = material_name.split('_')[-1]
                actual_material_name = actual_material_name if actual_material_name != 'Dress' else 'Body'  # if mat name is 'body' or 'hair' use that, else fallback to 'body'
                print(f'WARNING: Fallback to applying "{actual_material_name}" onto "{material_name}". Image name is not parseable for: {material_name}')
            return actual_material_name


class ComponentFunctionFactory:
    @staticmethod
    def create_component_function(component_name):
        if component_name == 'import_materials':
            return bpy.ops.genshin.import_materials
        elif component_name == 'import_character_model':
            return bpy.ops.genshin.import_model
        elif component_name == 'replace_default_materials':
            return bpy.ops.genshin.replace_default_materials
        elif component_name == 'import_character_textures':
            return bpy.ops.genshin.import_textures
        elif component_name == 'import_outlines':
            return bpy.ops.genshin.import_outlines
        elif component_name == 'setup_geometry_nodes':
            return bpy.ops.genshin.setup_geometry_nodes
        elif component_name == 'import_outline_lightmaps':
            return bpy.ops.genshin.import_outline_lightmaps
        elif component_name == 'import_material_data':
            return bpy.ops.genshin.import_material_data
        elif component_name == 'fix_mouth_outlines':
            return bpy.ops.genshin.fix_mouth_outlines
        elif component_name == 'delete_empties':
            return bpy.ops.genshin.delete_empties
        elif component_name ==  'delete_specific_objects':
            return bpy.ops.genshin.delete_specific_objects
        elif component_name == 'fix_transformations':
            return bpy.ops.genshin.fix_transformations
        elif component_name == 'set_color_management_to_standard':
            return bpy.ops.genshin.set_color_management_to_standard
        elif component_name == 'setup_head_driver':
            return bpy.ops.genshin.setup_head_driver
        else:
            raise Exception(f'Unknown component name passed into {__name__}: {component_name}')
