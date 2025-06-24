#!/usr/bin/env python3
"""
NexusNet: Universal Neural Network Core for AI Model Cognition
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="nexusnet",
    version="0.1.0",
    author="NexusNet Team",
    author_email="team@nexusnet.ai",
    description="Universal Neural Network Core for AI Model Cognition",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YourOrg/NexusNet",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.4.0",
            "pre-commit>=3.3.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
        "quantum": [
            "qiskit>=0.43.0",
            "pennylane>=0.31.0",
        ],
        "federated": [
            "flower>=1.4.0",
            "syft>=0.8.0",
        ],
        "wasm": [
            "wasmtime>=10.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nexusnet=nexusnet.cli:main",
            "nexusnet-train=nexusnet.training.cli:main",
            "nexusnet-serve=nexusnet.serving.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "nexusnet": [
            "configs/*.yaml",
            "configs/*.json",
            "web_ui/static/*",
            "web_ui/templates/*",
        ],
    },
    zip_safe=False,
    keywords="ai, machine learning, neural networks, transformers, multimodal, federated learning",
    project_urls={
        "Bug Reports": "https://github.com/YourOrg/NexusNet/issues",
        "Source": "https://github.com/YourOrg/NexusNet",
        "Documentation": "https://nexusnet.readthedocs.io/",
    },
)

