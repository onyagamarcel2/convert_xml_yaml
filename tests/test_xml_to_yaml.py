"""
Tests unitaires pour la conversion XML vers YAML.
"""
import pytest
from src.utils.validators import validate_xml, validate_yaml, validate_conversion_result
from src.utils.file_handlers import validate_file_size
import xmltodict
import yaml

# Données de test
SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <element id="1">
        <name>Test</name>
        <value>123</value>
    </element>
</root>"""

SAMPLE_YAML = """root:
  element:
    '@id': '1'
    name: Test
    value: '123'"""

def test_validate_xml():
    """Test de validation XML."""
    assert validate_xml(SAMPLE_XML)
    assert not validate_xml("<invalid>xml</invalid")

def test_validate_yaml():
    """Test de validation YAML."""
    assert validate_yaml(SAMPLE_YAML)
    assert not validate_yaml("invalid: yaml: :")

def test_validate_conversion_result():
    """Test de validation du résultat de conversion."""
    xml_dict = xmltodict.parse(SAMPLE_XML)
    yaml_dict = yaml.safe_load(SAMPLE_YAML)
    assert validate_conversion_result(xml_dict, yaml_dict)

def test_validate_file_size(tmp_path):
    """Test de validation de la taille du fichier."""
    # Créer un fichier temporaire
    test_file = tmp_path / "test.xml"
    test_file.write_text(SAMPLE_XML)
    
    assert validate_file_size(str(test_file), max_size_mb=1)
    
    # Créer un fichier trop grand
    large_file = tmp_path / "large.xml"
    large_file.write_text(SAMPLE_XML * 1000000)  # Répéter le contenu pour créer un gros fichier
    
    assert not validate_file_size(str(large_file), max_size_mb=1) 