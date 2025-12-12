import bpy
import math

def calculate_ev(iso, aperture, shutter_speed):
    """
    Calculate EV (Exposure Value) based on camera settings.
    EV = log2(N^2 / t) - log2(ISO/100)
    """
    # Safety checks
    if shutter_speed <= 0: shutter_speed = 0.001
    if iso <= 0: iso = 100
    if aperture <= 0: aperture = 1.4
    
    # EV at ISO 100
    ev_100 = math.log2((aperture ** 2) / shutter_speed)
    
    # ISO adjustment
    iso_shift = math.log2(iso / 100.0)
    
    return ev_100 - iso_shift

class SS_OT_apply_exposure(bpy.types.Operator):
    """Apply Physical Camera Exposure to Scene"""
    bl_idname = "camera.ss_apply_exposure"
    bl_label = "Apply Exposure"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.camera and context.scene.camera.type == 'CAMERA'

    def execute(self, context):
        cam_data = context.scene.camera.data
        
        iso = cam_data.ss_iso
        aperture = cam_data.ss_fstop
        shutter = cam_data.ss_shutter_speed
        
        ev = calculate_ev(iso, aperture, shutter)
        calibration = context.scene.ss_exposure_calibration
        
        # Apply: Lower EV means brighter image, so we negate
        context.scene.view_settings.exposure = -ev + calibration
        
        self.report({'INFO'}, f"Applied EV {ev:.1f} (Exposure: {context.scene.view_settings.exposure:.2f})")
        return {'FINISHED'}

class SS_OT_reset_exposure(bpy.types.Operator):
    """Reset Scene Exposure to Default"""
    bl_idname = "camera.ss_reset_exposure"
    bl_label = "Reset Exposure"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.view_settings.exposure = 0.0
        self.report({'INFO'}, "Exposure reset to 0")
        return {'FINISHED'}

# Callback for property changes (only updates if user wants auto-update)
def update_camera_exposure(self, context):
    """Optional: Auto-update when properties change"""
    # Currently disabled - user clicks Apply manually
    pass
