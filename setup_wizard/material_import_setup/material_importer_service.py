
from setup_wizard.material_import_setup.game_material_importers import GameMaterialImporter


class MaterialImporterService:
    def __init__(self, game_material_importer: GameMaterialImporter):
        self.game_material_importer = game_material_importer

    def import_materials(self):
        return self.game_material_importer.import_materials()
