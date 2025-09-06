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
        RIM_X_SIZE_ORIGIN = 'Origin-RimX'
        RIM_X_SIZE_SLIDER = 'Slider-RimX'
        RIM_Y_SIZE_ORIGIN = 'Origin-RimY'
        RIM_Y_SIZE_SLIDER = 'Slider-RimY'

        # v4
        ORIGIN_FRESNEL_SIZE = 'Origin-FresnelSize'
        ORIGIN_FRESNEL_TOGGLE = 'Origin-FresnelToggle'
        ORIGIN_RIM_SIZE = 'Origin-RimSize'
        ORIGIN_SHADOW_OFFSET = 'Origin-ShadowOffset'
        SLIDER_FRESNEL_SIZE = 'Slider-FresnelSize'
        SLIDER_FRESNEL_TOGGLE = 'Slider-FresnelToggle'
        SLIDER_RIM_SIZE = 'Slider-RimSize'
        SLIDER_SHADOW_OFFSET = 'Slider-ShadowOffset'

    class GeometryNodeInputs:
        AMBIENT_COLOR_WHEEL = 'Socket_0'
        AMBIENT_COLOR_PICKER = 'Socket_1'
        LIT_COLOR_WHEEL = 'Socket_2'
        LIT_COLOR_PICKER = 'Socket_3'
        SHADOW_COLOR_WHEEL = 'Socket_4'
        SHADOW_COLOR_PICKER = 'Socket_5'
        FRESNEL_TOGGLE_ORIGIN = 'Socket_38'  # v4
        FRESNEL_TOGGLE_SLIDER = 'Socket_37'  # v4
        RIM_LIT_COLOR_WHEEL = 'Socket_6'
        RIM_LIT_COLOR_PICKER = 'Socket_7'
        FRESNEL_COLOR_WHEEL = 'Socket_15'
        FRESNEL_COLOR_PICKER = 'Socket_16'
        FRESNEL_SIZE_ORIGIN = 'Socket_35'  # v4
        FRESNEL_SIZE_SLIDER = 'Socket_36'  # v4
        SOFT_LIT_COLOR_WHEEL = 'Socket_17'
        SOFT_LIT_COLOR_PICKER = 'Socket_18'
        SOFT_SHADOW_COLOR_WHEEL = 'Socket_19'
        SOFT_SHADOW_COLOR_PICKER = 'Socket_22'
        RIM_SHADOW_COLOR_WHEEL = 'Socket_8'
        RIM_SHADOW_COLOR_PICKER = 'Socket_9'
        RIM_X_SIZE_ORIGIN = 'Socket_26'
        RIM_X_SIZE_SLIDER = 'Socket_27'
        RIM_SIZE_ORIGIN = 'Socket_26'  # v4
        RIM_SIZE_SLIDER = 'Socket_27'  # v4
        RIM_Y_SIZE_ORIGIN = 'Socket_28'
        RIM_Y_SIZE_SLIDER = 'Socket_29'
        SHADOW_OFFSET_ORIGIN = 'Socket_28'  # v4
        SHADOW_OFFSET_SLIDER = 'Socket_29'  # v4

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
        (GeometryNodeInputs.RIM_SHADOW_COLOR_PICKER, Objects.RIMSHADOW_COLOR_PICKER),
        (GeometryNodeInputs.RIM_X_SIZE_ORIGIN, Objects.RIM_X_SIZE_ORIGIN),
        (GeometryNodeInputs.RIM_X_SIZE_SLIDER, Objects.RIM_X_SIZE_SLIDER),
        (GeometryNodeInputs.RIM_Y_SIZE_ORIGIN, Objects.RIM_Y_SIZE_ORIGIN),
        (GeometryNodeInputs.RIM_Y_SIZE_SLIDER, Objects.RIM_Y_SIZE_SLIDER),
        (GeometryNodeInputs.FRESNEL_TOGGLE_ORIGIN, Objects.ORIGIN_FRESNEL_TOGGLE),  # v4
        (GeometryNodeInputs.FRESNEL_TOGGLE_SLIDER, Objects.SLIDER_FRESNEL_TOGGLE),  # v4
        (GeometryNodeInputs.FRESNEL_SIZE_ORIGIN, Objects.ORIGIN_FRESNEL_SIZE),  # v4
        (GeometryNodeInputs.FRESNEL_SIZE_SLIDER, Objects.SLIDER_FRESNEL_SIZE),  # v4
        (GeometryNodeInputs.RIM_SIZE_ORIGIN, Objects.ORIGIN_RIM_SIZE),  # v4
        (GeometryNodeInputs.RIM_SIZE_SLIDER, Objects.SLIDER_RIM_SIZE),  # v4
        (GeometryNodeInputs.SHADOW_OFFSET_ORIGIN, Objects.ORIGIN_SHADOW_OFFSET),  # v4
        (GeometryNodeInputs.SHADOW_OFFSET_SLIDER, Objects.SLIDER_SHADOW_OFFSET),  # v4
    ]
