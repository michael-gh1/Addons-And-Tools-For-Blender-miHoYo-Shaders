from bpy.types import Panel 

class B_PT_Bakery_UI_Layout(Panel):
    bl_label = "Bakery (Batch Job Runner)"
    bl_idname = "B_PT_Bakery_UI_Layout"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Batch Runner"

    def draw(self, context):
        layout = self.layout
        column = layout.column()

        column.operator(
            operator='b.batch_append',
            text='Run Batch Append Job',
            icon='PLAY'
        )

        column.operator(
            operator='b.batch_link',
            text='Run Batch Link Job',
            icon='PLAY'
        )

        column.operator(
            operator='b.library_override_all_collections',
            text='Library Override All Collections',
            icon='PLAY'
        )

        column.operator(
            operator='b.space_out_armatures',
            text='Space Out Armatures',
            icon='PLAY'
        )

        column.operator(
            operator='b.hide_eyestar',
            text='Bulk: Hide EyeStar',
            icon='PLAY'
        )

        column.operator(
            operator='b.set_rimlight',
            text='Bulk: Set Rimlight',
            icon='PLAY'
        )

        column.operator(
            operator='b.toggle_rimlight',
            text='Bulk: Toggle Rimlight',
            icon='PLAY'
        )
