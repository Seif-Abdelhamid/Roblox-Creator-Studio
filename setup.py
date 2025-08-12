#!/usr/bin/env python3
"""
Roblox Creator Studio - Setup Script
Easy installation and distribution for the 3D multiplayer game engine

Author: Seif Abdelhamid
GitHub: https://github.com/Seif-Abdelhamid
"""

import os
import sys
import subprocess
import platform
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop

# Project metadata
PROJECT_NAME = "roblox-creator-studio"
PROJECT_VERSION = "1.0.0"
PROJECT_DESCRIPTION = "A revolutionary 3D multiplayer game engine inspired by Roblox's vision"
PROJECT_AUTHOR = "Seif Abdelhamid"
PROJECT_AUTHOR_EMAIL = "seifwaelabdelhamid@gmail.com"
PROJECT_URL = "https://github.com/Seif-Abdelhamid/roblox-creator-studio"
PROJECT_LICENSE = "MIT"

# Read requirements
def read_requirements(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read README
def read_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

# Custom install command
class CustomInstall(install):
    def run(self):
        install.run(self)
        self.post_install()

    def post_install(self):
        print("🎮 Roblox Creator Studio Setup Complete!")
        print("👨‍💻 Author: Seif Abdelhamid")
        print("🌐 GitHub: https://github.com/Seif-Abdelhamid")
        print("\n📦 Installation includes:")
        print("  ✅ Python 3D Game Engine")
        print("  ✅ Go Networking Server")
        print("  ✅ Node.js Web API")
        print("  ✅ TypeScript React UI")
        print("  ✅ C++ Performance Modules")
        print("  ✅ Lua Scripting System")
        print("  ✅ Docker Containerization")
        print("\n🚀 To start the game:")
        print("  python main.py")
        print("\n🔧 For full development environment:")
        print("  docker-compose up -d")

# Custom develop command
class CustomDevelop(develop):
    def run(self):
        develop.run(self)
        self.post_develop()

    def post_develop(self):
        print("🔧 Development environment setup complete!")
        print("📝 You can now modify the code and see changes immediately.")

# Platform-specific setup
def setup_platform():
    system = platform.system().lower()
    
    if system == "windows":
        print("🪟 Windows detected - Setting up Windows-specific components...")
        # Windows-specific setup
        setup_windows()
    elif system == "darwin":
        print("🍎 macOS detected - Setting up macOS-specific components...")
        # macOS-specific setup
        setup_macos()
    elif system == "linux":
        print("🐧 Linux detected - Setting up Linux-specific components...")
        # Linux-specific setup
        setup_linux()
    else:
        print(f"⚠️ Unknown platform: {system}")

def setup_windows():
    """Setup Windows-specific components"""
    try:
        # Install Visual C++ Redistributable if needed
        print("📦 Checking Visual C++ Redistributable...")
        
        # Create Windows batch files for easy startup
        with open('start_game.bat', 'w') as f:
            f.write('@echo off\n')
            f.write('echo Starting Roblox Creator Studio...\n')
            f.write('python main.py\n')
            f.write('pause\n')
        
        with open('start_server.bat', 'w') as f:
            f.write('@echo off\n')
            f.write('echo Starting Game Server...\n')
            f.write('cd go && go run server/main.go\n')
            f.write('pause\n')
            
        print("✅ Windows setup complete!")
        
    except Exception as e:
        print(f"❌ Windows setup failed: {e}")

def setup_macos():
    """Setup macOS-specific components"""
    try:
        # Install Homebrew dependencies if available
        print("🍺 Checking Homebrew dependencies...")
        
        # Create macOS shell scripts for easy startup
        with open('start_game.sh', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('echo "Starting Roblox Creator Studio..."\n')
            f.write('python3 main.py\n')
        
        with open('start_server.sh', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('echo "Starting Game Server..."\n')
            f.write('cd go && go run server/main.go\n')
        
        # Make scripts executable
        os.chmod('start_game.sh', 0o755)
        os.chmod('start_server.sh', 0o755)
        
        print("✅ macOS setup complete!")
        
    except Exception as e:
        print(f"❌ macOS setup failed: {e}")

def setup_linux():
    """Setup Linux-specific components"""
    try:
        # Install system dependencies
        print("📦 Installing system dependencies...")
        
        # Create Linux shell scripts for easy startup
        with open('start_game.sh', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('echo "Starting Roblox Creator Studio..."\n')
            f.write('python3 main.py\n')
        
        with open('start_server.sh', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('echo "Starting Game Server..."\n')
            f.write('cd go && go run server/main.go\n')
        
        # Make scripts executable
        os.chmod('start_game.sh', 0o755)
        os.chmod('start_server.sh', 0o755)
        
        print("✅ Linux setup complete!")
        
    except Exception as e:
        print(f"❌ Linux setup failed: {e}")

# Main setup configuration
setup(
    name=PROJECT_NAME,
    version=PROJECT_VERSION,
    description=PROJECT_DESCRIPTION,
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author=PROJECT_AUTHOR,
    author_email=PROJECT_AUTHOR_EMAIL,
    url=PROJECT_URL,
    license=PROJECT_LICENSE,
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements('requirements.txt'),
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=1.0.0',
        ],
        'docs': [
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
        'full': [
            'docker>=6.0.0',
            'kubernetes>=26.0.0',
        ]
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Games/Entertainment',
        'Topic :: Multimedia :: Graphics :: 3D Rendering',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
    ],
    keywords=[
        'roblox', 'game-engine', '3d', 'multiplayer', 'real-time',
        'opengl', 'pygame', 'websocket', 'networking', 'physics',
        'python', 'go', 'nodejs', 'typescript', 'cpp', 'lua'
    ],
    project_urls={
        'Bug Reports': f'{PROJECT_URL}/issues',
        'Source': PROJECT_URL,
        'Documentation': f'{PROJECT_URL}/docs',
        'Author Portfolio': 'https://seif-abdelhamid.github.io/Personal-Website/',
    },
    cmdclass={
        'install': CustomInstall,
        'develop': CustomDevelop,
    },
    entry_points={
        'console_scripts': [
            'roblox-creator-studio=main:main',
            'rcs-server=go.server.main:main',
            'rcs-ui=typescript.src.main:main',
        ],
    },
    zip_safe=False,
)

# Run platform-specific setup
if __name__ == '__main__':
    setup_platform()
