# Author: michael-gh1

import bpy

from abc import ABC, abstractmethod
from bpy.types import Material

from setup_wizard.domain.character_types import CharacterType
from setup_wizard.domain.game_types import GameType
from setup_wizard.domain.outline_material_data import OutlineMaterialGroup
from setup_wizard.domain.shader_material_names import V3_BonnyFestivityGenshinImpactMaterialNames


class MaterialDataAppliersFactory:
    def create(game_type, material_data_parser, outline_material_group: OutlineMaterialGroup, character_type: CharacterType):
        if game_type == GameType.GENSHIN_IMPACT.name:
            if character_type is CharacterType.GI_EQUIPMENT:
                # V2_WeaponMaterialDataApplier is technically unnecessary for now, does same logic as V2_MaterialDataApplier
                return [
                    V2_WeaponMaterialDataApplier(material_data_parser, outline_material_group),  
                    V1_MaterialDataApplier(material_data_parser, outline_material_group),
                ]
            else:
                return [
                    V3_MaterialDataApplier(material_data_parser, outline_material_group),
                    V2_MaterialDataApplier(material_data_parser, outline_material_group), 
                    V1_MaterialDataApplier(material_data_parser, outline_material_group),
                ]
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            return [
                StellarToon_MaterialDataApplier(material_data_parser, outline_material_group),
                V2_HSR_MaterialDataApplier(material_data_parser, outline_material_group),
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

    def __init__(self, material_data_parser, outline_material_group: OutlineMaterialGroup, outlines_node_tree_node_name):
        self.material_data_parser = material_data_parser
        self.material = outline_material_group.material
        self.outline_material = outline_material_group.outlines_material
        self.outlines_node_tree_node_name = outlines_node_tree_node_name
    
    @abstractmethod
    def set_up_mesh_material_data(self):
        raise NotImplementedError()

    def set_up_outline_colors(self):
        outlines_shader_node_inputs = self.outline_material.node_tree.nodes.get(self.outlines_node_tree_node_name).inputs

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

            # StellarToon: handle two "Stockings Color" inputs in same shader node
            if material_node_name == 'Stockings Color':
                stockings_color_inputs = [node_input for node_input in node_inputs if node_input.name == 'Stockings Color']
                if len(stockings_color_inputs) > 1:
                    node_input = stockings_color_inputs[1]
            else:
                node_input = node_inputs.get(material_node_name)
            try:
                # Convert to sRGB to Hex to RGB for Nya222 Shader 
                # Currently it doesn't do a conversion from gamma-corrected RGB to linear color space
                if type(self) is V2_HSR_MaterialDataApplier and type(material_json_value) is tuple:
                    material_json_value = self.convert_color_srgb_to_hex_to_rgb(material_json_value)
                node_input.default_value = material_json_value
            except AttributeError as ex:
                print(f'Did not find {material_node_name} in {self.material.name}/{self.outline_material.name} material using {self} \
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
        print(f'Info: Unable to find material data: {material_json_name} in selected JSON.')

    def convert_color_srgb_to_hex_to_rgb(self, material_json_value):
        r = material_json_value[0]
        g = material_json_value[1]
        b = material_json_value[2]
        a = material_json_value[3]

        hex_color = self.srgb_to_hex(r, g, b)
        r, g, b = self.hex_to_linear_rgb(hex_color)

        return (r, g, b, a)

    @staticmethod
    def hex_to_linear(val):
        val = int(val, 16) / 255.0
        if val <= 0.04045:
            return val / 12.92
        else:
            return ((val + 0.055) / 1.055) ** 2.4

    @staticmethod
    def hex_to_linear_rgb(hex_color):
        r = MaterialDataApplier.hex_to_linear(hex_color[1:3])
        g = MaterialDataApplier.hex_to_linear(hex_color[3:5])
        b = MaterialDataApplier.hex_to_linear(hex_color[5:7])
        return r, g, b

    @staticmethod
    def srgb_to_hex(r, g, b):
        def to_byte(val):
            val = min(max(0, val), 1)
            return int(val * 255)
        
        hex_color = "#{:02X}{:02X}{:02X}".format(to_byte(r), to_byte(g), to_byte(b))
        return hex_color


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

    def __init__(self, material_data_parser, material: Material):
        super().__init__(material_data_parser, material, self.outlines_node_tree_node_name)

    def set_up_mesh_material_data(self):
        if 'Face' not in self.material.name:
            shader_node_tree_inputs = self.material.node_tree.nodes[self.shader_node_tree_node_name].inputs

            super().apply_material_data(
                self.local_material_mapping,
                shader_node_tree_inputs,
            )

        if 'Body' in self.material.name:
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
        '_MetalMaterial': 'Enable Metallics?',
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
        '_CoolShadowMultColor': 'Nighttime Shadow Color',
        '_CoolShadowMultColor2': 'Nighttime Shadow Color 2',
        '_CoolShadowMultColor3': 'Nighttime Shadow Color 3',
        '_CoolShadowMultColor4': 'Nighttime Shadow Color 4',
        '_CoolShadowMultColor5': 'Nighttime Shadow Color 5',
        '_FirstShadowMultColor': 'Daytime Shadow Color',
        '_FirstShadowMultColor2': 'Daytime Shadow Color 2',
        '_FirstShadowMultColor3': 'Daytime Shadow Color 3',
        '_FirstShadowMultColor4': 'Daytime Shadow Color 4',
        '_FirstShadowMultColor5': 'Daytime Shadow Color 5',
        '_UseShadowRamp': 'Use Shadow Ramp',
        '_UseLightMapColorAO': 'Use Lightmap AO',
        '_UseVertexColorAO': 'Use Vertex Color AO',
    }

    shader_node_tree_node_name = 'Group.006'
    outlines_node_tree_node_name = 'Group.006'

    def __init__(self, material_data_parser, outline_material_group: OutlineMaterialGroup, outlines_node_tree_node_name=None):
        if outlines_node_tree_node_name:
            self.outlines_node_tree_node_name = outlines_node_tree_node_name
        super().__init__(material_data_parser, outline_material_group, self.outlines_node_tree_node_name)

    def set_up_mesh_material_data(self):
        base_material_shader_node_tree_inputs = self.material.node_tree.nodes[self.shader_node_tree_node_name].inputs
        outline_material_shader_node_tree_inputs = self.outline_material.node_tree.nodes[self.shader_node_tree_node_name].inputs

        super().apply_material_data(
            self.local_material_mapping,
            base_material_shader_node_tree_inputs,
        )
        self.set_up_alpha_options_material_data(base_material_shader_node_tree_inputs)
        self.set_up_alpha_options_material_data(outline_material_shader_node_tree_inputs, outlines_alpha_only=True)

        super().apply_material_data(
            self.local_material_mapping,
            outline_material_shader_node_tree_inputs
        )

    # We should consider abstracting this logic if we need to add additional logic for other material data values
    def set_up_alpha_options_material_data(self, node_inputs, outlines_alpha_only=False):
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
        elif outlines_alpha_only and _MainTexAlphaUse_value != 1:
            # For outlines ignore 0, 2
            # Only apply material data if it's 1
            return

        for material_node_name, material_json_value in _MainTexAlphaUse_material_node_dict.items():
            node_input = node_inputs.get(material_node_name)
            try:
                node_input.default_value = material_json_value
            except AttributeError as ex:
                print(f'Did not find {material_node_name} in {self.material.name} material using {self} \
                    Skipped.')
                continue  # This used to be raise ex, but we're setting to Continue for NPCs using V3 Shader


class V3_MaterialDataApplier(V2_MaterialDataApplier):
    face_material_mapping = {
        '_FaceBlushColor': 'Face Blush Color',
        '_FaceBlushStrength': 'Face Blush Strength',
        '_FaceMapSoftness': 'Face Shadow Softness',  # material data values are either 0.001 or 1E-06
        '_CoolShadowMultColor': 'Nighttime Shadow Color',  # Teeth
        '_CoolShadowMultColor': 'Nighttime Shadow Color',  # Teeth
        '_CoolShadowMultColor2': 'Nighttime Shadow Color 2',  # Teeth
        '_CoolShadowMultColor3': 'Nighttime Shadow Color 3',  # Teeth
        '_FirstShadowMultColor': 'Daytime Shadow Color',  # Teeth
        '_FirstShadowMultColor2': 'Daytime Shadow Color 2',  # Teeth
        '_FirstShadowMultColor3': 'Daytime Shadow Color 3',  # Teeth
    }

    outline_mapping = {
        "_UseMaterial2": 'Use Material 2',
        "_UseMaterial3": 'Use Material 3',
        "_UseMaterial4": 'Use Material 4',
        "_UseMaterial5": 'Use Material 5',
        '_OutlineColor': 'Outline Color 1',
        '_OutlineColor2': 'Outline Color 2',
        '_OutlineColor3': 'Outline Color 3',
        '_OutlineColor4': 'Outline Color 4',
        '_OutlineColor5': 'Outline Color 5'
    }

    local_material_mapping = {
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
        '_MetalMaterial': 'Enable Metallics?',
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
        '_CoolShadowMultColor': 'Nighttime Shadow Color',
        '_CoolShadowMultColor2': 'Nighttime Shadow Color 2',
        '_CoolShadowMultColor3': 'Nighttime Shadow Color 3',
        '_CoolShadowMultColor4': 'Nighttime Shadow Color 4',
        '_CoolShadowMultColor5': 'Nighttime Shadow Color 5',
        '_FirstShadowMultColor': 'Daytime Shadow Color',
        '_FirstShadowMultColor2': 'Daytime Shadow Color 2',
        '_FirstShadowMultColor3': 'Daytime Shadow Color 3',
        '_FirstShadowMultColor4': 'Daytime Shadow Color 4',
        '_FirstShadowMultColor5': 'Daytime Shadow Color 5',
        '_UseShadowRamp': 'Use Shadow Ramp',
        '_UseLightMapColorAO': 'Use Lightmap AO',
        '_UseVertexColorAO': 'Use Vertex Color AO',
        '_MainTexAlphaCutoff': 'Transparency Cutoff',
    }

    body_shader_node_tree_node_name = 'Body Shader'
    face_shader_node_tree_node_name = 'Face Shader'
    outlines_node_tree_node_name = 'Outlines'

    def __init__(self, material_data_parser, outline_material_group: OutlineMaterialGroup):
        super().__init__(material_data_parser, outline_material_group, self.outlines_node_tree_node_name)
        self.shader_node_tree_node_name = self.face_shader_node_tree_node_name if 'Face' in self.material.name else \
            self.body_shader_node_tree_node_name

    def set_up_mesh_material_data(self):
        base_material_shader_node_tree_inputs = self.material.node_tree.nodes[self.shader_node_tree_node_name].inputs
        outline_material_shader_node_tree_inputs = self.outline_material.node_tree.nodes[self.outlines_node_tree_node_name].inputs

        if self.material.name == V3_BonnyFestivityGenshinImpactMaterialNames.FACE:
            super().apply_material_data(
                self.face_material_mapping,
                base_material_shader_node_tree_inputs,
            )
        else:
            super().apply_material_data(
                self.local_material_mapping,
                base_material_shader_node_tree_inputs,
            )
        self.set_up_alpha_options_material_data(base_material_shader_node_tree_inputs)
        self.set_up_alpha_options_material_data(outline_material_shader_node_tree_inputs, outlines_alpha_only=True)

        super().apply_material_data(
            self.outline_mapping,
            outline_material_shader_node_tree_inputs
        )


class V2_WeaponMaterialDataApplier(V2_MaterialDataApplier):
    def __init__(self, material_data_parser, outline_material_group: OutlineMaterialGroup):
        super().__init__(material_data_parser, outline_material_group)

    def set_up_mesh_material_data(self):
        weapon_material = self.material
        shader_node_tree_inputs = weapon_material.node_tree.nodes[self.shader_node_tree_node_name].inputs

        super().apply_material_data(
            self.local_material_mapping,
            shader_node_tree_inputs,
        )


class V2_HSR_MaterialDataApplier(V2_MaterialDataApplier):
    outline_mapping = {
        '_OutlineColor0': 'Outline Color 0',
        '_OutlineColor1': 'Outline Color 1',
        '_OutlineColor2': 'Outline Color 2',
        '_OutlineColor3': 'Outline Color 3',
        '_OutlineColor4': 'Outline Color 4',
        '_OutlineColor5': 'Outline Color 5',
        '_OutlineColor6': 'Outline Color 6',
        '_OutlineColor7': 'Outline Color 7',
    }

    face_outline_mapping = {
        '_OutlineColor': 'Outline Color 0',
    }

    local_material_mapping = {
        '_EnableAlphaCutoff': 'Use Alpha',
        '_SpecularColor0': '_SpecularColor0',
        '_SpecularColor1': '_SpecularColor1',
        '_SpecularColor2': '_SpecularColor2',
        '_SpecularColor3': '_SpecularColor3',
        '_SpecularColor4': '_SpecularColor4',
        '_SpecularColor5': '_SpecularColor5',
        '_SpecularColor6': '_SpecularColor6',
        '_SpecularColor7': '_SpecularColor7',
        '_SpecularRoughness0': '_SpecularRoughness0',
        '_SpecularRoughness1': '_SpecularRoughness1',
        '_SpecularRoughness2': '_SpecularRoughness2',
        '_SpecularRoughness3': '_SpecularRoughness3',
        '_SpecularRoughness4': '_SpecularRoughness4',
        '_SpecularRoughness5': '_SpecularRoughness5',
        '_SpecularRoughness6': '_SpecularRoughness6',
        '_SpecularRoughness7': '_SpecularRoughness7',
        '_SpecularIntensity0': '_SpecularIntensity0',
        '_SpecularIntensity1': '_SpecularIntensity1',
        '_SpecularIntensity2': '_SpecularIntensity2',
        '_SpecularIntensity3': '_SpecularIntensity3',
        '_SpecularIntensity4': '_SpecularIntensity4',
        '_SpecularIntensity5': '_SpecularIntensity5',
        '_SpecularIntensity6': '_SpecularIntensity6',
        '_SpecularIntensity7': '_SpecularIntensity7',
        '_SpecularShininess0': '_SpecularShininess0',
        '_SpecularShininess1': '_SpecularShininess1',
        '_SpecularShininess2': '_SpecularShininess2',
        '_SpecularShininess3': '_SpecularShininess3',
        '_SpecularShininess4': '_SpecularShininess4',
        '_SpecularShininess5': '_SpecularShininess5',
        '_SpecularShininess6': '_SpecularShininess6',
        '_SpecularShininess7': '_SpecularShininess7',
        '_StockDarkcolor': '_StockDarkcolor',
        '_Stockcolor': '_StockColor',
        '_StockRoughness': '_StockRoughness',
        '_Stockpower': '_Stockpower',
        '_Stockpower1': '_Stockpower1',
        '_StockDarkWidth': '_StockDarkWidth',
        '_StockSP': '_StockSP',
    }

    shader_node_tree_node_name = 'Group'
    outlines_node_tree_node_name = 'グループ.008'

    def __init__(self, material_data_parser, outline_material_group: OutlineMaterialGroup):
        super().__init__(material_data_parser, outline_material_group)

        if 'Face' in self.material.name:
            self.outline_mapping = self.face_outline_mapping

    def set_up_mesh_material_data(self):
        shader_node_tree_inputs = self.material.node_tree.nodes[self.shader_node_tree_node_name].inputs

        super().apply_material_data(
            self.local_material_mapping,
            shader_node_tree_inputs,
        )


class StellarToon_MaterialDataApplier(V2_MaterialDataApplier):
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

    hair_material_mapping = {
        '_SpecularColor0': 'Specular Color',
        '_SpecularRoughness0': 'Specular Roughness',
        '_SpecularIntensity0': 'Specular Intensity',
        '_SpecularShininess0': 'Specular Shininess',
    }

    face_material_mapping = {
        '_EyeShadowColor': 'Eye Shadow Color',
        '_ShadowColor': 'Warm Shadow Color',
        '_DarkColor': 'Cool Shadow Color',
        '_NoseLinePower': 'Nose Line Power',
        '_NoseLineColor': 'Nose Line Color',
    }

    local_material_mapping = {
        '_SpecularColor0': 'Specular Color 1',
        '_SpecularColor1': 'Specular Color 2',
        '_SpecularColor2': 'Specular Color 3',
        '_SpecularColor3': 'Specular Color 4',
        '_SpecularColor4': 'Specular Color 5',
        '_SpecularColor5': 'Specular Color 6',
        '_SpecularColor6': 'Specular Color 7',
        '_SpecularColor7': 'Specular Color 8',
        '_SpecularRoughness0': 'Specular Roughness 1',
        '_SpecularRoughness1': 'Specular Roughness 2',
        '_SpecularRoughness2': 'Specular Roughness 3',
        '_SpecularRoughness3': 'Specular Roughness 4',
        '_SpecularRoughness4': 'Specular Roughness 5',
        '_SpecularRoughness5': 'Specular Roughness 6',
        '_SpecularRoughness6': 'Specular Roughness 7',
        '_SpecularRoughness7': 'Specular Roughness 8',
        '_SpecularIntensity0': 'Specular Intensity 1',
        '_SpecularIntensity1': 'Specular Intensity 2',
        '_SpecularIntensity2': 'Specular Intensity 3',
        '_SpecularIntensity3': 'Specular Intensity 4',
        '_SpecularIntensity4': 'Specular Intensity 5',
        '_SpecularIntensity5': 'Specular Intensity 6',
        '_SpecularIntensity6': 'Specular Intensity 7',
        '_SpecularIntensity7': 'Specular Intensity 8',
        '_SpecularShininess0': 'Specular Shininess 1',
        '_SpecularShininess1': 'Specular Shininess 2',
        '_SpecularShininess2': 'Specular Shininess 3',
        '_SpecularShininess3': 'Specular Shininess 4',
        '_SpecularShininess4': 'Specular Shininess 5',
        '_SpecularShininess5': 'Specular Shininess 6',
        '_SpecularShininess6': 'Specular Shininess 7',
        '_SpecularShininess7': 'Specular Shininess 8',
        '_Stockcolor': 'Stockings Color',
        '_StockDarkcolor': 'Stockings Darkened Color',
        '_StockDarkWidth': 'Stockings Rim Width',
        '_Stockpower': 'Stockings Power',
        '_Stockpower1': 'Stockings Lighted Width',
        '_StockSP': 'Stockings Lighted Intensity',
        '_StockRoughness': 'Stockings Texture Intensity',
        '_Stockthickness': 'Stockings Thickness',
    }

    shader_node_tree_node_name = 'Group.006'
    outlines_node_tree_node_name = 'Group.006'

    def __init__(self, material_data_parser, outline_material_group: OutlineMaterialGroup):
        super().__init__(material_data_parser, outline_material_group)

        if 'Face' in self.material.name:
            self.outline_mapping = self.face_outline_mapping

    def set_up_mesh_material_data(self):
        shader_node_tree_inputs = self.material.node_tree.nodes[self.shader_node_tree_node_name].inputs

        if 'Hair' in self.material.name:
            super().apply_material_data(
                self.hair_material_mapping,
                shader_node_tree_inputs,
            )
        elif 'Face' in self.material.name:
            super().apply_material_data(
                self.face_material_mapping,
                shader_node_tree_inputs,
            )
            self.material.node_tree.nodes.get(self.shader_node_tree_node_name).inputs.get('Enable Emission').default_value = 1.0
        else:
            super().apply_material_data(
                self.local_material_mapping,
                shader_node_tree_inputs,
            )

