"""
Build script for Simulation Studio addon
Copies all files from src/ to build/SimulationStudio/ and creates ZIP
"""

import shutil
import os
import sys

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(SCRIPT_DIR, "src")
BUILD_DIR = os.path.join(SCRIPT_DIR, "build", "SimulationStudio")
ZIP_PATH = os.path.join(SCRIPT_DIR, "build", "SimulationStudio.zip")

def build():
    # Remove old build
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    
    # Copy src to build
    shutil.copytree(SRC_DIR, BUILD_DIR)
    
    # Create ZIP
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)
    shutil.make_archive(
        os.path.join(SCRIPT_DIR, "build", "SimulationStudio"),
        'zip',
        os.path.join(SCRIPT_DIR, "build"),
        "SimulationStudio"
    )
    
    print(f"✅ Build complete!")
    print(f"   Source: {SRC_DIR}")
    print(f"   Folder: {BUILD_DIR}")
    print(f"   ZIP:    {ZIP_PATH}")
    print()
    print("=" * 60)
    print("INSTALLATION OPTIONS:")
    print("=" * 60)
    print()
    print("🔄 OPTION 1: Dev Mode (Recommandé pour développement)")
    print("   Permet de refresh l'addon sans réinstaller:")
    print()
    print("   1. Désinstalle l'addon ZIP actuel dans Blender")
    print("   2. Crée un symlink vers le dossier src/:")
    print()
    blender_addons = r"C:\Users\flofi\AppData\Roaming\Blender Foundation\Blender\4.0\scripts\addons"
    print(f'      mklink /D "{blender_addons}\\SimulationStudio" "{SRC_DIR}"')
    print()
    print("   3. Active l'addon dans Blender")
    print("   4. Pour rafraîchir: F3 > 'Reload Scripts' ou Ctrl+Shift+F5")
    print()
    print("📦 OPTION 2: Réinstaller le ZIP")
    print(f"   Installe ce fichier: {ZIP_PATH}")
    print()

if __name__ == "__main__":
    build()
