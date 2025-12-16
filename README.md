# Simulation Studio - Blender Addon

A professional lighting simulation tool for Blender, designed to bridge the gap between photo studio workflows and 3D rendering.

## Key Features

### 🚦 Photometric Light Simulation
- **Real-world Units**: Lights operate with accurate Lumen and Wattage values.
- **COB Projectors**: Preset library of Chip-on-Board LED lights (60W - 300W).
- **Physical Color Temperature**: Reliable kelvin temperature control synced with blackbody radiation.

### 🎥 Light Modifiers System
Attach virtual modifiers that physically alter light beam properties:
- **Diffusers**: Soften light and increase spread.
- **Honeycomb Grids**: Tighten beam angle (10°, 20°, 40°) and reduce spill.
- **Softboxes**: Simulate large area sources.
- **Barn Doors**: Shape light edges.
- **Stacking Upgrade**: Modifiers calculate and apply cumulative light loss and diffusion.

### 📷 Physical Camera Settings
Control Blender's exposure using photography terms:
- **ISO, Aperture (f-stop), Shutter Speed**.
- **Calculated Exposure**: Automatically sets the scene's exposure value (EV) based on camera settings.

### 📐 Studio Planning
- **2D Lighting Diagram**: Auto-generate an SVG vector diagram of your scene layout for studio planning.

## Installation

1. Download the latest `SimulationStudio.zip` release.
2. In Blender, go to **Edit > Preferences > Get Extensions**.
3. Choose **Install from Disk...** and select the ZIP file.
4. Enable the addon "Simulation Studio".
5. Find the panel in the 3D Viewport **N-Panel** under the **Sim Studio** tab.

## Usage

### Adding Lights
1. Open the **Sim Studio** panel.
2. Under **Light Library**, click **Add** next to a desired light (e.g., "COB 300W").
3. The light will spawn at the 3D cursor.

### Modifying Lights
1. Select a Sim Studio light.
2. Use the **Power %** slider to adjust intensity while keeping max wattage reference.
3. Click **Add Modifier** to attach accessories like Grids or Softboxes.
4. Click **Convert Selected** to treat a standard Blender light as a physical light.

## Development

### Project Structure
```
AddonBlender/
├── src/                    # Source code (addon files)
│   ├── assets/             # JSON presets (lights, modifiers)
│   ├── __init__.py         # Addon entry point
│   ├── ui_panel.py         # UI Panel
│   ├── light_modifiers.py  # Operators
│   ├── geometry_nodes.py   # GN Rig generator
│   └── ...
├── build/                  # Build output (auto-generated)
├── SimulationStudio.zip    # Packaged addon
└── README.md
```

### Build Commands

**Build the addon (Windows PowerShell):**
```powershell
python -c "import shutil, os; build_dir = r'build\SimulationStudio'; shutil.rmtree('build', ignore_errors=True); os.makedirs(build_dir, exist_ok=True); shutil.copytree('src', build_dir, dirs_exist_ok=True); shutil.make_archive('SimulationStudio', 'zip', 'build')"
```

**Build the addon (Linux/macOS):**
```bash
rm -rf build && mkdir -p build/SimulationStudio && cp -r src/* build/SimulationStudio/ && cd build && zip -r ../SimulationStudio.zip SimulationStudio
```

This creates `SimulationStudio.zip` ready for installation in Blender.
