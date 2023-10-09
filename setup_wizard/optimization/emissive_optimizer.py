# Author: michael-gh1

import bpy
import os

from bpy.types import Operator

from setup_wizard.domain.shader_material_names import ShaderMaterialNames
from setup_wizard.setup_wizard_operator_base_classes import CustomOperatorProperties

EMISSIVE_MATERIAL_SUFFIX = ' HELPER'


class GI_OT_Emissive_Optimizer(Operator, CustomOperatorProperties):
    """Swaps shader materials with optimized material"""
    bl_idname = "hoyoverse.emissive_optimizer"
    bl_label = "Swaps shader materials with optimized material"

    def execute(self, context):
        selected_objects = bpy.context.selected_objects

        for armature in [obj for obj in selected_objects if obj.type == 'ARMATURE']:
            armature: bpy.types.Object
            armature_meshes = [object for object in armature.children if object.type == 'MESH']
            emissive_template_material_name = ShaderMaterialNames.EMISSIVE_TEMPLATE_MATERIAL_NAME

            for mesh in armature_meshes:
                for material_slot in mesh.material_slots:
                    material = material_slot.material
                    is_original_material = EMISSIVE_MATERIAL_SUFFIX not in material.name

                    if is_original_material and self.__get_original_material(material.name):
                        emissive_material = self.__get_emissive_material(material.name)
                        self.__set_outlines(mesh, False)

                        if emissive_material:
                            material_slot.material = emissive_material
                            continue

                        diffuse_uv0_node = [node for node in material.node_tree.nodes.values() if 'Diffuse_UV0' in node.name or 'Face_Diffuse' in node.name][0]
                        texture_image = diffuse_uv0_node.image
                        template_material = bpy.data.materials.get(emissive_template_material_name)
                        if not template_material:
                            self.__append_optimizer_material()
                            template_material = bpy.data.materials.get(emissive_template_material_name)
                        emissive_material = template_material.copy()
                        emissive_material.name = f'{material.name}{EMISSIVE_MATERIAL_SUFFIX}'
                        emissive_material.node_tree.nodes.get('Image Texture').image = texture_image

                        material_slot.material = emissive_material
                    elif not is_original_material and self.__get_emissive_material(material.name):
                        self.__set_outlines(mesh, True)
                        original_material = self.__get_original_material(material.name)
                        material_slot.material = original_material
        self.__set_selected_objects(selected_objects)
        super().clear_custom_properties()
        return {'FINISHED'}

    def __append_optimizer_material(self):
        OPTIMIZER_BLEND_FILENAME = 'emissive_optimizer_helper_template.blend'
        MATERIAL_PATH_INSIDE_BLEND_FILE = 'Material'
        NAMES_OF_OPTIMIZER_MATERIALS = [
            {'name': ShaderMaterialNames.EMISSIVE_TEMPLATE_MATERIAL_NAME},
        ]
        optimizer_blend_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), OPTIMIZER_BLEND_FILENAME, MATERIAL_PATH_INSIDE_BLEND_FILE)

        bpy.ops.wm.append(
            directory=optimizer_blend_filepath,
            files=NAMES_OF_OPTIMIZER_MATERIALS,
            set_fake=True
        )

    def __get_original_material(self, material_name):
        return bpy.data.materials.get(f"{material_name.replace(EMISSIVE_MATERIAL_SUFFIX, '')}") if EMISSIVE_MATERIAL_SUFFIX in material_name else bpy.data.materials.get(material_name)

    def __get_emissive_material(self, material_name):
        return bpy.data.materials.get(f"{material_name}{EMISSIVE_MATERIAL_SUFFIX}") if EMISSIVE_MATERIAL_SUFFIX not in material_name else bpy.data.materials.get(material_name)

    def __set_outlines(self, mesh, enabled):
        OUTLINES_KEYWORD_IDENTIFIER = 'GeometryNodes'  # TODO: May need to consider handling multiple identifiers

        print(f'{mesh}: {enabled}')

        outlines_modifiers = \
            [modifier for modifier in mesh.modifiers.values() if OUTLINES_KEYWORD_IDENTIFIER in modifier.name]
        if outlines_modifiers:
            outlines_modifiers[0].show_viewport = enabled

    def __set_selected_objects(self, selected_objects):
        bpy.ops.object.select_all(action='DESELECT')
        for selected_object in selected_objects:
            selected_object.select_set(True)
