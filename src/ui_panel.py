import bpy
from . import light_engine
from . import asset_library

class SS_PT_light_mixer(bpy.types.Panel):
    """Creates a Panel in the 3D View N-Panel"""
    bl_label = "Light Mixer"
    bl_idname = "SS_PT_light_mixer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Sim Studio'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # ===== ASSET LIBRARY =====
        row = layout.row()
        row.label(text="Light Library", icon='ASSET_MANAGER')
        row.operator("light.ss_reload_assets", text="", icon='FILE_REFRESH')
        
        # Scrollable list style (using a box/col)
        lib_box = layout.box()
        lib_col = lib_box.column(align=True)
        
        from . import asset_library # Ensure import is available
        
        presets = asset_library.get_light_presets()
        if not presets:
            lib_col.label(text="No assets found", icon='ERROR')
            lib_col.label(text=f"Path: {asset_library.get_assets_path()}", icon='INFO')
        else:
            for preset in presets:
                # Row with Icon and Add Button
                row = lib_col.row(align=True)
                # We don't have real thumbnails yet, use generic icon
                row.label(text=preset['name'], icon='LIGHT')
                op = row.operator("light.ss_spawn_cob", text="Add", icon='ADD')
                op.preset_name = preset['name']
        
        layout.separator()

        # Tools Header
        row = layout.row()
        row.operator("scene.export_lighting_diagram", icon='FILE', text="Export Diagram")

        # ===== SELECTED LIGHT SETTINGS =====
        obj = context.active_object
        if obj and obj.type == 'LIGHT':
            layout.separator()
            box = layout.box()
            box.label(text="Modifier Stack", icon='MODIFIER')
            
            # Show current preset info
            preset_name = obj.data.get('ss_preset_name', None)
            if preset_name:
                row = box.row()
                row.label(text=f"Base: {preset_name}", icon='LIGHT')
                
                # Power percentage slider
                power_pct = obj.data.get('ss_power_percent', 100.0)
                row = box.row(align=True)
                row.label(text="Power:")
                
                # Custom slider using operator
                sub = row.row(align=True)
                sub.scale_x = 2.0
                op = sub.operator("light.ss_set_power", text=f"{power_pct:.0f}%")
                op.power_percent = power_pct
                
                # Show wattage info
                power_watts = obj.data.get('ss_power_watts', 0)
                if power_watts > 0:
                    actual_watts = power_watts * (power_pct / 100.0)
                    row.label(text=f"({actual_watts:.0f}W / {power_watts}W)")
                
                # Show effective values
                base_lumens = obj.data.get('ss_base_lumens', 0)
                eff_lumens = obj.data.get('ss_effective_lumens', base_lumens)
                if base_lumens > 0:
                    box.label(text=f"Output: {int(eff_lumens):,} lm")
            else:
                 box.label(text="Light is not a SimStudio Asset", icon='INFO')
                 box.operator("light.ss_apply_preset", text="Convert to Asset")
            
            # Modifiers section (Available for all lights, but best for assets)
            box.separator()
            
            mod_presets = asset_library.get_modifier_presets()
            if not mod_presets:
                box.label(text="No modifiers found!", icon='ERROR')
                box.label(text="Check assets/modifiers folder", icon='INFO')
            else:
                row = box.row()
                row.menu("SS_MT_modifier_presets", text="Add Modifier", icon='MODIFIER')
                # Check for active modifiers to enable clear button
                if obj.data.get('ss_modifiers', ''):
                    row.operator("light.ss_clear_modifiers", text="", icon='X')
            
            # Show active modifiers
            modifiers = obj.data.get('ss_modifiers', '')
            if modifiers:
                mod_box = box.box()
                mod_box.label(text="Active Modifiers:", icon='PREFERENCES')
                for mod in modifiers.split(','):
                    if mod.strip():
                        mod_box.label(text=f"  • {mod.strip()}")
        else:
            box = layout.box()
            box.label(text="Select a light to configure", icon='INFO')

        # ===== CAMERA SECTION =====
        layout.separator()
        layout.label(text="Physical Camera", icon='CAMERA_DATA')
        
        cam = scene.camera
        if cam and cam.type == 'CAMERA':
            box = layout.box()
            box.label(text=f"Active: {cam.name}")
            
            col = box.column(align=True)
            col.prop(cam.data, "ss_iso")
            col.prop(cam.data, "ss_fstop")
            
            row = col.row(align=True)
            row.prop(cam.data, "ss_shutter_speed", text="Shutter")
            if cam.data.ss_shutter_speed > 0:
                denom = 1.0 / cam.data.ss_shutter_speed
                row.label(text=f"(1/{int(denom)})")
            
            col.separator()
            col.prop(scene, "ss_exposure_calibration")
            
            row = box.row(align=True)
            row.operator("camera.ss_apply_exposure", text="Apply", icon='CHECKMARK')
            row.operator("camera.ss_reset_exposure", text="Reset", icon='LOOP_BACK')
            
            box.label(text=f"Current Exposure: {scene.view_settings.exposure:.2f}")
        else:
            layout.label(text="No active camera", icon='INFO')

        # ===== LIGHTS LIST =====
        layout.separator()
        layout.label(text="Scene Lights", icon='LIGHT')

        lights = [o for o in scene.objects if o.type == 'LIGHT']
        
        if not lights:
            layout.label(text="No lights in scene", icon='INFO')
            return

        col = layout.column(align=True)
        for light_obj in lights:
            box = col.box()
            row = box.row()
            
            row.prop(light_obj, "hide_viewport", text="", icon='HIDE_OFF' if not light_obj.hide_viewport else 'HIDE_ON', emboss=False)
            row.label(text=light_obj.name)
            
            # Show preset indicator
            preset = light_obj.data.get('ss_preset_name', None)
            if preset:
                row.label(text=f"[{preset}]")
            
            if hasattr(light_obj.data, "ss_flash_power"):
                row.prop(light_obj.data, "ss_flash_power", text="Ws")
            else:
                row.prop(light_obj.data, "energy", text="W")
            
            row.prop(light_obj.data, "temperature", text="K")
