from setup_wizard.domain.game_types import GameType


class UIRenderChecker:
    @classmethod
    def poll(cls, context):
        return context.scene.game_type_dropdown == cls.GAME_TYPE


class GenshinImpactUIRenderChecker(UIRenderChecker):
    GAME_TYPE = GameType.GENSHIN_IMPACT.name


class HonkaiStarRailUIRenderChecker(UIRenderChecker):
    GAME_TYPE = GameType.HONKAI_STAR_RAIL.name


class PunishingGrayRavenUIRenderChecker(UIRenderChecker):
    GAME_TYPE = GameType.PUNISHING_GRAY_RAVEN.name
