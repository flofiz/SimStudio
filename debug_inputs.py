import bpy

obj = bpy.context.active_object
if obj and obj.type == 'LIGHT' and obj.data.use_nodes:
    print(f"Inspecting Light: {obj.name}")
    for node in obj.data.node_tree.nodes:
        if node.type == 'GROUP':
            print(f"Found Group Node: {node.name}, Tree: {node.node_tree.name}")
            print("Inputs via keys:", node.inputs.keys())
            for i, inp in enumerate(node.inputs):
                print(f"  Input {i}: Name='{inp.name}', Identifier='{inp.identifier}'")
else:
    print("No valid light selected")
