from bpy.props import IntProperty, StringProperty

class CustomOperatorProperties:
    next_step_idx: IntProperty()
    file_directory: StringProperty()
    invoker_type: StringProperty()
    high_level_step_name: StringProperty()
