from bpy.types import Panel 

class B_PT_EnvironmentSetupWizard_UI_Layout(Panel):
    bl_label = "Environment Setup Wizard"
    bl_idname = "B_PT_EnvironmentSetupWizard_UI_Layout"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Environment Setup Wizard"

    def draw(self, context):
        layout = self.layout
        column = layout.column()

        column.operator(
            operator='genshin_environment.import_materials',
            text='Import Environ. Materials',
            icon='MATERIAL'
        )

        column.operator(
            operator='genshin_environment.import_textures',
            text='Import Environ. Textures',
            icon='TEXTURE'
        )
