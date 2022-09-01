# Written by Mken from Discord

import bpy
from bpy.types import Operator

from setup_wizard.import_order import invoke_next_step
from setup_wizard.models import CustomOperatorProperties

CAMERA_INPUT = 'Input_4'
DEPTH_OFFSET_INPUT = 'Input_8'

CAMERA_NAME = 'Camera'
FACE_MESH_NAME = 'Face'
FACE_EYE_MESH_NAME = 'Face_Eye'
GEOMETRY_NODES_PREFIX = 'GeometryNodes'


class GI_OT_FixMouthOutlines(Operator, CustomOperatorProperties):
    '''Fixes mouth outlines by assigning 'Camera' to Face outlines and applies a Depth Offset'''
    bl_idname = 'genshin.fix_mouth_outlines'
    bl_label = 'Genshin: Fix Mouth Outlines'

    def execute(self, context):
        self.fix_face_mouth_outlines_protruding_out(self.next_step_idx)
        return {'FINISHED'}

    def fix_face_mouth_outlines_protruding_out(self, next_step_idx):
        camera = bpy.context.scene.objects.get(CAMERA_NAME)
        if not camera:
            camera = self.create_camera(CAMERA_NAME)

        face_objects = [object for object in bpy.data.objects \
            if FACE_MESH_NAME in object.name and FACE_EYE_MESH_NAME not in object.name]
        for face_object in face_objects:
            outline_modifiers = [outline_modifier for outline_modifier in face_object.modifiers.values() \
                if GEOMETRY_NODES_PREFIX in outline_modifier.name]
            self.set_camera_and_depth_offset(outline_modifiers, camera)
            self.fix_meshes_by_setting_genshin_materials(face_object.name)

        if next_step_idx:
            invoke_next_step(next_step_idx)


    def set_camera_and_depth_offset(self, outline_modifiers, camera):
        for outline_modifier in outline_modifiers:
            outline_modifier[CAMERA_INPUT] = camera
            outline_modifier[DEPTH_OFFSET_INPUT] = 3.0
            self.set_camera_in_front_of_armature(camera)


    def create_camera(self, camera_name):
        camera_data = bpy.data.cameras.new(name=camera_name)
        camera = bpy.data.objects.new(camera_name, camera_data)
        bpy.context.scene.collection.objects.link(camera)

        return camera


    def set_camera_in_front_of_armature(self, camera):
        for object in bpy.context.scene.objects:
            if object.type == 'ARMATURE':
                camera.location = object.location
                break
        camera.location[1] += -1.5  # y-axis, facing character
        camera.location[2] += 1.3  # z-axis, head level
        camera.rotation_euler[0] = 1.5708  # x-axis, 90 degrees 
        camera.rotation_euler[2] = 0  # z-axis, facing character


    def fix_meshes_by_setting_genshin_materials(self, mesh_name):
        for material_slot_name, material_slot in bpy.context.scene.objects[mesh_name].material_slots.items():
            bpy.context.scene.objects[mesh_name].material_slots.get(material_slot_name).material = material_slot.material


register, unregister = bpy.utils.register_classes_factory(GI_OT_FixMouthOutlines)
