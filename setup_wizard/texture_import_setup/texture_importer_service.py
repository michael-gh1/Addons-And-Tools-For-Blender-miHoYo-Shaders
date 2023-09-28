
from setup_wizard.texture_import_setup.game_texture_importers import GameTextureImporter
from setup_wizard.texture_import_setup.material_default_value_setters import MaterialDefaultValueSetter


class TextureImporterService:
    def __init__(self, game_texture_importer: GameTextureImporter, material_default_value_setter: MaterialDefaultValueSetter):
        self.game_texture_importer = game_texture_importer
        self.material_default_value_setter = material_default_value_setter

    def import_textures(self):
        return self.game_texture_importer.import_textures()

    def set_default_values(self):
        return self.material_default_value_setter.set_default_values()
