# Author: michael-gh1


class ShaderNodeNames:
    BODY_SHADER = ''
    BODY_SHADER_LABEL = ''
    BODY_SHADER_OUTPUT = ''
    HAIR_SHADER = ''
    FACE_SHADER = ''
    FACE_MATERIAL_ID = ''
    OUTLINES_SHADER = ''
    VFX_SHADER = ''
    VFX_SHADER_INPUT = ''
    USE_SHADOW_RAMP = ''
    USE_LIGHTMAP_AO = ''
    DEPTH_BASED_RIM = ''
    BODY_HAIR_RAMP_SWITCH = ''
    OUTLINES = 'Outlines'  # Outlines material node OUTPUT
    EXTERNAL_GLOBAL_PROPERTIES = 'Global Properties'
    INTERNAL_GLOBAL_PROPERTIES = 'Global Properties'
    OUTLINES_OUTPUT = 'Outlines'
    NIGHT_SOUL_OUTPUT = ''
    MATERIAL_OUTPUT_NODE = ''
    MATERIAL_OUTPUT_SHADER_INPUT = ''
    STAR_CLOAK_TYPE = ''
    TOGGLE_FACE_OUTLINES = ''
    TOGGLE_GLASS_STAR_CLOAK = ''

    # StellarToon
    ENABLE_STOCKINGS = ''

    # PGR
    MAIN_SHADER = ''
    USE_LUT = ''


class V2_GenshinShaderNodeNames(ShaderNodeNames):
    BODY_SHADER = 'Group.006'
    HAIR_SHADER = 'Group.006'
    FACE_SHADER = 'Group.006'
    FACE_MATERIAL_ID = 'Face Material ID'
    USE_SHADOW_RAMP = 'Use Shadow Ramp'
    USE_LIGHTMAP_AO = 'Use Lightmap AO'
    DEPTH_BASED_RIM = 'Group.010'


class V3_GenshinShaderNodeNames(ShaderNodeNames):
    BODY_SHADER = 'Body Shader'
    HAIR_SHADER = 'Body Shader'  # Not a typo
    FACE_SHADER = 'Face Shader'
    OUTLINES_SHADER = 'Outlines'
    BODY_HAIR_RAMPS = 'Body / Hair Ramps'
    FACE_MATERIAL_ID = 'Face Material ID'
    USE_SHADOW_RAMP = 'Use Shadow Ramp'
    USE_LIGHTMAP_AO = 'Use Lightmap AO'

    BODY_HAIR_RAMP_SWITCH = 'Body / Hair'


class V4_PrimoToonShaderNodeNames(V3_GenshinShaderNodeNames):
    BODY_SHADER = 'PrimoToon'
    BODY_SHADER_LABEL = 'PrimoToon v4.0'
    BODY_SHADER_OUTPUT = 'PrimoToon'
    HAIR_SHADER = BODY_SHADER
    FACE_SHADER = BODY_SHADER
    OUTLINES_SHADER = BODY_SHADER
    VFX_SHADER = BODY_SHADER
    VFX_SHADER_INPUT = 'PrimoToon'
    STAR_CLOAK_TYPE = '[Paimon / Dainslief / Skirk / Asmoday] - Star Cloak'
    TOGGLE_FACE_OUTLINES = 'Toggle Face Outlines'
    TOGGLE_GLASS_STAR_CLOAK = '[Glass / Star Cloak]'
    OUTLINES_OUTPUT = 'PrimoToon (Outlines)'
    NIGHT_SOUL_OUTPUT = 'PrimoToon (Night Soul)'
    MATERIAL_OUTPUT_NODE = 'Material Output'
    MATERIAL_OUTPUT_SHADER_INPUT = 'Surface'

class StellarToonShaderNodeNames(ShaderNodeNames):
    MAIN_SHADER = 'Group.006'
    BODY_SHADER = 'Group.006'
    OUTLINES_SHADER = 'Group.006'
    ENABLE_STOCKINGS = 'Enable Stockings'

class JaredNyts_PunishingGrayRavenNodeNames(ShaderNodeNames):
    MAIN_SHADER = 'Group.001'
    FACE_SHADER = 'Group'
    USE_LUT = 'Use LUT = 1, No LUT = 0'
