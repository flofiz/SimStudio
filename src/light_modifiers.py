"""
Light Modifiers Module
Operators for applying COB presets and modifiers to lights.
"""

import bpy
from . import asset_library

class SS_OT_apply_light_preset(bpy.types.Operator):
    """Apply a COB Light Preset to Selected Light"""
    bl_idname = "light.ss_apply_preset"
    bl_label = "Apply Light Preset"
    bl_options = {'REGISTER', 'UNDO'}
    
    preset_name: bpy.props.StringProperty(name="Preset")
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'LIGHT'

    def execute(self, context):
        light = context.active_object.data
        
        # Load preset
        preset_data = asset_library.load_preset_by_name(self.preset_name, 'light')
        if not preset_data:
            self.report({'ERROR'}, f"Preset '{self.preset_name}' not found")
            return {'CANCELLED'}
        
        # Apply preset (handles type conversion internally)
        if asset_library.apply_light_preset(light, preset_data):
            self.report({'INFO'}, f"Applied preset: {preset_data.get('name', 'Unknown')}")
        
        return {'FINISHED'}

class SS_OT_add_modifier(bpy.types.Operator):
    """Add a Modifier to Selected Light"""
    bl_idname = "light.ss_add_modifier"
    bl_label = "Add Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    
    modifier_name: bpy.props.StringProperty(name="Modifier")
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'LIGHT'

    def execute(self, context):
        light = context.active_object.data
        
        # Load modifier
        modifier_data = asset_library.load_preset_by_name(self.modifier_name, 'modifier')
        if not modifier_data:
            self.report({'ERROR'}, f"Modifier '{self.modifier_name}' not found")
            return {'CANCELLED'}
        
        # Apply modifier
        if asset_library.apply_modifier_to_light(light, modifier_data):
            self.report({'INFO'}, f"Added modifier: {modifier_data.get('name', 'Unknown')}")
        
        return {'FINISHED'}

class SS_OT_clear_modifiers(bpy.types.Operator):
    """Remove All Modifiers from Selected Light"""
    bl_idname = "light.ss_clear_modifiers"
    bl_label = "Clear Modifiers"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'LIGHT'

    def execute(self, context):
        light = context.active_object.data
        asset_library.clear_modifiers(light)
        self.report({'INFO'}, "Cleared all modifiers")
        return {'FINISHED'}

# Menu for light presets
class SS_MT_light_presets(bpy.types.Menu):
    bl_label = "COB Light Presets"
    bl_idname = "SS_MT_light_presets"

    def draw(self, context):
        layout = self.layout
        for preset in asset_library.get_light_presets():
            op = layout.operator("light.ss_apply_preset", text=preset['name'])
            op.preset_name = preset['name']

# Menu for modifiers
class SS_MT_modifier_presets(bpy.types.Menu):
    bl_label = "Light Modifiers"
    bl_idname = "SS_MT_modifier_presets"

    def draw(self, context):
        layout = self.layout
        for preset in asset_library.get_modifier_presets():
            op = layout.operator("light.ss_add_modifier", text=preset['name'])
            op.modifier_name = preset['name']

class SS_OT_set_power(bpy.types.Operator):
    """Set COB Light Power Percentage"""
    bl_idname = "light.ss_set_power"
    bl_label = "Set Power %"
    bl_options = {'REGISTER', 'UNDO'}
    
    power_percent: bpy.props.FloatProperty(
        name="Power %",
        default=100.0,
        min=0.0,
        max=100.0,
        subtype='PERCENTAGE'
    )
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'LIGHT'
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        light = context.active_object.data
        light['ss_power_percent'] = self.power_percent
        asset_library.update_power_percent(light)
        return {'FINISHED'}

class SS_OT_spawn_cob(bpy.types.Operator):
    """Spawn a new COB Light Asset"""
    bl_idname = "light.ss_spawn_cob"
    bl_label = "Add COB Light"
    bl_options = {'REGISTER', 'UNDO'}
    
    preset_name: bpy.props.StringProperty(name="Preset Name")
    
    def execute(self, context):
        # 1. Load preset data
        preset_data = asset_library.load_preset_by_name(self.preset_name, 'light')
        if not preset_data:
            self.report({'ERROR'}, f"Preset '{self.preset_name}' not found")
            return {'CANCELLED'}
            
        # 2. Create new Light Data
        light_data = bpy.data.lights.new(name=self.preset_name, type='SPOT')
        
        # 3. Apply Preset
        # We can pass the new light data directly
        asset_library.apply_light_preset(light_data, preset_data)
        
        # 4. Create Object and Link
        light_obj = bpy.data.objects.new(name=self.preset_name, object_data=light_data)
        context.collection.objects.link(light_obj)
        
        # 5. Position at 3D Cursor
        light_obj.location = context.scene.cursor.location
        # Default rotation (pointing down? or forward?)
        # Standard Blender add is usually looking down (-Z) but objects create at 0,0,0
        # Let's leave rotation default (pointing down -Z usually for spots)
        
        # 6. Select and Activate
        bpy.ops.object.select_all(action='DESELECT')
        light_obj.select_set(True)
        context.view_layer.objects.active = light_obj
        
        self.report({'INFO'}, f"Spawned {self.preset_name}")
        return {'FINISHED'}

class SS_OT_reload_assets(bpy.types.Operator):
    """Reload Asset Library from Disk"""
    bl_idname = "light.ss_reload_assets"
    bl_label = "Reload Assets"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        asset_library.reload_assets()
        self.report({'INFO'}, "Assets reloaded")
        return {'FINISHED'}
