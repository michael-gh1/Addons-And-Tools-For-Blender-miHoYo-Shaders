# Author: michael-gh1

import bpy

from abc import abstractmethod

from setup_wizard.domain.shader_node_names import V2_GenshinShaderNodeNames, V3_GenshinShaderNodeNames, V4_PrimoToonShaderNodeNames
from setup_wizard.domain.shader_identifier_service import GenshinImpactShaders, ShaderIdentifierService, ShaderIdentifierServiceFactory
from setup_wizard.domain.shader_material_names import ShaderMaterialNames, V2_FestivityGenshinImpactMaterialNames, \
    V3_BonnyFestivityGenshinImpactMaterialNames, V4_PrimoToonGenshinImpactMaterialNames
from setup_wizard.domain.shader_node_names import ShaderNodeNames

from setup_wizard.domain.game_types import GameType
from setup_wizard.texture_import_setup.texture_node_names import V4_GenshinImpactTextureNodeNames


class MaterialDefaultValueSetterFactory:
    def create(game_type: GameType):
        shader_identifier_service: ShaderIdentifierService = ShaderIdentifierServiceFactory.create(game_type)

        if game_type == GameType.GENSHIN_IMPACT.name:
            shader = shader_identifier_service.identify_shader(bpy.data.materials, bpy.data.node_groups)
            if shader is GenshinImpactShaders.V1_GENSHIN_IMPACT_SHADER or shader is GenshinImpactShaders.V2_GENSHIN_IMPACT_SHADER:
                return GenshinImpactMaterialDefaultValueSetter(V2_FestivityGenshinImpactMaterialNames, V2_GenshinShaderNodeNames)
            elif shader is GenshinImpactShaders.V3_GENSHIN_IMPACT_SHADER:
                return GenshinImpactMaterialDefaultValueSetter(V3_BonnyFestivityGenshinImpactMaterialNames, V3_GenshinShaderNodeNames)
            else:
                return GenshinImpactMaterialDefaultValueSetter(V4_PrimoToonGenshinImpactMaterialNames, V4_PrimoToonShaderNodeNames)
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            return HonkaiStarRailMaterialDefaultValueSetter()
        elif game_type == GameType.PUNISHING_GRAY_RAVEN.name:
            return PunishingGrayRavenMaterialDefaultValueSetter()
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
        possible_shadow_ramp_node_group_names = [
            f'{body_part} Shadow Ramp',
            'Shadow Ramp',
        ]
        for shadow_ramp_node_name in possible_shadow_ramp_node_group_names:
            shadow_ramp_node_group = bpy.data.node_groups.get(shadow_ramp_node_name)
            if shadow_ramp_node_group:
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
        lightmap_all = material.node_tree.nodes.get(V4_GenshinImpactTextureNodeNames.LIGHTMAP)  # >= v4.0 Body/Hair use same node name

        if (not lightmap_uv0 or not lightmap_uv1) and not lightmap_all:
            return

        if lightmap_uv0 and lightmap_uv1:
            default_value = default_missing if not lightmap_uv0.image or not lightmap_uv1.image else default_exists
        else:
            default_value = default_missing if not lightmap_all.image else default_exists

        body_shader_node = material.node_tree.nodes.get(self.shader_node_names.BODY_SHADER)
        if body_shader_node:
            shader_use_lightmap_ao_input = body_shader_node.inputs.get(self.shader_node_names.USE_LIGHTMAP_AO)
            if shader_use_lightmap_ao_input:
                shader_use_lightmap_ao_input.default_value = default_value

    def set_up_hair_material(self, material):
        raise NotImplementedError("This method should be implemented in subclasses that require hair material setup.")


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

    def set_up_hair_material(self, material):
        material.name = self.material_names.HAIR
        material.use_fake_user = True

        body_shader = material.node_tree.nodes.get(self.shader_node_names.BODY_SHADER)
        body_hair_ramp_switch = body_shader.inputs.get(self.shader_node_names.BODY_HAIR_RAMP_SWITCH)
        if body_hair_ramp_switch:
            body_hair_ramp_switch.default_value = 1


class HonkaiStarRailMaterialDefaultValueSetter(MaterialDefaultValueSetter):
    def __init__(self) -> None:
        return

    def set_default_values(self):
        return


class PunishingGrayRavenMaterialDefaultValueSetter(MaterialDefaultValueSetter):
    def __init__(self) -> None:
        return

    def set_default_values(self):
        return
