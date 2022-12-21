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

        return {'FINISHED'}
