import bpy
import os

def create_svg_content(context):
    """
    Generates SVG string from current scene objects.
    Maps World (X, Y) to SVG (X, Y).
    """
    scene = context.scene
    
    # SVG Settings
    width = 800
    height = 600
    scale = 50.0  # 1 meter = 50 pixels
    center_x = width / 2
    center_y = height / 2
    
    # Header
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="100%" height="100%" fill="#f0f0f0" />', # Background
        f'<g transform="translate({center_x}, {center_y}) scale(1, -1)">', # Center and Flip Y for Cartesian
        # Grid lines (Optional)
        f'<line x1="-400" y1="0" x2="400" y2="0" stroke="#ccc" stroke-width="1" />',
        f'<line x1="0" y1="-300" x2="0" y2="300" stroke="#ccc" stroke-width="1" />'
    ]
    
    # Collect Objects
    for obj in scene.objects:
        if obj.hide_viewport:
            continue
            
        x = obj.location.x * scale
        y = obj.location.y * scale
        
        # Determine Color/Shape based on type
        if obj.type == 'LIGHT':
            # Yellow Circle
            svg_lines.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="15" fill="#FFD700" stroke="#000" stroke-width="2" />')
            # Label
            svg_lines.append(f'<text x="{x:.2f}" y="{y:.2f}" transform="scale(1, -1)" fill="black" font-size="12" text-anchor="middle" dy="-20">{obj.name}</text>')
            
        elif obj.type == 'CAMERA':
            # Blue Rect
            svg_lines.append(f'<rect x="{x-10:.2f}" y="{y-10:.2f}" width="20" height="20" fill="#4682B4" stroke="#000" stroke-width="2" />')
            
        elif obj.type == 'MESH':
            # Check if it's a stand or modifier?
            # For now just small gray circle for reference if selected?
            # Skip generic meshes to clean up diagram
            pass
            
    # Footer
    svg_lines.append('</g>')
    svg_lines.append('</svg>')
    
    return "\n".join(svg_lines)

class SS_OT_export_diagram(bpy.types.Operator):
    """Export 2D Lighting Diagram to SVG"""
    bl_idname = "scene.export_lighting_diagram"
    bl_label = "Export Diagram (SVG)"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    
    def execute(self, context):
        if not self.filepath.endswith(".svg"):
            self.filepath += ".svg"
            
        content = create_svg_content(context)
        
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.report({'INFO'}, f"Saved diagram to {self.filepath}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to save: {str(e)}")
            return {'CANCELLED'}
            
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
