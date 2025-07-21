from setuptools import setup, find_packages

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