# Author: michael-gh1


from abc import abstractmethod
from enum import Enum, auto

from setup_wizard.domain.game_types import GameType
from setup_wizard.domain.shader_material_names import JaredNytsPunishingGrayRavenShaderMaterialNames, Nya222HonkaiStarRailShaderMaterialNames, StellarToonShaderMaterialNames, V3_BonnyFestivityGenshinImpactMaterialNames, V2_FestivityGenshinImpactMaterialNames
from setup_wizard.texture_import_setup.texture_node_names import GenshinImpactTextureNodeNames, JaredNytsPunishingGrayRavenTextureNodeNames, Nya222HonkaiStarRailTextureNodeNames, StellarToonTextureNodeNames


class GenshinImpactShaders(Enum):
    V1_GENSHIN_IMPACT_SHADER = auto()
    V2_GENSHIN_IMPACT_SHADER = auto()
    V3_GENSHIN_IMPACT_SHADER = auto()

class HonkaiStarRailShaders(Enum):
    NYA222_HONKAI_STAR_RAIL_SHADER = auto()
    STELLARTOON_HONKAI_STAR_RAIL_SHADER = auto()


class PunishingGrayRavenShaders(Enum):
    V1_JAREDNYTS_PUNISHING_GRAY_RAVEN_SHADER = auto()

class ShaderIdentifierServiceFactory:
    def create(game_type):
        if game_type == GameType.GENSHIN_IMPACT.name:
            return GenshinImpactShaderIdentifierService()
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            return HonkaiStarRailShaderIdentifierService()
        elif game_type == GameType.PUNISHING_GRAY_RAVEN.name:
            return PunishingGrayRavenShaderIdentifierService()
        else:
            raise Exception(f'Unexpected input GameType "{game_type}" for ShaderIdentifierServiceFactory')


class ShaderIdentifierService:
    material_lists_to_search_through = {}
    node_groups_to_search_through = {}

    def __init__(self):
        pass

    def identify_shader(self, materials, node_groups):
        # Check for V1 shader first
        for shader, node_group_list in self.node_groups_to_search_through.items():
            found_all = True
            for node_group in node_group_list:
                if node_group not in node_groups:
                    found_all = False
                    break
            if found_all:
                return shader

        # Check for V2 shader next b/c V1 and V2 have same material names
        # Then check for later versions (V3, etc.)
        for shader, material_list in self.material_lists_to_search_through.items():
            found_all = True
            for material in material_list:
                if not [scene_material for scene_material in materials.values() if material in scene_material.name]:
                    found_all = False
                    break
            if found_all:
                return shader

    def get_shader_material_names(self, game_type, materials, node_groups):
        if game_type == GameType.GENSHIN_IMPACT.name:
            game_shader = self.identify_shader(materials, node_groups)
            if game_shader is GenshinImpactShaders.V2_GENSHIN_IMPACT_SHADER:
                return V2_FestivityGenshinImpactMaterialNames
            else:
                return V3_BonnyFestivityGenshinImpactMaterialNames
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            return Nya222HonkaiStarRailShaderMaterialNames
        elif game_type == GameType.PUNISHING_GRAY_RAVEN.name:
            return JaredNytsPunishingGrayRavenShaderMaterialNames
        else:
            raise Exception(f'Unknown {GameType}: {game_type}')

    def get_shader_material_names_using_shader(self, shader: GenshinImpactShaders):
        if shader is GenshinImpactShaders.V1_GENSHIN_IMPACT_SHADER or shader is GenshinImpactShaders.V2_GENSHIN_IMPACT_SHADER:
            return V2_FestivityGenshinImpactMaterialNames
        elif shader is GenshinImpactShaders.V3_GENSHIN_IMPACT_SHADER:
            return V3_BonnyFestivityGenshinImpactMaterialNames
        elif shader is HonkaiStarRailShaders.NYA222_HONKAI_STAR_RAIL_SHADER:
            return Nya222HonkaiStarRailShaderMaterialNames
        elif shader is HonkaiStarRailShaders.STELLARTOON_HONKAI_STAR_RAIL_SHADER:
            return StellarToonShaderMaterialNames
        elif shader is PunishingGrayRavenShaders.V1_JAREDNYTS_PUNISHING_GRAY_RAVEN_SHADER:
            return JaredNytsPunishingGrayRavenShaderMaterialNames
        else:
            raise Exception(f'Unknown Shader: {shader}')

    def get_shader_texture_node_names(self, shader):
        if shader is GenshinImpactShaders.V1_GENSHIN_IMPACT_SHADER or \
            shader is GenshinImpactShaders.V2_GENSHIN_IMPACT_SHADER or \
            shader is GenshinImpactShaders.V3_GENSHIN_IMPACT_SHADER:
                return GenshinImpactTextureNodeNames
        elif shader is HonkaiStarRailShaders.NYA222_HONKAI_STAR_RAIL_SHADER:
            return Nya222HonkaiStarRailTextureNodeNames
        elif shader is HonkaiStarRailShaders.STELLARTOON_HONKAI_STAR_RAIL_SHADER:
            return StellarToonTextureNodeNames
        elif shader is PunishingGrayRavenShaders.V1_JAREDNYTS_PUNISHING_GRAY_RAVEN_SHADER:
            return JaredNytsPunishingGrayRavenTextureNodeNames
        else:
            raise Exception(f'Unknown Shader: {shader}')

class GenshinImpactShaderIdentifierService(ShaderIdentifierService):
    V2_NAMES_OF_GENSHIN_MATERIALS = [
        V2_FestivityGenshinImpactMaterialNames.MATERIAL_PREFIX_AFTER_RENAME,
    ]
    V3_NAMES_OF_GENSHIN_MATERIALS = [
        V3_BonnyFestivityGenshinImpactMaterialNames.MATERIAL_PREFIX_AFTER_RENAME,
    ]
    material_lists_to_search_through = {
        GenshinImpactShaders.V3_GENSHIN_IMPACT_SHADER: V3_NAMES_OF_GENSHIN_MATERIALS,
        GenshinImpactShaders.V2_GENSHIN_IMPACT_SHADER: V2_NAMES_OF_GENSHIN_MATERIALS,
    }

    node_groups_to_search_through = {
        GenshinImpactShaders.V1_GENSHIN_IMPACT_SHADER: ['miHoYo - Genshin Face'],
    }

    def __init__(self):
        super().__init__()


class HonkaiStarRailShaderIdentifierService(ShaderIdentifierService):
    NYA222_NAMES_OF_SHADER_MATERIALS = [
        Nya222HonkaiStarRailShaderMaterialNames.MATERIAL_PREFIX_AFTER_RENAME,
    ]
    STELLARTOON_NAMES_OF_SHADER_MATERIALS = [
        StellarToonShaderMaterialNames.MATERIAL_PREFIX_AFTER_RENAME,
    ]
    material_lists_to_search_through = {
        HonkaiStarRailShaders.NYA222_HONKAI_STAR_RAIL_SHADER: NYA222_NAMES_OF_SHADER_MATERIALS,
        HonkaiStarRailShaders.STELLARTOON_HONKAI_STAR_RAIL_SHADER: STELLARTOON_NAMES_OF_SHADER_MATERIALS
    }

    def __init__(self):
        super().__init__()


# Unused.
class PunishingGrayRavenShaderIdentifierService(ShaderIdentifierService):
    V1_NAMES_OF_PGR_MATERIALS = [
        JaredNytsPunishingGrayRavenShaderMaterialNames.MATERIAL_PREFIX_AFTER_RENAME,
    ]
    material_lists_to_search_through = {
        PunishingGrayRavenShaders.V1_JAREDNYTS_PUNISHING_GRAY_RAVEN_SHADER: V1_NAMES_OF_PGR_MATERIALS
    }

    def __init__(self):
        super().__init__()
