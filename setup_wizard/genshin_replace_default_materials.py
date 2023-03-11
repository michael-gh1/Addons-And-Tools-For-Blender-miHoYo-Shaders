# Author: michael-gh1

import bpy

from bpy.props import StringProperty
from bpy.types import Operator

from setup_wizard.import_order import NextStepInvoker
from setup_wizard.import_order import get_actual_material_name_for_dress
from setup_wizard.models import CustomOperatorProperties


class GI_OT_GenshinReplaceDefaultMaterials(Operator, CustomOperatorProperties):
    """Swaps out the default character materials with Festivity's Shaders materials"""
    bl_idname = "genshin.replace_default_materials"  # important since its how we chain file dialogs
    bl_label = "Genshin: Replace Default Materials - Select Character Model Folder"

    # ImportHelper mixin class uses this
    filename_ext = "*.*"

    import_path: StringProperty(
        name="Path",
        description="Path to the folder of the Model",
        default="",
        subtype='DIR_PATH'
    )

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        self.replace_default_materials_with_genshin_materials()

        NextStepInvoker().invoke(
            self.next_step_idx, 
            self.invoker_type, 
            high_level_step_name=self.high_level_step_name
        )
        return {'FINISHED'}
    
    def replace_default_materials_with_genshin_materials(self):
        meshes = [mesh for mesh in bpy.context.scene.objects if mesh.type == 'MESH']

        for mesh in meshes:
            for material_slot in mesh.material_slots:
                material_name = material_slot.name
                mesh_body_part_name = self.__get_npc_mesh_body_part_name(material_name) if \
                    material_name.startswith('NPC') else material_name.split('_')[-1]
                genshin_material = bpy.data.materials.get(f'miHoYo - Genshin {mesh_body_part_name}')

                if genshin_material:
                    material_slot.material = genshin_material
                elif mesh_body_part_name and ('Dress' in mesh_body_part_name or 'Arm' in mesh_body_part_name or 'Cloak' in mesh_body_part_name):
                    # Xiao is the only character with an Arm material
                    # Dainsleif and Paimon are the only characters with Cloak materials
                    self.report({'INFO'}, 'Dress detected on character model!')

                    actual_material_for_dress = get_actual_material_name_for_dress(material_name)
                    if actual_material_for_dress == 'Cloak':
                        # short-circuit, no shader available for 'Cloak' so do nothing (Paimon)
                        continue

                    genshin_material = self.__clone_material_and_rename(
                        material_slot, 
                        f'miHoYo - Genshin {actual_material_for_dress}', 
                        mesh_body_part_name
                    )
                    self.report({'INFO'}, f'Replaced material: "{material_name}" with "{actual_material_for_dress}"')
                elif material_name == 'miHoYoDiffuse':
                    material_slot.material = bpy.data.materials.get(f'miHoYo - Genshin Body')
                    continue
                else:
                    self.report({'WARNING'}, f'Ignoring unknown mesh body part in character model: {mesh_body_part_name} / Material: {material_name}')
                    continue

                # Don't need to duplicate multiple Face shader nodes
                if genshin_material.name != f'miHoYo - Genshin Face':
                    genshin_main_shader_node = genshin_material.node_tree.nodes.get('Group.001')
                    genshin_main_shader_node.node_tree = self.__clone_shader_node_and_rename(genshin_material, mesh_body_part_name)
        self.report({'INFO'}, 'Replaced default materials with Genshin shader materials...')

    def __get_npc_mesh_body_part_name(self, material_name):
        if 'Hair' in material_name:
            return 'Hair'
        elif 'Face' in material_name:
            return 'Face'
        elif 'Body' in material_name:
            return 'Body'
        elif 'Dress' in material_name:
            return 'Dress'
        else:
            return None

    def __clone_material_and_rename(self, material_slot, mesh_body_part_name_template, mesh_body_part_name):
        new_material = bpy.data.materials.get(mesh_body_part_name_template).copy()
        new_material.name = f'miHoYo - Genshin {mesh_body_part_name}'
        new_material.use_fake_user = True

        material_slot.material = new_material
        return new_material

    def __clone_shader_node_and_rename(self, material, mesh_body_part_name):
        new_shader_node_tree = material.node_tree.nodes.get('Group.001').node_tree.copy()
        new_shader_node_tree.name = f'miHoYo - Genshin {mesh_body_part_name}'
        return new_shader_node_tree


register, unregister = bpy.utils.register_classes_factory(GI_OT_GenshinReplaceDefaultMaterials)
