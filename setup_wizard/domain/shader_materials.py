# Author: michael-gh1


class GameMaterialNames:
    MATERIAL_PREFIX = ''
    BODY = ''
    BODY1 = ''
    BODY2 = ''
    BODY_TRANS = ''
    HAIR = ''
    FACE = ''
    EYESHADOW = ''
    OUTLINES = ''
    WEAPON = ''


class FestivityGenshinImpactMaterialNames(GameMaterialNames):
    MATERIAL_PREFIX = 'miHoYo - Genshin '
    BODY = f'{MATERIAL_PREFIX}Body'
    HAIR = f'{MATERIAL_PREFIX}Hair'
    FACE = f'{MATERIAL_PREFIX}Face'
    OUTLINES = f'{MATERIAL_PREFIX}Outlines'


class Nya222HonkaiStarRailShaderMaterialNames(GameMaterialNames):
    MATERIAL_PREFIX = 'HSR - '
    BODY = 'HSR - Body'
    BODY1 = 'HSR - Body1'
    BODY2 = 'HSR - Body2'
    BODY_TRANS = 'HSR - Body_Trans'
    HAIR = 'HSR - Hair'
    FACE = 'HSR - Face'
    EYESHADOW = 'HSR - EyeShadow'
    OUTLINES = 'HSR - Outlines'
    WEAPON = 'HSR - Weapon'
