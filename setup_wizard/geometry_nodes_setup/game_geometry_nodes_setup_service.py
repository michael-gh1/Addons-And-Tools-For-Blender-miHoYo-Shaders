# Author: michael-gh1

from setup_wizard.geometry_nodes_setup.geometry_nodes_setups import GameGeometryNodesSetup


class GameGeometryNodesSetupService:
    def __init__(self, game_geometry_nodes_setup: GameGeometryNodesSetup):
        self.game_geometry_nodes_setup = game_geometry_nodes_setup

    def setup_geometry_nodes(self):
        self.game_geometry_nodes_setup.setup_geometry_nodes()
