from setuptools import setup, find_packages

# Lire le contenu du README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="convertisseur-xml-yaml",
    version="1.0.0",
    author="Votre Nom",
    author_email="votre.email@example.com",
    description="Un outil de conversion entre XML et YAML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/votre-username/convertisseur-xml-yaml",
    packages=find_packages(),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0.1",
        "xmltodict>=0.13.0",
    ],
    entry_points={
        "console_scripts": [
            "convertisseur=convertisseur:main",
        ],
    },
) 