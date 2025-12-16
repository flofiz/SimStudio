"""
Geometry Nodes Generator for Sim Studio Light Rigs
Generates the procedural geometry for tripods and light bodies.
"""

import bpy
import math

def create_light_rig_nodetree(name="SimStudio_Light_Rig"):
    """Create or return the Geometry Nodes tree for the light rig"""
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]
    
    # Create new node group
    ng = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    
    # Enable "fake user" to keep it
    ng.use_fake_user = True
    
    # Inputs
    # We will use the Interface API for Blender 4.0+ correctness
    # If 4.0+, use ng.interface.new_socket
    # If < 4.0, use ng.inputs.new
    
    is_blender_4 = bpy.app.version >= (4, 0, 0)
    
    if is_blender_4:
        # Clear existing interface if any (rebuilding)
        for item in ng.interface.items_tree:
            ng.interface.remove(item)
            
        # Tripod Height (Linear)
        sock = ng.interface.new_socket(name="Tripod Height", in_out='INPUT', socket_type='NodeSocketFloat')
        sock.default_value = 1.5
        sock.min_value = 0.5
        sock.max_value = 3.0
        # Note: Python API for setting Gizmos on sockets is experimental/undocumented in some 4.x versions.
        # We will try standard property access if available, otherwise fallback to standard inputs.
        # The user specifically asked for "nodes", maybe "Transform Logic" inside the tree?
        # But assuming Group Input Gizmos:
        
        # Tilt (Rotation X)
        sock = ng.interface.new_socket(name="Tilt", in_out='INPUT', socket_type='NodeSocketFloat')
        sock.default_value = 0.0
        sock.min_value = -1.57
        sock.max_value = 1.57
        sock.subtype = 'ANGLE'
        
        # Pan (Rotation Z)
        sock = ng.interface.new_socket(name="Pan", in_out='INPUT', socket_type='NodeSocketFloat')
        sock.default_value = 0.0
        sock.subtype = 'ANGLE'

        # Modifiers Toggles
        ng.interface.new_socket(name="Show Diffuser", in_out='INPUT', socket_type='NodeSocketBool')
        ng.interface.new_socket(name="Show Frame", in_out='INPUT', socket_type='NodeSocketBool')
        
        # Geometry Output
        ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
        
    else:
        # Legacy support
        ng.inputs.clear()
        ng.outputs.clear()
        ng.inputs.new('NodeSocketFloat', "Tripod Height")
        # ... (Legacy logic abbreviated for brevity, assuming Blender 4.0+ focus)
        ng.inputs[-1].default_value = 1.5
        ng.inputs.new('NodeSocketFloat', "Tilt")
        ng.inputs.new('NodeSocketFloat', "Pan")
        ng.inputs.new('NodeSocketBool', "Show Diffuser")
        ng.inputs.new('NodeSocketBool', "Show Frame")
        ng.outputs.new('NodeSocketGeometry', "Geometry")

    # Construct the Node Tree
    construct_nodes(ng)
    
    return ng

def construct_nodes(ng):
    """Builds the internal nodes for the rig"""
    nodes = ng.nodes
    links = ng.links
    
    # Clear default nodes
    nodes.clear()
    
    # --- Input/Output ---
    node_in = nodes.new('NodeGroupInput')
    node_in.location = (-1000, 0)
    
    node_out = nodes.new('NodeGroupOutput')
    node_out.location = (1000, 0)
    
    # --- 1. Tripod Base (Fixed Cylinder) ---
    cyl_base = nodes.new('GeometryNodeMeshCylinder')
    cyl_base.inputs['Vertices'].default_value = 32
    cyl_base.inputs['Radius'].default_value = 0.05
    cyl_base.inputs['Depth'].default_value = 1.0
    cyl_base.location = (-600, -200)
    
    trans_base = nodes.new('GeometryNodeTransform')
    trans_base.inputs['Translation'].default_value = (0, 0, 0.5)
    trans_base.location = (-400, -200)
    
    links.new(cyl_base.outputs['Mesh'], trans_base.inputs['Geometry'])
    
    # --- 2. Tripod Pole ---
    # Simplified visual: One Cylinder scaled/translated? 
    # Let's keep the user's structure or simplifying it.
    # Just linking base for now to Main Join.
    
    join_geo = nodes.new('GeometryNodeJoinGeometry')
    join_geo.location = (800, 0)
    
    links.new(trans_base.outputs['Geometry'], join_geo.inputs['Geometry'])
    
    # --- 3. Projector Head (Cube) ---
    cube_head = nodes.new('GeometryNodeMeshCube')
    cube_head.inputs['Size'].default_value = (0.2, 0.2, 0.2)
    cube_head.location = (-600, 600)
    
    # Offset Cube so its "Bottom" (-Z) face is at 0,0,0
    # This ensures the Light (which is at 0,0,0) sits on the surface, not inside.
    trans_cube_offset = nodes.new('GeometryNodeTransform')
    trans_cube_offset.inputs['Translation'].default_value = (0, 0, 0.1) # Move up 10cm
    trans_cube_offset.location = (-400, 600)
    
    # --- 4. Modifiers Logic (Diffuser & Frame) ---
    # We will join Diffuser and Frame to the Head geometry BEFORE transforming the whole head.
    
    join_head_parts = nodes.new('GeometryNodeJoinGeometry')
    join_head_parts.location = (-200, 600)
    
    links.new(cube_head.outputs['Mesh'], trans_cube_offset.inputs['Geometry'])
    links.new(trans_cube_offset.outputs['Geometry'], join_head_parts.inputs['Geometry'])
    
    # A. Diffuser Cone
    cone = nodes.new('GeometryNodeMeshCone')
    cone.inputs['Radius Bottom'].default_value = 0.3
    cone.inputs['Radius Top'].default_value = 0.1
    cone.inputs['Depth'].default_value = 0.4
    cone.location = (-600, 800)
    
    trans_cone = nodes.new('GeometryNodeTransform')
    trans_cone.inputs['Translation'].default_value = (0, 0, -0.3)
    trans_cone.location = (-400, 800)
    links.new(cone.outputs['Mesh'], trans_cone.inputs['Geometry'])
    
    switch_diff = nodes.new('GeometryNodeSwitch')
    switch_diff.input_type = 'GEOMETRY' 
    switch_diff.location = (-200, 800)
    links.new(trans_cone.outputs['Geometry'], switch_diff.inputs['True'])
    
    # B. Diffusion Frame
    # Curve Rectangle
    rect_curve = nodes.new('GeometryNodeCurvePrimitiveQuadrilateral')
    rect_curve.inputs['Width'].default_value = 0.6
    rect_curve.inputs['Height'].default_value = 0.6
    rect_curve.location = (-600, 1000)
    
    # Profile (Circle)
    profile_curve = nodes.new('GeometryNodeCurvePrimitiveCircle')
    profile_curve.inputs['Radius'].default_value = 0.01
    profile_curve.location = (-600, 900)
    
    # Curve to Mesh
    curve_to_mesh = nodes.new('GeometryNodeCurveToMesh')
    curve_to_mesh.location = (-400, 1000)
    links.new(rect_curve.outputs['Curve'], curve_to_mesh.inputs['Curve'])
    links.new(profile_curve.outputs['Curve'], curve_to_mesh.inputs['Profile Curve'])
    
    # Transform Frame (Position it)
    trans_frame = nodes.new('GeometryNodeTransform')
    trans_frame.inputs['Translation'].default_value = (0, 0, -0.55) # In front of cone
    trans_frame.location = (-200, 1000)
    links.new(curve_to_mesh.outputs['Mesh'], trans_frame.inputs['Geometry'])
    
    # Switch Frame
    switch_frame = nodes.new('GeometryNodeSwitch')
    switch_frame.input_type = 'GEOMETRY'
    switch_frame.location = (0, 1000)
    links.new(trans_frame.outputs['Geometry'], switch_frame.inputs['True'])
    
    # Connect Switches to Head Join
    links.new(switch_diff.outputs['Output'], join_head_parts.inputs['Geometry'])
    links.new(switch_frame.outputs['Output'], join_head_parts.inputs['Geometry'])
    
    # --- 5. Transform Head ---
    trans_head = nodes.new('GeometryNodeTransform')
    trans_head.location = (200, 600)
    links.new(join_head_parts.outputs['Geometry'], trans_head.inputs['Geometry'])
    
    # Drivers for Head Transform
    # Translation Z = Height
    combine_xyz = nodes.new('ShaderNodeCombineXYZ')
    combine_xyz.location = (0, 400)
    
    # Rotation
    combine_rot = nodes.new('ShaderNodeCombineXYZ')
    combine_rot.location = (0, 500)
    
    # Linking Inputs
    is_v4 = bpy.app.version >= (4, 0, 0)
    
    if is_v4:
        links.new(node_in.outputs.get('Tripod Height') or node_in.outputs[0], combine_xyz.inputs['Z'])
        links.new(node_in.outputs.get('Tilt') or node_in.outputs[1], combine_rot.inputs['X'])
        links.new(node_in.outputs.get('Pan') or node_in.outputs[2], combine_rot.inputs['Z'])
        links.new(node_in.outputs.get('Show Diffuser') or node_in.outputs[3], switch_diff.inputs['Switch'])
        links.new(node_in.outputs.get('Show Frame') or node_in.outputs[4], switch_frame.inputs['Switch'])
    else:
        links.new(node_in.outputs[0], combine_xyz.inputs['Z'])
        links.new(node_in.outputs[1], combine_rot.inputs['X'])
        links.new(node_in.outputs[2], combine_rot.inputs['Z'])
        links.new(node_in.outputs[3], switch_diff.inputs['Switch'])
        links.new(node_in.outputs[4], switch_frame.inputs['Switch'])
        
    links.new(combine_xyz.outputs['Vector'], trans_head.inputs['Translation'])
    links.new(combine_rot.outputs['Vector'], trans_head.inputs['Rotation'])
    
    # Final Join
    links.new(trans_head.outputs['Geometry'], join_geo.inputs['Geometry'])
    links.new(join_geo.outputs['Geometry'], node_out.inputs['Geometry'])

