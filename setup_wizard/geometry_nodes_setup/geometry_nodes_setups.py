# Author: michael-gh1

from typing import List
import bpy

from abc import ABC, abstractmethod
from bpy.types import Operator, Context

from setup_wizard.domain.node_group_names import ShaderNodeGroupNames
from setup_wizard.domain.star_cloak_types import StarCloakTypes
from setup_wizard.domain.mesh_names import MeshNames
from setup_wizard.domain.shader_material_name_keywords import ShaderMaterialNameKeywords
from setup_wizard.domain.shader_material import ShaderMaterial
from setup_wizard.domain.shader_node_names import ShaderNodeNames, StellarToonShaderNodeNames, V3_GenshinShaderNodeNames, V1_HoYoToonShaderNodeNames
from setup_wizard.domain.shader_identifier_service import GenshinImpactShaders, HonkaiStarRailShaders, ShaderIdentifierService, ShaderIdentifierServiceFactory
from setup_wizard.domain.shader_material_names import JaredNytsPunishingGrayRavenShaderMaterialNames, StellarToonShaderMaterialNames, V3_BonnyFestivityGenshinImpactMaterialNames, V2_FestivityGenshinImpactMaterialNames, ShaderMaterialNames, Nya222HonkaiStarRailShaderMaterialNames, V1_HoYoToonGenshinImpactMaterialNames

from setup_wizard.domain.game_types import GameType
from setup_wizard.material_import_setup.empty_names import LightDirectionEmptyNames
from setup_wizard.outline_import_setup.outline_node_groups import OutlineNodeGroupNames
from setup_wizard.texture_import_setup.texture_node_names import V1_HoYoToonGenshinImpactTextureNodeNames


# Constants
NAME_OF_GEOMETRY_NODES_MODIFIER = 'Outlines'
NAME_OF_VERTEX_COLORS_INPUT = 'Input_3'
OUTLINE_THICKNESS_INPUT = 'Input_7'
BODY_PART_SUFFIX = ''

# These are actually the Materials
NAME_OF_OUTLINE_1_MASK_INPUT = 'Input_10'  # Hair
NAME_OF_OUTLINE_2_MASK_INPUT = 'Input_11'  # Body
NAME_OF_OUTLINE_3_MASK_INPUT = 'Input_14'  # Face
NAME_OF_OUTLINE_4_MASK_INPUT = 'Input_18'  # Dress
NAME_OF_DRESS2_MASK_INPUT = 'Input_24'  # Dress 2
NAME_OF_LEATHER_MASK_INPUT = 'Socket_0'
NAME_OF_OUTLINE_OTHER_MASK_INPUT = 'Input_26'
NAME_OF_PUPIL_MASK_INPUT = 'Socket_32'  # Pupil
NAME_OF_VFX_MASK_INPUT = 'Socket_1'

# These are actually the Outlines
NAME_OF_OUTLINE_1_MATERIAL_INPUT = 'Input_5'  # Hair
NAME_OF_OUTLINE_2_MATERIAL_INPUT = 'Input_9'  # Body
NAME_OF_OUTLINE_3_MATERIAL_INPUT = 'Input_15'  # Face
NAME_OF_OUTLINE_4_MATERIAL_INPUT = 'Input_19'  # Dress
NAME_OF_DRESS2_MATERIAL_INPUT = 'Input_25'  # Dress 2
NAME_OF_LEATHER_MATERIAL_INPUT = 'Socket_2'
NAME_OF_OUTLINE_OTHER_MATERIAL_INPUT = 'Input_27'
NAME_OF_PUPIL_MATERIAL_INPUT = 'Socket_33'  # Pupil
NAME_OF_VFX_MATERIAL_INPUT = 'Socket_3'

LIGHT_VECTORS_LIGHT_DIRECTION = 'Input_3'
LIGHT_VECTORS_HEAD_ORIGIN = 'Input_4'
LIGHT_VECTORS_HEAD_FORWARD = 'Input_5'
LIGHT_VECTORS_HEAD_UP = 'Input_6'


outline_mask_to_material_mapping = {
    NAME_OF_OUTLINE_1_MASK_INPUT: NAME_OF_OUTLINE_1_MATERIAL_INPUT,
    NAME_OF_OUTLINE_2_MASK_INPUT: NAME_OF_OUTLINE_2_MATERIAL_INPUT,
    NAME_OF_OUTLINE_3_MASK_INPUT: NAME_OF_OUTLINE_3_MATERIAL_INPUT,
    NAME_OF_OUTLINE_4_MASK_INPUT: NAME_OF_OUTLINE_4_MATERIAL_INPUT
}

available_outline_mask_to_material_mapping = {
    NAME_OF_OUTLINE_1_MASK_INPUT: NAME_OF_OUTLINE_1_MATERIAL_INPUT,
    NAME_OF_OUTLINE_2_MASK_INPUT: NAME_OF_OUTLINE_2_MATERIAL_INPUT,
    NAME_OF_OUTLINE_3_MASK_INPUT: NAME_OF_OUTLINE_3_MATERIAL_INPUT,
    NAME_OF_OUTLINE_4_MASK_INPUT: NAME_OF_OUTLINE_4_MATERIAL_INPUT,
    NAME_OF_DRESS2_MASK_INPUT: NAME_OF_DRESS2_MATERIAL_INPUT,
    NAME_OF_LEATHER_MASK_INPUT: NAME_OF_LEATHER_MATERIAL_INPUT,
    NAME_OF_OUTLINE_OTHER_MASK_INPUT: NAME_OF_OUTLINE_OTHER_MATERIAL_INPUT,
    NAME_OF_VFX_MASK_INPUT: NAME_OF_VFX_MATERIAL_INPUT
}  # For smart assignment

gi_meshes_to_create_outlines_on = [
    'Bang',
    'Body',
    'Body1',
    'Body2',
    'Dress',
    'Dress1',
    'Dress2',
    'Face',
    'Face_Eye',
    'EffectHair',
    'Mask',
    'Cap',
    'Clothes',
    'Hair',
    'Handcuffs',
    'Hat',
    'Helmet',
    'SkillObj_Mavuika_Glass_Model',
    'Skirt',
    'Wriothesley_Gauntlet_L_Model',
    'Wriothesley_Gauntlet_R_Model',
    'Screw',  # Aranara
    'Hat',  # Aranara
    'Ribbon',
    'StarCloak',
    'Stockings',
    'Tail',
    'Veil',
]

hsr_meshes_to_create_outlines_on = [
    'Hair',
    'Weapon',
    'Weapon01',
    'Weapon02',
]

pgr_meshes_to_create_outlines_on = [
    'Down',
    'Upper',
    'Cloth',
    'Clothes',
]

mesh_keywords_to_create_geometry_nodes_on = [
    ShaderMaterialNameKeywords.SKILLOBJ,
]

meshes_to_create_outlines_on = \
    gi_meshes_to_create_outlines_on + \
    hsr_meshes_to_create_outlines_on + \
    pgr_meshes_to_create_outlines_on

meshes_to_create_light_vectors_on = meshes_to_create_outlines_on + [
    'Brow',
    'EyeStar',
]

material_keywords_to_not_create_outlines_on = [
    'Eff',
    'Pupil',
]


class GameGeometryNodesSetupFactory:
    def create(game_type: GameType, blender_operator: Operator, context: Context):
        shader_identifier_service: ShaderIdentifierService = ShaderIdentifierServiceFactory.create(game_type)
        shader = shader_identifier_service.identify_shader(bpy.data.materials, bpy.data.node_groups)

        if game_type == GameType.GENSHIN_IMPACT.name:
            if shader is GenshinImpactShaders.V1_GENSHIN_IMPACT_SHADER or shader is GenshinImpactShaders.V2_GENSHIN_IMPACT_SHADER:
                return GenshinImpactGeometryNodesSetup(blender_operator, context)
            elif shader is GenshinImpactShaders.V3_GENSHIN_IMPACT_SHADER:
                return V3_GenshinImpactGeometryNodesSetup(blender_operator, context)
            else:
                return V1_HoYoToonGenshinImpactGeometryNodesSetup(blender_operator, context)
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            if shader is HonkaiStarRailShaders.NYA222_HONKAI_STAR_RAIL_SHADER:
                return HonkaiStarRailGeometryNodesSetup(
                    blender_operator, 
                    context, 
                    Nya222HonkaiStarRailShaderMaterialNames, 
                    OutlineNodeGroupNames.NYA222_HSR_OUTLINES
                )
            else:  # is HonkaiStarRailShaders.STELLARTOON_HONKAI_STAR_RAIL_SHADER
                return StellarToonGeometryNodesSetup(
                    blender_operator, 
                    context, 
                    StellarToonShaderMaterialNames, 
                    OutlineNodeGroupNames.STELLARTOON_HSR_OUTLINES,
                    OutlineNodeGroupNames.STELLARTOON_LIGHT_VECTORS_GEOMETRY_NODES
                )
        elif game_type == GameType.PUNISHING_GRAY_RAVEN.name:
            for outline_node_group_name in OutlineNodeGroupNames.V2_JAREDNYTS_PGR_OUTLINES:
                if bpy.data.node_groups.get(outline_node_group_name):
                    return V2_PunishingGrayRavenGeometryNodesSetup(blender_operator, context)
            return PunishingGrayRavenGeometryNodesSetup(blender_operator, context)
        else:
            raise Exception(f'Unknown {GameType}: {game_type}')

class GameGeometryNodesSetup(ABC):
    GEOMETRY_NODES_MATERIAL_IGNORE_LIST = []
    DEFAULT_OUTLINE_THICKNESS = 0.25
    ENABLE_TRANSPARENCY = 'Enable Transparency'

    def __init__(self, blender_operator, context):
        self.blender_operator = blender_operator
        self.context = context
        self.light_vectors_node_group_names = []
        self.shader_node_names = ShaderNodeNames

    @abstractmethod
    def setup_geometry_nodes(self):
        raise NotImplementedError

    def clone_outlines(self, game_material_names: ShaderMaterialNames):
        materials = [material for material in bpy.data.materials.values() if material.name not in self.GEOMETRY_NODES_MATERIAL_IGNORE_LIST]

        for material in materials:
            if game_material_names.MATERIAL_PREFIX in material.name and material.name != game_material_names.OUTLINES and \
                not material.name.endswith('Outlines'):
                outline_material = bpy.data.materials.get(game_material_names.OUTLINES)
                new_outline_name = f'{material.name} Outlines'

                if not bpy.data.materials.get(new_outline_name) and not ShaderMaterial(material, self.shader_node_names).get_outlines_material():
                    new_outline_material = outline_material.copy()
                    new_outline_material.name = new_outline_name
                    new_outline_material.use_fake_user = True
                if '_Trans' in new_outline_name and type(self) is StellarToonGeometryNodesSetup:
                    new_outline_material = bpy.data.materials.get(new_outline_name)
                    new_outline_material.node_tree.nodes.get(StellarToonShaderNodeNames.OUTLINES_SHADER).inputs.get(self.ENABLE_TRANSPARENCY).default_value = 1.0

    def set_face_outlines_material_default_values(self, game_material_names: ShaderMaterialNames, outlines_shader_node_name: str):
        face_outlines_material = bpy.data.materials.get(f'{game_material_names.FACE} Outlines')
        if face_outlines_material:
            input_names = [
                'Use Face Shader',
                'Use Face Outlines'  # >= v4.0 Genshin Shader
            ]
            for input_name in input_names:
                face_outlines_node_input = face_outlines_material.node_tree.nodes.get(outlines_shader_node_name).inputs.get(input_name)
                if  face_outlines_node_input:
                    face_outlines_node_input.default_value = 1.0

    def set_up_modifier_default_values(self, modifier, mesh):
        if modifier[f'{NAME_OF_VERTEX_COLORS_INPUT}_use_attribute'] == 0:
            with bpy.context.temp_override(active_object=bpy.data.objects[mesh.name]):
                bpy.context.view_layer.objects.active = bpy.context.active_object

                if bpy.app.version >= (4,0,0):
                    bpy.ops.object.geometry_nodes_input_attribute_toggle(
                        input_name=NAME_OF_VERTEX_COLORS_INPUT, 
                        modifier_name=modifier.name
                    )
                else:
                    bpy.ops.object.geometry_nodes_input_attribute_toggle(
                        prop_path=f"[\"{NAME_OF_VERTEX_COLORS_INPUT}_use_attribute\"]", 
                        modifier_name=modifier.name
                    )

        modifier[f'{NAME_OF_VERTEX_COLORS_INPUT}_attribute_name'] = 'Col'
        modifier[OUTLINE_THICKNESS_INPUT] = self.DEFAULT_OUTLINE_THICKNESS

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
                self.blender_operator.report_message_level = {'ERROR'}
                self.blender_operator.report_message.append('Failed to reorder face material slots to fix face outlines. Not a catastrophic error. Continuing.')
                return
            bpy.context.view_layer.objects.active = face_mesh_object  # Select 'Face' mesh before swapping material slots

            face_mesh.materials.append(None)  # Add a "dummy" empty material slot
            bpy.ops.object.material_slot_move(direction='DOWN')  # Move the selected material down
            bpy.ops.object.material_slot_move(direction='UP')  # Return selected material to original position
            face_mesh.materials.pop()  # Remove "dummy" empty material slot

    def create_light_vectors_modifier(self, mesh_name):
        mesh = bpy.context.scene.objects[mesh_name]

        for light_vectors_node_group_name in self.light_vectors_node_group_names:
            light_vectors_node_group = bpy.data.node_groups.get(light_vectors_node_group_name)
            light_vectors_modifier = mesh.modifiers.get(f'{light_vectors_node_group_name} {mesh_name}')

            if not light_vectors_node_group:
                continue

            if not light_vectors_modifier:
                light_vectors_modifier = mesh.modifiers.new(f'{light_vectors_node_group_name} {mesh_name}', 'NODES')
                light_vectors_modifier.node_group = light_vectors_node_group
                self.set_up_light_vectors_modifier(light_vectors_modifier)
        print(f'Light Vector Setup Completed for {mesh_name}')
        return light_vectors_modifier

    '''
    Use existing object if it exists, otherwise attempt to set it with known object names for GI or HSR shaders
    '''
    def set_up_light_vectors_modifier(self, light_vectors_modifier):
        light_vectors_modifier[LIGHT_VECTORS_LIGHT_DIRECTION] = \
            light_vectors_modifier[LIGHT_VECTORS_LIGHT_DIRECTION] or \
            bpy.data.objects.get(LightDirectionEmptyNames.LIGHT_DIRECTION) or \
            bpy.data.objects.get(LightDirectionEmptyNames.MAIN_LIGHT_DIRECTION)
        light_vectors_modifier[LIGHT_VECTORS_HEAD_ORIGIN] = light_vectors_modifier[LIGHT_VECTORS_HEAD_ORIGIN] or bpy.data.objects.get(LightDirectionEmptyNames.HEAD_ORIGIN)
        light_vectors_modifier[LIGHT_VECTORS_HEAD_FORWARD] = light_vectors_modifier[LIGHT_VECTORS_HEAD_FORWARD] or bpy.data.objects.get(LightDirectionEmptyNames.HEAD_FORWARD)
        light_vectors_modifier[LIGHT_VECTORS_HEAD_UP] = light_vectors_modifier[LIGHT_VECTORS_HEAD_UP] or bpy.data.objects.get(LightDirectionEmptyNames.HEAD_UP) 


class GenshinImpactGeometryNodesSetup(GameGeometryNodesSetup):
    GEOMETRY_NODES_MATERIAL_IGNORE_LIST = []

    def __init__(self, blender_operator, context):
        super().__init__(blender_operator, context)
        self.material_names = V2_FestivityGenshinImpactMaterialNames
        self.outlines_node_group_names = OutlineNodeGroupNames.FESTIVITY_GENSHIN_OUTLINES

    def setup_geometry_nodes(self):
        self.clone_outlines(self.material_names)
        for mesh_name in meshes_to_create_outlines_on:
            for object_name, object_data in bpy.context.scene.objects.items():
                if object_data.type == 'MESH' and (mesh_name == object_name or f'_{mesh_name}' in object_name):
                    self.create_geometry_nodes_modifier(f'{object_name}{BODY_PART_SUFFIX}')
                    self.fix_meshes_by_setting_genshin_materials(object_name)

        face_meshes = [mesh for mesh_name, mesh in bpy.data.meshes.items() if 'Face' in mesh_name and 'Face_Eye' not in mesh_name]
        self.fix_face_outlines_by_reordering_material_slots(face_meshes)

    def create_geometry_nodes_modifier(self, mesh_name):
        mesh = bpy.context.scene.objects[mesh_name]

        for outlines_node_group_name in self.outlines_node_group_names:
            outlines_node_group = bpy.data.node_groups.get(outlines_node_group_name)
            geometry_nodes_modifier = mesh.modifiers.get(f'{NAME_OF_GEOMETRY_NODES_MODIFIER} {mesh_name}')

            if not outlines_node_group:
                continue
                
            if not geometry_nodes_modifier:
                geometry_nodes_modifier = mesh.modifiers.new(f'{NAME_OF_GEOMETRY_NODES_MODIFIER} {mesh_name}', 'NODES')
                geometry_nodes_modifier.node_group = outlines_node_group
            self.set_up_modifier_default_values(geometry_nodes_modifier, mesh)
        return geometry_nodes_modifier


class V3_GenshinImpactGeometryNodesSetup(GameGeometryNodesSetup):
    GEOMETRY_NODES_MATERIAL_IGNORE_LIST = []
    BASE_GEOMETRY_INPUT = 'Input_12'
    USE_VERTEX_COLORS_INPUT = 'Input_13'
    OUTLINE_THICKNESS_INPUT = 'Input_7'

    outline_to_material_mapping = {
        'Hair': (NAME_OF_OUTLINE_1_MASK_INPUT, NAME_OF_OUTLINE_1_MATERIAL_INPUT),
        'Body': (NAME_OF_OUTLINE_2_MASK_INPUT, NAME_OF_OUTLINE_2_MATERIAL_INPUT),
        'Face': (NAME_OF_OUTLINE_3_MASK_INPUT, NAME_OF_OUTLINE_3_MATERIAL_INPUT),
        'Dress': (NAME_OF_OUTLINE_4_MASK_INPUT, NAME_OF_OUTLINE_4_MATERIAL_INPUT),
        'Dress1': (NAME_OF_OUTLINE_4_MASK_INPUT, NAME_OF_OUTLINE_4_MATERIAL_INPUT),
        'Helmet': (NAME_OF_OUTLINE_4_MASK_INPUT, NAME_OF_OUTLINE_4_MATERIAL_INPUT),
        'Dress2': (NAME_OF_DRESS2_MASK_INPUT, NAME_OF_DRESS2_MATERIAL_INPUT),
        'Arm': (NAME_OF_OUTLINE_OTHER_MASK_INPUT, NAME_OF_OUTLINE_OTHER_MATERIAL_INPUT),
        'Effect': (NAME_OF_OUTLINE_OTHER_MASK_INPUT, NAME_OF_OUTLINE_OTHER_MATERIAL_INPUT),
        'EffectHair': (NAME_OF_OUTLINE_OTHER_MASK_INPUT, NAME_OF_OUTLINE_OTHER_MATERIAL_INPUT),
        'Gauntlet': (NAME_OF_OUTLINE_OTHER_MASK_INPUT, NAME_OF_OUTLINE_OTHER_MATERIAL_INPUT),
        'HelmetEmo': (NAME_OF_OUTLINE_OTHER_MASK_INPUT, NAME_OF_OUTLINE_OTHER_MATERIAL_INPUT),
    }

    npc_outline_to_material_mapping = {
        'Item_01': (NAME_OF_OUTLINE_4_MASK_INPUT, NAME_OF_OUTLINE_4_MATERIAL_INPUT),
        'Hat': (NAME_OF_DRESS2_MASK_INPUT, NAME_OF_DRESS2_MATERIAL_INPUT),
        'Item_02': (NAME_OF_DRESS2_MASK_INPUT, NAME_OF_DRESS2_MATERIAL_INPUT),
        'Crown': (NAME_OF_DRESS2_MASK_INPUT, NAME_OF_DRESS2_MATERIAL_INPUT),
        'Screw': (NAME_OF_OUTLINE_OTHER_MASK_INPUT, NAME_OF_OUTLINE_OTHER_MATERIAL_INPUT),
        'Item_03': (NAME_OF_OUTLINE_OTHER_MASK_INPUT, NAME_OF_OUTLINE_OTHER_MATERIAL_INPUT),
        'Others': (NAME_OF_OUTLINE_OTHER_MASK_INPUT, NAME_OF_OUTLINE_OTHER_MATERIAL_INPUT),
    }

    def __init__(self, blender_operator, context):
        super().__init__(blender_operator, context)
        self.material_names = V3_BonnyFestivityGenshinImpactMaterialNames
        self.outlines_node_group_names = OutlineNodeGroupNames.V3_BONNY_FESTIVITY_GENSHIN_OUTLINES
        self.light_vectors_node_group_names = OutlineNodeGroupNames.V3_LIGHT_VECTORS_GEOMETRY_NODES
        self.outlines_shader_node_name = V3_GenshinShaderNodeNames.OUTLINES_SHADER
        self.shader_node_names = V3_GenshinShaderNodeNames

    def setup_geometry_nodes(self):
        self.clone_outlines(self.material_names)
        self.set_face_outlines_material_default_values(self.material_names, self.outlines_shader_node_name)
        # Originally was just checked the meshes list, then we checked character meshes, then we went back to the original way
        # Keeping this here in case we run into bugs
        # character_armature = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE'][0]  # Expecting 1 armature in scene
        # character_armature_mesh_names = [obj.name for obj in character_armature.children if obj.type == 'MESH']

        # Set up Light Vectors for meshes that match the expected mesh name list
        for mesh_name in meshes_to_create_light_vectors_on:  # It is important that this is created and placed before Outlines!!
            for object_name, object_data in bpy.context.scene.objects.items():
                object_name_matches = (mesh_name == object_name or f'_{mesh_name}' in object_name)
                if object_data.type == 'MESH' and object_name_matches:
                    self.create_light_vectors_modifier(f'{object_name}{BODY_PART_SUFFIX}')
        # Set up Light Vectors for meshes that have keywords in their names (Ex. SkillObj)
        for object_name, object_data in bpy.context.scene.objects.items():
            object_name_matches = [object_name for mesh_keyword in mesh_keywords_to_create_geometry_nodes_on if mesh_keyword in object_name]
            if object_data.type == 'MESH' and object_name_matches:
                self.create_light_vectors_modifier(f'{object_name}{BODY_PART_SUFFIX}')

        # Set up Outlines for meshes that match the expected mesh name list
        for mesh_name in meshes_to_create_outlines_on:
            for object_name, object_data in bpy.context.scene.objects.items():
                object_name_matches = (mesh_name == object_name or f'_{mesh_name}' in object_name)
                if object_data.type == 'MESH' and object_name_matches:
                    self.create_geometry_nodes_modifier(f'{object_name}{BODY_PART_SUFFIX}')
                    self.fix_meshes_by_setting_genshin_materials(object_name)
        # Set up Outlines for meshes that have keywords in their names (Ex. SkillObj)
        for object_name, object_data in bpy.context.scene.objects.items():
            object_name_matches = [object_name for mesh_keyword in mesh_keywords_to_create_geometry_nodes_on if mesh_keyword in object_name]
            if object_data.type == 'MESH' and object_name_matches:
                    self.create_geometry_nodes_modifier(f'{object_name}{BODY_PART_SUFFIX}')
                    self.fix_meshes_by_setting_genshin_materials(object_name)

        face_meshes = [mesh for mesh_name, mesh in bpy.data.meshes.items() if 'Face' in mesh_name and 'Face_Eye' not in mesh_name]
        self.fix_face_outlines_by_reordering_material_slots(face_meshes)

    def create_geometry_nodes_modifier(self, mesh_name):
        mesh = bpy.context.scene.objects[mesh_name]

        for outlines_node_group_name in self.outlines_node_group_names:
            outlines_node_group = bpy.data.node_groups.get(outlines_node_group_name)
            geometry_nodes_modifier = mesh.modifiers.get(f'{NAME_OF_GEOMETRY_NODES_MODIFIER} {mesh_name}')

            if not outlines_node_group:
                continue

            if not geometry_nodes_modifier:
                geometry_nodes_modifier = mesh.modifiers.new(f'{NAME_OF_GEOMETRY_NODES_MODIFIER} {mesh_name}', 'NODES')
                geometry_nodes_modifier.node_group = outlines_node_group
            self.set_up_modifier_default_values(geometry_nodes_modifier, mesh)
        return geometry_nodes_modifier 

    def set_up_modifier_default_values(self, modifier, mesh):
        modifier[self.BASE_GEOMETRY_INPUT] = True
        modifier[self.USE_VERTEX_COLORS_INPUT] = True
        modifier[self.OUTLINE_THICKNESS_INPUT] = 0.25

        for input_name, (material_input_accessor, outline_material_input_accessor) in self.outline_to_material_mapping.items():
            material_name = f'{self.material_names.MATERIAL_PREFIX}{input_name}'
            outline_material_name = f'{self.material_names.MATERIAL_PREFIX}{input_name} Outlines'

            if bpy.data.materials.get(material_name) and bpy.data.materials.get(outline_material_name):
                modifier[material_input_accessor] = bpy.data.materials.get(material_name)
                modifier[outline_material_input_accessor] = bpy.data.materials.get(outline_material_name)

        is_npc = [material for material in bpy.data.materials if 'NPC' in material.name]
        if is_npc:
            for input_name, (material_input_accessor, outline_material_input_accessor) in self.npc_outline_to_material_mapping.items():
                shader_materials = [
                    material for material_name, material in bpy.data.materials.items() if \
                        input_name in material_name and 
                        self.material_names.MATERIAL_PREFIX in material_name and 
                        not ' Outlines' in material_name
                ]
                outline_materials = [
                    material for material_name, material in bpy.data.materials.items() if \
                        input_name in material_name and 
                        self.material_names.MATERIAL_PREFIX in material_name and 
                        ' Outlines' in material_name
                ]
                # If outlines could not be found, the material name may be too long.
                # Try searching for the outlines material by specific settings in it.
                if not outline_materials:
                    outline_materials = [
                        material for material_name, material in bpy.data.materials.items() if \
                            input_name in material_name and 
                            self.material_names.MATERIAL_PREFIX in material_name and 
                            ShaderMaterial(material, self.shader_node_names).is_outlines_material()
                    ]

                if shader_materials and outline_materials:
                    modifier[material_input_accessor] = shader_materials[0]
                    modifier[outline_material_input_accessor] = outline_materials[0]


class V1_HoYoToonGenshinImpactGeometryNodesSetup(V3_GenshinImpactGeometryNodesSetup):
    GEOMETRY_NODES_MATERIAL_IGNORE_LIST = []
    BASE_GEOMETRY_INPUT = 'Input_12'
    USE_VERTEX_COLORS_INPUT = 'Input_13'
    OUTLINE_THICKNESS_INPUT = 'Input_7'
    NIGHT_SOUL_OUTLINE_SOCKET = 'Socket_10'
    FACE_LIGHTMAP_SOCKET = 'Socket_31'
    TOGGLE_OUTLINES_SOCKET = 'Socket_24'

    outline_to_material_mapping = {
        'Hair': (NAME_OF_OUTLINE_1_MASK_INPUT, NAME_OF_OUTLINE_1_MATERIAL_INPUT),
        'Body': (NAME_OF_OUTLINE_2_MASK_INPUT, NAME_OF_OUTLINE_2_MATERIAL_INPUT),
        'Face': (NAME_OF_OUTLINE_3_MASK_INPUT, NAME_OF_OUTLINE_3_MATERIAL_INPUT),
        'Dress': (NAME_OF_OUTLINE_4_MASK_INPUT, NAME_OF_OUTLINE_4_MATERIAL_INPUT),
        'Dress1': (NAME_OF_OUTLINE_4_MASK_INPUT, NAME_OF_OUTLINE_4_MATERIAL_INPUT),
        'Helmet': (NAME_OF_OUTLINE_4_MASK_INPUT, NAME_OF_OUTLINE_4_MATERIAL_INPUT),
        'Dress2': (NAME_OF_DRESS2_MASK_INPUT, NAME_OF_DRESS2_MATERIAL_INPUT),
        'Leather': (NAME_OF_LEATHER_MASK_INPUT, NAME_OF_LEATHER_MATERIAL_INPUT),
        'Arm': (NAME_OF_OUTLINE_OTHER_MASK_INPUT, NAME_OF_OUTLINE_OTHER_MATERIAL_INPUT),
        'Effect': (NAME_OF_OUTLINE_OTHER_MASK_INPUT, NAME_OF_OUTLINE_OTHER_MATERIAL_INPUT),
        'EffectHair': (NAME_OF_OUTLINE_OTHER_MASK_INPUT, NAME_OF_OUTLINE_OTHER_MATERIAL_INPUT),
        'Gauntlet': (NAME_OF_OUTLINE_OTHER_MASK_INPUT, NAME_OF_OUTLINE_OTHER_MATERIAL_INPUT),
        'HelmetEmo': (NAME_OF_OUTLINE_OTHER_MASK_INPUT, NAME_OF_OUTLINE_OTHER_MATERIAL_INPUT),
        'Glass': (NAME_OF_OUTLINE_OTHER_MASK_INPUT, NAME_OF_OUTLINE_OTHER_MATERIAL_INPUT),
        'Glass_Eff': (NAME_OF_VFX_MASK_INPUT, NAME_OF_VFX_MATERIAL_INPUT),
        'Pupil': (NAME_OF_PUPIL_MASK_INPUT, NAME_OF_PUPIL_MATERIAL_INPUT),
        'StarCloak': (NAME_OF_VFX_MASK_INPUT, NAME_OF_VFX_MATERIAL_INPUT),
    }

    def __init__(self, blender_operator, context):
        super().__init__(blender_operator, context)
        self.material_names = V1_HoYoToonGenshinImpactMaterialNames
        self.outlines_node_group_names = OutlineNodeGroupNames.V3_BONNY_FESTIVITY_GENSHIN_OUTLINES
        self.light_vectors_node_group_names = OutlineNodeGroupNames.V3_LIGHT_VECTORS_GEOMETRY_NODES
        self.shader_node_names = V1_HoYoToonShaderNodeNames
        self.outlines_shader_node_name = V1_HoYoToonShaderNodeNames.OUTLINES_SHADER
        self.texture_node_names = V1_HoYoToonGenshinImpactTextureNodeNames

    def setup_geometry_nodes(self):
        for mesh in [obj for obj in bpy.data.objects.values() if obj.type == 'MESH']:
            self.__separate_materials_into_unique_meshes(mesh)
        super().setup_geometry_nodes()
        self.clone_night_soul_outlines()

        for mesh in [obj for obj in bpy.data.objects.values() if obj.type == 'MESH']:
            create_light_vectors = [
                material_slot.material for material_slot in mesh.material_slots if 
                material_slot.material.name.startswith(self.material_names.MATERIAL_PREFIX_AFTER_RENAME)
            ]  # Only create Light Vectors on meshes with Shader materials
            if create_light_vectors:
                self.create_light_vectors_modifier(mesh.name)

            create_outlines = [
                material_slot.material for material_slot in mesh.material_slots if 
                material_slot.material.name.startswith(self.material_names.MATERIAL_PREFIX_AFTER_RENAME) and
                [keyword for keyword in material_keywords_to_not_create_outlines_on if keyword not in material_slot.material.name]
            ]  # Only create Outlines on meshes with Shader materials and not in the ignore list (e.g. 'Eff' materials)
            if create_outlines:
                self.create_geometry_nodes_modifier(mesh.name)

        for material in bpy.data.materials:
            if 'Face Outlines' in material.name:
                outline_shader_node = material.node_tree.nodes.get(self.outlines_shader_node_name)
                outline_shader_node.inputs.get(self.shader_node_names.TOGGLE_FACE_OUTLINES).default_value = True

        starcloak_material = bpy.data.materials.get(self.material_names.STAR_CLOAK)
        if starcloak_material:
            self.__connect_shader_node_to_vfx_node(starcloak_material, [StarCloakTypes.ASMODA])

    def clone_night_soul_outlines(self):
        materials = [material for material in bpy.data.materials.values() if material.name not in self.GEOMETRY_NODES_MATERIAL_IGNORE_LIST]
        outline_material = bpy.data.materials.get(self.material_names.NIGHT_SOUL_OUTLINES)

        if not outline_material:
            return

        for material in materials:
            if self.material_names.MATERIAL_PREFIX in material.name and material.name != self.material_names.NIGHT_SOUL_OUTLINES and \
                not material.name.endswith('Outlines'):
                new_outline_name = f'{material.name} {self.material_names.NIGHT_SOUL_OUTLINES_SUFFIX}'

                if not bpy.data.materials.get(new_outline_name) and not ShaderMaterial(material, self.shader_node_names).get_night_soul_outlines_material():
                    new_outline_material = outline_material.copy()
                    new_outline_material.name = new_outline_name
                    new_outline_material.use_fake_user = True

    def set_up_modifier_default_values(self, modifier, mesh):
        super().set_up_modifier_default_values(modifier, mesh)
        self.assign_materials_to_empty_modifier_slots(mesh, modifier)
        self.assign_night_soul_outlines_material(mesh, modifier)
        self.assign_face_lightmap_texture(modifier)
        self.__disable_outlines(mesh, modifier, ['Paimon'])
        modifier.show_viewport = bpy.context.window_manager.enable_viewport_outlines
        print(f'Geometry Node Default Values Set for {modifier.name}: {mesh.name}')

    def assign_materials_to_empty_modifier_slots(self, mesh, modifier):
        for mesh_keyword in mesh_keywords_to_create_geometry_nodes_on + meshes_to_create_outlines_on:
            if mesh_keyword in mesh.name:
                for material_slot in mesh.material_slots:
                    material = material_slot.material
                    already_assigned = False
                    for _, (mask_input, material_input) in self.outline_to_material_mapping.items():
                        if modifier[mask_input] == material:
                            already_assigned = True
                    if not already_assigned:
                        for available_mask_input, available_material_input in available_outline_mask_to_material_mapping.items():
                            if not modifier[available_mask_input] and not modifier[available_material_input]:
                                modifier[available_mask_input] = bpy.data.materials.get(material.name)
                                modifier[available_material_input] = bpy.data.materials.get(material.name + ' Outlines')
                                break

    def assign_night_soul_outlines_material(self, mesh, modifier):
        night_soul_outlines_material_using_mesh_name = [
            material for material in bpy.data.materials.values() if 
            f'{mesh.name} {self.material_names.NIGHT_SOUL_OUTLINES_SUFFIX}' in material.name
        ]
        night_soul_outlines_material_using_mesh_material_name = [
            material for material in bpy.data.materials.values() if [
                material_slot.material for material_slot in mesh.material_slots if 
                material_slot.material.name.split(' ')[-1] in material.name and 
                material.name.endswith(self.material_names.NIGHT_SOUL_OUTLINES_SUFFIX)
            ]
        ]  # If, in the mesh, the last word in the material name is in a Night Soul Outlines material
        night_soul_outlines_material = night_soul_outlines_material_using_mesh_name or \
            night_soul_outlines_material_using_mesh_material_name

        if night_soul_outlines_material:
            modifier[self.NIGHT_SOUL_OUTLINE_SOCKET] = night_soul_outlines_material[0]

    def assign_face_lightmap_texture(self, modifier):
        face_lightmap_node_group = bpy.data.node_groups.get(self.texture_node_names.FACE_LIGHTMAP_NODE_GROUP)
        if face_lightmap_node_group:
            modifier[self.FACE_LIGHTMAP_SOCKET] = face_lightmap_node_group.nodes[self.texture_node_names.FACE_LIGHTMAP].image

    def __separate_materials_into_unique_meshes(self, mesh):
        if len(mesh.material_slots) > 1:
            separated_materials = []
            for material_slot in mesh.material_slots:
                bpy.context.view_layer.objects.active = mesh
                expected_mesh_name = material_slot.material.name.rsplit(' ')[-1]
                expected_mesh = bpy.data.objects.get(expected_mesh_name)
                if not expected_mesh or expected_mesh != mesh:
                    self.__separate_material_from_mesh(mesh, material_slot, expected_mesh_name)
                    separated_materials += [material_slot.material]

            # If we've separated all of the materials from the mesh, delete the original mesh
            if len(separated_materials) == len(mesh.material_slots):
                bpy.data.objects.remove(mesh)
            else:
                self.__remove_material_slots(mesh, separated_materials)

    def __separate_material_from_mesh(self, mesh, material_slot, new_mesh_name):
        print(f'Separating material for: {material_slot.material.name} from {mesh.name}')
        bpy.ops.object.mode_set(mode='EDIT')
        mesh.active_material_index = mesh.material_slots.get(material_slot.material.name).slot_index
        bpy.ops.object.material_slot_select()
        try:
            bpy.ops.mesh.separate(type='SELECTED')
        except RuntimeError as error:
            print(f'Skipping, failed to separate material for: {material_slot.material.name} from {mesh.name}')
            print(error)
            return
        bpy.ops.object.mode_set(mode='OBJECT')

        # OR-check added for Blender < 4.1 where the separated mesh name is different than the parent mesh name
        # Body [Mesh] --(Hair Material Selected)--> Body.001 [Mesh] (Blender >= 4.1)
        # Body [Mesh] --(Hair Material Selected)--> Hair.001 [Mesh] (Blender <  4.0)
        new_separated_mesh = bpy.data.objects.get(f'{mesh.name}.001') or bpy.data.objects.get(f'{new_mesh_name}.001')
        new_mesh_name_mesh = bpy.data.objects.get(new_mesh_name)

        # Clean the separated mesh of any other materials
        self.__remove_material_slots(new_separated_mesh, [material_slot.material], exclude=True)

        if not new_mesh_name_mesh:
            print(f'Renaming {new_separated_mesh.name} to {new_mesh_name}')
            new_separated_mesh.name = new_mesh_name
            return new_separated_mesh
        else:
            # Join meshes
            bpy.ops.object.select_all(action='DESELECT')
            new_separated_mesh.select_set(True)
            new_mesh_name_mesh.select_set(True)
            bpy.context.view_layer.objects.active = new_mesh_name_mesh
            print(f'Joining {new_separated_mesh} to {new_mesh_name_mesh}')
            bpy.ops.object.join()
            renamed_mesh_name = new_mesh_name_mesh.material_slots[0].material.name.split(' ')[-1]
            print(f'Renaming {new_mesh_name_mesh.name} to {renamed_mesh_name}')
            new_mesh_name_mesh.name = renamed_mesh_name


    def __remove_material_slots(self, mesh, materials, exclude=False):
        bpy.ops.object.mode_set(mode='OBJECT')
        # Reversing is IMPORTANT in order to avoid index errors while removing during runtime
        for material_slot_material in reversed(mesh.material_slots):
            if (not exclude and material_slot_material.material in materials) or (exclude and material_slot_material.material not in materials):
                mesh.active_material_index = mesh.material_slots.get(material_slot_material.material.name).slot_index
                print(f'Removing material: {material_slot_material.material.name} from {mesh.name}')
                bpy.context.view_layer.objects.active = mesh
                bpy.ops.object.material_slot_remove()

    '''
    Very targeted method for disabling outlines on Paimon's cloak
    May require refactoring if used for other purposes.
    '''
    def __disable_outlines(self, mesh, modifier, character_names):
        for material_slot in mesh.material_slots:
            material = material_slot.material

            for character_name in character_names:
                if material.name == self.material_names.STAR_CLOAK and character_name in material.node_tree.nodes.get(self.texture_node_names.VFX_DIFFUSE).image.name:
                    modifier[self.TOGGLE_OUTLINES_SOCKET] = False

    def __connect_shader_node_to_vfx_node(self, material, starcloak_types: List[StarCloakTypes]):
        MAIN_SHADER_NODE_NAME = f'{self.shader_node_names.BODY_SHADER_FOR_VFX}'
        MAIN_SHADER_OUTPUT_NAME = self.shader_node_names.BODY_SHADER_OUTPUT
        VFX_SHADER_NODE_NAME = self.shader_node_names.VFX_SHADER
        VFX_SHADER_INPUT_NAME = self.shader_node_names.VFX_SHADER_INPUT

        vfx_shader_node = material.node_tree.nodes.get(VFX_SHADER_NODE_NAME)
        for starcloak_type in starcloak_types:
            if vfx_shader_node.inputs.get(self.shader_node_names.STAR_CLOAK_TYPE).default_value == starcloak_type.value:
                self.__connect_main_shader_to_vfx_shader(material, MAIN_SHADER_NODE_NAME, MAIN_SHADER_OUTPUT_NAME, VFX_SHADER_NODE_NAME, VFX_SHADER_INPUT_NAME)
                vfx_main_shader = material.node_tree.nodes.get(MAIN_SHADER_NODE_NAME)
                vfx_main_shader.mute = False

    def __connect_main_shader_to_vfx_shader(self, 
                                            material, 
                                            main_shader_node_name, 
                                            main_shader_output_name, 
                                            vfx_shader_node_name, 
                                            vfx_shader_input_name
                                            ):
        main_shader_node = material.node_tree.nodes.get(main_shader_node_name)
        vfx_shader_node = material.node_tree.nodes.get(vfx_shader_node_name)

        output = main_shader_node.outputs.get(main_shader_output_name)
        input = vfx_shader_node.inputs.get(vfx_shader_input_name)
        material.node_tree.links.new(output, input)

class HonkaiStarRailGeometryNodesSetup(GameGeometryNodesSetup):
    GEOMETRY_NODES_MATERIAL_IGNORE_LIST = []

    def __init__(self, blender_operator, context, material_names, outline_node_group_names):
        super().__init__(blender_operator, context)
        self.material_names = material_names
        self.outlines_node_group_names = outline_node_group_names

    def setup_geometry_nodes(self):
        self.clone_outlines(self.material_names)
        for mesh_name in meshes_to_create_outlines_on:
            for object_name, object_data in bpy.context.scene.objects.items():
                if object_data.type == 'MESH' and (mesh_name == object_name or f'_{mesh_name}' in object_name):
                    self.create_geometry_nodes_modifier(f'{object_name}{BODY_PART_SUFFIX}')
                    self.fix_meshes_by_setting_genshin_materials(object_name)

        face_meshes = [mesh for mesh_name, mesh in bpy.data.meshes.items() if 'Face' in mesh_name and 'Face_Mask' not in mesh_name]
        self.fix_face_outlines_by_reordering_material_slots(face_meshes)

    def create_geometry_nodes_modifier(self, mesh_name):
        mesh = bpy.context.scene.objects[mesh_name]

        for outlines_node_group_name in self.outlines_node_group_names:
            outlines_node_group = bpy.data.node_groups.get(outlines_node_group_name)
            geometry_nodes_modifier = mesh.modifiers.get(f'{NAME_OF_GEOMETRY_NODES_MODIFIER} {mesh_name}')

            if not outlines_node_group:
                continue

            if not geometry_nodes_modifier:
                geometry_nodes_modifier = mesh.modifiers.new(f'{NAME_OF_GEOMETRY_NODES_MODIFIER} {mesh_name}', 'NODES')
                geometry_nodes_modifier.node_group = outlines_node_group
            self.set_up_modifier_default_values(geometry_nodes_modifier, mesh)
        return geometry_nodes_modifier


class StellarToonGeometryNodesSetup(HonkaiStarRailGeometryNodesSetup):
    GEOMETRY_NODES_MATERIAL_IGNORE_LIST = []
    LIGHTDIR_OUTPUT_ATTRIBUTE = 'Output_7_attribute_name'
    HEADFORWARD_OUTPUT_ATTRIBUTE = 'Output_8_attribute_name'
    HEADUP_OUTPUT_ATTRIBUTE = 'Output_9_attribute_name'

    def __init__(self, blender_operator, context, material_names, outline_node_group_names, light_vector_node_group_names):
        super().__init__(blender_operator, context, material_names, outline_node_group_names)
        self.material_names = material_names
        self.outlines_node_group_names = outline_node_group_names
        self.light_vectors_node_group_names = light_vector_node_group_names or []

    def setup_geometry_nodes(self):
        self.clone_outlines(self.material_names)

        if self.light_vectors_node_group_names:
            character_armature = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE'][0]  # Expecting 1 armature in scene
            character_armature_mesh_names = [obj.name for obj in character_armature.children if obj.type == 'MESH']
            for mesh_name in character_armature_mesh_names:  # It is important that this is created and placed before Outlines!!
                for object_name, object_data in bpy.context.scene.objects.items():
                    if object_data.type == 'MESH' and (mesh_name == object_name or f'_{mesh_name}' in object_name):
                        light_vectors_modifier = self.create_light_vectors_modifier(f'{object_name}{BODY_PART_SUFFIX}')
                        self.__set_light_vectors_default_output_attributes(light_vectors_modifier)
        for mesh_name in meshes_to_create_outlines_on:
            for object_name, object_data in bpy.context.scene.objects.items():
                if object_data.type == 'MESH' and (mesh_name == object_name or f'_{mesh_name}' in object_name):
                    self.create_geometry_nodes_modifier(f'{object_name}{BODY_PART_SUFFIX}')
                    self.fix_meshes_by_setting_genshin_materials(object_name)

        face_meshes = [mesh for mesh_name, mesh in bpy.data.meshes.items() if 'Face' in mesh_name and 'Face_Mask' not in mesh_name]
        self.fix_face_outlines_by_reordering_material_slots(face_meshes)

    def __set_light_vectors_default_output_attributes(self, light_vectors_modifier):
        light_vectors_modifier[self.LIGHTDIR_OUTPUT_ATTRIBUTE] = 'lightDir'
        light_vectors_modifier[self.HEADFORWARD_OUTPUT_ATTRIBUTE] = 'headForward'
        light_vectors_modifier[self.HEADUP_OUTPUT_ATTRIBUTE] = 'headUp'


class PunishingGrayRavenGeometryNodesSetup(V3_GenshinImpactGeometryNodesSetup):
    GEOMETRY_NODES_MATERIAL_IGNORE_LIST = []
    MESH_IGNORE_LIST = [
        JaredNytsPunishingGrayRavenShaderMaterialNames.EYE
    ]

    def __init__(self, blender_operator, context):
        super().__init__(blender_operator, context)
        self.material_names = JaredNytsPunishingGrayRavenShaderMaterialNames
        self.outlines_node_group_names = OutlineNodeGroupNames.V3_JAREDNYTS_PGR_OUTLINES

    def setup_geometry_nodes(self):
        self.clone_outlines(self.material_names)
        character_armature = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE'][0]  # Expecting 1 armature in scene
        character_armature_mesh_names = [obj.name for obj in character_armature.children if obj.type == 'MESH']

        for mesh_name in character_armature_mesh_names:  # It is important that this is created and placed before Outlines!!
            for object_name, object_data in bpy.context.scene.objects.items():
                if object_data.type == 'MESH' and (mesh_name == object_name or f'_{mesh_name}' in object_name):
                    self.create_light_vectors_modifier(f'{object_name}{BODY_PART_SUFFIX}')

        local_mesh_names_to_create_geometry_nodes_on = [
            mesh.name for mesh in bpy.data.meshes if [
                material for material in mesh.materials if material.name.startswith(JaredNytsPunishingGrayRavenShaderMaterialNames.MATERIAL_PREFIX)
            ]
        ]
        local_mesh_names_to_create_geometry_nodes_on = [
            mesh_name for mesh_name in local_mesh_names_to_create_geometry_nodes_on if 
                mesh_name not in self.MESH_IGNORE_LIST and
                'Alpha' not in mesh_name
        ]
        for mesh_name in [item for item in local_mesh_names_to_create_geometry_nodes_on]:
            for object_name, object_data in bpy.context.scene.objects.items():
                if object_data.type == 'MESH' and (mesh_name.lower() in object_name.lower()):
                    self.create_geometry_nodes_modifier(f'{object_name}{BODY_PART_SUFFIX}')
                    self.fix_meshes_by_setting_genshin_materials(object_name)

        face_meshes = [mesh for mesh_name, mesh in bpy.data.meshes.items() if 'face' in mesh_name.lower()]
        self.fix_face_outlines_by_reordering_material_slots(face_meshes)

    def create_geometry_nodes_modifier(self, mesh_name):
        mesh = bpy.context.scene.objects[mesh_name]

        for outlines_node_group_name in self.outlines_node_group_names:
            outlines_node_group = bpy.data.node_groups.get(outlines_node_group_name)
            geometry_nodes_modifier = mesh.modifiers.get(f'{NAME_OF_GEOMETRY_NODES_MODIFIER} {mesh_name}')

            if not outlines_node_group:
                continue

            if not geometry_nodes_modifier:
                geometry_nodes_modifier = mesh.modifiers.new(f'{NAME_OF_GEOMETRY_NODES_MODIFIER} {mesh_name}', 'NODES')
                geometry_nodes_modifier.node_group = outlines_node_group
            self.set_up_modifier_default_values(geometry_nodes_modifier, mesh)
        return geometry_nodes_modifier

    def set_up_modifier_default_values(self, modifier, mesh):
        modifier[self.BASE_GEOMETRY_INPUT] = True
        modifier[self.USE_VERTEX_COLORS_INPUT] = True
        modifier[self.OUTLINE_THICKNESS_INPUT] = 0.1

        # V2
        self.DEFAULT_OUTLINE_THICKNESS = 0.1
        GenshinImpactGeometryNodesSetup.set_up_modifier_default_values(self, modifier, mesh)

        # V3
        # outline_to_material_mapping = {
        #     'Hair': (NAME_OF_OUTLINE_1_MASK_INPUT, NAME_OF_OUTLINE_1_MATERIAL_INPUT),
        #     'Hair01': (NAME_OF_OUTLINE_1_MASK_INPUT, NAME_OF_OUTLINE_1_MATERIAL_INPUT),
        #     'Body': (NAME_OF_OUTLINE_2_MASK_INPUT, NAME_OF_OUTLINE_2_MATERIAL_INPUT),
        #     'Face': (NAME_OF_OUTLINE_3_MASK_INPUT, NAME_OF_OUTLINE_3_MATERIAL_INPUT),
        #     'Down': (NAME_OF_OUTLINE_4_MASK_INPUT, NAME_OF_OUTLINE_4_MATERIAL_INPUT),  # Dress slot
        #     'Cloth': (NAME_OF_OUTLINE_4_MASK_INPUT, NAME_OF_OUTLINE_4_MATERIAL_INPUT),  # Dress slot
        #     'Clothes': (NAME_OF_OUTLINE_4_MASK_INPUT, NAME_OF_OUTLINE_4_MATERIAL_INPUT),  # Dress slot
        #     'Cloth01': (NAME_OF_OUTLINE_4_MASK_INPUT, NAME_OF_OUTLINE_4_MATERIAL_INPUT),  # Dress slot
        #     'Cloth02': (NAME_OF_DRESS2_MASK_INPUT, NAME_OF_DRESS2_MATERIAL_INPUT),
        #     'Hair02': (NAME_OF_OUTLINE_OTHER_MASK_INPUT, NAME_OF_OUTLINE_OTHER_MATERIAL_INPUT),
        #     'Upper': (NAME_OF_OUTLINE_OTHER_MASK_INPUT, NAME_OF_OUTLINE_OTHER_MATERIAL_INPUT),
        # }

        # for input_name, (material_input_accessor, outline_material_input_accessor) in outline_to_material_mapping.items():
        #     material_name = f'{self.material_names.MATERIAL_PREFIX}{input_name}'
        #     outline_material_name = f'{self.material_names.MATERIAL_PREFIX}{input_name} Outlines'

        #     if bpy.data.materials.get(material_name) and bpy.data.materials.get(outline_material_name):
        #         modifier[material_input_accessor] = bpy.data.materials.get(material_name)
        #         modifier[outline_material_input_accessor] = bpy.data.materials.get(outline_material_name)


class V2_PunishingGrayRavenGeometryNodesSetup(GameGeometryNodesSetup):
    GEOMETRY_NODES_MATERIAL_IGNORE_LIST = []
    MESH_IGNORE_LIST = []
    DEFAULT_OUTLINE_THICKNESS = 0.1

    def __init__(self, blender_operator, context):
        super().__init__(blender_operator, context)
        self.material_names = JaredNytsPunishingGrayRavenShaderMaterialNames
        self.outlines_node_group_names = OutlineNodeGroupNames.V2_JAREDNYTS_PGR_OUTLINES
        self.light_vectors_node_group_names = OutlineNodeGroupNames.V3_LIGHT_VECTORS_GEOMETRY_NODES  # support V3 Light Vectors w/ V2 Outlines

    def setup_geometry_nodes(self):
        self.clone_outlines(self.material_names)
        character_armature = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE'][0]  # Expecting 1 armature in scene
        character_armature_mesh_names = [obj.name for obj in character_armature.children if obj.type == 'MESH']

        for mesh_name in character_armature_mesh_names:  # It is important that this is created and placed before Outlines!!
            for object_name, object_data in bpy.context.scene.objects.items():
                if object_data.type == 'MESH' and (mesh_name == object_name or f'_{mesh_name}' in object_name):
                    self.create_light_vectors_modifier(f'{object_name}{BODY_PART_SUFFIX}')

        local_mesh_names_to_create_geometry_nodes_on = [
            mesh.name for mesh in bpy.data.meshes if [
                material for material in mesh.materials if material.name.startswith(JaredNytsPunishingGrayRavenShaderMaterialNames.MATERIAL_PREFIX)
            ]
        ]
        local_mesh_names_to_create_geometry_nodes_on = [
            mesh_name for mesh_name in local_mesh_names_to_create_geometry_nodes_on if 
                'Eye' not in mesh_name and
                'Alpha' not in mesh_name
        ]
        for mesh_name in [item for item in local_mesh_names_to_create_geometry_nodes_on]:
            for object_name, object_data in bpy.context.scene.objects.items():
                if object_data.type == 'MESH' and (mesh_name.lower() in object_name.lower()):
                    self.create_geometry_nodes_modifier(f'{object_name}{BODY_PART_SUFFIX}')
                    self.fix_meshes_by_setting_genshin_materials(object_name)

        face_meshes = [mesh for mesh_name, mesh in bpy.data.meshes.items() if 'face' in mesh_name.lower()]
        self.fix_face_outlines_by_reordering_material_slots(face_meshes)

    def create_geometry_nodes_modifier(self, mesh_name):
        mesh = bpy.context.scene.objects[mesh_name]

        for outlines_node_group_name in self.outlines_node_group_names:
            outlines_node_group = bpy.data.node_groups.get(outlines_node_group_name)
            geometry_nodes_modifier = mesh.modifiers.get(f'{NAME_OF_GEOMETRY_NODES_MODIFIER} {mesh_name}')

            if not outlines_node_group:
                continue

            if not geometry_nodes_modifier:
                geometry_nodes_modifier = mesh.modifiers.new(f'{NAME_OF_GEOMETRY_NODES_MODIFIER} {mesh_name}', 'NODES')
                geometry_nodes_modifier.node_group = outlines_node_group
            self.set_up_modifier_default_values(geometry_nodes_modifier, mesh)
        return geometry_nodes_modifier
