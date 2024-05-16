class LightingPanelNames:
    class Bones:
        LIGHTING_PANEL = 'Lighting Panel'

    class Collections:
        LIGHTING_PANEL = 'Lighting Panel'
        WIDGET_COLLECTION = 'lighting panel wgt'
        WHEEL = 'Wheel'
        PICKER = 'Picker'

    class Objects:
        LIGHTING_PANEL = 'Lighting Panel'
        AMBIENT_COLOR_PICKER = 'ColorPicker-Ambient'
        FRESNEL_COLOR_PICKER = 'ColorPicker-Fresnel'
        LIT_COLOR_PICKER = 'ColorPicker-Lit'
        RIMLIT_COLOR_PICKER = 'ColorPicker-RimLit'
        RIMSHADOW_COLOR_PICKER = 'ColorPicker-RimShadow'
        SHADOW_COLOR_PICKER = 'ColorPicker-Shadow'
        SOFTLIT_COLOR_PICKER = 'ColorPicker-SoftLit'
        SOFTSHADOW_COLOR_PICKER = 'ColorPicker-SoftShadow'
        AMBIENT_COLOR_WHEEL = 'ColorWheel-Ambient'
        FRESNEL_COLOR_WHEEL = 'ColorWheel-Fresnel'
        LIT_COLOR_WHEEL = 'ColorWheel-Lit'
        RIMLIT_COLOR_WHEEL = 'ColorWheel-RimLit'
        RIMSHADOW_COLOR_WHEEL = 'ColorWheel-RimShadow'
        SHADOW_COLOR_WHEEL = 'ColorWheel-Shadow'
        SOFTLIT_COLOR_WHEEL = 'ColorWheel-SoftLit'
        SOFTSHADOW_COLOR_WHEEL = 'ColorWheel-SoftShadow'

    class GeometryNodeInputs:
        AMBIENT_COLOR_WHEEL = 'Socket_0'
        AMBIENT_COLOR_PICKER = 'Socket_1'
        LIT_COLOR_WHEEL = 'Socket_2'
        LIT_COLOR_PICKER = 'Socket_3'
        SHADOW_COLOR_WHEEL = 'Socket_4'
        SHADOW_COLOR_PICKER = 'Socket_5'
        RIM_LIT_COLOR_WHEEL = 'Socket_6'
        RIM_LIT_COLOR_PICKER = 'Socket_7'
        FRESNEL_COLOR_WHEEL = 'Socket_15'
        FRESNEL_COLOR_PICKER = 'Socket_16'
        SOFT_LIT_COLOR_WHEEL = 'Socket_17'
        SOFT_LIT_COLOR_PICKER = 'Socket_18'
        SOFT_SHADOW_COLOR_WHEEL = 'Socket_19'
        SOFT_SHADOW_COLOR_PICKER = 'Socket_22'
        RIM_SHADOW_COLOR_WHEEL = 'Socket_8'
        RIM_SHADOW_COLOR_PICKER = 'Socket_9'

    FILENAME = 'LightingPanel.blend'
    LIGHT_VECTORS_MODIFIER_INPUT_NAME_TO_OBJECT_NAME = [
        (GeometryNodeInputs.AMBIENT_COLOR_WHEEL, Objects.AMBIENT_COLOR_WHEEL),
        (GeometryNodeInputs.AMBIENT_COLOR_PICKER, Objects.AMBIENT_COLOR_PICKER),
        (GeometryNodeInputs.LIT_COLOR_WHEEL, Objects.LIT_COLOR_WHEEL),
        (GeometryNodeInputs.LIT_COLOR_PICKER, Objects.LIT_COLOR_PICKER),
        (GeometryNodeInputs.SHADOW_COLOR_WHEEL, Objects.SHADOW_COLOR_WHEEL),
        (GeometryNodeInputs.SHADOW_COLOR_PICKER, Objects.SHADOW_COLOR_PICKER),
        (GeometryNodeInputs.RIM_LIT_COLOR_WHEEL, Objects.RIMLIT_COLOR_WHEEL),
        (GeometryNodeInputs.RIM_LIT_COLOR_PICKER, Objects.RIMLIT_COLOR_PICKER),
        (GeometryNodeInputs.FRESNEL_COLOR_WHEEL, Objects.FRESNEL_COLOR_WHEEL),
        (GeometryNodeInputs.FRESNEL_COLOR_PICKER, Objects.FRESNEL_COLOR_PICKER),
        (GeometryNodeInputs.SOFT_LIT_COLOR_WHEEL, Objects.SOFTLIT_COLOR_WHEEL),
        (GeometryNodeInputs.SOFT_LIT_COLOR_PICKER, Objects.SOFTLIT_COLOR_PICKER),
        (GeometryNodeInputs.SOFT_SHADOW_COLOR_WHEEL, Objects.SOFTSHADOW_COLOR_WHEEL),
        (GeometryNodeInputs.SOFT_SHADOW_COLOR_PICKER, Objects.SOFTSHADOW_COLOR_PICKER),
        (GeometryNodeInputs.RIM_SHADOW_COLOR_WHEEL, Objects.RIMSHADOW_COLOR_WHEEL),
        (GeometryNodeInputs.RIM_SHADOW_COLOR_PICKER, Objects.RIMSHADOW_COLOR_PICKER)
    ]
