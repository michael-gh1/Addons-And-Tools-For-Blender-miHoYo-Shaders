from enum import Enum, auto


class StarCloakTypes(Enum):
    '''
    The following StarCloak types MUST remain in the same order as in the shader.
    The value set here is used to set the value in the VFX shader node input.
    '''
    PAIMON = 1
    DAINSLAIF = 2  # intentional "typo" based on armature name
    SKIRK = 3
    ASMODA = 4  # inetntional "typo" based on the character/armature/material name
