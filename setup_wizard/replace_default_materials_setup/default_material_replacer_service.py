
from setup_wizard.replace_default_materials_setup.game_default_material_replacers import GameDefaultMaterialReplacer


class DefaultMaterialReplacerService:
    def __init__(self, game_default_material_replacer: GameDefaultMaterialReplacer):
        self.game_default_material_replacer = game_default_material_replacer

    def replace_default_materials(self):
        return self.game_default_material_replacer.replace_default_materials()
