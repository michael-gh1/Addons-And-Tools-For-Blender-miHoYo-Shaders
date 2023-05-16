# Author: michael-gh1

import bpy

from abc import ABC, abstractmethod

from setup_wizard.domain.game_types import GameType


class MaterialDataAppliersFactory:
    def create(game_type, material_data_parser, body_part):
        WEAPON_NAME_IDENTIFIER = 'Mat'

        if game_type == GameType.GENSHIN_IMPACT.name:
            # Was tempted to add another check, but holding off for now: file.name.startswith('Equip')
            is_weapon = body_part == WEAPON_NAME_IDENTIFIER

            if is_weapon:
                # V2_WeaponMaterialDataApplier is technically unnecessary for now, does same logic as V2_MaterialDataApplier
                return [
                    V2_WeaponMaterialDataApplier(material_data_parser, 'Body'),  
                    V1_MaterialDataApplier(material_data_parser, 'Body'),
                ]
            else:
                return [
                    V2_MaterialDataApplier(material_data_parser, body_part), 
                    V1_MaterialDataApplier(material_data_parser, body_part),
                ]
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            return [
                V2_HSR_MaterialDataApplier(material_data_parser, body_part), 
            ]
        else:
            raise Exception(f'Unknown {GameType}: {game_type}')


class MaterialDataApplier(ABC):
    outline_mapping = {
        '_OutlineColor': 'Outline Color 1',
        '_OutlineColor2': 'Outline Color 2',
        '_OutlineColor3': 'Outline Color 3',
        '_OutlineColor4': 'Outline Color 4',
        '_OutlineColor5': 'Outline Color 5'
    }

    def __init__(self, material_data_parser, body_part, outlines_node_tree_node_name):
        self.material_data_parser = material_data_parser
        self.body_part = body_part
        self.outlines_node_tree_node_name = outlines_node_tree_node_name
    
    @abstractmethod
    def set_up_mesh_material_data(self):
        raise NotImplementedError()

    def set_up_outline_colors(self):
        outlines_material = bpy.data.materials[f'miHoYo - Genshin {self.body_part} Outlines']
        outlines_shader_node_inputs = outlines_material.node_tree.nodes.get(self.outlines_node_tree_node_name).inputs

        self.apply_material_data(
            self.outline_mapping, 
            outlines_shader_node_inputs,
        )

    def apply_material_data(self, material_mapping, node_inputs):
        for material_json_name, material_node_name in material_mapping.items():
            material_json_value = self.get_value_in_json_parser(self.material_data_parser, material_json_name)

            if material_json_value is None:  # explicitly check for None
                self.__handle_material_value_not_found(material_json_name)
                continue

            node_input = node_inputs.get(material_node_name)
            try:
                node_input.default_value = material_json_value
            except AttributeError as ex:
                print(f'Did not find {material_node_name} in {self.body_part} material using {self} \
                    Falling back to next MaterialDataApplier version')
                raise ex

    def get_value_in_json_parser(self, parser, key):
        try:
            return getattr(parser.m_floats, key)
        except AttributeError:
            return getattr(parser.m_colors, key, None)
        except Exception:
            return None

    def __handle_material_value_not_found(self, material_json_name):
        print(f'Info: Unable to find material data: {material_json_name} in {self.body_part} JSON.')


class V1_MaterialDataApplier(MaterialDataApplier):
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

    global_material_mapping = {
        '_MTUseSpecularRamp': 'Use Specular Ramp?',
        '_FaceBlushColor': 'Blush Color',
    }

    shader_node_tree_node_name = 'Group.001'
    global_node_group_node_name = 'Group Output'
    outlines_node_tree_node_name = 'Group.002'

    def __init__(self, material_data_parser, body_part):
        super().__init__(material_data_parser, body_part, self.outlines_node_tree_node_name)

    def set_up_mesh_material_data(self):
        if self.body_part != 'Face':
            body_part_material = bpy.data.materials[f'miHoYo - Genshin {self.body_part}']
            shader_node_tree_inputs = body_part_material.node_tree.nodes[self.shader_node_tree_node_name].inputs

            super().apply_material_data(
                self.local_material_mapping,
                shader_node_tree_inputs,
            )
            
        # Not sure, should we only apply Global Material Properties from Body .dat file?
        if self.body_part == 'Body':
            global_material_properties_node_inputs = \
                bpy.data.node_groups["GLOBAL MATERIAL PROPERTIES"].nodes[self.global_node_group_node_name].inputs

            super().apply_material_data(
                self.global_material_mapping,
                global_material_properties_node_inputs,
            )


class V2_MaterialDataApplier(MaterialDataApplier):
    local_material_mapping = {
        '_FaceBlushColor': 'Face Blush Color',
        '_FaceBlushStrength': 'Face Blush Strength',
        # '_FaceMapSoftness': 'Face Shadow Softness',  # material data values are either 0.001 or 1E-06
        "_EmissionColor_MHY": "Emission Tint",
        "_UseMaterial2": 'Use Material 2',
        "_UseMaterial3": 'Use Material 3',
        "_UseMaterial4": 'Use Material 4',
        "_UseMaterial5": 'Use Material 5',
        '_UseBumpMap': 'Use Normal Map',
        '_ShadowRampWidth': 'Shadow Ramp Width',
        "_ShadowTransitionRange": 'Shadow Transition Range',
        "_ShadowTransitionRange2": 'Shadow Transition Range 2',
        "_ShadowTransitionRange3": 'Shadow Transition Range 3',
        "_ShadowTransitionRange4": 'Shadow Transition Range 4',
        "_ShadowTransitionRange5": 'Shadow Transition Range 5',
        "_ShadowTransitionSoftness": 'Shadow Transition Softness',
        "_ShadowTransitionSoftness2": 'Shadow Transition Softness 2',
        "_ShadowTransitionSoftness3": 'Shadow Transition Softness 3',
        "_ShadowTransitionSoftness4": 'Shadow Transition Softness 4',
        "_ShadowTransitionSoftness5": 'Shadow Transition Softness 5',
        '_MTMapBrightness': 'Metallic Matcap Brightness',
        '_MTMapTileScale': 'Metallic Matcap Tile Scale',
        '_MTMapLightColor': 'Metallic Matcap Light Color',
        '_MTMapDarkColor': 'Metallic Matcap Dark Color',
        '_MTShadowMultiColor': 'Metallic Matcap Shadow Multiply Color',
        '_Shininess': 'Shininess',
        '_Shininess2': 'Shininess 2',
        '_Shininess3': 'Shininess 3',
        '_Shininess4': 'Shininess 4',
        '_Shininess5': 'Shininess 5',
        '_SpecMulti': 'Specular Multiplier',
        '_SpecMulti2': 'Specular Multiplier 2',
        '_SpecMulti3': 'Specular Multiplier 3',
        '_SpecMulti4': 'Specular Multiplier 4',
        '_SpecMulti5': 'Specular Multiplier 5',
        '_SpecularColor': 'Specular Color',
        '_MTShininess': 'Metallic Specular Shininess',
        '_MTSpecularScale': 'Metallic Specular Scale',
        '_MTSpecularAttenInShadow': 'Metallic Specular Attenuation',
        '_MTSharpLayerOffset': 'Metallic Specular Sharp Layer Offset',
        '_MTSpecularColor': 'MT Specular Color',
        '_MTSharpLayerColor': 'MT Sharp Layer Color',
        '_MTUseSpecularRamp': 'Use Specular Ramp',
    }

    shader_node_tree_node_name = 'Group.006'
    outlines_node_tree_node_name = 'Group.006'

    def __init__(self, material_data_parser, body_part):
        super().__init__(material_data_parser, body_part, self.outlines_node_tree_node_name)

    def set_up_mesh_material_data(self):
        body_part_material = bpy.data.materials[f'miHoYo - Genshin {self.body_part}']
        shader_node_tree_inputs = body_part_material.node_tree.nodes[self.shader_node_tree_node_name].inputs

        super().apply_material_data(
            self.local_material_mapping,
            shader_node_tree_inputs,
        )
        self.set_up_alpha_options_material_data(shader_node_tree_inputs)

    # We should consider abstracting this logic if we need to add additional logic for other material data values
    def set_up_alpha_options_material_data(self, node_inputs):
        _MainTexAlphaUse_name = '_MainTexAlphaUse'
        _MainTexAlphaUse_mapping = {
            0: {
                "Use Alpha": 0,
                "0 = Emission, 1 = Transparency": 0
            },
            1: {
                "Use Alpha": 1,
                "0 = Emission, 1 = Transparency": 1
            },
            2: {
                "Use Alpha": 1,
                "0 = Emission, 1 = Transparency": 0
            },
            3: {},
        }

        _MainTexAlphaUse_value = int(self.get_value_in_json_parser(self.material_data_parser, _MainTexAlphaUse_name))
        _MainTexAlphaUse_material_node_dict = _MainTexAlphaUse_mapping.get(_MainTexAlphaUse_value)

        if _MainTexAlphaUse_value is None:  # explicitly check for None
            self.__handle_material_value_not_found(_MainTexAlphaUse_name)
            return

        for material_node_name, material_json_value in _MainTexAlphaUse_material_node_dict.items():
            node_input = node_inputs.get(material_node_name)
            try:
                node_input.default_value = material_json_value
            except AttributeError as ex:
                print(f'Did not find {material_node_name} in {self.body_part} material using {self} \
                    Falling back to next MaterialDataApplier version')
                raise ex


class V2_WeaponMaterialDataApplier(V2_MaterialDataApplier):
    def __init__(self, material_data_parser, body_part):
        super().__init__(material_data_parser, body_part)

    def set_up_mesh_material_data(self):
        weapon_material = bpy.data.materials[f'miHoYo - Genshin {self.body_part}']
        shader_node_tree_inputs = weapon_material.node_tree.nodes[self.shader_node_tree_node_name].inputs

        super().apply_material_data(
            self.local_material_mapping,
            shader_node_tree_inputs,
        )


class V2_HSR_MaterialDataApplier(V2_MaterialDataApplier):
    outline_mapping = {
        '_OutlineColor0': 'Outline Color 1',
        '_OutlineColor1': 'Outline Color 2',
        '_OutlineColor2': 'Outline Color 3',
        '_OutlineColor3': 'Outline Color 4',
        '_OutlineColor4': 'Outline Color 5',
        '_OutlineColor5': 'Outline Color 6',
        '_OutlineColor6': 'Outline Color 7',
        '_OutlineColor7': 'Outline Color 8',
    }

    face_outline_mapping = {
        '_OutlineColor': 'Outline Color 1',
    }

    local_material_mapping = {
        '_MTSharpLayerOffset': 'Metallic Specular Sharp Layer Offset',
        # '_SpecularColor': 'Specular Color',  # GI - RGBA | HSR - Float
    }

    def __init__(self, material_data_parser, body_part):
        super().__init__(material_data_parser, body_part)

        if self.body_part == 'Face':
            self.outline_mapping = self.face_outline_mapping

    def set_up_mesh_material_data(self):
        body_part_material = bpy.data.materials[f'miHoYo - Genshin {self.body_part}']
        shader_node_tree_inputs = body_part_material.node_tree.nodes[self.shader_node_tree_node_name].inputs

        super().apply_material_data(
            self.local_material_mapping,
            shader_node_tree_inputs,
        )
