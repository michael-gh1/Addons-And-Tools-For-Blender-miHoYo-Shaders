import bpy
import json
import math
import mathutils

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, CollectionProperty
from bpy.types import Operator, PropertyGroup
import os


class GI_OT_ImportAnimation(Operator, ImportHelper):
    """Import Animation"""
    bl_idname = "genshin.import_animation"
    bl_label = "Genshin: Import Animation"

    # ImportHelper mixin class uses this
    filename_ext = "*.*"

    import_path: StringProperty(
        name="Path",
        description="Path to the animation json data files",
        default="",
        subtype='DIR_PATH'
    )

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    files: CollectionProperty(type=PropertyGroup)

    def execute(self, context):
        directory_file_path = os.path.dirname(self.filepath)

        for file in self.files:
            fp = open(f'{directory_file_path}/{file.name}')
            json_animation_data = json.load(fp)

            armature = [object for object in bpy.data.objects if object.type == 'ARMATURE'][0]  # assuming one armature only!
            data_bones = json_animation_data['AnimationClip']['m_RotationCurves']  # list for all bones

            for data_bone in data_bones:
                # Get the actual bone
                armature_bones = armature.pose.bones
                path_to_bone = data_bone.get('path')
                bone_family = path_to_bone.split('/')

                final_child_bone = None

                for bone_family_member in bone_family:
                    final_child_bone = armature_bones.get(bone_family_member)
                    if not final_child_bone:
                        print(bone_family_member)

                if not final_child_bone:
                    continue

                # Assign data
                armature_bone_keyframe_data = data_bone['curve']['m_Curve']  # list of kf
                curr_frame = 0
                for armature_bone_keyframe in armature_bone_keyframe_data:  # this is top-level bones
                    armature_rotation_values = armature_bone_keyframe.get('value')
                    w, x, y, z = \
                        armature_rotation_values.get('w'), \
                        armature_rotation_values.get('x'), \
                        armature_rotation_values.get('y'), \
                        armature_rotation_values.get('z')
                        # armature_rotation_values.get('w'), \
                        # armature_rotation_values.get('z'), \
                        # armature_rotation_values.get('x'), \
                        # armature_rotation_values.get('y')
                    final_child_bone.rotation_quaternion = (w, x, y, z)
                    unity_to_blender_conversion = mathutils.Euler(
                        (0.0, 0.0, math.radians(90.0)), 
                        'XYZ'
                    ).to_quaternion()
                    # final_child_bone.rotation_quaternion += unity_to_blender_conversion
                    

                    final_child_bone.keyframe_insert('rotation_quaternion', frame=curr_frame)
                    curr_frame += 1


        self.report({'INFO'}, 'Imported animation data')
        return {'FINISHED'}


register, unregister = bpy.utils.register_classes_factory(GI_OT_ImportAnimation)
