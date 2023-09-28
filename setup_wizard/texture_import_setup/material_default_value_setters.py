# Author: michael-gh1

import bpy

from abc import abstractmethod

from setup_wizard.domain.shader_node_names import V2_GenshinShaderNodeNames, V3_GenshinShaderNodeNames
from setup_wizard.domain.shader_identifier_service import GenshinImpactShaders, ShaderIdentifierService, ShaderIdentifierServiceFactory
from setup_wizard.domain.shader_material_names import ShaderMaterialNames, V2_FestivityGenshinImpactMaterialNames, \
    V3_BonnyFestivityGenshinImpactMaterialNames
from setup_wizard.domain.shader_node_names import ShaderNodeNames

from setup_wizard.domain.game_types import GameType


class MaterialDefaultValueSetterFactory:
    def create(game_type: GameType):
        shader_identifier_service: ShaderIdentifierService = ShaderIdentifierServiceFactory.create(game_type)

        if game_type == GameType.GENSHIN_IMPACT.name:
            if shader_identifier_service.identify_shader(bpy.data.materials, bpy.data.node_groups) is GenshinImpactShaders.V3_GENSHIN_IMPACT_SHADER:
                return GenshinImpactMaterialDefaultValueSetter(V3_BonnyFestivityGenshinImpactMaterialNames, V3_GenshinShaderNodeNames)
            else:
                return GenshinImpactMaterialDefaultValueSetter(V2_FestivityGenshinImpactMaterialNames, V2_GenshinShaderNodeNames)
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            return HonkaiStarRailMaterialDefaultValueSetter()
        else:
            raise Exception(f'Unknown {GameType}: {game_type}')


class MaterialDefaultValueSetter:
    def __init__(self, material_names: ShaderMaterialNames, shader_node_names: ShaderNodeNames):
        self.material_names = material_names
        self.shader_node_names = shader_node_names

    @abstractmethod
    def set_default_values(self):
        raise NotImplementedError()

    def set_up_shadow_ramp_default_value(self, body_part, material, default_missing=0, default_exists=1):
        shadow_ramp_node_group = bpy.data.node_groups.get(f'{body_part} Shadow Ramp')
        shadow_ramp_node = shadow_ramp_node_group.nodes.get(f'{body_part}_Shadow_Ramp')

        if not shadow_ramp_node_group or not shadow_ramp_node:
            return

        default_value = default_missing if not shadow_ramp_node.image else default_exists

        body_shader_node = material.node_tree.nodes.get(self.shader_node_names.BODY_SHADER)
        if body_shader_node:
            shader_use_shadow_ramp_input = body_shader_node.inputs.get(self.shader_node_names.USE_SHADOW_RAMP)
            if shader_use_shadow_ramp_input:
                shader_use_shadow_ramp_input.default_value = default_value

    def set_up_lightmap_ao_default_value(self, body_part, material, default_missing=0, default_exists=1):
        lightmap_uv0 = material.node_tree.nodes.get(f'{body_part}_Lightmap_UV0')
        lightmap_uv1 = material.node_tree.nodes.get(f'{body_part}_Lightmap_UV1')

        if not lightmap_uv0 or not lightmap_uv1:
            return

        default_value = default_missing if not lightmap_uv0.image or not lightmap_uv1.image else default_exists

        body_shader_node = material.node_tree.nodes.get(self.shader_node_names.BODY_SHADER)
        if body_shader_node:
            shader_use_lightmap_ao_input = body_shader_node.inputs.get(self.shader_node_names.USE_LIGHTMAP_AO)
            if shader_use_lightmap_ao_input:
                shader_use_lightmap_ao_input.default_value = default_value


class GenshinImpactMaterialDefaultValueSetter(MaterialDefaultValueSetter):
    def __init__(self, material_names: ShaderMaterialNames, shader_node_names: ShaderNodeNames) -> None:
        super().__init__(material_names, shader_node_names)

    def set_default_values(self):
        materials_to_check = [material for material in bpy.data.materials if \
                              material.name.startswith(self.material_names.MATERIAL_PREFIX)]

        for material in materials_to_check:
            # The reason we try both is so that we don't need to explicitly list out materials
            # Basically it's to futureproof Setup Wizard when future characters have different material names
            self.set_up_shadow_ramp_default_value('Body', material)
            self.set_up_shadow_ramp_default_value('Hair', material)

            self.set_up_lightmap_ao_default_value('Body', material)
            self.set_up_lightmap_ao_default_value('Hair', material)


class HonkaiStarRailMaterialDefaultValueSetter(MaterialDefaultValueSetter):
    def __init__(self) -> None:
        return

    def set_default_values(self):
        return
