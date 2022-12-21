import bpy

from bakery.ui_bakery import B_PT_Bakery_UI_Layout
from bakery.runner_operator import B_OT_Bakery, B_OT_BatchAppend

bl_info = {
    "name": "Bakery (Batch Job Runner)",
    "author": "Mken",
    "version": (1, 0, 0),
    "blender": (3, 3, 1),
    "location": "3D View > Sidebar > Bakery",
    "description": "[PLACEHOLDER]",
    "warning": "",
    "doc_url": "",
    "support": 'COMMUNITY',
    "category": "miHoYo",
    "tracker_url": "",
    "doc_url": ""
}

classes = [
    B_PT_Bakery_UI_Layout,
    B_OT_Bakery,
    B_OT_BatchAppend,
]

register, unregister = bpy.utils.register_classes_factory(classes)
