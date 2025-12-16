"""
Geometry Nodes Generator for Diffusion Frame (Scrim) Rigs
Generates procedural geometry for diffusion frames with dual support legs.
Based on Manfrotto Pro Scrim Medium specifications.
"""

import bpy
import math


def create_scrim_rig_nodetree(name="SimStudio_Scrim_Rig"):
    """Create or return the Geometry Nodes tree for the scrim rig"""
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]
    
    # Create new node group
    ng = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    ng.use_fake_user = True
    
    is_blender_4 = bpy.app.version >= (4, 0, 0)
    
    if is_blender_4:
        # Clear existing interface if any
        for item in list(ng.interface.items_tree):
            ng.interface.remove(item)
        
        # Frame Height (Linear) - Height of the frame center
        sock = ng.interface.new_socket(name="Frame Height", in_out='INPUT', socket_type='NodeSocketFloat')
        sock.default_value = 1.5
        sock.min_value = 0.5
        sock.max_value = 3.0
        
        # Tilt (Rotation around local horizontal axis) - Only frame tilts, legs stay vertical
        sock = ng.interface.new_socket(name="Tilt", in_out='INPUT', socket_type='NodeSocketFloat')
        sock.default_value = 0.0
        sock.min_value = -1.57
        sock.max_value = 1.57
        sock.subtype = 'ANGLE'
        
        # Pan (Rotation Z) - Entire rig rotates including legs
        sock = ng.interface.new_socket(name="Pan", in_out='INPUT', socket_type='NodeSocketFloat')
        sock.default_value = 0.0
        sock.subtype = 'ANGLE'
        
        # Geometry Output
        ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
        
    else:
        # Legacy Blender < 4.0
        ng.inputs.clear()
        ng.outputs.clear()
        ng.inputs.new('NodeSocketFloat', "Frame Height")
        ng.inputs[-1].default_value = 1.5
        ng.inputs.new('NodeSocketFloat', "Tilt")
        ng.inputs.new('NodeSocketFloat', "Pan")
        ng.outputs.new('NodeSocketGeometry', "Geometry")
    
    # Build the node tree
    construct_scrim_nodes(ng)
    
    return ng


def construct_scrim_nodes(ng):
    """Builds the internal nodes for the scrim rig"""
    nodes = ng.nodes
    links = ng.links
    
    nodes.clear()
    
    # --- Input/Output ---
    node_in = nodes.new('NodeGroupInput')
    node_in.location = (-1200, 0)
    
    node_out = nodes.new('NodeGroupOutput')
    node_out.location = (1200, 0)
    
    is_blender_4 = bpy.app.version >= (4, 0, 0)
    
    # === CONSTANTS (from Manfrotto Pro Scrim Medium specs) ===
    LEG_RADIUS = 0.0175      # 35mm diameter legs
    LEG_HEIGHT = 2.0         # Leg height (will be adjusted dynamically)
    LEG_SPACING = 1.2        # Distance between legs (slightly wider than frame)
    FRAME_TUBE_RADIUS = 0.0125  # 25mm diameter frame tubes
    PANEL_WIDTH = 1.1        # 110cm
    PANEL_HEIGHT = 2.0       # 200cm
    
    # ============================================
    # SECTION 1: LEFT LEG (Cylinder)
    # ============================================
    cyl_leg_left = nodes.new('GeometryNodeMeshCylinder')
    cyl_leg_left.inputs['Vertices'].default_value = 16
    cyl_leg_left.inputs['Radius'].default_value = LEG_RADIUS
    cyl_leg_left.inputs['Depth'].default_value = LEG_HEIGHT
    cyl_leg_left.location = (-800, -300)
    
    # Position left leg: move up by half height, offset left
    trans_leg_left = nodes.new('GeometryNodeTransform')
    trans_leg_left.inputs['Translation'].default_value = (-LEG_SPACING / 2, 0, LEG_HEIGHT / 2)
    trans_leg_left.location = (-600, -300)
    
    links.new(cyl_leg_left.outputs['Mesh'], trans_leg_left.inputs['Geometry'])
    
    # ============================================
    # SECTION 2: RIGHT LEG (Cylinder)
    # ============================================
    cyl_leg_right = nodes.new('GeometryNodeMeshCylinder')
    cyl_leg_right.inputs['Vertices'].default_value = 16
    cyl_leg_right.inputs['Radius'].default_value = LEG_RADIUS
    cyl_leg_right.inputs['Depth'].default_value = LEG_HEIGHT
    cyl_leg_right.location = (-800, -500)
    
    # Position right leg: move up by half height, offset right
    trans_leg_right = nodes.new('GeometryNodeTransform')
    trans_leg_right.inputs['Translation'].default_value = (LEG_SPACING / 2, 0, LEG_HEIGHT / 2)
    trans_leg_right.location = (-600, -500)
    
    links.new(cyl_leg_right.outputs['Mesh'], trans_leg_right.inputs['Geometry'])
    
    # ============================================
    # SECTION 3: JOIN LEGS
    # ============================================
    join_legs = nodes.new('GeometryNodeJoinGeometry')
    join_legs.location = (-400, -400)
    
    links.new(trans_leg_left.outputs['Geometry'], join_legs.inputs['Geometry'])
    links.new(trans_leg_right.outputs['Geometry'], join_legs.inputs['Geometry'])
    
    # ============================================
    # SECTION 4: FRAME (4 tubes forming rectangle)
    # ============================================
    # We'll create 4 cylinders for the frame edges
    
    # -- Top horizontal bar --
    frame_top = nodes.new('GeometryNodeMeshCylinder')
    frame_top.inputs['Vertices'].default_value = 12
    frame_top.inputs['Radius'].default_value = FRAME_TUBE_RADIUS
    frame_top.inputs['Depth'].default_value = PANEL_WIDTH
    frame_top.location = (-800, 200)
    
    trans_frame_top = nodes.new('GeometryNodeTransform')
    trans_frame_top.inputs['Translation'].default_value = (0, 0, PANEL_HEIGHT / 2)
    trans_frame_top.inputs['Rotation'].default_value = (0, math.radians(90), 0)  # Rotate to horizontal
    trans_frame_top.location = (-600, 200)
    
    links.new(frame_top.outputs['Mesh'], trans_frame_top.inputs['Geometry'])
    
    # -- Bottom horizontal bar --
    frame_bottom = nodes.new('GeometryNodeMeshCylinder')
    frame_bottom.inputs['Vertices'].default_value = 12
    frame_bottom.inputs['Radius'].default_value = FRAME_TUBE_RADIUS
    frame_bottom.inputs['Depth'].default_value = PANEL_WIDTH
    frame_bottom.location = (-800, 50)
    
    trans_frame_bottom = nodes.new('GeometryNodeTransform')
    trans_frame_bottom.inputs['Translation'].default_value = (0, 0, -PANEL_HEIGHT / 2)
    trans_frame_bottom.inputs['Rotation'].default_value = (0, math.radians(90), 0)
    trans_frame_bottom.location = (-600, 50)
    
    links.new(frame_bottom.outputs['Mesh'], trans_frame_bottom.inputs['Geometry'])
    
    # -- Left vertical bar --
    frame_left = nodes.new('GeometryNodeMeshCylinder')
    frame_left.inputs['Vertices'].default_value = 12
    frame_left.inputs['Radius'].default_value = FRAME_TUBE_RADIUS
    frame_left.inputs['Depth'].default_value = PANEL_HEIGHT
    frame_left.location = (-800, -100)
    
    trans_frame_left = nodes.new('GeometryNodeTransform')
    trans_frame_left.inputs['Translation'].default_value = (-PANEL_WIDTH / 2, 0, 0)
    trans_frame_left.location = (-600, -100)
    
    links.new(frame_left.outputs['Mesh'], trans_frame_left.inputs['Geometry'])
    
    # -- Right vertical bar --
    frame_right = nodes.new('GeometryNodeMeshCylinder')
    frame_right.inputs['Vertices'].default_value = 12
    frame_right.inputs['Radius'].default_value = FRAME_TUBE_RADIUS
    frame_right.inputs['Depth'].default_value = PANEL_HEIGHT
    frame_right.location = (-800, -200)
    
    trans_frame_right = nodes.new('GeometryNodeTransform')
    trans_frame_right.inputs['Translation'].default_value = (PANEL_WIDTH / 2, 0, 0)
    trans_frame_right.location = (-600, -200)
    
    links.new(frame_right.outputs['Mesh'], trans_frame_right.inputs['Geometry'])
    
    # ============================================
    # SECTION 5: DIFFUSION PANEL (Plane)
    # ============================================
    panel = nodes.new('GeometryNodeMeshGrid')
    panel.inputs['Size X'].default_value = PANEL_WIDTH
    panel.inputs['Size Y'].default_value = PANEL_HEIGHT
    panel.inputs['Vertices X'].default_value = 4
    panel.inputs['Vertices Y'].default_value = 4
    panel.location = (-800, 400)
    
    # Rotate panel to face forward (Y axis) - default grid is XY plane
    trans_panel = nodes.new('GeometryNodeTransform')
    trans_panel.inputs['Rotation'].default_value = (math.radians(90), 0, 0)
    trans_panel.location = (-600, 400)
    
    links.new(panel.outputs['Mesh'], trans_panel.inputs['Geometry'])
    
    # ============================================
    # SECTION 6: JOIN FRAME + PANEL
    # ============================================
    join_frame = nodes.new('GeometryNodeJoinGeometry')
    join_frame.location = (-400, 200)
    
    links.new(trans_frame_top.outputs['Geometry'], join_frame.inputs['Geometry'])
    links.new(trans_frame_bottom.outputs['Geometry'], join_frame.inputs['Geometry'])
    links.new(trans_frame_left.outputs['Geometry'], join_frame.inputs['Geometry'])
    links.new(trans_frame_right.outputs['Geometry'], join_frame.inputs['Geometry'])
    links.new(trans_panel.outputs['Geometry'], join_frame.inputs['Geometry'])
    
    # ============================================
    # SECTION 7: APPLY TILT TO FRAME ONLY
    # ============================================
    # Tilt rotates around local X axis (tilts forward/backward)
    trans_frame_tilt = nodes.new('GeometryNodeTransform')
    trans_frame_tilt.location = (-200, 200)
    
    # Combine XYZ for Tilt rotation
    combine_tilt = nodes.new('ShaderNodeCombineXYZ')
    combine_tilt.location = (-400, 350)
    
    if is_blender_4:
        links.new(node_in.outputs['Tilt'], combine_tilt.inputs['X'])
    else:
        links.new(node_in.outputs[1], combine_tilt.inputs['X'])
    
    links.new(combine_tilt.outputs['Vector'], trans_frame_tilt.inputs['Rotation'])
    links.new(join_frame.outputs['Geometry'], trans_frame_tilt.inputs['Geometry'])
    
    # ============================================
    # SECTION 8: TRANSLATE FRAME TO HEIGHT
    # ============================================
    trans_frame_height = nodes.new('GeometryNodeTransform')
    trans_frame_height.location = (0, 200)
    
    combine_height = nodes.new('ShaderNodeCombineXYZ')
    combine_height.location = (-200, 350)
    
    if is_blender_4:
        links.new(node_in.outputs['Frame Height'], combine_height.inputs['Z'])
    else:
        links.new(node_in.outputs[0], combine_height.inputs['Z'])
    
    links.new(combine_height.outputs['Vector'], trans_frame_height.inputs['Translation'])
    links.new(trans_frame_tilt.outputs['Geometry'], trans_frame_height.inputs['Geometry'])
    
    # ============================================
    # SECTION 9: JOIN LEGS + FRAME
    # ============================================
    join_all = nodes.new('GeometryNodeJoinGeometry')
    join_all.location = (200, 0)
    
    links.new(join_legs.outputs['Geometry'], join_all.inputs['Geometry'])
    links.new(trans_frame_height.outputs['Geometry'], join_all.inputs['Geometry'])
    
    # ============================================
    # SECTION 10: APPLY PAN TO EVERYTHING
    # ============================================
    trans_pan = nodes.new('GeometryNodeTransform')
    trans_pan.location = (400, 0)
    
    combine_pan = nodes.new('ShaderNodeCombineXYZ')
    combine_pan.location = (200, 150)
    
    if is_blender_4:
        links.new(node_in.outputs['Pan'], combine_pan.inputs['Z'])
    else:
        links.new(node_in.outputs[2], combine_pan.inputs['Z'])
    
    links.new(combine_pan.outputs['Vector'], trans_pan.inputs['Rotation'])
    links.new(join_all.outputs['Geometry'], trans_pan.inputs['Geometry'])
    
    # ============================================
    # SECTION 11: SET MATERIAL
    # ============================================
    set_material = nodes.new('GeometryNodeSetMaterial')
    set_material.location = (600, 0)
    
    links.new(trans_pan.outputs['Geometry'], set_material.inputs['Geometry'])
    
    # Create or get the diffuser material
    mat = get_or_create_diffuser_material()
    if mat:
        set_material.inputs['Material'].default_value = mat
    
    # ============================================
    # OUTPUT
    # ============================================
    links.new(set_material.outputs['Geometry'], node_out.inputs['Geometry'])


def get_or_create_diffuser_material(name="SimStudio_Diffuser_Fabric"):
    """Create or return the diffuser fabric material"""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.use_fake_user = True
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create output node
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # Create Principled BSDF
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    
    # Configure for diffuser fabric
    principled.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1.0)  # White
    principled.inputs['Roughness'].default_value = 0.8  # Matte fabric
    
    # Transmission for translucency (Blender 4.0+ uses different input names)
    if bpy.app.version >= (4, 0, 0):
        if 'Transmission Weight' in principled.inputs:
            principled.inputs['Transmission Weight'].default_value = 0.5
        elif 'Transmission' in principled.inputs:
            principled.inputs['Transmission'].default_value = 0.5
    else:
        principled.inputs['Transmission'].default_value = 0.5
    
    # Subsurface for fabric-like light scattering
    if bpy.app.version >= (4, 0, 0):
        if 'Subsurface Weight' in principled.inputs:
            principled.inputs['Subsurface Weight'].default_value = 0.1
        elif 'Subsurface' in principled.inputs:
            principled.inputs['Subsurface'].default_value = 0.1
    else:
        principled.inputs['Subsurface'].default_value = 0.1
    
    # Link to output
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat
