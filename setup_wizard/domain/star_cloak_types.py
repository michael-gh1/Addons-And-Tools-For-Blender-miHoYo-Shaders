from enum import Enum, auto


class StarCloakTypes(Enum):
    '''
    The following StarCloak types MUST remain in the same order as in the shader.
    The value set here is used to set the value in the VFX shader node input.
    '''
    PAIMON = 1
    DAINSLIEF = 2
    SKIRK = 3
    ASMODAY = 4
