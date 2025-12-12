import bpy
import mathutils

def snap_modifier_to_light(modifier_obj, threshold=0.5):
    """
    Checks if the modifier_obj is close to a Light object.
    If so, parent it to the light and reset transforms.
    """
    # Find all lights in the scene
    lights = [o for o in bpy.context.scene.objects if o.type == 'LIGHT']
    
    closest_light = None
    min_dist = float('inf')
    
    for light in lights:
        dist = (light.location - modifier_obj.location).length
        if dist < min_dist:
            min_dist = dist
            closest_light = light
            
    if closest_light and min_dist < threshold:
        # Snap!
        modifier_obj.parent = closest_light
        modifier_obj.matrix_parent_inverse = closest_light.matrix_world.inverted()
        
        # Reset location (assume origin of modifier matches mount point)
        modifier_obj.location = (0, 0, 0)
        
        # Align rotation? Usually modifiers face -Y or -Z. 
        # For now, let's keep rotation as is or zero it out.
        modifier_obj.rotation_euler = (0, 0, 0)
        
        print(f"B_SIM: Snapped {modifier_obj.name} to {closest_light.name}")
        return True
        
    return False

# Post-operation handler to detect new objects (Drag & Drop usually triggers this)
# Note: Blender doesn't have a direct "OnDragDrop" event for Python.
# We rely on depsgraph_update_post or detecting new objects.

from bpy.app.handlers import persistent

_last_object_names = set()

@persistent
def on_depsgraph_update(scene, depsgraph):
    # This is heavy, we need a better trigger.
    # Alternatives: `bpy.msgbus` on 'kb_item' (unreliable).
    # Standard way for Asset Browser drag and drop:
    # There isn't one. The asset is appended/linked.
    # We can check if active object changed and is a mesh?
    pass

# Better approach for Drag & Drop detection in 4.0:
# Define an operator that runs AFTER the drop? No.
# Use a Timer? No.

# Let's use the 'depsgraph_update_post' but filter carefully.
# Actally, standard Asset Browser drop selects the new object.
# We can check if the active object is a Mesh and has no parent.

@persistent
def auto_attach_handler(scene):
    obj = bpy.context.active_object
    if not obj:
        return
        
    # Check if we just added this object?
    # Hard to distinguish "Just Added" from "Just Selected".
    # But usually, when dragging an asset, it is placed at cursor or on surface.
    
    # We will add a manual operator "Attach to Closest Light" to be safe first,
    # OR we try to be smart: if name implies modifier?
    
    # Let's keep it simple: Add an operator `SS_OT_attach_modifier` 
    # and maybe a modal operator that runs in background? No, that's heavy.
    
    # For this POC, we will implement the logic in an operator 
    # that the user can call, OR verify if we can hook into the Drop.
    pass

class SS_OT_attach_to_light(bpy.types.Operator):
    """Attaches selected object to the closest light source"""
    bl_idname = "object.ss_attach_to_light"
    bl_label = "Attach to Closest Light"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'

    def execute(self, context):
        obj = context.active_object
        if snap_modifier_to_light(obj):
            self.report({'INFO'}, f"Attached to light")
        else:
            self.report({'WARNING'}, "No light nearby to attach to")
        return {'FINISHED'}
