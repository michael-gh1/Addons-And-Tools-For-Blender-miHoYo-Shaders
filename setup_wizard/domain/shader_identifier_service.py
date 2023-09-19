# Author: michael-gh1


from abc import abstractmethod
from enum import Enum, auto

from setup_wizard.domain.game_types import GameType
from setup_wizard.domain.shader_material_names import V3_BonnyFestivityGenshinImpactMaterialNames, V2_FestivityGenshinImpactMaterialNames


class GenshinImpactShaders(Enum):
    V1_GENSHIN_IMPACT_SHADER = auto()
    V2_GENSHIN_IMPACT_SHADER = auto()
    V3_GENSHIN_IMPACT_SHADER = auto()


class ShaderIdentifierServiceFactory:
    def create(game_type):
        if game_type == GameType.GENSHIN_IMPACT.name:
            return GenshinImpactShaderIdentifierService()
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            return HonkaiStarRailShaderIdentifierService()
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
                if material not in materials:
                    found_all = False
                    break
            if found_all:
                return shader


class GenshinImpactShaderIdentifierService(ShaderIdentifierService):
    V2_NAMES_OF_GENSHIN_MATERIALS = [
        V2_FestivityGenshinImpactMaterialNames.BODY,
        V2_FestivityGenshinImpactMaterialNames.FACE,
        V2_FestivityGenshinImpactMaterialNames.HAIR,
        V2_FestivityGenshinImpactMaterialNames.OUTLINES
    ]
    V3_NAMES_OF_GENSHIN_MATERIALS = [
        V3_BonnyFestivityGenshinImpactMaterialNames.BODY,
        V3_BonnyFestivityGenshinImpactMaterialNames.FACE,
        V3_BonnyFestivityGenshinImpactMaterialNames.HAIR,
        V3_BonnyFestivityGenshinImpactMaterialNames.OUTLINES
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
    def __init__(self):
        super().__init__()
