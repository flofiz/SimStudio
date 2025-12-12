"""
Asset Library Module
Handles loading and managing COB light presets and modifiers from JSON files.
"""

import bpy
import os
import json
import math

# Caching variables
_LIGHT_PRESETS_CACHE = None
_MODIFIER_PRESETS_CACHE = None

# Get the addon's assets directory
def get_assets_path():
    """Returns the path to the assets directory"""
    addon_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(addon_dir, "assets")

def reload_assets():
    """Force reload of asset caches"""
    global _LIGHT_PRESETS_CACHE, _MODIFIER_PRESETS_CACHE
    _LIGHT_PRESETS_CACHE = None
    _MODIFIER_PRESETS_CACHE = None
    print(f"Sim Studio: Assets reloaded from {get_assets_path()}")

def get_light_presets():
    """Returns a list of available light presets (cached)"""
    global _LIGHT_PRESETS_CACHE
    if _LIGHT_PRESETS_CACHE is not None:
        return _LIGHT_PRESETS_CACHE
        
    lights_path = os.path.join(get_assets_path(), "lights")
    presets = []
    
    if os.path.exists(lights_path):
        for filename in os.listdir(lights_path):
            if filename.endswith(".json"):
                filepath = os.path.join(lights_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        presets.append({
                            'file': filename,
                            'name': data.get('name', filename),
                            'data': data
                        })
                except Exception as e:
                    print(f"Error loading preset {filename}: {e}")
    
    # Sort by name
    presets.sort(key=lambda x: x['name'])
    _LIGHT_PRESETS_CACHE = presets
    return presets

def get_modifier_presets():
    """Returns a list of available modifier presets (cached)"""
    global _MODIFIER_PRESETS_CACHE
    if _MODIFIER_PRESETS_CACHE is not None:
        return _MODIFIER_PRESETS_CACHE
        
    modifiers_path = os.path.join(get_assets_path(), "modifiers")
    presets = []
    
    if os.path.exists(modifiers_path):
        for filename in os.listdir(modifiers_path):
            if filename.endswith(".json"):
                filepath = os.path.join(modifiers_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        presets.append({
                            'file': filename,
                            'name': data.get('name', filename),
                            'type': data.get('type', 'unknown'),
                            'data': data
                        })
                except Exception as e:
                    print(f"Error loading modifier {filename}: {e}")
    
    # Sort by name
    presets.sort(key=lambda x: x['name'])
    _MODIFIER_PRESETS_CACHE = presets
    return presets

def load_preset_by_name(preset_name, preset_type='light'):
    """Load a specific preset by name"""
    if preset_type == 'light':
        presets = get_light_presets()
    else:
        presets = get_modifier_presets()
    
    for preset in presets:
        if preset['name'] == preset_name:
            return preset['data']
    return None

def apply_light_preset(light_data, preset_data):
    """Apply a COB light preset to a Blender light"""
    if not preset_data or 'specs' not in preset_data:
        return False
    
    specs = preset_data['specs']
    
    # Convert to SPOT for beam angle control
    original_type = light_data.type
    if original_type != 'SPOT':
        light_data.type = 'SPOT'
        bpy.context.view_layer.update()
    
    # Store base values FIRST (before applying power percent)
    base_lumens = specs.get('lumens', 12000)
    light_data['ss_preset_name'] = preset_data.get('name', 'Unknown')
    light_data['ss_base_lumens'] = base_lumens
    light_data['ss_base_beam_angle'] = specs.get('beam_angle_deg', 120)
    light_data['ss_power_watts'] = specs.get('power_watts', 200)
    
    # Initialize power percent to 100% if not set
    if 'ss_power_percent' not in light_data:
        light_data['ss_power_percent'] = 100.0
    
    # Apply energy based on power percent
    power_pct = light_data.get('ss_power_percent', 100.0) / 100.0
    light_data.energy = (base_lumens * power_pct) / 100.0
    light_data['ss_effective_lumens'] = base_lumens * power_pct
    
    # Set color temperature
    light_data.temperature = specs.get('cct_kelvin', 5600)
    
    # Set beam angle
    if light_data.type == 'SPOT':
        beam_angle_rad = math.radians(specs.get('beam_angle_deg', 120))
        light_data.spot_size = min(beam_angle_rad, math.pi)
        light_data.spot_blend = 0.15
    
    return True

def update_power_percent(light_data):
    """Update light energy based on power percentage"""
    base_lumens = light_data.get('ss_base_lumens', 12000)
    power_pct = light_data.get('ss_power_percent', 100.0) / 100.0
    
    # Account for modifiers
    modifiers = light_data.get('ss_modifiers', '')
    modifier_loss = 0
    if modifiers:
        # Rough estimate: each modifier ~20% loss on average
        modifier_loss = len(modifiers.split(',')) * 0.15
    
    effective_lumens = base_lumens * power_pct * (1 - modifier_loss)
    light_data.energy = effective_lumens / 100.0
    light_data['ss_effective_lumens'] = effective_lumens

def apply_modifier_to_light(light_data, modifier_data):
    """Apply a modifier preset to a Blender light"""
    if not modifier_data or 'specs' not in modifier_data:
        return False
    
    specs = modifier_data['specs']
    mod_type = modifier_data.get('type', 'unknown')
    
    # Get base values
    base_lumens = light_data.get('ss_base_lumens', light_data.energy * 100)
    base_angle = light_data.get('ss_base_beam_angle', 120)
    
    # Calculate light loss
    light_loss = specs.get('light_loss_percent', 0) / 100.0
    effective_lumens = base_lumens * (1 - light_loss)
    
    # Apply energy reduction
    light_data.energy = effective_lumens / 100.0
    
    # Handle beam angle changes
    if light_data.type == 'SPOT':
        if mod_type == 'grid':
            # Grids override angle to their output angle
            new_angle = specs.get('output_beam_angle_deg', base_angle)
            light_data.spot_size = math.radians(new_angle)
            light_data.spot_blend = specs.get('edge_falloff', 0.5)
        elif mod_type == 'diffuser':
            # Diffusers add to the angle
            angle_mod = specs.get('beam_angle_modifier_deg', 0)
            new_angle = min(base_angle + angle_mod, 180)
            light_data.spot_size = math.radians(new_angle)
            light_data.spot_blend = specs.get('softness', 0.5)
        elif mod_type == 'softbox':
            new_angle = specs.get('output_beam_angle_deg', 90)
            light_data.spot_size = math.radians(new_angle)
            light_data.spot_blend = specs.get('softness', 0.75)
    
    # Store modifier info
    current_mods = light_data.get('ss_modifiers', '')
    if current_mods:
        light_data['ss_modifiers'] = current_mods + ',' + modifier_data.get('name', 'Unknown')
    else:
        light_data['ss_modifiers'] = modifier_data.get('name', 'Unknown')
    
    light_data['ss_effective_lumens'] = effective_lumens
    
    return True

def clear_modifiers(light_data):
    """Remove all modifiers and restore base values"""
    base_lumens = light_data.get('ss_base_lumens', light_data.energy * 100)
    base_angle = light_data.get('ss_base_beam_angle', 120)
    
    light_data.energy = base_lumens / 100.0
    
    if light_data.type == 'SPOT':
        light_data.spot_size = math.radians(base_angle)
        light_data.spot_blend = 0.15
    
    light_data['ss_modifiers'] = ''
    light_data['ss_effective_lumens'] = base_lumens

def get_enum_items_lights(self, context):
    """Generate enum items for light presets dropdown"""
    items = [('NONE', 'Select Preset...', 'Choose a COB light preset')]
    for preset in get_light_presets():
        items.append((
            preset['file'].replace('.json', ''),
            preset['name'],
            f"Apply {preset['name']} settings"
        ))
    return items

def get_enum_items_modifiers(self, context):
    """Generate enum items for modifier presets dropdown"""
    items = [('NONE', 'Select Modifier...', 'Choose a modifier to add')]
    for preset in get_modifier_presets():
        items.append((
            preset['file'].replace('.json', ''),
            preset['name'],
            f"{preset['data'].get('description', 'Add modifier')}"
        ))
    return items
