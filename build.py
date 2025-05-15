import os
import sys
import shutil
import subprocess
import PyQt5

def clean_build():
    """Clean previous build files"""
    dirs_to_clean = ['build', 'dist']
    files_to_clean = ['MIUnlockTool.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name} directory")
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Cleaned {file_name}")

def build_app():
    """Build the application using PyInstaller"""
    # PyInstaller command with icon
    cmd = [
        'pyinstaller',
        '--name=MIUnlockTool',
        '--onefile',
        '--windowed',
        '--icon=icon.ico',
        '--add-data=icon.ico;.',
        'mi_unlock_tool.py'
    ]
    
    subprocess.run(cmd, check=True)
    print("\nBuild completed successfully!")
    print("You can find the executable in the 'dist' folder")

def main():
    print("Starting build process...")
    clean_build()
    build_app()

if __name__ == '__main__':
    main() 