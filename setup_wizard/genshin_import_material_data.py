# Author: michael-gh1

import bpy
import json
from pathlib import PurePosixPath

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, CollectionProperty
from bpy.types import Operator, PropertyGroup
import os
from setup_wizard.exceptions import UnsupportedMaterialDataJsonFormatException

from setup_wizard.import_order import NextStepInvoker
from setup_wizard.models import CustomOperatorProperties
from setup_wizard.parsers.material_data_json_parsers import HoyoStudioMaterialDataJsonParser, MaterialDataJsonParser, UABEMaterialDataJsonParser


class GI_OT_GenshinImportMaterialData(Operator, ImportHelper, CustomOperatorProperties):
    """Select the Character Material Data Json Files for Outlines"""
    bl_idname = "genshin.import_material_data"  # important since its how we chain file dialogs
    bl_label = "Genshin: Select Material Json Data Files"

    # ImportHelper mixin class uses this
    filename_ext = "*.*"

    import_path: StringProperty(
        name="Path",
        description="Path to the material json data files",
        default="",
        subtype='DIR_PATH'
    )

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    files: CollectionProperty(type=PropertyGroup)

    local_material_mapping = {
        '_SpecMulti': 'Non-Metallic Specular Multiplier 1',
        '_SpecMulti2': 'Non-Metallic Specular Multiplier 2',
        '_SpecMulti3': 'Non-Metallic Specular Multiplier 3',
        '_SpecMulti4': 'Non-Metallic Specular Multiplier 4',
        '_SpecMulti5': 'Non-Metallic Specular Multiplier 5',
        '_Shininess': 'Non-Metallic Specular Shininess 1',
        '_Shininess2': 'Non-Metallic Specular Shininess 2',
        '_Shininess3': 'Non-Metallic Specular Shininess 3',
        '_Shininess4': 'Non-Metallic Specular Shininess 4',
        '_Shininess5': 'Non-Metallic Specular Shininess 5',
        '_MTMapLightColor': 'Metallic Light Color',
        '_MTMapDarkColor': 'Metallic Dark Color',
        '_MTShadowMultiColor': 'Metallic Shadow Multiply Color',
        '_MTMapTileScale': 'Metallic Map Tile Scale',
        '_MTMapBrightness': 'Metallic Brightness',
        '_MTSpecularColor': 'Metallic Specular Color',
        '_MTSpecularScale': 'Metallic Specular Scale',
        '_MTShininess': 'Metallic Specular Shininess',
        '_ShadowRampWidth': 'Ramp Width *NdotL only* *Ramp only*'
    }

    outline_mapping = {
        '_OutlineColor': 'Outline Color 1',
        '_OutlineColor2': 'Outline Color 2',
        '_OutlineColor3': 'Outline Color 3',
        '_OutlineColor4': 'Outline Color 4',
        '_OutlineColor5': 'Outline Color 5'
    }

    global_material_mapping = {
        '_MTUseSpecularRamp': 'Use Specular Ramp?',
        '_FaceBlushColor': 'Blush Color',
    }

    parsers = [
        HoyoStudioMaterialDataJsonParser,
        UABEMaterialDataJsonParser,
    ]

    def execute(self, context):
        directory_file_path = os.path.dirname(self.filepath)

        if not self.filepath or not self.files:
            bpy.ops.genshin.import_material_data(
                'INVOKE_DEFAULT',
                next_step_idx=self.next_step_idx, 
                file_directory=self.file_directory,
                invoker_type=self.invoker_type,
                high_level_step_name=self.high_level_step_name
            )
            return {'FINISHED'}

        for file in self.files:
            body_part = PurePosixPath(file.name).stem.split('_')[-1]

            fp = open(f'{directory_file_path}/{file.name}')
            json_material_data = json.load(fp)
            material_data_parser = self.__get_material_data_json_parser(json_material_data)

            try:
                self.set_up_mesh_material_data(material_data_parser, body_part)
                self.set_up_outline_colors(material_data_parser, body_part)
            except KeyError:
                self.report({'WARNING'}, \
                    f'Continuing to apply other material data, but: \n'
                    f'* Material Data JSON "{body_part}" was selected, but there is no material named "miHoYo - Genshin {body_part}"')
                continue

        self.report({'INFO'}, 'Imported material data')
        NextStepInvoker().invoke(
            self.next_step_idx, 
            self.invoker_type, 
            high_level_step_name=self.high_level_step_name
        )
        super().reset()
        return {'FINISHED'}

    def set_up_mesh_material_data(self, material_data_parser, body_part):
        if body_part != 'Face':
            body_part_material = bpy.data.materials[f'miHoYo - Genshin {body_part}']
            node_tree_group001_inputs = body_part_material.node_tree.nodes["Group.001"].inputs

            self.__apply_material_data(
                self.local_material_mapping,
                node_tree_group001_inputs,
                material_data_parser,
                body_part
            )
            
        # Not sure, should we only apply Global Material Properties from Body .dat file?
        if body_part == 'Body':
            global_material_properties_node_inputs = \
                bpy.data.node_groups["GLOBAL MATERIAL PROPERTIES"].nodes["Group Output"].inputs

            self.__apply_material_data(
                self.global_material_mapping,
                global_material_properties_node_inputs,
                material_data_parser,
                body_part
            )

    def set_up_outline_colors(self, material_data_parser, body_part):
        outlines_material = bpy.data.materials[f'miHoYo - Genshin {body_part} Outlines']
        outlines_shader_node_inputs = outlines_material.node_tree.nodes.get('Group.002').inputs

        self.__apply_material_data(
            self.outline_mapping, 
            outlines_shader_node_inputs,
            material_data_parser,
            body_part
        )

    def __get_material_data_json_parser(self, json_material_data):
        for index, parser_class in enumerate(self.parsers):
            try:
                parser: MaterialDataJsonParser  = parser_class(json_material_data)
                parser.parse()
                return parser
            except AttributeError:
                if index == len(self.parsers) - 1:
                    raise UnsupportedMaterialDataJsonFormatException(self.parsers)

    def __apply_material_data(self, material_mapping, node_inputs, material_data_parser, body_part):
        for material_json_name, material_node_name in material_mapping.items():
            material_json_value = self.__get_value_in_json_parser(material_data_parser, material_json_name)

            if not material_json_value:
                self.__handle_material_value_not_found(body_part, material_json_name)
                continue

            node_input = node_inputs.get(material_node_name)
            node_input.default_value = material_json_value

    def __get_value_in_json_parser(self, parser, key):
        return getattr(parser.m_floats, key, None) or getattr(parser.m_colors, key, None)

    def __handle_material_value_not_found(self, body_part, material_json_name):
        # Log at INFO level because otherwise it may become "just another warning" and get ignored
        self.report({'INFO'}, f'Unable to find material data: {material_json_name} on {body_part} JSON. \n' \
            '* This may or may not be expected. Continuing to apply other material data.')


register, unregister = bpy.utils.register_classes_factory(GI_OT_GenshinImportMaterialData)
