import bpy

# Test script to understand Temperature control
obj = bpy.context.active_object
if obj and obj.type == 'LIGHT':
    print(f"\n=== Light: {obj.name} ===")
    print(f"use_nodes: {obj.data.use_nodes}")
    
    if obj.data.use_nodes and obj.data.node_tree:
        print(f"Node tree: {obj.data.node_tree.name}")
        for node in obj.data.node_tree.nodes:
            print(f"  Node: {node.name}, Type: {node.type}")
            if node.type == 'BLACKBODY':
                print(f"    BLACKBODY found!")
                temp_socket = node.inputs['Temperature']
                print(f"    Temperature Socket: {temp_socket}")
                print(f"    default_value: {temp_socket.default_value}")
                print(f"    identifier: {temp_socket.identifier}")
                print(f"    path_from_id: {temp_socket.path_from_id()}")
else:
    print("No light selected")
