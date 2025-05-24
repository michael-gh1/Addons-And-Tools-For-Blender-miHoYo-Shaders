from setup_wizard.domain.shader_node_names import V3_GenshinShaderNodeNames, V4_PrimoToonShaderNodeNames


class BodyHairRampSwitchValues:
    BODY = -1
    BODY2 = -1
    HAIR = -1

    def __init__(self, shader_node_names):
        if shader_node_names == V3_GenshinShaderNodeNames:
            self.BODY = V3_BodyHairRampSwitchValues.BODY
            self.BODY2 = V3_BodyHairRampSwitchValues.BODY2
        elif shader_node_names == V4_PrimoToonShaderNodeNames:
            self.BODY = V4_BodyHairRampSwitchValues.BODY
            self.BODY2 = V4_BodyHairRampSwitchValues.BODY2
            self.HAIR = V4_BodyHairRampSwitchValues.HAIR


class V3_BodyHairRampSwitchValues(BodyHairRampSwitchValues):
    BODY = 0
    HAIR = 1


class V4_BodyHairRampSwitchValues(BodyHairRampSwitchValues):
    BODY = 1
    BODY2 = 2
    HAIR = 3
