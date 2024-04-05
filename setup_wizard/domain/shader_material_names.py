# Author: michael-gh1


class ShaderMaterialNames:
    EMISSIVE_TEMPLATE_MATERIAL_NAME = 'HoYoverse - HELPER Template'
    MATERIAL_PREFIX = ''
    BODY = ''
    BODY1 = ''
    BODY2 = ''
    BODY3 = ''
    BODY_TRANS = ''
    BODY2_TRANS = ''
    DRESS = ''
    EFFECT = ''
    EFFECT_HAIR = ''
    GAUNTLET = ''
    HELMET = ''
    HELMET_EMO = ''
    HAIR = ''
    FACE = ''
    EYESHADOW = ''
    OUTLINES = ''
    # HSR
    WEAPON = ''
    WEAPON01 = ''
    WEAPON02 = ''
    HANDBAG = ''  # Sampo
    KENDAMA = ''  # Sparkle
    # HSR: StellarToon
    BASE = ''
    BASE_OUTLINES = ''
    HAIR_OUTLINES = ''
    FACE_OUTLINES = ''
    WEAPON_OUTLINES = ''
    # PGR
    ALPHA = ''
    EYE = ''
    FACE = ''
    HAIR = ''
    MAIN = ''
    OUTLINES = ''
    BODY = ''
    XDEFAULTMATERIAL = ''
    CHIBIFACE = ''

class V2_FestivityGenshinImpactMaterialNames(ShaderMaterialNames):
    MATERIAL_PREFIX = 'miHoYo - Genshin '
    BODY = f'{MATERIAL_PREFIX}Body'
    DRESS = f'{MATERIAL_PREFIX}Dress'
    EFFECT = f'{MATERIAL_PREFIX}Effect'
    EFFECT_HAIR = f'{MATERIAL_PREFIX}EffectHair'
    GAUNTLET = f'{MATERIAL_PREFIX}Gauntlet'
    HAIR = f'{MATERIAL_PREFIX}Hair'
    HELMET = f'{MATERIAL_PREFIX}Helmet'
    HELMET_EMO = f'{MATERIAL_PREFIX}HelmetEmo'
    FACE = f'{MATERIAL_PREFIX}Face'
    OUTLINES = f'{MATERIAL_PREFIX}Outlines'


class V3_BonnyFestivityGenshinImpactMaterialNames(ShaderMaterialNames):
    MATERIAL_PREFIX = 'HoYoverse - Genshin '
    BODY = f'{MATERIAL_PREFIX}Body'
    DRESS = f'{MATERIAL_PREFIX}Dress'
    EFFECT = f'{MATERIAL_PREFIX}Effect'
    EFFECT_HAIR = f'{MATERIAL_PREFIX}EffectHair'
    GAUNTLET = f'{MATERIAL_PREFIX}Gauntlet'
    HAIR = f'{MATERIAL_PREFIX}Hair'
    HELMET = f'{MATERIAL_PREFIX}Helmet'
    HELMET_EMO = f'{MATERIAL_PREFIX}HelmetEmo'
    FACE = f'{MATERIAL_PREFIX}Face'
    OUTLINES = f'{MATERIAL_PREFIX}Outlines'



class Nya222HonkaiStarRailShaderMaterialNames(ShaderMaterialNames):
    MATERIAL_PREFIX = 'HSR - '
    BODY = f'{MATERIAL_PREFIX}Body'
    BODY1 = f'{MATERIAL_PREFIX}Body1'
    BODY2 = f'{MATERIAL_PREFIX}Body2'
    BODY3 = f'{MATERIAL_PREFIX}Body3'
    BODY_TRANS = f'{MATERIAL_PREFIX}Body_Trans'
    BODY2_TRANS = f'{MATERIAL_PREFIX}Body2_Trans'
    HAIR = f'{MATERIAL_PREFIX}Hair'
    FACE = f'{MATERIAL_PREFIX}Face'
    EYESHADOW = f'{MATERIAL_PREFIX}EyeShadow'
    OUTLINES = f'{MATERIAL_PREFIX}Outlines'
    WEAPON = f'{MATERIAL_PREFIX}Weapon'
    WEAPON1 = f'{MATERIAL_PREFIX}Weapon1'
    WEAPON01 = f'{MATERIAL_PREFIX}Weapon01'
    WEAPON02 = f'{MATERIAL_PREFIX}Weapon02'
    HANDBAG = f'{MATERIAL_PREFIX}Handbag'
    KENDAMA = f'{MATERIAL_PREFIX}Kendama'  # Sparkle


class StellarToonShaderMaterialNames(ShaderMaterialNames):
    # Shader Materials
    MATERIAL_PREFIX = 'StellarToon - '
    BASE = f'{MATERIAL_PREFIX}Base'
    HAIR = f'{MATERIAL_PREFIX}Hair'
    FACE = f'{MATERIAL_PREFIX}Face'
    WEAPON = f'{MATERIAL_PREFIX}Weapon'
    BASE_OUTLINES = f'{MATERIAL_PREFIX}Base Outlines'
    OUTLINES = BASE_OUTLINES
    HAIR_OUTLINES = f'{MATERIAL_PREFIX}Hair Outlines'
    FACE_OUTLINES = f'{MATERIAL_PREFIX}Face Outlines'
    WEAPON_OUTLINES = f'{MATERIAL_PREFIX}Weapon Outlines'

    # Game Materials
    BODY = f'{MATERIAL_PREFIX}Body'
    BODY1 = f'{MATERIAL_PREFIX}Body1'
    BODY2 = f'{MATERIAL_PREFIX}Body2'
    BODY3 = f'{MATERIAL_PREFIX}Body3'
    BODY_TRANS = f'{MATERIAL_PREFIX}Body_Trans'
    BODY2_TRANS = f'{MATERIAL_PREFIX}Body2_Trans'
    HAIR = f'{MATERIAL_PREFIX}Hair'
    FACE = f'{MATERIAL_PREFIX}Face'
    EYESHADOW = f'{MATERIAL_PREFIX}EyeShadow'
    WEAPON = f'{MATERIAL_PREFIX}Weapon'
    WEAPON1 = f'{MATERIAL_PREFIX}Weapon1'
    WEAPON01 = f'{MATERIAL_PREFIX}Weapon01'
    WEAPON02 = f'{MATERIAL_PREFIX}Weapon02'
    HANDBAG = f'{MATERIAL_PREFIX}Handbag'
    KENDAMA = f'{MATERIAL_PREFIX}Kendama'  # Sparkle


class JaredNytsPunishingGrayRavenShaderMaterialNames(ShaderMaterialNames):
    MATERIAL_PREFIX = 'PGR - '
    ALPHA = f'{MATERIAL_PREFIX}Alpha'
    EYE = f'{MATERIAL_PREFIX}Eye'
    FACE = f'{MATERIAL_PREFIX}Face'
    HAIR = f'{MATERIAL_PREFIX}Hair'
    MAIN = f'{MATERIAL_PREFIX}Main'
    OUTLINES = f'{MATERIAL_PREFIX}Outlines'

    # Custom
    BODY = f'{MATERIAL_PREFIX}Body'
    XDEFAULTMATERIAL = f'{MATERIAL_PREFIX}XDefaultMaterial'  # Chibi Body
    CHIBIFACE = 'ChibiFace'  # Chibi Face
