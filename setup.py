from setuptools import setup, find_packages
import os
import sys
import logging
from pathlib import Path

setup(
    name="organigramma-manager",
    version="1.0.0",
    description="Web application per gestione organigramma aziendale",
    author="Paolo Mancini",
    author_email="paolo.mancini@openeconomics.eu",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "jinja2>=3.1.2",
        "python-multipart>=0.0.6",
        "pydantic>=2.5.0",
        "click>=8.1.7",
        "aiofiles>=23.2.1",
        "pillow>=10.0.0",  # Per favicon
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
        ]
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "organigramma=main:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

def setup_organigramma():
    """Setup completo dell'applicazione"""
    print("🚀 Setup Organigramma Manager v2.0")
    print("=" * 50)
    
    # Crea directory necessarie
    dirs = [
        "data",
        "logs", 
        "src/web/static",
        "src/web/templates/admin",
        "database"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory: {dir_path}")
    
    # Crea file vuoti necessari
    init_files = [
        "src/web/__init__.py",
        "src/web/routes/__init__.py"
    ]
    
    for file_path in init_files:
        Path(file_path).touch()
        print(f"✅ File: {file_path}")
    
    # Test import e inizializzazione database
    try:
        from src.database.connection import DatabaseConnection
        db = DatabaseConnection()
        print("✅ Database inizializzato")
    except Exception as e:
        print(f"❌ Errore database: {e}")
        return False
    
    print("\n✅ Setup completato!")
    print("\nComandi disponibili:")
    print("  python main.py start                # Avvia server")
    print("  python -m uvicorn src.ui.app:app    # Avvia direttamente")
    
    return True

if __name__ == "__main__":
    setup_organigramma()