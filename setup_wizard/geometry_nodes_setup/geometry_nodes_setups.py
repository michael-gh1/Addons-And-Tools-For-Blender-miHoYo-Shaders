# Author: michael-gh1

import bpy

from abc import ABC, abstractmethod
from bpy.types import Operator, Context

from setup_wizard.domain.shader_identifier_service import GenshinImpactShaders, ShaderIdentifierService, ShaderIdentifierServiceFactory
from setup_wizard.domain.shader_materials import V3_BonnyFestivityGenshinImpactMaterialNames, FestivityGenshinImpactMaterialNames, GameMaterialNames, Nya222HonkaiStarRailShaderMaterialNames

from setup_wizard.domain.game_types import GameType
from setup_wizard.outline_import_setup.outline_node_groups import OutlineNodeGroupNames


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
NAME_OF_OUTLINE_5_MASK_INPUT = 'Input_24'
NAME_OF_OUTLINE_5_MATERIAL_INPUT = 'Input_25'



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
    'Hair',  # HSR Support
    'Weapon',  # HSR Support
    'Weapon01',  # HSR Support
    'Weapon02',  # HSR Support
]


class GameGeometryNodesSetupFactory:
    def create(game_type: GameType, blender_operator: Operator, context: Context):
        shader_identifier_service: ShaderIdentifierService = ShaderIdentifierServiceFactory.create(game_type)

        if game_type == GameType.GENSHIN_IMPACT.name:
            if shader_identifier_service.identify_shader(bpy.data.materials) is GenshinImpactShaders.V3_GENSHIN_IMPACT_SHADER:
                return V3_GenshinImpactGeometryNodesSetup(blender_operator, context)
            else:
                return GenshinImpactGeometryNodesSetup(blender_operator, context)
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            return HonkaiStarRailGeometryNodesSetup(blender_operator, context)
        else:
            raise Exception(f'Unknown {GameType}: {game_type}')

class GameGeometryNodesSetup(ABC):
    GEOMETRY_NODES_MATERIAL_IGNORE_LIST = []

    @abstractmethod
    def setup_geometry_nodes(self):
        raise NotImplementedError

    def clone_outlines(self, game_material_names: GameMaterialNames):
        materials = [material for material in bpy.data.materials.values() if material.name not in self.GEOMETRY_NODES_MATERIAL_IGNORE_LIST]

        for material in materials:
            if game_material_names.MATERIAL_PREFIX in material.name and material.name != game_material_names.OUTLINES and \
                not material.name.endswith('Outlines'):
                outline_material = bpy.data.materials.get(game_material_names.OUTLINES)
                new_outline_name = f'{material.name} Outlines'

                if not bpy.data.materials.get(new_outline_name):
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
            if bpy.data.materials.get(material.name) and bpy.data.materials.get(f'{material.name} Outlines'):
                if material.name not in self.GEOMETRY_NODES_MATERIAL_IGNORE_LIST:
                    modifier[mask_input] = bpy.data.materials.get(material.name)
                    modifier[material_input] = bpy.data.materials.get(f'{material.name} Outlines')

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


class GenshinImpactGeometryNodesSetup(GameGeometryNodesSetup):
    GEOMETRY_NODES_MATERIAL_IGNORE_LIST = []

    def __init__(self, blender_operator, context):
        self.blender_operator = blender_operator
        self.context = context

    def setup_geometry_nodes(self):
        self.clone_outlines(FestivityGenshinImpactMaterialNames)
        for mesh_name in meshes_to_create_geometry_nodes_on:
            for object_name, object_data in bpy.context.scene.objects.items():
                if object_data.type == 'MESH' and (mesh_name == object_name or f'_{mesh_name}' in object_name):
                    self.create_geometry_nodes_modifier(f'{object_name}{BODY_PART_SUFFIX}')
                    self.fix_meshes_by_setting_genshin_materials(object_name)

        face_meshes = [mesh for mesh_name, mesh in bpy.data.meshes.items() if 'Face' in mesh_name and 'Face_Eye' not in mesh_name]
        self.fix_face_outlines_by_reordering_material_slots(face_meshes)

    def create_geometry_nodes_modifier(self, mesh_name):
        mesh = bpy.context.scene.objects[mesh_name]
        outlines_node_group = \
            bpy.data.node_groups.get(OutlineNodeGroupNames.FESTIVITY_GENSHIN_OUTLINES)

        geometry_nodes_modifier = mesh.modifiers.get(f'{NAME_OF_GEOMETRY_NODES_MODIFIER} {mesh_name}')

        if not geometry_nodes_modifier:
            geometry_nodes_modifier = mesh.modifiers.new(f'{NAME_OF_GEOMETRY_NODES_MODIFIER} {mesh_name}', 'NODES')
            geometry_nodes_modifier.node_group = outlines_node_group

        self.set_up_modifier_default_values(geometry_nodes_modifier, mesh)
        return geometry_nodes_modifier


class V3_GenshinImpactGeometryNodesSetup(GameGeometryNodesSetup):
    GEOMETRY_NODES_MATERIAL_IGNORE_LIST = []
    BASE_GEOMETRY_INPUT = 'Input_12'
    USE_VERTEX_COLORS_INPUT = 'Input_13'


    def __init__(self, blender_operator, context):
        self.blender_operator = blender_operator
        self.context = context
        self.material_names = V3_BonnyFestivityGenshinImpactMaterialNames
        self.outline_node_group_name = OutlineNodeGroupNames.V3_BONNY_FESTIVITY_GENSHIN_OUTLINES

    def setup_geometry_nodes(self):
        self.clone_outlines(self.material_names)
        for mesh_name in meshes_to_create_geometry_nodes_on:
            for object_name, object_data in bpy.context.scene.objects.items():
                if object_data.type == 'MESH' and (mesh_name == object_name or f'_{mesh_name}' in object_name):
                    self.create_geometry_nodes_modifier(f'{object_name}{BODY_PART_SUFFIX}')
                    self.fix_meshes_by_setting_genshin_materials(object_name)

        face_meshes = [mesh for mesh_name, mesh in bpy.data.meshes.items() if 'Face' in mesh_name and 'Face_Eye' not in mesh_name]
        self.fix_face_outlines_by_reordering_material_slots(face_meshes)

    def create_geometry_nodes_modifier(self, mesh_name):
        mesh = bpy.context.scene.objects[mesh_name]
        outlines_node_group = \
            bpy.data.node_groups.get(self.outline_node_group_name)

        geometry_nodes_modifier = mesh.modifiers.get(f'{NAME_OF_GEOMETRY_NODES_MODIFIER} {mesh_name}')

        if not geometry_nodes_modifier:
            geometry_nodes_modifier = mesh.modifiers.new(f'{NAME_OF_GEOMETRY_NODES_MODIFIER} {mesh_name}', 'NODES')
            geometry_nodes_modifier.node_group = outlines_node_group

        self.set_up_modifier_default_values(geometry_nodes_modifier, mesh)
        return geometry_nodes_modifier 

    def set_up_modifier_default_values(self, modifier, mesh):
        modifier[self.BASE_GEOMETRY_INPUT] = True
        modifier[self.USE_VERTEX_COLORS_INPUT] = True

        outline_to_material_mapping = {
            'Hair': (NAME_OF_OUTLINE_1_MASK_INPUT, NAME_OF_OUTLINE_1_MATERIAL_INPUT),
            'Body': (NAME_OF_OUTLINE_2_MASK_INPUT, NAME_OF_OUTLINE_2_MATERIAL_INPUT),
            'Face': (NAME_OF_OUTLINE_3_MASK_INPUT, NAME_OF_OUTLINE_3_MATERIAL_INPUT),
            'Dress': (NAME_OF_OUTLINE_4_MASK_INPUT, NAME_OF_OUTLINE_4_MATERIAL_INPUT),
            'Dress1': (NAME_OF_OUTLINE_4_MASK_INPUT, NAME_OF_OUTLINE_4_MATERIAL_INPUT),
            'Dress2': (NAME_OF_OUTLINE_5_MASK_INPUT, NAME_OF_OUTLINE_5_MATERIAL_INPUT),
        }

        for input_name, (material_input_accessor, outline_material_input_accessor) in outline_to_material_mapping.items():
            material_name = f'{self.material_names.MATERIAL_PREFIX}{input_name}'
            outline_material_name = f'{self.material_names.MATERIAL_PREFIX}{input_name} Outlines'

            if bpy.data.materials.get(material_name) and bpy.data.materials.get(outline_material_name):
                modifier[material_input_accessor] = bpy.data.materials.get(material_name)
                modifier[outline_material_input_accessor] = bpy.data.materials.get(outline_material_name)


class HonkaiStarRailGeometryNodesSetup(GameGeometryNodesSetup):
    GEOMETRY_NODES_MATERIAL_IGNORE_LIST = []

    def __init__(self, blender_operator, context):
        self.blender_operator = blender_operator
        self.context = context

    def setup_geometry_nodes(self):
        self.clone_outlines(Nya222HonkaiStarRailShaderMaterialNames)
        for mesh_name in meshes_to_create_geometry_nodes_on:
            for object_name, object_data in bpy.context.scene.objects.items():
                if object_data.type == 'MESH' and (mesh_name == object_name or f'_{mesh_name}' in object_name):
                    self.create_geometry_nodes_modifier(f'{object_name}{BODY_PART_SUFFIX}')
                    self.fix_meshes_by_setting_genshin_materials(object_name)

        face_meshes = [mesh for mesh_name, mesh in bpy.data.meshes.items() if 'Face' in mesh_name and 'Face_Mask' not in mesh_name]
        self.fix_face_outlines_by_reordering_material_slots(face_meshes)

    def create_geometry_nodes_modifier(self, mesh_name):
        mesh = bpy.context.scene.objects[mesh_name]
        outlines_node_group = \
            bpy.data.node_groups.get(OutlineNodeGroupNames.NYA222_HSR_OUTLINES)

        geometry_nodes_modifier = mesh.modifiers.get(f'{NAME_OF_GEOMETRY_NODES_MODIFIER} {mesh_name}')

        if not geometry_nodes_modifier:
            geometry_nodes_modifier = mesh.modifiers.new(f'{NAME_OF_GEOMETRY_NODES_MODIFIER} {mesh_name}', 'NODES')
            geometry_nodes_modifier.node_group = outlines_node_group

        self.set_up_modifier_default_values(geometry_nodes_modifier, mesh)
        return geometry_nodes_modifier
