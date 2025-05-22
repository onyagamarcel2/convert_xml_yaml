"""
Module de validation pour le convertisseur XML/YAML.
"""
import logging
from typing import Dict, Any, Optional
import xml.parsers.expat
import yaml
import xmltodict

logger = logging.getLogger(__name__)

def validate_xml(content: str, filepath: Optional[str] = None) -> bool:
    """
    Valide le contenu XML.
    
    Args:
        content: Contenu XML à valider
        filepath: Chemin du fichier (optionnel)
        
    Returns:
        True si le XML est valide, False sinon
    """
    try:
        xmltodict.parse(content)
        return True
    except xml.parsers.expat.ExpatError as e:
        file_detail = f" in file '{filepath}'" if filepath else ''
        logger.error(f"Invalid XML{file_detail}: {e}")
        return False

def validate_yaml(content: str, filepath: Optional[str] = None) -> bool:
    """
    Valide le contenu YAML.
    
    Args:
        content: Contenu YAML à valider
        filepath: Chemin du fichier (optionnel)
        
    Returns:
        True si le YAML est valide, False sinon
    """
    try:
        yaml.safe_load(content)
        return True
    except yaml.YAMLError as e:
        file_detail = f" in file '{filepath}'" if filepath else ''
        logger.error(f"Invalid YAML{file_detail}: {e}")
        return False

def validate_conversion_result(original: Dict[str, Any], converted: Dict[str, Any]) -> bool:
    """
    Vérifie la cohérence des données après conversion.
    
    Args:
        original: Données originales
        converted: Données converties
        
    Returns:
        True si les données sont cohérentes, False sinon
    """
    def normalize_dict(d: Dict[str, Any]) -> Dict[str, Any]:
        """Normalise un dictionnaire pour la comparaison."""
        result = {}
        for k, v in d.items():
            if isinstance(v, dict):
                result[k] = normalize_dict(v)
            elif isinstance(v, list):
                result[k] = [normalize_dict(i) if isinstance(i, dict) else i for i in v]
            else:
                result[k] = v
        return result

    try:
        original_norm = normalize_dict(original)
        converted_norm = normalize_dict(converted)
        return original_norm == converted_norm
    except Exception as e:
        logger.error(f"Error validating conversion result: {e}")
        return False 