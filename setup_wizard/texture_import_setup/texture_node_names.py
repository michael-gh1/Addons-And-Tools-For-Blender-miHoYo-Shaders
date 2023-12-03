# Author: michael-gh1


class TextureNodeNames:
    DIFFUSE = ''
    BODY_DIFFUSE_UV0 = ''
    LIGHTMAP = ''
    STOCKINGS_BODY1_NODE_GROUP = ''
    STOCKINGS_BODY2_NODE_GROUP = ''
    STOCKINGS = ''
    BODY_RAMP_NODE_GROUP = ''
    BODY_RAMP = ''
    HAIR_RAMP_NODE_GROUP = ''
    HAIR_RAMP = ''
    FACE_MAP_NODE_GROUP = ''
    FACE_MAP = ''
    FACE_EXPRESSION_NODE_GROUP = ''
    FACE_EXPRESSION_MAP = ''
    WEAPON_RAMP_NODE_GROUP = ''
    WEAPON_RAMP = ''

    # PGR
    EYE = ''
    FACE_DIFFUSE = ''
    FACE_HEAO_NODE_GROUP = ''
    FACE_HEAO = ''
    FACE_LUT = ''
    LUT = ''
    NORMALMAP = ''
    PBR = ''
    METALLIC_MATCAP_NODE_GROUP = ''
    METALLIC_MATCAP = ''

class GenshinImpactTextureNodeNames(TextureNodeNames):
    BODY_DIFFUSE_UV0 = 'Body_Diffuse_UV0'

class Nya222HonkaiStarRailTextureNodeNames(TextureNodeNames):
    DIFFUSE = '画像テクスチャ'
    LIGHTMAP = '画像テクスチャ.001'
    STOCKINGS_BODY1_NODE_GROUP = '_Stockings Body1'  # From bpy.data.node_groups, not the node name in material
    STOCKINGS_BODY2_NODE_GROUP = '_Stockings Body2'  # From bpy.data.node_groups, not the node name in material
    STOCKINGS = '画像テクスチャ.002'
    BODY_RAMP_NODE_GROUP = 'グループ.009'
    BODY_RAMP = 'Image Texture.002'
    HAIR_RAMP_NODE_GROUP = 'グループ.007'
    HAIR_RAMP = 'Image Texture.002'
    FACE_MAP_NODE_GROUP = '_FaceMap'  # From bpy.data.node_groups, not the node name in material
    FACE_MAP = 'Face_Lightmap'
    FACE_EXPRESSION_NODE_GROUP = '_Expression'  # From bpy.data.node_groups, not the node name in material
    FACE_EXPRESSION_MAP = '画像テクスチャ.001'
    WEAPON_RAMP_NODE_GROUP = 'Weapon_Ramp'  # From bpy.data.node_groups, not the node name in material
    WEAPON_RAMP = 'Image Texture.002'


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

    # Metallic Matcap
    METALLIC_MATCAP_NODE_GROUP = 'Metallic Matcap'
    METALLIC_MATCAP = 'MetalMap'
