# Author: michael-gh1

import bpy
from bpy.types import Operator
from setup_wizard.geometry_nodes_setup.game_geometry_nodes_setup_service import GameGeometryNodesSetupService
from setup_wizard.geometry_nodes_setup.geometry_nodes_setups import GameGeometryNodesSetupFactory

from setup_wizard.import_order import NextStepInvoker
from setup_wizard.setup_wizard_operator_base_classes import CustomOperatorProperties


class GI_OT_SetUpGeometryNodes(Operator, CustomOperatorProperties):
    '''Sets Up Geometry Nodes for Outlines'''
    bl_idname = 'genshin.setup_geometry_nodes'
    bl_label = 'Genshin: Setup Geometry Nodes'

    report_message_level = {'INFO'}
    report_message = []

    def execute(self, context):
        try:
            game_geometry_nodes_setup = GameGeometryNodesSetupFactory.create(self.game_type, self, context)

            geometry_nodes_service = GameGeometryNodesSetupService(game_geometry_nodes_setup)
            geometry_nodes_service.setup_geometry_nodes()

            NextStepInvoker().invoke(
                self.next_step_idx, 
                self.invoker_type, 
                high_level_step_name=self.high_level_step_name,
                game_type=self.game_type,
            )
        except Exception as ex:
            raise ex
        finally:
            super().clear_custom_properties()

        self.report(self.report_message_level, str(self.report_message + ['Successfully set up geometry nodes (for outlines)']))
        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory(GI_OT_SetUpGeometryNodes)
