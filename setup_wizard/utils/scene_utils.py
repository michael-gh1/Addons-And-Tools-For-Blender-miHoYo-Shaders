import bpy


def move_objects_between_scenes(source_scene_name, target_scene_name=None, object_names=None, target_collection_name=None):
    """
    Move objects from source scene to target scene
    
    Args:
        source_scene_name: Name of the scene to move objects from
        target_scene_name: Name of the target scene (None for current scene)
        object_names: List of object names to move (None to move all objects)
        target_collection_name: Name of the collection to move objects to (None for scene collection)
    """
    source_scene = bpy.data.scenes.get(source_scene_name)
    if not source_scene:
        print(f"Source scene '{source_scene_name}' not found")
        return

    target_scene = bpy.data.scenes.get(target_scene_name) if target_scene_name else bpy.context.scene

    if target_collection_name:
        target_collection = target_scene.collection.children.get(target_collection_name)
        if not target_collection:
            target_collection = target_scene.collection
    else:
        target_collection = target_scene.collection

    if object_names:
        objects_to_move = [obj for obj in source_scene.objects if obj.name in object_names]
    else:
        objects_to_move = list(source_scene.objects)

    for obj in objects_to_move:
        source_scene.collection.objects.unlink(obj)
        target_collection.objects.link(obj)

        collection_info = f" to collection '{target_collection_name}'" if target_collection_name else ""
        print(f"INFO: Moved object '{obj.name}' from '{source_scene.name}' to '{target_scene.name}'{collection_info}")