
import bpy

from abc import ABC, abstractmethod
from bpy.types import Context, Operator

from setup_wizard.import_order import get_actual_material_name_for_dress
from setup_wizard.domain.game_types import GameType


class GameDefaultMaterialReplacer(ABC):
    @abstractmethod
    def replace_default_materials(self):
        raise NotImplementedError()


class GameDefaultMaterialReplacerFactory:
    def create(game_type: GameType, blender_operator: Operator, context: Context):
        # Because we inject the GameType via StringProperty, we need to compare using the Enum's name (a string)
        if game_type == GameType.GENSHIN_IMPACT.name:
            return GenshinImpactDefaultMaterialReplacer(blender_operator, context)
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            return HonkaiStarRailDefaultMaterialReplacer(blender_operator, context)
        else:
            raise Exception(f'Unknown {GameType}: {game_type}')


class GenshinImpactDefaultMaterialReplacer(GameDefaultMaterialReplacer):
    def __init__(self, blender_operator, context):
        self.blender_operator: Operator = blender_operator
        self.context: Context = context

    def replace_default_materials(self):
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
                    self.blender_operator.report({'INFO'}, 'Dress detected on character model!')

                    actual_material_for_dress = get_actual_material_name_for_dress(material_name)
                    if actual_material_for_dress == 'Cloak':
                        # short-circuit, no shader available for 'Cloak' so do nothing (Paimon)
                        continue

                    genshin_material = self.__clone_material_and_rename(
                        material_slot, 
                        f'miHoYo - Genshin {actual_material_for_dress}', 
                        mesh_body_part_name
                    )
                    self.blender_operator.report({'INFO'}, f'Replaced material: "{material_name}" with "{actual_material_for_dress}"')
                elif material_name == 'miHoYoDiffuse':
                    material_slot.material = bpy.data.materials.get(f'miHoYo - Genshin Body')
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

    def __clone_material_and_rename(self, material_slot, mesh_body_part_name_template, mesh_body_part_name):
        new_material = bpy.data.materials.get(mesh_body_part_name_template).copy()
        new_material.name = f'miHoYo - Genshin {mesh_body_part_name}'
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
    def __init__(self, blender_operator, context):
        self.blender_operator: Operator = blender_operator
        self.context: Context = context

    def replace_default_materials(self):
        meshes = [mesh for mesh in bpy.context.scene.objects if mesh.type == 'MESH']

        for mesh in meshes:
            for material_slot in mesh.material_slots:
                material_name = material_slot.name
                mesh_body_part_name = material_name.split('_')[-1]

                # Hacky-solution, suggest that the shader change name to "EyeShadow"
                # Otherwise "EyeShadow" doesn't get replaced since we have "Eye Shadow" and not "EyeShadow"
                if mesh_body_part_name == 'EyeShadow':
                    mesh_body_part_name = 'Eye Shadow'

                # Another hacky-solution, some characters only have a "Body" material, but the shader materials
                # only have Body1, Body2 and Body_A. Should request Shader to have a "Body" material
                # Some characters have a mismatch between Texture and Material Data too... (Body_Color_A and Body)
                # Checklist:
                # 1. Materials
                # 2. Textures
                # 3. Material Data
                # The best fix would be to create a "Body" material via code in case the shader is updated to have the same
                if mesh_body_part_name == 'Body':
                    body_material = bpy.data.materials.get('miHoYo - Genshin Body1').copy()
                    body_material.name = 'miHoYo - Genshin Body'
                    body_material.use_fake_user = True
                    mesh.material_slots.get(material_name).material = body_material
                    material_name = material_slot.name

                honkai_star_rail_material = bpy.data.materials.get(f'miHoYo - Genshin {mesh_body_part_name}')

                if honkai_star_rail_material:
                    material_slot.material = honkai_star_rail_material
                else:
                    self.blender_operator.report({'WARNING'}, f'Ignoring unknown mesh body part in character model: {mesh_body_part_name} / Material: {material_name}')
                    continue
        self.blender_operator.report({'INFO'}, 'Replaced default materials with Genshin shader materials...')
