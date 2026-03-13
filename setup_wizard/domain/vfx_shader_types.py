from enum import Enum, auto


class VFXShaderTypes(Enum):
    '''
    The following VFX shader types MUST remain in the same order as in the shader.
    The value set here is used to set the value in the VFX shader node input.
    '''
    GLASS = 1
    STARCLOAK = 2
    VEIL = 3
    RIBBON = 3
