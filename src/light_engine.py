import bpy

def watts_to_lumens(watts, type='FLASH'):
    # Luminous efficacy approximations
    efficacy = 35.0  # Xenon Flash
    if type == 'LED':
        efficacy = 90.0
    if type == 'TUNGSTEN':
        efficacy = 15.0
    """
    Convert electrical Watts to Photometric Lumens based on emitter type.
    Includes simplified efficacy logic.
    """
    return watts * efficacy


class SS_OT_convert_to_real_light(bpy.types.Operator):
    """Convert selected light to RealLight (Photometric)"""
    bl_idname = "light.convert_to_real_light"
    bl_label = "Convert to Real Light"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'LIGHT'

    def execute(self, context):
        selected_lights = [obj for obj in context.selected_objects if obj.type == 'LIGHT']
        
        if not selected_lights:
            if context.active_object and context.active_object.type == 'LIGHT':
                selected_lights = [context.active_object]
            else:
                self.report({'WARNING'}, "No lights selected")
                return {'CANCELLED'}
        
        for obj in selected_lights:
            light_data = obj.data
            light_data.use_nodes = True
            tree = light_data.node_tree
            tree.nodes.clear()
            
            # 1. Output Node
            out_node = tree.nodes.new('ShaderNodeOutputLight')
            out_node.location = (300, 0)
            
            # 2. Emission Node
            emission = tree.nodes.new('ShaderNodeEmission')
            emission.location = (0, 0)
            emission.inputs['Strength'].default_value = 1.0
            
            # 3. Blackbody Node
            blackbody = tree.nodes.new('ShaderNodeBlackbody')
            blackbody.location = (-300, 0)
            blackbody.name = "SS_Blackbody"
            
            # CRITICAL: Set initial temperature from Light's native property
            blackbody.inputs['Temperature'].default_value = light_data.temperature
            
            # Add driver to link Blackbody temperature to Light's native temperature
            # This ensures they stay in sync automatically
            driver = blackbody.inputs['Temperature'].driver_add('default_value')
            driver.driver.type = 'AVERAGE'
            
            # Add variable pointing to light.temperature
            var = driver.driver.variables.new()
            var.name = 'temp'
            var.type = 'SINGLE_PROP'
            
            # Set the target
            target = var.targets[0]
            target.id_type = 'LIGHT'
            target.id = light_data
            target.data_path = 'temperature'
            
            # Simple expression: just use the temperature value
            driver.driver.expression = 'temp'
            
            # Links
            tree.links.new(blackbody.outputs['Color'], emission.inputs['Color'])
            tree.links.new(emission.outputs['Emission'], out_node.inputs['Surface'])
            
            # Initialize Properties
            light_data.ss_flash_power = 500.0
            
            self.report({'INFO'}, f"Converted {obj.name} to RealLight (Driver-linked)")
            
        return {'FINISHED'}

def update_light_power(self, context):
    """Callback when ss_flash_power changes"""
    self.energy = self.ss_flash_power

def menu_func(self, context):
    self.layout.operator(SS_OT_convert_to_real_light.bl_idname)
