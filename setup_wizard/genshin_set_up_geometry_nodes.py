# Author: michael-gh1

import bpy
from bpy.types import Operator

from setup_wizard.import_order import NextStepInvoker
from setup_wizard.models import CustomOperatorProperties

# Constants
NAME_OF_GEOMETRY_NODES_MODIFIER = 'GeometryNodes'
NAME_OF_VERTEX_COLORS_INPUT = 'Input_3'
OUTLINE_THICKNESS_INPUT = 'Input_7'
BODY_PART_SUFFIX = ''

NAME_OF_OUTLINE_1_MASK_INPUT = 'Input_10'
NAME_OF_OUTLINE_1_MATERIAL_INPUT = 'Input_5'
NAME_OF_OUTLINE_2_MASK_INPUT = 'Input_11'
NAME_OF_OUTLINE_2_MATERIAL_INPUT = 'Input_9'
NAME_OF_OUTLINE_3_MASK_INPUT = 'Input_14'
NAME_OF_OUTLINE_3_MATERIAL_INPUT = 'Input_15'
NAME_OF_OUTLINE_4_MASK_INPUT = 'Input_18'
NAME_OF_OUTLINE_4_MATERIAL_INPUT = 'Input_19'


outline_mask_to_material_mapping = {
    NAME_OF_OUTLINE_1_MASK_INPUT: NAME_OF_OUTLINE_1_MATERIAL_INPUT,
    NAME_OF_OUTLINE_2_MASK_INPUT: NAME_OF_OUTLINE_2_MATERIAL_INPUT,
    NAME_OF_OUTLINE_3_MASK_INPUT: NAME_OF_OUTLINE_3_MATERIAL_INPUT,
    NAME_OF_OUTLINE_4_MASK_INPUT: NAME_OF_OUTLINE_4_MATERIAL_INPUT
}

meshes_to_create_geometry_nodes_on = [
    'Body',
    'Face',
    'Face_Eye',
]


class GI_OT_SetUpGeometryNodes(Operator, CustomOperatorProperties):
    '''Sets Up Geometry Nodes for Outlines'''
    bl_idname = 'genshin.setup_geometry_nodes'
    bl_label = 'Genshin: Setup Geometry Nodes'

    report_message_level = {'INFO'}
    report_message = []

    def execute(self, context):
        self.setup_geometry_nodes(self.next_step_idx)
        self.report(self.report_message_level, str(self.report_message + ['Successfully set up geometry nodes (for outlines)']))
        return {'FINISHED'}

    def setup_geometry_nodes(self, next_step_idx):
        self.clone_outlines()
        for mesh_name in meshes_to_create_geometry_nodes_on:
            for object_name, object_data in bpy.context.scene.objects.items():
                if object_data.type == 'MESH' and (mesh_name == object_name or f'_{mesh_name}' in object_name):
                    self.create_geometry_nodes_modifier(f'{object_name}{BODY_PART_SUFFIX}')
                    self.fix_meshes_by_setting_genshin_materials(object_name)

        face_meshes = [mesh for mesh_name, mesh in bpy.data.meshes.items() if 'Face' in mesh_name and 'Face_Eye' not in mesh_name]
        self.fix_face_outlines_by_reordering_material_slots(face_meshes)

        if next_step_idx:
            NextStepInvoker().invoke(
                self.next_step_idx, 
                self.invoker_type, 
                high_level_step_name=self.high_level_step_name,
                game_type=self.game_type,
            )


    def create_geometry_nodes_modifier(self, mesh_name):
        mesh = bpy.context.scene.objects[mesh_name]
        outlines_node_group = bpy.data.node_groups.get('miHoYo - Outlines')

        geometry_nodes_modifier = mesh.modifiers.get(f'{NAME_OF_GEOMETRY_NODES_MODIFIER} {mesh_name}')

        if not geometry_nodes_modifier:
            geometry_nodes_modifier = mesh.modifiers.new(f'{NAME_OF_GEOMETRY_NODES_MODIFIER} {mesh_name}', 'NODES')
            geometry_nodes_modifier.node_group = outlines_node_group

        self.set_up_modifier_default_values(geometry_nodes_modifier, mesh)
        return geometry_nodes_modifier


    def clone_outlines(self):
        materials = bpy.data.materials.values()

        for material in materials:
            if 'miHoYo - Genshin' in material.name and material.name != 'miHoYo - Genshin Outlines':
                outline_material = bpy.data.materials.get('miHoYo - Genshin Outlines')
                new_outline_name = f'{material.name} Outlines'

                new_outline_material = outline_material.copy()
                new_outline_material.name = new_outline_name
                new_outline_material.use_fake_user = True


    def set_up_modifier_default_values(self, modifier, mesh):
        if modifier[f'{NAME_OF_VERTEX_COLORS_INPUT}_use_attribute'] == 0:
            # Important! Override object key so we don't use the context (ex. selected object)
            bpy.ops.object.geometry_nodes_input_attribute_toggle(
                {"object": bpy.data.objects[mesh.name]},
                prop_path=f"[\"{NAME_OF_VERTEX_COLORS_INPUT}_use_attribute\"]", 
                modifier_name=modifier.name)

        modifier[f'{NAME_OF_VERTEX_COLORS_INPUT}_attribute_name'] = 'Col'
        modifier[OUTLINE_THICKNESS_INPUT] = 0.25

        for (mask_input, material_input), material in zip(outline_mask_to_material_mapping.items(), mesh.material_slots):
            modifier[mask_input] = bpy.data.materials[material.name]
            modifier[material_input] = bpy.data.materials[f'{material.name} Outlines']


    def disable_face_eye_outlines(self, modifier):
        # Specifically do not try to get modifiers from context because context does not have newly
        # created geometry nodes yet during the setup_wizard!! (or it just doesn't work in general)
        # face_eye_outlines = bpy.context.object.modifiers.get('GeometryNodes Face_Eye')  # Bad!
        modifier[OUTLINE_THICKNESS_INPUT] = 0.0

    '''
        Necessary otherwise meshes/textures on character are visually messed up
        Steps to Reproduce: Run `Basic Setup` (not entire setup) without this function
    '''
    def fix_meshes_by_setting_genshin_materials(self, mesh_name):
        for material_slot_name, material_slot in bpy.context.scene.objects[mesh_name].material_slots.items():
            bpy.context.scene.objects[mesh_name].material_slots.get(material_slot_name).material = material_slot.material

    '''
        A very specific fix for Face outlines not showing up correctly after setup when importing using BetterFBX
    '''
    def fix_face_outlines_by_reordering_material_slots(self, face_meshes):
        for face_mesh in face_meshes:
            face_mesh = bpy.data.meshes.get(face_mesh.name)
            face_mesh_object = bpy.data.objects.get(face_mesh.name)

            if not face_mesh or not face_mesh_object:
                self.report_message_level = {'ERROR'}
                self.report_message.append('Failed to reorder face material slots to fix face outlines. Not a catastrophic error. Continuing.')
                return
            bpy.context.view_layer.objects.active = face_mesh_object  # Select 'Face' mesh before swapping material slots

            face_mesh.materials.append(None)  # Add a "dummy" empty material slot
            bpy.ops.object.material_slot_move(direction='DOWN')  # Move the selected material down
            bpy.ops.object.material_slot_move(direction='UP')  # Return selected material to original position
            face_mesh.materials.pop()  # Remove "dummy" empty material slot


register, unregister = bpy.utils.register_classes_factory(GI_OT_SetUpGeometryNodes)
