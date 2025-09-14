# Author: michael-gh1

import bpy
from functools import wraps


def preserve_context(func):
    """
    Decorator that preserves the active object and mode before function execution
    and restores them after the function completes.
    Useful for adding new context-sensitive operations without breaking existing functionality.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        initial_active_object = bpy.context.object
        initial_mode = bpy.context.object.mode if bpy.context.object else None

        try:
            # Execute the original function
            result = func(*args, **kwargs)
            return result
        finally:
            # Always restore the context, even if function raises an exception
            if initial_active_object:
                bpy.context.view_layer.objects.active = initial_active_object
            if initial_mode and bpy.context.object and bpy.context.object.mode != initial_mode:
                bpy.ops.object.mode_set(mode=initial_mode)
    return wrapper
