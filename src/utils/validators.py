"""
Module de validation et correction des données.
"""

from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ValidationResult:
    """Classe pour stocker les résultats de validation."""
    def __init__(self, is_valid: bool, warnings: List[str], corrected_data: Dict):
        self.is_valid = is_valid
        self.warnings = warnings
        self.corrected_data = corrected_data

def validate_and_correct_component(component: Dict, component_types: Dict) -> ValidationResult:
    """
    Valide et corrige un composant.
    Retourne un tuple (is_valid, warnings, corrected_component)
    """
    warnings = []
    corrected = component.copy()
    
    # Validation des champs requis
    if not corrected.get('id'):
        warnings.append("ID manquant, génération d'un ID temporaire")
        corrected['id'] = f"temp_{hash(str(component))}"
    
    if not corrected.get('name'):
        warnings.append("Nom manquant, utilisation de la valeur par défaut")
        corrected['name'] = "Unnamed Component"
    
    # Validation et correction du type
    if not corrected.get('type') or corrected['type'] not in component_types:
        warnings.append(f"Type invalide ou manquant: {corrected.get('type')}, détection automatique")
        # Détection automatique du type basée sur la valeur
        corrected['type'] = _detect_component_type(corrected.get('value', ''), component_types)
    
    # Correction des attributs de sécurité
    type_info = component_types.get(corrected['type'], {})
    if type_info:
        if corrected.get('authentication') not in ['required', 'none']:
            warnings.append(f"Authentication invalide, utilisation de la valeur par défaut: {type_info['authentication']}")
            corrected['authentication'] = type_info['authentication']
        
        if corrected.get('authorization') not in ['required', 'none']:
            warnings.append(f"Authorization invalide, utilisation de la valeur par défaut: {type_info['authorization']}")
            corrected['authorization'] = type_info['authorization']
        
        if corrected.get('data_sensitivity') not in ['public', 'internal', 'confidential', 'restricted']:
            warnings.append(f"Sensibilité des données invalide, utilisation de la valeur par défaut: {type_info['data_sensitivity']}")
            corrected['data_sensitivity'] = type_info['data_sensitivity']
    
    return ValidationResult(True, warnings, corrected)

def validate_and_correct_flow(flow: Dict, components: Dict[str, Dict], protocols: Dict) -> ValidationResult:
    """
    Valide et corrige un flux.
    Retourne un tuple (is_valid, warnings, corrected_flow)
    """
    warnings = []
    corrected = flow.copy()
    
    # Validation de la source et de la cible
    if not corrected.get('source') or corrected['source'] not in components:
        warnings.append(f"Source invalide: {corrected.get('source')}, utilisation de la première source valide")
        corrected['source'] = next(iter(components.keys()))
    
    if not corrected.get('target') or corrected['target'] not in components:
        warnings.append(f"Cible invalide: {corrected.get('target')}, utilisation de la première cible valide")
        corrected['target'] = next(iter(components.keys()))
    
    # Validation et correction du protocole
    if not corrected.get('protocol') or corrected['protocol'] not in protocols:
        warnings.append(f"Protocole invalide: {corrected.get('protocol')}, détection automatique")
        corrected['protocol'] = _detect_protocol(
            components[corrected['source']],
            components[corrected['target']],
            protocols
        )
    
    # Correction des attributs de sécurité
    protocol_info = protocols.get(corrected['protocol'], {})
    if protocol_info:
        if corrected.get('authentication') not in ['required', 'none']:
            warnings.append(f"Authentication invalide, utilisation de la valeur par défaut: {protocol_info['authentication']}")
            corrected['authentication'] = protocol_info['authentication']
        
        if corrected.get('authorization') not in ['required', 'none']:
            warnings.append(f"Authorization invalide, utilisation de la valeur par défaut: {protocol_info['authorization']}")
            corrected['authorization'] = protocol_info['authorization']
        
        if corrected.get('encryption') not in [True, False]:
            warnings.append(f"Encryption invalide, utilisation de la valeur par défaut: {protocol_info['encryption']}")
            corrected['encryption'] = protocol_info['encryption']
    
    return ValidationResult(True, warnings, corrected)

def validate_and_correct_threat(threat: Dict, known_threats: Dict, risk_levels: Dict) -> ValidationResult:
    """
    Valide et corrige une menace.
    Retourne un tuple (is_valid, warnings, corrected_threat)
    """
    warnings = []
    corrected = threat.copy()
    
    # Validation de l'ID de la menace
    if not corrected.get('id') or corrected['id'] not in known_threats:
        warnings.append(f"ID de menace invalide: {corrected.get('id')}, génération d'un ID temporaire")
        corrected['id'] = f"temp_threat_{hash(str(threat))}"
    
    # Correction du niveau de risque
    if not corrected.get('risk') or corrected['risk'] not in risk_levels:
        warnings.append(f"Niveau de risque invalide: {corrected.get('risk')}, utilisation de 'low'")
        corrected['risk'] = 'low'
    
    # Correction du score de risque
    risk_score = corrected.get('risk_score', 0)
    if not isinstance(risk_score, (int, float)) or not 0 <= risk_score <= 1:
        warnings.append(f"Score de risque invalide: {risk_score}, normalisation à 0.5")
        corrected['risk_score'] = 0.5
    
    return ValidationResult(True, warnings, corrected)

def _detect_component_type(value: str, component_types: Dict) -> str:
    """Détecte automatiquement le type de composant."""
    value = value.lower()
    
    for comp_type, info in component_types.items():
        if any(keyword in value for keyword in info['styles']):
            return comp_type
    
    return 'process'  # Type par défaut

def _detect_protocol(source: Dict, target: Dict, protocols: Dict) -> str:
    """Détecte automatiquement le protocole."""
    source_type = source.get('type', '').lower()
    target_type = target.get('type', '').lower()
    
    if 'database' in source_type or 'database' in target_type:
        return 'tcp'
    elif 'api' in source_type or 'api' in target_type:
        return 'https'
    elif 'message-queue' in source_type or 'message-queue' in target_type:
        return 'amqp'
    elif 'cache' in source_type or 'cache' in target_type:
        return 'tcp'
    
    return 'https'  # Protocole par défaut 