import bpy
import os

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator

class B_OT_Bakery(Operator):
    """Execute batch job"""
    bl_idname = "b.bakery"
    bl_label = "Bakery: Execute Batch Job"

    def exec(self, context):
        pass

class B_OT_BatchAppend(Operator, ImportHelper):
    """Append batch of characters"""
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
        character_blends_directory = os.path.dirname(self.filepath)
        character_blends = os.listdir(character_blends_directory)

        filtered_character_blends = list(filter(lambda x: x.endswith('.blend'), character_blends))

        for character_blend in filtered_character_blends:
            character_blend_file_path = os.path.join(
                character_blends_directory,
                character_blend,
                'Collection'
            )
            bpy.ops.wm.append(
                directory=character_blend_file_path,
                filename='Collection'
            )
            print(f'Appending: {character_blend}')

        loc_x = 0
        character_armatures = [object for object in bpy.data.objects if object.type == 'ARMATURE']
        character_armatures.sort(key=lambda x: x.name)
        for character_armature in character_armatures:
            character_armature.location.x = loc_x
            loc_x += 1
        return {'FINISHED'}
