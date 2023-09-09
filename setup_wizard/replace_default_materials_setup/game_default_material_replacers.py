# Author: michael-gh1

import bpy

from abc import ABC, abstractmethod
from bpy.types import Context, Operator

from setup_wizard.import_order import get_actual_material_name_for_dress
from setup_wizard.domain.game_types import GameType
from setup_wizard.domain.shader_identifier_service import GenshinImpactShaders, ShaderIdentifierService, \
    ShaderIdentifierServiceFactory
from setup_wizard.domain.shader_materials import BonnyGenshinImpactMaterialNames, FestivityGenshinImpactMaterialNames, \
    GameMaterialNames, Nya222HonkaiStarRailShaderMaterialNames
from setup_wizard.texture_import_setup.texture_importer_types import TextureImporterType


class GameDefaultMaterialReplacer(ABC):
    @abstractmethod
    def replace_default_materials(self):
        raise NotImplementedError()


class GameDefaultMaterialReplacerFactory:
    def create(game_type: GameType, blender_operator: Operator, context: Context):
        shader_identifier_service: ShaderIdentifierService = ShaderIdentifierServiceFactory.create(game_type)

        # Because we inject the GameType via StringProperty, we need to compare using the Enum's name (a string)
        if game_type == GameType.GENSHIN_IMPACT.name:
            if shader_identifier_service.identify_shader(bpy.data.materials) is GenshinImpactShaders.V3_GENSHIN_IMPACT_SHADER:
                material_names = BonnyGenshinImpactMaterialNames
            else:
                material_names = FestivityGenshinImpactMaterialNames 
            return GenshinImpactDefaultMaterialReplacer(blender_operator, context, material_names)
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            return HonkaiStarRailDefaultMaterialReplacer(blender_operator, context)
        else:
            raise Exception(f'Unknown {GameType}: {game_type}')


class GenshinImpactDefaultMaterialReplacer(GameDefaultMaterialReplacer):
    def __init__(self, blender_operator, context, material_names: GameMaterialNames):
        self.blender_operator: Operator = blender_operator
        self.context: Context = context
        self.material_names = material_names

    def replace_default_materials(self):
        meshes = [mesh for mesh in bpy.context.scene.objects if mesh.type == 'MESH']

        for mesh in meshes:
            for material_slot in mesh.material_slots:
                material_name = material_slot.name
                mesh_body_part_name = None
                character_type = None

                if material_name.startswith('NPC'):
                    mesh_body_part_name = self.__get_npc_mesh_body_part_name(material_name)
                    character_type = TextureImporterType.NPC
                elif material_name.startswith('Monster'):
                    mesh_body_part_name = self.__get_monster_mesh_body_part_name(material_name)
                    character_type = TextureImporterType.MONSTER
                else:
                    mesh_body_part_name = material_name.split('_')[-1]
                    character_type = TextureImporterType.AVATAR

                genshin_material = bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}{mesh_body_part_name}')

                if genshin_material:
                    material_slot.material = genshin_material
                elif mesh_body_part_name and ('Dress' in mesh_body_part_name or 'Arm' in mesh_body_part_name or 'Cloak' in mesh_body_part_name):
                    # Xiao is the only character with an Arm material
                    # Dainsleif and Paimon are the only characters with Cloak materials
                    self.blender_operator.report({'INFO'}, 'Dress detected on character model!')

                    actual_material_for_dress = get_actual_material_name_for_dress(material_name, character_type.name)
                    if actual_material_for_dress == 'Cloak':
                        # short-circuit, no shader available for 'Cloak' so do nothing (Paimon)
                        continue

                    genshin_material = self.__clone_material_and_rename(
                        material_slot, 
                        f'{self.material_names.MATERIAL_PREFIX}{actual_material_for_dress}', 
                        mesh_body_part_name
                    )
                    self.blender_operator.report({'INFO'}, f'Replaced material: "{material_name}" with "{actual_material_for_dress}"')
                elif material_name == 'miHoYoDiffuse':
                    material_slot.material = bpy.data.materials.get(FestivityGenshinImpactMaterialNames.BODY)
                    continue
                else:
                    self.blender_operator.report({'WARNING'}, f'Ignoring unknown mesh body part in character model: {mesh_body_part_name} / Material: {material_name}')
                    continue

                # Deprecated: I don't think cloning and renaming groups is necessary? (original commit: 6a4772e)
                # Don't need to duplicate multiple Face shader nodes
                # if genshin_material.name != f'miHoYo - Genshin Face':
                #     genshin_main_shader_node = genshin_material.node_tree.nodes.get('Group.001')
                #     genshin_main_shader_node.node_tree = self.__clone_shader_node_and_rename(genshin_material, mesh_body_part_name)
        self.blender_operator.report({'INFO'}, 'Replaced default materials with Genshin shader materials...')

    def __get_npc_mesh_body_part_name(self, material_name):
        if 'Hair' in material_name:
            return 'Hair'
        elif 'Face' in material_name:
            return 'Face'
        elif 'Body' in material_name:
            return 'Body'
        elif 'Dress' in material_name:  # I don't think this is a valid case, either they use Hair or Body textures
            return 'Dress'
        else:
            return None

    def __get_monster_mesh_body_part_name(self, material_name):
        if 'Hair' in material_name:
            return 'Hair'
        elif 'Face' in material_name:
            return 'Face'
        elif 'Body' in material_name:
            return 'Body'
        elif 'Dress' in material_name:
            return 'Dress'  # TODO: Not sure if all 'Dress' are 'Body'
        else:
            return 'Body'  # Assumption that everything else should be a Body material

    def __clone_material_and_rename(self, material_slot, mesh_body_part_name_template, mesh_body_part_name):
        new_material = bpy.data.materials.get(mesh_body_part_name_template).copy()
        new_material.name = f'{self.material_names.MATERIAL_PREFIX}{mesh_body_part_name}'
        new_material.use_fake_user = True

        material_slot.material = new_material
        return new_material

    '''
    This method was used for V1 shader and should NOT be used for V2 shader because the group name is different.
    The intent was purely to have separate shader nodes and matching the name to the material.
    This does not seem necessary. Haven't checked if there's a performance impact
    '''
    def __clone_shader_node_and_rename(self, material, mesh_body_part_name):
        new_shader_node_tree = material.node_tree.nodes.get('Group.001').node_tree.copy()
        new_shader_node_tree.name = f'miHoYo - Genshin {mesh_body_part_name}'
        return new_shader_node_tree


class HonkaiStarRailDefaultMaterialReplacer(GameDefaultMaterialReplacer):
    MESH_IGNORE_LIST = [
        'Face_Mask'
    ]

    def __init__(self, blender_operator, context):
        self.blender_operator: Operator = blender_operator
        self.context: Context = context

    def replace_default_materials(self):
        meshes = [mesh for mesh in bpy.context.scene.objects if mesh.type == 'MESH' and mesh.name not in self.MESH_IGNORE_LIST]

        for mesh in meshes:
            for material_slot in mesh.material_slots:
                material_name = material_slot.name
                mesh_body_part_name = self.find_body_part_name(material_name)

                # Another hacky-solution, some characters only have a "Body" material, but the shader materials
                # only have Body1, Body2 and Body_A. Should request Shader to have a "Body" material
                # Some characters have a mismatch between Texture and Material Data too... (Body_Color_A and Body)
                # Checklist:
                # 1. Materials
                # 2. Textures
                # 3. Material Data
                # The best fix would be to create a "Body" material via code in case the shader is updated to have the same
                if mesh_body_part_name == 'Body':
                    body_material = self.create_body_material(mesh, Nya222HonkaiStarRailShaderMaterialNames.BODY)
                    material_name = body_material.name
                if mesh_body_part_name == 'Body3':
                    body_material = self.create_body_material(mesh, Nya222HonkaiStarRailShaderMaterialNames.BODY3)
                    material_name = body_material.name
                if mesh_body_part_name ==  'Body2_Trans':
                    body_material = self.create_body_trans_material(mesh, Nya222HonkaiStarRailShaderMaterialNames.BODY2_TRANS) 
                    material_name = body_material.name

                if 'Weapon' in mesh_body_part_name:
                    weapon_material = self.create_weapon_materials(mesh_body_part_name)
                    material_name = weapon_material.name

                honkai_star_rail_material = bpy.data.materials.get(
                    f'{Nya222HonkaiStarRailShaderMaterialNames.MATERIAL_PREFIX}{mesh_body_part_name}'
                )

                if honkai_star_rail_material:
                    material_slot.material = honkai_star_rail_material
                else:
                    self.blender_operator.report({'WARNING'}, f'Ignoring unknown mesh body part in character model: {mesh_body_part_name} / Material: {material_name}')
                    continue
        self.blender_operator.report({'INFO'}, 'Replaced default materials with Genshin shader materials...')

    def find_body_part_name(self, material_name):
        expected_format_body_part_name = self.__expected_format_body_part_name_search(material_name)
        naive_search_body_part_name = self.__naive_body_part_name_search(material_name)
        body_part_name = ''

        # If the two are equal, then we're confident that the body part name is correct (pick either)
        # Elif the naive search found none of the expected body part names, return expected format search body part name
        # Else expected format and naive searches do not equal, use the naive search (pulls from list of expected body part names)
        if expected_format_body_part_name == naive_search_body_part_name:
            body_part_name = expected_format_body_part_name
        elif expected_format_body_part_name and not naive_search_body_part_name:
            body_part_name = expected_format_body_part_name
        else:
            return naive_search_body_part_name
        return body_part_name

    '''
    Expected Format Search: Search for body part name at expected location, at the end of the material name (ex. 'Body')
    '''
    def __expected_format_body_part_name_search(self, material_name):
        return material_name.split('_')[-1]

    '''
    Naive Search: Search for body part name in material name
    '''
    def __naive_body_part_name_search(self, material_name):
        EXPECTED_BODY_PART_NAMES = [
            'Hair',
            'Body1',
            'Body2_Trans',
            'Body2',
            'Body3',
            'Body_Trans',
            'Face',
            'EyeShadow',
            'Body',  # Important this is last in the list because it could interfere with Body1 and Body2
        ]

        for expected_body_part_name in EXPECTED_BODY_PART_NAMES:
            if expected_body_part_name in material_name:
                return expected_body_part_name

    def create_body_material(self, mesh, material_name):
        body_material = bpy.data.materials.get(material_name)
        if not body_material:
            body_material = bpy.data.materials.get(Nya222HonkaiStarRailShaderMaterialNames.BODY1).copy()
            body_material.name = material_name
            body_material.use_fake_user = True
        return body_material

    def create_body_trans_material(self, mesh, material_name):
        body_material = bpy.data.materials.get(material_name)
        if not body_material:
            body_material = bpy.data.materials.get(Nya222HonkaiStarRailShaderMaterialNames.BODY_TRANS).copy()
            body_material.name = material_name
            body_material.use_fake_user = True
        return body_material

    def create_weapon_materials(self, mesh_body_part_name):
        weapon_material_name = \
            f'{Nya222HonkaiStarRailShaderMaterialNames.MATERIAL_PREFIX}{mesh_body_part_name}' if \
            mesh_body_part_name == 'Weapon01' or mesh_body_part_name == 'Weapon02' else \
            f'{Nya222HonkaiStarRailShaderMaterialNames.WEAPON}'
        weapon_material = bpy.data.materials.get(weapon_material_name)

        if not weapon_material:
            weapon_material = bpy.data.materials.get(f'{Nya222HonkaiStarRailShaderMaterialNames.WEAPON}').copy()
            weapon_material.name = weapon_material_name
            weapon_material.use_fake_user = True
        return weapon_material
