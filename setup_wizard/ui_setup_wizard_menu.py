import bpy
from bpy.types import Panel


class GI_PT_Setup_Wizard_UI_Layout(Panel):
    bl_label = "Genshin Impact Setup Wizard"
    bl_idname = "GI_PT_Setup_Wizard_UI_Layout"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Genshin"

    def draw(self, context):
        layout = self.layout


class GI_PT_UI_Character_Model_Menu(Panel):
    bl_label = 'Character Model Menu'
    bl_idname = 'GI_PT_UI_Character_Model_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'GI_PT_Setup_Wizard_UI_Layout'

    def draw(self, context):
        layout = self.layout
        # layout.operator(
        #     operator='', 
        #     text='Setup Character Model',
        #     icon='OUTLINER_OB_ARMATURE'
        # )
        
        box = layout.box()
        box.operator(
            operator='file.genshin_import_model', 
            text='Import Character Model',
            icon='OUTLINER_OB_ARMATURE'
        )
        box.label(text='Delete Empties (!!!)')
        # box.operator(
        #     operator='file.genshin_import_model',
        #     text='Delete Empties (!!!)',
        #     icon='TRASH'
        # )


class GI_PT_UI_Materials_Menu(Panel):
    bl_label = 'Materials Menu'
    bl_idname = 'GI_PT_UI_Materials_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'GI_PT_Setup_Wizard_UI_Layout'

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text='Import Materials')
        box.label(text='Replace Default Materials')
        box.label(text='Import Character Textures')


class GI_PT_UI_Outlines_Menu(Panel):
    bl_label = 'Outlines Menu'
    bl_idname = 'GI_PT_UI_Outlines_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'GI_PT_Setup_Wizard_UI_Layout'

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text='Import Outlines')
        box.label(text='Setup Geometry Nodes')
        box.label(text='Import Outline Lightmaps')
        box.label(text='Import Material Data')


class GI_PT_UI_Misc_Setup_Menu(Panel):
    bl_label = 'Misc Setup Menu'
    bl_idname = 'GI_PT_UI_Misc_Setup_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'GI_PT_Setup_Wizard_UI_Layout'

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text='Make Character Upright')
        box.label(text='Setup Head Driver')


class GI_PT_UI_Misc_Menu(Panel):
    bl_label = 'Misc Menu'
    bl_idname = 'GI_PT_UI_Misc_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'GI_PT_Setup_Wizard_UI_Layout'

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text='Set Color Mgmt to Standard')
        box.label(text='Delete EffectMesh & Other Objs')
