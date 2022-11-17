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
from setup_wizard.material_data_applier import MaterialDataApplier, V1_MaterialDataApplier, V2_MaterialDataApplier
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

            for material_data_applier_cls in [V2_MaterialDataApplier, V1_MaterialDataApplier]:
                try:
                    material_data_applier: MaterialDataApplier = material_data_applier_cls(material_data_parser, body_part)
                    material_data_applier.set_up_mesh_material_data()
                    material_data_applier.set_up_outline_colors()
                except AttributeError:
                    continue # fallback and try next version
                except KeyError:
                    self.report({'WARNING'}, \
                        f'Continuing to apply other material data, but: \n'
                        f'* Material Data JSON "{body_part}" was selected, but there is no material named "miHoYo - Genshin {body_part}"')
                    break

        self.report({'INFO'}, 'Imported material data')
        NextStepInvoker().invoke(
            self.next_step_idx, 
            self.invoker_type, 
            high_level_step_name=self.high_level_step_name
        )
        super().clear_custom_properties()
        return {'FINISHED'}

    def __get_material_data_json_parser(self, json_material_data):
        for index, parser_class in enumerate(self.parsers):
            try:
                parser: MaterialDataJsonParser  = parser_class(json_material_data)
                parser.parse()
                return parser
            except AttributeError:
                if index == len(self.parsers) - 1:
                    raise UnsupportedMaterialDataJsonFormatException(self.parsers)


register, unregister = bpy.utils.register_classes_factory(GI_OT_GenshinImportMaterialData)
