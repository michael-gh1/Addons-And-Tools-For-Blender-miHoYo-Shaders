# Author: michael-gh1

from bpy.types import Operator, Context

from setup_wizard.character_rig_setup.character_riggers import CharacterRiggerFactory
from setup_wizard.domain.game_types import GameType


class RigifyCharacterService:
    def __init__(self, game_type: GameType, blender_operator: Operator, context: Context):
        self.character_rigger = CharacterRiggerFactory.create(game_type, blender_operator, context)

    def rig_character(self):
        self.character_rigger.rig_character()
