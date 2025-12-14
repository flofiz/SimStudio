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
        
        # Geometry Output
        ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
        
    else:
        # Legacy support
        ng.inputs.clear()
        ng.outputs.clear()
        ng.inputs.new('NodeSocketFloat', "Tripod Height")
        ng.inputs[-1].default_value = 1.5
        ng.inputs.new('NodeSocketFloat', "Tilt")
        ng.inputs.new('NodeSocketFloat', "Pan")
        ng.inputs.new('NodeSocketBool', "Show Diffuser")
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
    node_in.location = (-800, 0)
    
    node_out = nodes.new('NodeGroupOutput')
    node_out.location = (800, 0)
    
    # --- 1. Tripod Base (Fixed Cylinder) ---
    # Cylinder Node
    cyl_base = nodes.new('GeometryNodeMeshCylinder')
    cyl_base.inputs['Vertices'].default_value = 32
    cyl_base.inputs['Radius'].default_value = 0.05
    cyl_base.inputs['Depth'].default_value = 1.0
    cyl_base.location = (-400, -200)
    
    # Transform Base (Move up by half height so pivot is at bottom)
    trans_base = nodes.new('GeometryNodeTransform')
    trans_base.inputs['Translation'].default_value = (0, 0, 0.5)
    trans_base.location = (-200, -200)
    
    links.new(cyl_base.outputs['Mesh'], trans_base.inputs['Geometry'])
    
    # --- 2. Tripod Pole (Adjustable Height) ---
    # Cylinder Node
    cyl_pole = nodes.new('GeometryNodeMeshCylinder')
    cyl_pole.inputs['Vertices'].default_value = 32
    cyl_pole.inputs['Radius'].default_value = 0.04
    cyl_pole.location = (-400, 200)
    
    # The pole depth should match the input height roughly, but let's keep it simple
    # We will just scale/move a cylinder based on "Tripod Height"
    # Actually, simpler: Translate a second cylinder to the top
    
    # Combine Base + Pole? 
    # Let's make "Tripod Height" move the HEAD, and the pole stretches.
    # For POC, let's just use one cylinder scaled z.
    
    # Combine Geometry
    join_geo = nodes.new('GeometryNodeJoinGeometry')
    join_geo.location = (600, 0)
    
    links.new(trans_base.outputs['Geometry'], join_geo.inputs['Geometry'])
    
    # --- 3. Projector Head (Cube) ---
    cube_head = nodes.new('GeometryNodeMeshCube')
    cube_head.inputs['Size'].default_value = (0.2, 0.2, 0.2)
    cube_head.location = (-400, 600)
    
    # Transform Head
    trans_head = nodes.new('GeometryNodeTransform')
    trans_head.location = (0, 600)
    
    # We need to rotate and translate the head
    # Translation Z = Tripod Height Input
    
    # Combine XYZ for Translation
    combine_xyz = nodes.new('ShaderNodeCombineXYZ')
    combine_xyz.location = (-200, 400)
    
    # Link Input Height to Z
    if bpy.app.version >= (4, 0, 0):
        # By names usually works if sockets exist
        links.new(node_in.outputs['Tripod Height'], combine_xyz.inputs['Z'])
    else:
         links.new(node_in.outputs[0], combine_xyz.inputs['Z']) # 0 is Height
         
    links.new(combine_xyz.outputs['Vector'], trans_head.inputs['Translation'])
    
    # Rotation (Tilt/Pan)
    combine_rot = nodes.new('ShaderNodeCombineXYZ')
    combine_rot.location = (-200, 550)
    
    # Link Tilt (X) and Pan (Z)
    if bpy.app.version >= (4, 0, 0):
        links.new(node_in.outputs['Tilt'], combine_rot.inputs['X'])
        links.new(node_in.outputs['Pan'], combine_rot.inputs['Z'])
    else:
        links.new(node_in.outputs[1], combine_rot.inputs['X'])
        links.new(node_in.outputs[2], combine_rot.inputs['Z'])
        
    links.new(combine_rot.outputs['Vector'], trans_head.inputs['Rotation'])
    links.new(cube_head.outputs['Mesh'], trans_head.inputs['Geometry'])
    
    links.new(trans_head.outputs['Geometry'], join_geo.inputs['Geometry'])
    
    # --- 4. Diffuser (Cone) ---
    # Switch node to toggle
    switch_diff = nodes.new('GeometryNodeSwitch')
    switch_diff.input_type = 'GEOMETRY' 
    switch_diff.location = (400, 800)
    
    # Cone Geometry
    cone = nodes.new('GeometryNodeMeshCone')
    cone.inputs['Radius Bottom'].default_value = 0.3
    cone.inputs['Radius Top'].default_value = 0.1
    cone.inputs['Depth'].default_value = 0.4
    cone.location = (-200, 800)
    
    # Transform Cone (Move to front of head)
    trans_cone = nodes.new('GeometryNodeTransform')
    trans_cone.location = (0, 800)
    # Move locally? No, we transform the cone then attach to head transform?
    # Better: Join Cube + Cone, THEN Apply Head Transform.
    
    # Let's restructure Head Transform
    # Cube -> Join 1
    # Cone -> Switch -> Join 1
    # Join 1 -> Transform Head -> Final Join
    
    # Delete previous links to restructure
    # Remove link trans_head -> join_geo
    # Remove link cube_head -> trans_head
    
    # Create Head Join
    join_head = nodes.new('GeometryNodeJoinGeometry')
    join_head.location = (-100, 600)
    
    links.new(cube_head.outputs['Mesh'], join_head.inputs['Geometry'])
    
    # Setup Cone Logic
    # Move cone down -Z (default cone points up Z) so it aligned with front (let's say -Y is front)
    # Standard Blender light points -Z.
    # So lets make the cone point -Z.
    # Cone default is along Z. Rotate 180 X? Or just translate.
    # Let's just create it and translate it relative to Cube.
    # Say Cube is at 0,0,0 local (Head space).
    # Cone should be below it (-Z).
    
    trans_cone_local = nodes.new('GeometryNodeTransform')
    trans_cone_local.inputs['Translation'].default_value = (0, 0, -0.3) # Move down
    trans_cone_local.location = (0, 800)
    
    links.new(cone.outputs['Mesh'], trans_cone_local.inputs['Geometry'])
    links.new(trans_cone_local.outputs['Geometry'], switch_diff.inputs['True'])
    
    # Link Switch
    if bpy.app.version >= (4, 0, 0):
        links.new(node_in.outputs['Show Diffuser'], switch_diff.inputs['Switch'])
    else:
        links.new(node_in.outputs[3], switch_diff.inputs['Switch'])
        
    links.new(switch_diff.outputs['Output'], join_head.inputs['Geometry'])
    
    # Now link Head Join to existing Head Transform
    links.new(join_head.outputs['Geometry'], trans_head.inputs['Geometry'])
    
    # Link Head Transform to Final Join
    links.new(trans_head.outputs['Geometry'], join_geo.inputs['Geometry'])
    
    # Output
    links.new(join_geo.outputs['Geometry'], node_out.inputs['Geometry'])

