bl_info = {
    "name": "Simulation Studio",
    "author": "Your Name",
    "version": (0, 5, 0),
    "blender": (4, 0, 0),
    "location": "View3D > N-Panel > Sim Studio",
    "description": "Photo Studio Simulation Tools with COB Lights and Modifiers",
    "category": "Lighting",
}

import bpy

from . import light_engine
from . import asset_handler
from . import ui_panel
from . import diagram_generator
from . import camera_sim
from . import asset_library
from . import light_modifiers

classes = (
    light_engine.SS_OT_convert_to_real_light,
    asset_handler.SS_OT_attach_to_light,
    ui_panel.SS_PT_light_mixer,
    diagram_generator.SS_OT_export_diagram,
    camera_sim.SS_OT_apply_exposure,
    camera_sim.SS_OT_reset_exposure,
    light_modifiers.SS_OT_apply_light_preset,
    light_modifiers.SS_OT_add_modifier,
    light_modifiers.SS_OT_clear_modifiers,
    light_modifiers.SS_OT_set_power,
    light_modifiers.SS_OT_spawn_cob,
    light_modifiers.SS_OT_spawn_cob_poc,
    light_modifiers.SS_OT_reload_assets,
    light_modifiers.SS_MT_light_presets,
    light_modifiers.SS_MT_modifier_presets,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.VIEW3D_MT_object.append(light_engine.menu_func)
    
    # Light Properties
    bpy.types.Light.ss_flash_power = bpy.props.FloatProperty(
        name="Flash Power (Ws)",
        description="Power in Watt-Seconds",
        default=500.0,
        min=0.0,
        update=light_engine.update_light_power
    )
    
    # Camera Properties
    bpy.types.Camera.ss_iso = bpy.props.IntProperty(
        name="ISO",
        default=100,
        min=10,
        max=128000
    )
    
    bpy.types.Camera.ss_fstop = bpy.props.FloatProperty(
        name="f-stop",
        default=2.8,
        min=0.1,
        max=128.0
    )
    
    bpy.types.Camera.ss_shutter_speed = bpy.props.FloatProperty(
        name="Shutter (s)",
        description="Shutter speed in seconds",
        default=0.02,
        min=0.0001,
        max=300.0
    )
    
    # Global Calibration
    bpy.types.Scene.ss_exposure_calibration = bpy.props.FloatProperty(
        name="EV Offset",
        description="Calibration offset for exposure simulation",
        default=0.0,
        min=-20.0,
        max=20.0
    )

def unregister():
    bpy.types.VIEW3D_MT_object.remove(light_engine.menu_func)
    
    del bpy.types.Light.ss_flash_power
    del bpy.types.Camera.ss_iso
    del bpy.types.Camera.ss_fstop
    del bpy.types.Camera.ss_shutter_speed
    del bpy.types.Scene.ss_exposure_calibration
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
