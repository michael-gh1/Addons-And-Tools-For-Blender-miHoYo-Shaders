from setup_wizard.domain.shader_node_names import V3_GenshinShaderNodeNames, V1_HoYoToonShaderNodeNames


class BodyHairRampSwitchValues:
    BODY = -1
    BODY2 = -1
    HAIR = -1

    def __init__(self, shader_node_names):
        if shader_node_names == V3_GenshinShaderNodeNames:
            self.BODY = V3_BodyHairRampSwitchValues.BODY
            self.BODY2 = V3_BodyHairRampSwitchValues.BODY2
        elif shader_node_names == V1_HoYoToonShaderNodeNames:
            self.BODY = V1_HoYoToonBodyHairRampSwitchValues.BODY
            self.BODY2 = V1_HoYoToonBodyHairRampSwitchValues.BODY2
            self.HAIR = V1_HoYoToonBodyHairRampSwitchValues.HAIR


class V3_BodyHairRampSwitchValues(BodyHairRampSwitchValues):
    BODY = 0
    HAIR = 1


class V1_HoYoToonBodyHairRampSwitchValues(BodyHairRampSwitchValues):
    BODY = 1
    BODY2 = 2
    HAIR = 3
