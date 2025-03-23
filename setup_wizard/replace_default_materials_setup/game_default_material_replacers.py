# Author: michael-gh1

import bpy

from abc import ABC, abstractmethod
from bpy.types import Context, Operator
from setup_wizard.domain.shader_node_names import ShaderNodeNames, StellarToonShaderNodeNames, V2_GenshinShaderNodeNames, V3_GenshinShaderNodeNames, V4_PrimoToonShaderNodeNames
from setup_wizard.domain.star_cloak_types import StarCloakTypes
from setup_wizard.domain.material_identifier_service import PunishingGrayRavenMaterialIdentifierService

from setup_wizard.import_order import get_actual_material_name_for_dress
from setup_wizard.domain.game_types import GameType
from setup_wizard.domain.shader_identifier_service import GenshinImpactShaders, HonkaiStarRailShaders, ShaderIdentifierService, \
    ShaderIdentifierServiceFactory
from setup_wizard.domain.shader_material_names import StellarToonShaderMaterialNames, V3_BonnyFestivityGenshinImpactMaterialNames, V2_FestivityGenshinImpactMaterialNames, \
    ShaderMaterialNames, Nya222HonkaiStarRailShaderMaterialNames, JaredNytsPunishingGrayRavenShaderMaterialNames, V4_PrimoToonGenshinImpactMaterialNames
from setup_wizard.texture_import_setup.texture_importer_types import TextureImporterType
from setup_wizard.domain.shader_material_name_keywords import ShaderMaterialNameKeywords
from setup_wizard.utils.genshin_body_part_deducer import get_monster_body_part_name, \
    get_npc_mesh_body_part_name

class GameDefaultMaterialReplacer(ABC):
    @abstractmethod
    def replace_default_materials(self):
        raise NotImplementedError()


class GameDefaultMaterialReplacerFactory:
    def create(game_type: GameType, blender_operator: Operator, context: Context):
        shader_identifier_service: ShaderIdentifierService = ShaderIdentifierServiceFactory.create(game_type)
        shader = shader_identifier_service.identify_shader(bpy.data.materials, bpy.data.node_groups)

        # Because we inject the GameType via StringProperty, we need to compare using the Enum's name (a string)
        if game_type == GameType.GENSHIN_IMPACT.name:
            if shader is GenshinImpactShaders.V1_GENSHIN_IMPACT_SHADER or shader is GenshinImpactShaders.V2_GENSHIN_IMPACT_SHADER:
                material_names = V2_FestivityGenshinImpactMaterialNames
                shader_node_names = V2_GenshinShaderNodeNames
            elif shader is GenshinImpactShaders.V3_GENSHIN_IMPACT_SHADER:
                material_names = V3_BonnyFestivityGenshinImpactMaterialNames
                shader_node_names = V3_GenshinShaderNodeNames
            else:
                material_names = V4_PrimoToonGenshinImpactMaterialNames 
                shader_node_names = V4_PrimoToonShaderNodeNames
            return GenshinImpactDefaultMaterialReplacer(blender_operator, context, material_names, shader_node_names)
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            if shader is HonkaiStarRailShaders.NYA222_HONKAI_STAR_RAIL_SHADER:
                return HonkaiStarRailDefaultMaterialReplacer(blender_operator, context, Nya222HonkaiStarRailShaderMaterialNames)
            else:  # shader is HonkaiStarRailShaders.STELLARTOON_HONKAI_STAR_RAIL_SHADER
                return StellarToonDefaultMaterialReplacer(blender_operator, context, StellarToonShaderMaterialNames)
        elif game_type == GameType.PUNISHING_GRAY_RAVEN.name:
            return PunishingGrayRavenDefaultMaterialReplacer(blender_operator, context)
        else:
            raise Exception(f'Unknown {GameType}: {game_type}')


class GenshinImpactDefaultMaterialReplacer(GameDefaultMaterialReplacer):
    def __init__(self, blender_operator, context, material_names: ShaderMaterialNames, shader_node_names: ShaderNodeNames):
        self.blender_operator: Operator = blender_operator
        self.context: Context = context
        self.material_names = material_names
        self.shader_node_names = shader_node_names

    def replace_default_materials(self):
        mesh_ignore_list = [
            'Dress',  # Scaramouche
        ]
        meshes = [mesh for mesh in bpy.context.scene.objects if mesh.type == 'MESH' and mesh.name not in mesh_ignore_list]

        for mesh in meshes:
            for material_slot in mesh.material_slots:
                material_name = material_slot.name
                mesh_body_part_name = None
                character_type = None

                if material_name.startswith('NPC'):
                    mesh_body_part_name = get_npc_mesh_body_part_name(material_name)
                    character_type = TextureImporterType.NPC
                elif material_name.startswith('Monster'):
                    mesh_body_part_name = get_monster_body_part_name(material_name)
                    character_type = TextureImporterType.MONSTER
                else:
                    mesh_body_part_name = material_name.split('_')[-1]
                    character_type = TextureImporterType.AVATAR

                if material_name.startswith(ShaderMaterialNameKeywords.SKILLOBJ) and material_name.endswith('Glass_Mat'):
                    mesh_body_part_name = 'Glass'
                elif material_name.startswith(ShaderMaterialNameKeywords.SKILLOBJ) and material_name.endswith('Glass_Eff_Mat'):
                    mesh_body_part_name = 'Glass_Eff'
                elif material_name.startswith(ShaderMaterialNameKeywords.SKILLOBJ):
                    skillobj_identifier = material_name.split('_')[2]
                    mesh_body_part_name = f'{ShaderMaterialNameKeywords.SKILLOBJ} {skillobj_identifier}'
                elif material_name.endswith('Hand_Eff_Mat'):  # Asmoday
                    mesh_body_part_name = 'StarCloak'

                # If material_name is ever 'Dress', 'Arm' or 'Cloak', there could be issues with get_actual_material_name_for_dress()
                material_name = self.create_shader_material_if_unique_mesh(mesh, mesh_body_part_name, material_name)
                genshin_material = bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}{mesh_body_part_name}')

                if genshin_material:
                    material_slot.material = genshin_material
                elif mesh_body_part_name and ('Dress' in mesh_body_part_name or 'Arm' in mesh_body_part_name or 'Cloak' in mesh_body_part_name):
                    # Xiao is the only character with an Arm material
                    # Dainsleif and Paimon are the only characters with Cloak materials
                    self.blender_operator.report({'INFO'}, 'Dress detected on character model!')

                    actual_material_for_dress = get_actual_material_name_for_dress(material_name, character_type.name)
                    if actual_material_for_dress == 'Cloak' or mesh_body_part_name == 'Cloak':
                        if bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}VFX'):
                            actual_material_for_dress = 'VFX'
                            mesh_body_part_name = 'StarCloak'
                        elif mesh_body_part_name == 'Cloak':
                            pass  # Give Dainslief basic body shader (backwards compatibility)
                        else:
                            # short-circuit, no shader available for 'Cloak' so do nothing (Paimon)
                            continue
                    elif actual_material_for_dress == 'Effect':  # Dress2 material w/ Effect texture filename (Skirk support)
                        # (dangerous) assumption that all Dress w/ Effect texture filename are Hair-type
                        actual_material_for_dress = 'Hair'  # backwards compatible before VFX shader existed, pre-v4.0

                        if bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}VFX'):
                            actual_material_for_dress = 'VFX'
                            mesh_body_part_name = 'StarCloak'
                    elif actual_material_for_dress == 'Eff':  # Asmoday support
                        # (dangerous) assumption that all Eff texture filename are Body-type
                        actual_material_for_dress = 'Body'  # backwards compatible before VFX shader existed, pre-v4.0

                        if bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}VFX'):
                            actual_material_for_dress = 'VFX'
                            mesh_body_part_name = 'StarCloak'

                    genshin_material = self.__clone_material_and_rename(
                        material_slot, 
                        f'{self.material_names.MATERIAL_PREFIX}{actual_material_for_dress}', 
                        mesh_body_part_name
                    )
                    if genshin_material.name == f'{self.material_names.STAR_CLOAK}':
                        self.__set_glass_star_cloak_toggle(genshin_material, True)
                        self.__set_star_cloak_type(genshin_material, material_name)  # original material name, which contains character name
                    self.blender_operator.report({'INFO'}, f'Replaced material: "{material_name}" with "{actual_material_for_dress}"')
                elif material_name == 'miHoYoDiffuse':
                    material_slot.material = bpy.data.materials.get(self.material_names.BODY)
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

    def create_shader_material_if_unique_mesh(self, mesh, mesh_body_part_name, material_name):
        if mesh_body_part_name == 'EffectHair':  # Furina
            hair_material = self.create_hair_material(self.material_names, self.material_names.EFFECT_HAIR)
            material_name = hair_material.name
        elif mesh_body_part_name == 'Effect':  # Furina (Default)
            hair_material = self.create_hair_material(self.material_names, self.material_names.EFFECT)
            material_name = hair_material.name
        elif mesh_body_part_name == 'Helmet':  # Frem
            helmet_material = self.create_hair_material(self.material_names, self.material_names.HELMET)
            material_name = helmet_material.name
        elif mesh_body_part_name == 'HelmetEmo':  # Frem
            helmet_material = self.create_hair_material(self.material_names, self.material_names.HELMET_EMO)
            material_name = helmet_material.name
        elif mesh_body_part_name == 'Gauntlet':  # Wrioth
            gauntlet_material = self.create_body_material(self.material_names, self.material_names.GAUNTLET)
            material_name = gauntlet_material.name
        elif mesh_body_part_name == 'Leather':
            leather_material = self.create_body_material(self.material_names, self.material_names.LEATHER)
            material_name = leather_material.name
        elif mesh_body_part_name == 'Glass':
            glass_material = self.create_body_material(self.material_names, self.material_names.GLASS)
            material_name = glass_material.name
        elif mesh_body_part_name == 'Glass_Eff':
            glass_material = self.create_glass_material(self.material_names, self.material_names.GLASS_EFF)
            if glass_material:
                self.__set_glass_star_cloak_toggle(glass_material, False)
                glass_material.blend_method = 'BLEND'
                glass_material.shadow_method = 'NONE'
                glass_material.show_transparent_back = False
                material_name = glass_material.name
        elif mesh_body_part_name and mesh_body_part_name.startswith(ShaderMaterialNameKeywords.SKILLOBJ):
            skillobj_material = self.create_body_material(self.material_names, self.material_names.SKILLOBJ)
            skillobj_material.name = skillobj_material.name.replace(ShaderMaterialNameKeywords.SKILLOBJ, mesh_body_part_name)
            material_name = skillobj_material.name
        elif mesh_body_part_name and 'Item' in mesh_body_part_name:  # NPCs
            item_material = self.create_body_material(self.material_names, f'{self.material_names.MATERIAL_PREFIX}{mesh_body_part_name}')
            material_name = item_material.name
        elif mesh_body_part_name and ('Screw' in mesh_body_part_name or 'Hat' in mesh_body_part_name):  # Aranaras
            new_material = self.create_body_material(self.material_names, f'{self.material_names.MATERIAL_PREFIX}{mesh_body_part_name}')
            material_name = new_material.name
        elif mesh_body_part_name and 'Others' in mesh_body_part_name:  # NPCs, Frem Penguins
            new_material = self.create_body_material(self.material_names, f'{self.material_names.MATERIAL_PREFIX}{mesh_body_part_name}')
            material_name = new_material.name
        return material_name

    def __clone_material_and_rename(self, material_slot, mesh_body_part_name_template, mesh_body_part_name):
        new_material = bpy.data.materials.get(mesh_body_part_name_template).copy()
        new_material.name = f'{self.material_names.MATERIAL_PREFIX}{mesh_body_part_name}'
        new_material.use_fake_user = True

        material_slot.material = new_material
        return new_material

    def __set_glass_star_cloak_toggle(self, material, value):
        vfx_shader_node = material.node_tree.nodes.get(self.shader_node_names.VFX_SHADER)
        vfx_shader_node.inputs.get(self.shader_node_names.TOGGLE_GLASS_STAR_CLOAK).default_value = value

    def __set_star_cloak_type(self, material, original_material_name):
        for star_cloak_type in StarCloakTypes._member_names_:
            if star_cloak_type.lower() in original_material_name.lower():
                vfx_shader_node = material.node_tree.nodes.get(self.shader_node_names.VFX_SHADER)
                vfx_shader_node.inputs.get(self.shader_node_names.STAR_CLOAK_TYPE).default_value = getattr(StarCloakTypes, star_cloak_type).value

    def create_body_material(self, shader_material_names: ShaderMaterialNames, material_name):
        body_material = bpy.data.materials.get(material_name)
        if not body_material:
            body_material = bpy.data.materials.get(shader_material_names.BODY).copy()
            body_material.name = material_name
            body_material.use_fake_user = True
        return body_material

    def create_hair_material(self, shader_material_names: ShaderMaterialNames, material_name):
        hair_material = bpy.data.materials.get(material_name)
        if not hair_material:
            hair_material = bpy.data.materials.get(shader_material_names.HAIR).copy()
            hair_material.name = material_name
            hair_material.use_fake_user = True
        return hair_material

    def create_glass_material(self, shader_material_names: ShaderMaterialNames, material_name):
        glass_material = bpy.data.materials.get(material_name)
        vfx_template_material = bpy.data.materials.get(shader_material_names.VFX)
        if vfx_template_material and not glass_material:
            glass_material = vfx_template_material.copy()
            glass_material.name = material_name
            glass_material.use_fake_user = True
        return glass_material

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

    def __init__(self, blender_operator, context, material_names: ShaderMaterialNames):
        self.blender_operator: Operator = blender_operator
        self.context: Context = context
        self.shader_material_names = material_names

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
                    body_material = self.create_body_material(mesh, self.shader_material_names.BODY)
                    material_name = body_material.name
                elif mesh_body_part_name == 'Body1':  # for StellarToon
                    body_material = self.create_body_material(mesh, self.shader_material_names.BODY1)
                    material_name = body_material.name
                elif mesh_body_part_name == 'Body2':  # for StellarToon
                    body_material = self.create_body_material(mesh, self.shader_material_names.BODY2)
                    material_name = body_material.name
                elif mesh_body_part_name == 'Body3':
                    body_material = self.create_body_material(mesh, self.shader_material_names.BODY3)
                    material_name = body_material.name
                elif mesh_body_part_name ==  'Body_Trans' or mesh_body_part_name == 'Mat_Trans':
                    body_material = self.create_body_trans_material(mesh, self.shader_material_names.BODY_TRANS) 
                    mesh_body_part_name = 'Body_Trans'
                    material_name = body_material.name
                elif mesh_body_part_name ==  'Body2_Trans':
                    body_material = self.create_body_trans_material(mesh, self.shader_material_names.BODY2_TRANS) 
                    material_name = body_material.name
                elif 'Coat' in mesh_body_part_name:
                    body_material = self.create_body_material(mesh, self.shader_material_names.COAT)
                    material_name = body_material.name
                elif 'Weapon' in mesh_body_part_name:
                    weapon_material = self.create_weapon_materials(mesh_body_part_name)
                    material_name = weapon_material.name
                elif 'Handbag' in mesh_body_part_name:
                    handbag_material = self.create_weapon_materials(mesh_body_part_name)
                    material_name = handbag_material.name
                elif 'Kendama' in mesh_body_part_name:
                    handbag_material = self.create_weapon_materials(mesh_body_part_name)
                    material_name = handbag_material.name
                else:  # Fallback, best guess attempt by creating a Body-type material for the unknown material body part
                    material_name = f'{self.shader_material_names.MATERIAL_PREFIX}{mesh_body_part_name}'
                    self.create_body_material(mesh, material_name)

                honkai_star_rail_material = bpy.data.materials.get(
                    f'{self.shader_material_names.MATERIAL_PREFIX}{mesh_body_part_name}'
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
        if material_name.endswith('_S') or material_name.endswith('_D'):
            return material_name.split('_')[-2]
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
            'Mat_Trans',
            'Face',
            'EyeShadow',
            'Weapon_Trans',
            'Body',  # Important this is last in the list because it could interfere with Body1 and Body2
        ]

        for expected_body_part_name in EXPECTED_BODY_PART_NAMES:
            if expected_body_part_name in material_name:
                return expected_body_part_name

    def create_body_material(self, mesh, material_name):
        body_material = bpy.data.materials.get(material_name)
        if not body_material:
            body_material = bpy.data.materials.get(self.shader_material_names.BODY1).copy()
            body_material.name = material_name
            body_material.use_fake_user = True
        return body_material

    def create_body_trans_material(self, mesh, material_name):
        body_material = bpy.data.materials.get(material_name)
        if not body_material:
            body_material = bpy.data.materials.get(self.shader_material_names.BODY_TRANS).copy()
            body_material.name = material_name
            body_material.use_fake_user = True
        return body_material

    def create_weapon_materials(self, mesh_body_part_name):
        weapon_material_name = \
            f'{self.shader_material_names.MATERIAL_PREFIX}{mesh_body_part_name}' if \
            mesh_body_part_name == 'Weapon01' or \
            mesh_body_part_name == 'Weapon02' or \
            mesh_body_part_name == 'Weapon1' or \
            mesh_body_part_name == 'Weapon_Trans' or \
            mesh_body_part_name == 'Handbag' or \
            mesh_body_part_name == 'Kendama' else \
            f'{self.shader_material_names.WEAPON}'
        weapon_material = bpy.data.materials.get(weapon_material_name)

        if not weapon_material:
            weapon_material = bpy.data.materials.get(f'{self.shader_material_names.WEAPON}').copy()
            weapon_material.name = weapon_material_name
            weapon_material.use_fake_user = True
        return weapon_material


class StellarToonDefaultMaterialReplacer(HonkaiStarRailDefaultMaterialReplacer):
    MESH_IGNORE_LIST = [
        'Face_Mask'
    ]

    ENABLE_TRANSPARENCY = 'Enable Transparency'

    def __init__(self, blender_operator, context, material_names: ShaderMaterialNames):
        self.blender_operator: Operator = blender_operator
        self.context: Context = context
        self.shader_material_names = material_names

    def replace_default_materials(self):
        super().replace_default_materials()

    def create_body_material(self, mesh, material_name):
        body_material = bpy.data.materials.get(material_name)
        if not body_material:
            body_material = bpy.data.materials.get(self.shader_material_names.BASE).copy()
            body_material.name = material_name
            body_material.use_fake_user = True
        return body_material

    def create_body_trans_material(self, mesh, material_name):
        body_material = bpy.data.materials.get(material_name)
        if not body_material:
            body_material = bpy.data.materials.get(self.shader_material_names.BASE).copy()
            body_material.name = material_name
            body_material.use_fake_user = True
        body_material.node_tree.nodes.get(StellarToonShaderNodeNames.BODY_SHADER).inputs.get(self.ENABLE_TRANSPARENCY).default_value = 1.0
        return body_material

    def create_weapon_materials(self, mesh_body_part_name):
        weapon_material = super().create_weapon_materials(mesh_body_part_name)
        if self.shader_material_names.WEAPON_TRANS in weapon_material.name:
            weapon_material.node_tree.nodes.get(StellarToonShaderNodeNames.MAIN_SHADER).inputs.get(self.ENABLE_TRANSPARENCY).default_value = 1.0
        return weapon_material


class PunishingGrayRavenDefaultMaterialReplacer(GameDefaultMaterialReplacer):
    MESH_IGNORE_LIST = []

    def __init__(self, blender_operator, context):
        self.blender_operator: Operator = blender_operator
        self.context: Context = context

    def replace_default_materials(self):
        meshes = [mesh for mesh in bpy.context.scene.objects if mesh.type == 'MESH' and mesh.name not in self.MESH_IGNORE_LIST]

        for mesh in meshes:
            for material_slot in mesh.material_slots:
                material_name = material_slot.name
                material_identifier_service = PunishingGrayRavenMaterialIdentifierService()
                mesh_body_part_name = material_identifier_service.get_body_part_name(material_name) or \
                    self.find_body_part_name(material_name)  # If in different naming schema, fallback to best guess mode
                mesh_body_part_name = \
                    material_identifier_service.get_body_part_name_of_shared_material(material_name) or \
                    mesh_body_part_name
                if 'Face' in mesh_body_part_name:  # 6.Karenina_Ember (material w/ Face in it, but no called just Face)
                    mesh_body_part_name = 'Face'
                if 'OL' in mesh_body_part_name:  # 9S (Generic), Bianca_Veritas (Ink-lit Hermit)
                    mesh_body_part_name = mesh_body_part_name.replace('OL', '')

                if mesh_body_part_name and 'Alpha' not in mesh_body_part_name:
                    material_type = JaredNytsPunishingGrayRavenShaderMaterialNames.HAIR if 'Hair' in mesh_body_part_name else \
                        JaredNytsPunishingGrayRavenShaderMaterialNames.MAIN
                    material_name = f'{JaredNytsPunishingGrayRavenShaderMaterialNames.MATERIAL_PREFIX}{mesh_body_part_name}'
                    self.create_main_material(mesh, material_type, material_name)
                elif mesh_body_part_name and 'Alpha' in mesh_body_part_name:
                    material_name = JaredNytsPunishingGrayRavenShaderMaterialNames.ALPHA
                    mesh_body_part_name = 'Alpha'
                else:
                    self.blender_operator.report({'WARNING'}, f'Ignoring unknown mesh body part in character model: {mesh_body_part_name} / Material: {material_name}')
                    continue

                punishing_gray_raven_material = bpy.data.materials.get(
                    f'{JaredNytsPunishingGrayRavenShaderMaterialNames.MATERIAL_PREFIX}{mesh_body_part_name}'
                )

                if punishing_gray_raven_material:
                    material_slot.material = punishing_gray_raven_material
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
        armature =  [object for object in bpy.data.objects if object.type == 'ARMATURE'][0]
        return material_name.split(armature.name)[-1]

    '''
    Naive Search: Search for body part name in material name
    '''
    def __naive_body_part_name_search(self, material_name):
        EXPECTED_BODY_PART_NAMES = [
            'Alpha',
            'Alpha01',
            'Alpha02',
            'Upper',
            'Down',
            'Eye',
            'Face',
            'Cloth01',
            'Cloth02',
            'Hair01',
            'Hair02',
            'Mantilla',
            'Pipe',
            'Weapon',
            'Cloth',
            'Hair',
            'Body',  # Default to Body last
        ]

        for expected_body_part_name in EXPECTED_BODY_PART_NAMES:
            if expected_body_part_name in material_name:
                return expected_body_part_name

    def create_main_material(self, mesh, material_type: ShaderMaterialNames, material_name):
        body_material = bpy.data.materials.get(material_name)
        if not body_material:
            body_material = bpy.data.materials.get(material_type).copy()
            body_material.name = material_name
            body_material.use_fake_user = True
        return body_material
