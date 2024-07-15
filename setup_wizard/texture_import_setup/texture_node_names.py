# Author: michael-gh1


class TextureNodeNames:
    DIFFUSE = ''
    BODY_DIFFUSE_UV0 = ''
    MAIN_DIFFUSE = ''
    LIGHTMAP = ''
    # HSR
    STOCKINGS_BODY1_NODE_GROUP = ''
    STOCKINGS_BODY2_NODE_GROUP = ''
    STOCKINGS_NODE_GROUP = ''
    STOCKINGS = ''
    BODY_WARM_RAMP_NODE_GROUP = ''
    BODY_WARM_RAMP = ''
    HAIR_WARM_RAMP_NODE_GROUP = ''
    HAIR_WARM_RAMP = ''
    BODY_COOL_RAMP_NODE_GROUP = ''
    BODY_COOL_RAMP = ''
    HAIR_COOL_RAMP_NODE_GROUP = ''
    HAIR_COOL_RAMP = ''
    FACE_MAP_NODE_GROUP = ''
    FACE_MAP = ''
    FACE_EXPRESSION_NODE_GROUP = ''
    FACE_EXPRESSION_MAP = ''
    WEAPON_RAMP_NODE_GROUP = ''
    WEAPON_RAMP = ''

    # StellarToon
    FACE_COLOR_SUFFIX = ''
    DIFFUSE_UV0_SUFFIX = ''
    DIFFUSE_UV1_SUFFIX = ''
    LIGHTMAP_UV0_SUFFIX = ''
    LIGHTMAP_UV1_SUFFIX = ''

    # PGR
    EYE = ''
    FACE_DIFFUSE = ''
    FACE_HEAO_NODE_GROUP = ''
    FACE_HEAO = ''
    FACE_LUT = ''
    CHIBI_FACE = ''
    LUT = ''
    NORMALMAP = ''
    PBR = ''
    METALLIC_MATCAP_NODE_GROUP = ''
    METALLIC_MATCAP = ''

class GenshinImpactTextureNodeNames(TextureNodeNames):
    BODY_DIFFUSE_UV0 = 'Body_Diffuse_UV0'
    MAIN_DIFFUSE = 'Main_Diffuse'

class Nya222HonkaiStarRailTextureNodeNames(TextureNodeNames):
    DIFFUSE = '画像テクスチャ'
    LIGHTMAP = '画像テクスチャ.001'
    STOCKINGS_BODY1_NODE_GROUP = '_Stockings Body1'  # From bpy.data.node_groups, not the node name in material
    STOCKINGS_BODY2_NODE_GROUP = '_Stockings Body2'  # From bpy.data.node_groups, not the node name in material
    STOCKINGS = '画像テクスチャ.002'
    BODY_WARM_RAMP_NODE_GROUP = 'Body_Ramp'
    BODY_WARM_RAMP = 'Image Texture.002'
    HAIR_WARM_RAMP_NODE_GROUP = 'Hair_Ramp'
    HAIR_WARM_RAMP = 'Image Texture.002'
    FACE_MAP_NODE_GROUP = '_FaceMap'  # From bpy.data.node_groups, not the node name in material
    FACE_MAP = 'Face_Lightmap'
    FACE_EXPRESSION_NODE_GROUP = '_Expression'  # From bpy.data.node_groups, not the node name in material
    FACE_EXPRESSION_MAP = '画像テクスチャ.001'
    WEAPON_RAMP_NODE_GROUP = 'Weapon_Ramp'  # From bpy.data.node_groups, not the node name in material
    WEAPON_RAMP = 'Image Texture.002'

'''
All "NODE_GROUP"s below are from bpy.data.node_groups and not the node name in material
'''
class StellarToonTextureNodeNames(TextureNodeNames):
    DIFFUSE = 'Image Texture.001'
    LIGHTMAP = 'Image Texture.002'
    DIFFUSE_UV0_SUFFIX = '_Color_UV0'
    DIFFUSE_UV1_SUFFIX = '_Color_UV1'
    LIGHTMAP_UV0_SUFFIX = '_Lightmap_UV0'
    LIGHTMAP_UV1_SUFFIX = '_Lightmap_UV1'
    STOCKINGS = 'Body_Stockings'

    FACE_COLOR_SUFFIX = '_Color'
    FACE_EXPRESSION_MAP = 'ExpressionMap'

    FACE_MAP_NODE_GROUP = 'Face Lightmap'
    FACE_MAP = 'FaceMap'

    BODY_WARM_RAMP_NODE_GROUP = 'Body Warm Shadow Ramp'
    BODY_WARM_RAMP = 'Body_Warm_Ramp'

    BODY_COOL_RAMP_NODE_GROUP = 'Body Cool Shadow Ramp'
    BODY_COOL_RAMP = 'Body_Cool_Ramp'

    STOCKINGS_NODE_GROUP = 'Stockings'
    STOCKINGS = 'Body_Stockings'

    HAIR_WARM_RAMP_NODE_GROUP = 'Hair Warm Shadow Ramp'
    HAIR_WARM_RAMP = 'Hair_Warm_Ramp'

    HAIR_COOL_RAMP_NODE_GROUP = 'Hair Cool Shadow Ramp'  
    HAIR_COOL_RAMP = 'Hair_Cool_Ramp'

    WEAPON_RAMP_NODE_GROUP = 'Weapon Shadow Ramp'
    WEAPON_RAMP = 'Weapon_Ramp'


class JaredNytsPunishingGrayRavenTextureNodeNames(TextureNodeNames):
    # Common, reused across shader
    DIFFUSE = 'Body_Diffuse_UV0'
    LIGHTMAP = 'Body_Lightmap_UV0'
    LUT = 'Image Texture'
    NORMALMAP = 'Body_Normalmap_UV0'
    PBR = 'Body_Lightmap_UV0.001'

    # Eyes
    EYE = 'Image Texture'

    # Face
    FACE_DIFFUSE = 'Face_Diffuse'
    FACE_SHADOW_MAP = 'Image Texture'
    FACE_LUT = 'Image Texture.001'
    FACE_HEAO_NODE_GROUP = 'Face HEAO'
    FACE_HEAO = 'Face_Lightmap.004'
    CHIBI_FACE = 'Image Texture'

    # Metallic Matcap
    METALLIC_MATCAP_NODE_GROUP = 'Metallic Matcap'
    METALLIC_MATCAP = 'MetalMap'
