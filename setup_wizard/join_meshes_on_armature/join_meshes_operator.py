# Author: michael-gh1

import bpy
from bpy.types import Operator

from setup_wizard.domain.game_types import GameType
from setup_wizard.domain.mesh_names import MeshNames
from setup_wizard.import_order import NextStepInvoker
from setup_wizard.setup_wizard_operator_base_classes import CustomOperatorProperties


class GI_OT_JoinMeshesOnArmature(Operator, CustomOperatorProperties):
    '''Joins Meshes on Armature'''
    bl_idname = 'hoyoverse.join_meshes_on_armature'
    bl_label = 'HoYoverse: Join Meshes on Armature'

    def execute(self, context):
        join_meshes = self.game_type == GameType.GENSHIN_IMPACT.name

        if join_meshes:
            self.__join_face_meshes()

        if self.next_step_idx:
            NextStepInvoker().invoke(
                self.next_step_idx, 
                self.invoker_type, 
                high_level_step_name=self.high_level_step_name,
                game_type=self.game_type,
            )
        return {'FINISHED'}

    def __join_face_meshes(self):
        face_mesh = bpy.data.objects.get(MeshNames.FACE)
        face_eye_mesh = bpy.data.objects.get(MeshNames.FACE_EYE)
        brow_mesh = bpy.data.objects.get(MeshNames.Brow)

        bpy.ops.object.select_all(action='DESELECT')
        face_mesh.select_set(True)
        face_eye_mesh.select_set(True)
        brow_mesh.select_set(True)
        bpy.context.view_layer.objects.active = face_mesh
        print(f'Joining {face_eye_mesh}, {brow_mesh} to {face_mesh}')
        bpy.ops.object.join()

