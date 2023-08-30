# Author: michael-gh1

from setup_wizard.outline_import_setup.outline_importers import GameOutlineNodeGroupImporter


class GameOutlineImporterService:
    def __init__(self, game_outline_importer: GameOutlineNodeGroupImporter):
        self.game_outline_importer = game_outline_importer

    def import_outlines(self):
        return self.game_outline_importer.import_outline_node_group()
