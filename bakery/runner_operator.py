from enum import Enum
import bpy
import os

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator


OBJECT_TUPLE_INDEX = 1


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


class B_OT_LibraryOverrideSelectedCollections(Operator):
    """Library override selected objects"""
    bl_idname = "b.library_override_all_collections"
    bl_label = "Bakery: Library Override All Collections"

    def execute(self, context):
        linked_collections = [obj for obj in bpy.data.objects if obj.type == 'EMPTY' and obj.instance_type == 'COLLECTION']
        for linked_collection in linked_collections:
            print(f'Overriding Library for: {linked_collection.name}')
            bpy.context.view_layer.objects.active = linked_collection
            bpy.ops.object.make_override_library()
        return {'FINISHED'}


class B_OT_SpaceOutArmatures(Operator):
    """Space out armatures from each other"""
    bl_idname = "b.space_out_armatures"
    bl_label = "Bakery: Space Out Armatures"

    spacing_factor = 1.0

    def execute(self, context):
        collections = [collection[1] for collection in bpy.data.collections.items()]
        collections.sort(key=lambda x: x.name)  # sort alphabetically by collection name (which is the character's name)
        loc_x = 0

        for collection in collections:
            character_armatures = [
                object for object in collection.objects.items() if \
                    object[OBJECT_TUPLE_INDEX].type == 'ARMATURE' and not object[OBJECT_TUPLE_INDEX].library
            ]  # `not object.library` is important because there seems to be a lingering "ghost" armature that exists
            if character_armatures:
                character_armature = character_armatures[0][OBJECT_TUPLE_INDEX]  # first element in list, then the armature in tuple
                character_armature.location.x = loc_x
                loc_x += self.spacing_factor
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

        character_name = character_blend.replace('.blend', '')
        if action == BatchActions.APPEND:
            bpy.ops.wm.append(
                directory=character_blend_file_path,
                filename=character_name
            )
            print(f'Appending: {character_name} collection in {character_blend}')
        elif action == BatchActions.LINK:
            bpy.ops.wm.link(
                directory=character_blend_file_path,
                filename=character_name
            )
            print(f'Linking: {character_name} collection in {character_blend}')
        else:
            print(f'Unknown action: {action} to perform on {filepath}')
