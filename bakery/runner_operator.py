from enum import Enum
import bpy
import os

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator


class BatchActions(Enum):
    APPEND = 'APPEND_ACTION'
    LINK = 'LINK_ACITON'


class B_OT_Bakery(Operator):
    """Execute batch job"""
    bl_idname = "b.bakery"
    bl_label = "Bakery: Execute Batch Job"

    def exec(self, context):
        pass

class B_OT_BatchAppend(Operator, ImportHelper):
    """Batch append characters"""
    bl_idname = "b.batch_append"
    bl_label = "Bakery: Batch Append"

    # ImportHelper mixin class uses this
    filename_ext = "*.*"

    import_path: StringProperty(
        name="Path",
        description="Path to the folder of the Model",
        default="",
        subtype='DIR_PATH'
    )

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        batch_action(self.filepath, BatchActions.APPEND)
        return {'FINISHED'}


class B_OT_BatchLink(Operator, ImportHelper):
    """Batch link characters"""
    bl_idname = "b.batch_link"
    bl_label = "Bakery: Batch Link"

    # ImportHelper mixin class uses this
    filename_ext = "*.*"

    import_path: StringProperty(
        name="Path",
        description="Path to the folder of the Model",
        default="",
        subtype='DIR_PATH'
    )

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        batch_action(self.filepath, BatchActions.LINK)
        return {'FINISHED'}


def batch_action(filepath, action):
    character_blends_directory = os.path.dirname(filepath)
    character_blends = os.listdir(character_blends_directory)

    filtered_character_blends = list(filter(lambda x: x.endswith('.blend'), character_blends))

    for character_blend in filtered_character_blends:
        character_blend_file_path = os.path.join(
            character_blends_directory,
            character_blend,
            'Collection'
        )
        if action == BatchActions.APPEND:
            bpy.ops.wm.append(
                directory=character_blend_file_path,
                filename='Collection'
            )
            print(f'Appending: {character_blend}')
        elif action == BatchActions.LINK:
            bpy.ops.wm.link(
                directory=character_blend_file_path,
                filename='Collection'
            )
            print(f'Linking: {character_blend}')
        else:
            print(f'Unknown action: {action} to perform on {filepath}')

    loc_x = 0
    character_armatures = [object for object in bpy.data.objects if object.type == 'ARMATURE']
    character_armatures.sort(key=lambda x: x.name)  # TODO: Does not actually sort correctly
    for character_armature in character_armatures:
        character_armature.location.x = loc_x
        loc_x += 1
