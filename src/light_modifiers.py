"""
Light Modifiers Module
Operators for applying COB presets and modifiers to lights.
"""

import bpy
from . import asset_library

def get_target_light(context):
    """
    Resolve the actual Light object.
    - If active object is a Light, return it.
    - If active object is a Rig (Mesh), try to find the child Light.
    """
    obj = context.active_object
    if not obj:
        return None
        
    if obj.type == 'LIGHT':
        return obj
    
    # Check if it's a Rig (parent of a light or has specific prop)
    # Simple check: Is a light parented to it?
    if obj.children:
        for child in obj.children:
            if child.type == 'LIGHT':
                return child
                
    return None

class SS_OT_apply_light_preset(bpy.types.Operator):
    """Apply a COB preset to the selected light"""
    bl_idname = "light.ss_apply_preset"
    bl_label = "Apply COB Preset"
    bl_options = {'REGISTER', 'UNDO'}
    
    preset_name: bpy.props.StringProperty()
    
    @classmethod
    def poll(cls, context):
        return get_target_light(context) is not None
        
    def execute(self, context):
        light_obj = get_target_light(context)
        if not light_obj:
            return {'CANCELLED'}
        light_data = light_obj.data
        preset_data = asset_library.load_preset_by_name(self.preset_name, 'light')
        
        if asset_library.apply_light_preset(light_data, preset_data):
            self.report({'INFO'}, f"Applied preset: {self.preset_name}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to apply preset")
            return {'CANCELLED'}

class SS_OT_add_modifier(bpy.types.Operator):
    """Add a modifier to the active light"""
    bl_idname = "light.ss_add_modifier"
    bl_label = "Add Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    
    modifier_name: bpy.props.StringProperty()
    
    @classmethod
    def poll(cls, context):
        return get_target_light(context) is not None
        
    def execute(self, context):
        light_obj = get_target_light(context)
        if not light_obj:
            return {'CANCELLED'}
        light_data = light_obj.data
        
        modifier_data = asset_library.load_preset_by_name(self.modifier_name, 'modifier')
        if not modifier_data:
            self.report({'ERROR'}, f"Modifier '{self.modifier_name}' not found")
            return {'CANCELLED'}
            
        asset_library.apply_modifier_to_light(light_data, modifier_data)
        
        # Check for GN Rig and update visualization (POC)
        # If parent is Rig, likely has GN inputs
        if light_obj.parent and light_obj.parent.modifiers.get("SimStudio Rig"):
             # If "Show Diffuser" logic applies
             # For POC, if modifier type is 'softbox' or 'diffuser', enable
             m_type = modifier_data.get('type', '')
             if 'diffuser' in m_type or 'softbox' in m_type:
                  light_obj.parent.modifiers["SimStudio Rig"]["Show Diffuser"] = True

        return {'FINISHED'}

class SS_OT_clear_modifiers(bpy.types.Operator):
    """Clear all modifiers from the active light"""
    bl_idname = "light.ss_clear_modifiers"
    bl_label = "Clear Modifiers"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return get_target_light(context) is not None
        
    def execute(self, context):
        light_obj = get_target_light(context)
        if not light_obj:
            return {'CANCELLED'}
        asset_library.clear_modifiers(light_obj.data)
        
        # Update GN POC
        if light_obj.parent and light_obj.parent.modifiers.get("SimStudio Rig"):
             light_obj.parent.modifiers["SimStudio Rig"]["Show Diffuser"] = False

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
        return get_target_light(context) is not None
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        light_obj = get_target_light(context)
        if not light_obj:
            return {'CANCELLED'}
        light_data = light_obj.data
        light_data['ss_power_percent'] = self.power_percent
        asset_library.update_power_percent(light_data)
        return {'FINISHED'}

class SS_OT_spawn_cob(bpy.types.Operator):
    """Spawn a new COB Light Asset"""
    bl_idname = "light.ss_spawn_cob"
    bl_label = "Add COB Light"
    bl_options = {'REGISTER', 'UNDO'}
    
    preset_name: bpy.props.StringProperty(name="Preset Name")
    
    def execute(self, context):
        import math
        from . import geometry_nodes, asset_library
        
        # 1. Load preset data
        preset_data = asset_library.load_preset_by_name(self.preset_name, 'light')
        if not preset_data:
            self.report({'ERROR'}, f"Preset '{self.preset_name}' not found")
            return {'CANCELLED'}

        # 2. Create the Rig Object (Mesh)
        # Unique name based on preset
        safe_name = self.preset_name.replace(" ", "_")
        mesh = bpy.data.meshes.new(f"{safe_name}_Rig_Mesh")
        rig_obj = bpy.data.objects.new(f"{safe_name}_Rig", mesh)
        context.collection.objects.link(rig_obj)
        rig_obj.location = context.scene.cursor.location
        
        # Store metadata on Rig
        rig_obj['ss_asset_type'] = 'light_rig'
        rig_obj['ss_preset_name'] = self.preset_name
        
        # 3. Add Geometry Nodes Modifier (Shared Tree)
        mod = rig_obj.modifiers.new(name="SimStudio Rig", type='NODES')
        node_group = geometry_nodes.get_cob_rig_nodetree()
        mod.node_group = node_group
        
        # 4. Spawn the Actual Light
        light_data = bpy.data.lights.new(name=f"{safe_name}_Light", type='SPOT')
        light_obj = bpy.data.objects.new(f"{safe_name}_Light", light_data)
        context.collection.objects.link(light_obj)
        
        # 5. Apply Preset Properties to Light
        asset_library.apply_light_preset(light_data, preset_data)
        
        # 6. Sync Light to Rig via Robust Drivers
        light_obj.parent = rig_obj
        # Offset logic: Pivot is at cube front face (GN offset), light is at pivot (0,0,0)
        light_obj.location = (0, 0, 0)
        
        # Helper to find identifier (Define inside or import?)
        def get_input_identifier(ng, name):
            if bpy.app.version >= (4, 0, 0):
                if hasattr(ng, 'interface'):
                    for item in ng.interface.items_tree:
                        if item.name == name:
                            return f'["{item.identifier}"]' 
            else:
                for item in ng.inputs:
                    if item.name == name:
                        return f'["{item.identifier}"]'
            return f'["{name}"]'

        # Driver for Location Z -> Modifier "Tripod Height"
        h_id = get_input_identifier(node_group, "Tripod Height")
        d = light_obj.driver_add("location", 2)
        var = d.driver.variables.new()
        var.name = "h"
        var.type = 'SINGLE_PROP'
        var.targets[0].id = rig_obj
        var.targets[0].data_path = f'modifiers["SimStudio Rig"]{h_id}' 
        d.driver.expression = "h"
        
        # Driver for Rotation X -> Modifier "Tilt"
        tilt_id = get_input_identifier(node_group, "Tilt")
        d = light_obj.driver_add("rotation_euler", 0)
        var = d.driver.variables.new()
        var.name = "tilt"
        var.type = 'SINGLE_PROP'
        var.targets[0].id = rig_obj
        var.targets[0].data_path = f'modifiers["SimStudio Rig"]{tilt_id}'
        d.driver.expression = "tilt"
        
        # Driver for Rotation Z -> Modifier "Pan"
        pan_id = get_input_identifier(node_group, "Pan")
        d = light_obj.driver_add("rotation_euler", 2) 
        var = d.driver.variables.new()
        var.name = "pan"
        var.type = 'SINGLE_PROP'
        var.targets[0].id = rig_obj
        var.targets[0].data_path = f'modifiers["SimStudio Rig"]{pan_id}'
        d.driver.expression = "pan"
        
        # 7. Select Rig
        bpy.ops.object.select_all(action='DESELECT')
        rig_obj.select_set(True)
        context.view_layer.objects.active = rig_obj
        
        self.report({'INFO'}, f"Spawned {self.preset_name} (GN)")
        return {'FINISHED'}




class SS_OT_spawn_diffusion_frame(bpy.types.Operator):
    """Spawn a Diffusion Frame (Scrim) with Geometry Nodes Rig"""
    bl_idname = "light.ss_spawn_diffusion_frame"
    bl_label = "Add Diffusion Frame"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        from . import geometry_nodes_scrim
        
        # 1. Create the Rig Object (Mesh)
        mesh = bpy.data.meshes.new("Scrim_Rig_Mesh")
        rig_obj = bpy.data.objects.new("Diffusion_Frame_110x200", mesh)
        context.collection.objects.link(rig_obj)
        rig_obj.location = context.scene.cursor.location
        
        # 2. Add Geometry Nodes Modifier
        mod = rig_obj.modifiers.new(name="SimStudio Scrim Rig", type='NODES')
        node_group = geometry_nodes_scrim.create_scrim_rig_nodetree()
        mod.node_group = node_group
        
        # 3. Store asset info
        rig_obj['ss_asset_type'] = 'diffusion_frame'
        rig_obj['ss_asset_name'] = 'Diffusion Frame 110x200'
        rig_obj['ss_reference'] = 'Manfrotto Pro Scrim Medium (MLLC1201K)'
        
        # 4. Select the Rig
        bpy.ops.object.select_all(action='DESELECT')
        rig_obj.select_set(True)
        context.view_layer.objects.active = rig_obj
        
        self.report({'INFO'}, "Spawned Diffusion Frame (110x200cm)")
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
