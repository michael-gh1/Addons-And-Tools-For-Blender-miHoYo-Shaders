# Author: michael-gh1


from abc import abstractmethod
from enum import Enum, auto

from setup_wizard.domain.game_types import GameType
from setup_wizard.domain.shader_materials import V3_BonnyFestivityGenshinImpactMaterialNames, FestivityGenshinImpactMaterialNames


class GenshinImpactShaders(Enum):
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

    def __init__(self):
        pass

    def identify_shader(self, materials):
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
        FestivityGenshinImpactMaterialNames.BODY,
        FestivityGenshinImpactMaterialNames.FACE,
        FestivityGenshinImpactMaterialNames.HAIR,
        FestivityGenshinImpactMaterialNames.OUTLINES
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

    def __init__(self):
        super().__init__()

class HonkaiStarRailShaderIdentifierService(ShaderIdentifierService):
    def __init__(self):
        super().__init__()
