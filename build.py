import PyInstaller.__main__
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

print("Starting compilation of Demand Forecaster...")

PyInstaller.__main__.run([
    'app.py',
    '--name=DemandaSanFernando',
    '--onefile',
    '--windowed', # No console window
    '--hidden-import=pandas',
    '--hidden-import=numpy',
    '--hidden-import=matplotlib',
    '--hidden-import=prophet',
    '--hidden-import=duckdb',
    '--hidden-import=customtkinter',
    '--hidden-import=darkdetect',
    '--collect-all=prophet',
    '--collect-all=customtkinter',
    '--clean'
])

print("Compilation finished. Executable should be in the 'dist' folder.")
