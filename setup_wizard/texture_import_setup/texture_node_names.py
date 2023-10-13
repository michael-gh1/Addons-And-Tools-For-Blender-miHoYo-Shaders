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


