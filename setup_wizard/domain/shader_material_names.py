# Author: michael-gh1


class ShaderMaterialNames:
    EMISSIVE_TEMPLATE_MATERIAL_NAME = 'HoYoverse - HELPER Template'
    MATERIAL_PREFIX = ''
    MATERIAL_PREFIX_AFTER_RENAME = ''
    BODY = ''
    BODY1 = ''
    BODY2 = ''
    BODY3 = ''
    BODY_TRANS = ''
    BODY2_TRANS = ''
    BROW = ''
    DRESS = ''
    EFFECT = ''
    EFFECT_HAIR = ''
    GAUNTLET = ''
    GLASS = ''
    GLASS_EFF = ''
    HELMET = ''
    HELMET_EMO = ''
    LEATHER = ''
    HAIR = ''
    FACE = ''
    EYESHADOW = ''
    OUTLINES = ''
    NIGHT_SOUL_OUTLINES_SUFFIX = 'Night Soul Outlines'
    NIGHT_SOUL_OUTLINES = ''
    PUPIL = ''
    SKILLOBJ = f'{MATERIAL_PREFIX}SkillObj'
    SKIRT = ''
    STAR_CLOAK = ''
    VFX = ''
    # HSR
    WEAPON = ''
    WEAPON01 = ''
    WEAPON02 = ''
    WEAPON_TRANS = ''  # Serval
    HANDBAG = ''  # Sampo
    KENDAMA = ''  # Sparkle
    COAT = ''  # Feixiao
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
    MATERIAL_PREFIX_AFTER_RENAME = 'miHoYo - '
    BODY = f'{MATERIAL_PREFIX}Body'
    BODY1 = f'{MATERIAL_PREFIX}Body1'
    BODY2 = f'{MATERIAL_PREFIX}Body2'
    DRESS = f'{MATERIAL_PREFIX}Dress'
    EFFECT = f'{MATERIAL_PREFIX}Effect'
    EFFECT_HAIR = f'{MATERIAL_PREFIX}EffectHair'
    GAUNTLET = f'{MATERIAL_PREFIX}Gauntlet'
    GLASS = f'{MATERIAL_PREFIX}Glass'
    HAIR = f'{MATERIAL_PREFIX}Hair'
    HELMET = f'{MATERIAL_PREFIX}Helmet'
    HELMET_EMO = f'{MATERIAL_PREFIX}HelmetEmo'
    FACE = f'{MATERIAL_PREFIX}Face'
    OUTLINES = f'{MATERIAL_PREFIX}Outlines'
    PUPIL = f'{MATERIAL_PREFIX}Pupil'
    SKILLOBJ = f'{MATERIAL_PREFIX}SkillObj'
    SKIRT = f'{MATERIAL_PREFIX}Skirt'


class V3_BonnyFestivityGenshinImpactMaterialNames(ShaderMaterialNames):
    MATERIAL_PREFIX = 'HoYoverse - Genshin '
    MATERIAL_PREFIX_AFTER_RENAME = 'HoYoverse - '
    BODY = f'{MATERIAL_PREFIX}Body'
    BODY1 = f'{MATERIAL_PREFIX}Body1'
    BODY2 = f'{MATERIAL_PREFIX}Body2'
    BROW = f'{MATERIAL_PREFIX}Brow'
    DRESS = f'{MATERIAL_PREFIX}Dress'
    EFFECT = f'{MATERIAL_PREFIX}Effect'
    EFFECT_HAIR = f'{MATERIAL_PREFIX}EffectHair'
    GAUNTLET = f'{MATERIAL_PREFIX}Gauntlet'
    GLASS = f'{MATERIAL_PREFIX}Glass'
    HAIR = f'{MATERIAL_PREFIX}Hair'
    HELMET = f'{MATERIAL_PREFIX}Helmet'
    HELMET_EMO = f'{MATERIAL_PREFIX}HelmetEmo'
    FACE = f'{MATERIAL_PREFIX}Face'
    OUTLINES = f'{MATERIAL_PREFIX}Outlines'
    PUPIL = f'{MATERIAL_PREFIX}Pupil'
    SKILLOBJ = f'{MATERIAL_PREFIX}SkillObj'
    SKIRT = f'{MATERIAL_PREFIX}Skirt'


class V1_HoYoToonGenshinImpactMaterialNames(V3_BonnyFestivityGenshinImpactMaterialNames):
    MATERIAL_PREFIX = 'HoYoverse - Genshin '
    MATERIAL_PREFIX_AFTER_RENAME = 'HoYoverse - '
    GLASS = f'{MATERIAL_PREFIX}Glass'
    GLASS_EFF = f'{MATERIAL_PREFIX}Glass_Eff'
    LEATHER = f'{MATERIAL_PREFIX}Leather'
    SKILLOBJ = f'{MATERIAL_PREFIX}SkillObj'
    VFX = f'{MATERIAL_PREFIX}VFX'
    NIGHT_SOUL_OUTLINES_SUFFIX = 'Night Soul Outlines'
    NIGHT_SOUL_OUTLINES = f'{MATERIAL_PREFIX}{NIGHT_SOUL_OUTLINES_SUFFIX}'
    STAR_CLOAK = f'{MATERIAL_PREFIX}StarCloak'


class Nya222HonkaiStarRailShaderMaterialNames(ShaderMaterialNames):
    MATERIAL_PREFIX = 'HSR - '
    MATERIAL_PREFIX_AFTER_RENAME = 'HSR - '
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
    COAT = f'{MATERIAL_PREFIX}Coat'  # Feixiao


class StellarToonShaderMaterialNames(ShaderMaterialNames):
    # Shader Materials
    MATERIAL_PREFIX = 'StellarToon - '
    MATERIAL_PREFIX_AFTER_RENAME = 'StellarToon - '
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
    WEAPON_TRANS = f'{MATERIAL_PREFIX}Weapon_Trans'
    HANDBAG = f'{MATERIAL_PREFIX}Handbag'
    KENDAMA = f'{MATERIAL_PREFIX}Kendama'  # Sparkle
    COAT = f'{MATERIAL_PREFIX}Coat'  # Feixiao


class JaredNytsPunishingGrayRavenShaderMaterialNames(ShaderMaterialNames):
    MATERIAL_PREFIX = 'PGR - '
    MATERIAL_PREFIX_AFTER_RENAME = 'PGR - '
    ALPHA = f'{MATERIAL_PREFIX}Alpha'
    EYE = f'{MATERIAL_PREFIX}Eye'
    FACE = f'{MATERIAL_PREFIX}Face'
    HAIR = f'{MATERIAL_PREFIX}Hair'
    MAIN = f'{MATERIAL_PREFIX}Main'
    OUTLINES = f'{MATERIAL_PREFIX}Outlines'

    # Custom
    BODY = f'{MATERIAL_PREFIX}Body'
    BODY1 = f'{MATERIAL_PREFIX}Body01'
    XDEFAULTMATERIAL = f'{MATERIAL_PREFIX}XDefaultMaterial'  # Chibi Body
    CHIBIFACE = 'ChibiFace'  # Chibi Face
