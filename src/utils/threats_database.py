"""
Base de données des menaces connues et leurs caractéristiques.
"""

from typing import Dict, Any, List

# Facteurs de risque et leurs poids
RISK_FACTORS = {
    'authentication': {
        'none': 3,
        'optional': 2,
        'required': 1
    },
    'authorization': {
        'none': 3,
        'optional': 2,
        'required': 1
    },
    'encryption': {
        False: 3,
        True: 1
    },
    'protocol_security': {
        'low': 3,
        'medium': 2,
        'high': 1
    },
    'data_sensitivity': {
        'public': 1,
        'internal': 2,
        'confidential': 3,
        'restricted': 4
    },
    'component_type': {
        'database': 4,
        'api': 3,
        'web-application': 3,
        'cloud-service': 3,
        'serverless': 2,
        'microservice': 2,
        'load-balancer': 2,
        'cache': 2,
        'message-queue': 2,
        'process': 1
    }
}

# Niveaux de risque et leurs seuils
RISK_LEVELS = {
    'critical': 15,  # Score >= 15
    'high': 12,      # Score >= 12
    'medium': 8,     # Score >= 8
    'low': 4         # Score >= 4
}

# Base de données des menaces connues
KNOWN_THREATS: Dict[str, Dict[str, Any]] = {
    'xss': {
        'name': 'Cross-Site Scripting',
        'base_risk': 3,
        'affected_components': ['web-application', 'api'],
        'mitigation': ['input-validation', 'output-encoding'],
        'description': 'Attaque permettant d\'injecter du code malveillant dans une page web',
        'owasp_category': 'A7:2021',
        'cwe': 'CWE-79'
    },
    'sql-injection': {
        'name': 'SQL Injection',
        'base_risk': 4,
        'affected_components': ['database', 'api'],
        'mitigation': ['prepared-statements', 'input-validation'],
        'description': 'Attaque permettant d\'injecter des commandes SQL malveillantes',
        'owasp_category': 'A3:2021',
        'cwe': 'CWE-89'
    },
    'csrf': {
        'name': 'Cross-Site Request Forgery',
        'base_risk': 2,
        'affected_components': ['web-application'],
        'mitigation': ['csrf-tokens', 'same-site-cookies'],
        'description': 'Attaque exploitant l\'authentification d\'un utilisateur',
        'owasp_category': 'A1:2021',
        'cwe': 'CWE-352'
    },
    'dos': {
        'name': 'Denial of Service',
        'base_risk': 3,
        'affected_components': ['*'],
        'mitigation': ['rate-limiting', 'load-balancing'],
        'description': 'Attaque visant à rendre un service indisponible',
        'owasp_category': 'A5:2021',
        'cwe': 'CWE-400'
    },
    'data-leak': {
        'name': 'Data Leakage',
        'base_risk': 4,
        'affected_components': ['database', 'api', 'web-application'],
        'mitigation': ['encryption', 'access-controls'],
        'description': 'Exposition non autorisée de données sensibles',
        'owasp_category': 'A4:2021',
        'cwe': 'CWE-200'
    },
    'auth-bypass': {
        'name': 'Authentication Bypass',
        'base_risk': 4,
        'affected_components': ['*'],
        'mitigation': ['strong-auth', 'mfa'],
        'description': 'Contournement des mécanismes d\'authentification',
        'owasp_category': 'A2:2021',
        'cwe': 'CWE-287'
    },
    'man-in-middle': {
        'name': 'Man in the Middle',
        'base_risk': 3,
        'affected_components': ['*'],
        'mitigation': ['tls', 'certificate-pinning'],
        'description': 'Interception des communications entre deux parties',
        'owasp_category': 'A6:2021',
        'cwe': 'CWE-300'
    },
    'insecure-api': {
        'name': 'Insecure API',
        'base_risk': 3,
        'affected_components': ['api'],
        'mitigation': ['api-security', 'rate-limiting'],
        'description': 'API mal sécurisée exposant des vulnérabilités',
        'owasp_category': 'A8:2021',
        'cwe': 'CWE-20'
    },
    'weak-crypto': {
        'name': 'Weak Cryptography',
        'base_risk': 3,
        'affected_components': ['*'],
        'mitigation': ['strong-crypto', 'key-management'],
        'description': 'Utilisation de cryptographie faible ou obsolète',
        'owasp_category': 'A9:2021',
        'cwe': 'CWE-326'
    },
    'misconfig': {
        'name': 'Security Misconfiguration',
        'base_risk': 2,
        'affected_components': ['*'],
        'mitigation': ['security-hardening', 'configuration-management'],
        'description': 'Configuration de sécurité incorrecte ou par défaut',
        'owasp_category': 'A5:2021',
        'cwe': 'CWE-16'
    }
}

def get_threat_info(threat_id: str) -> Dict[str, Any]:
    """
    Récupère les informations d'une menace par son ID.
    
    Args:
        threat_id: Identifiant de la menace
        
    Returns:
        Informations de la menace ou dictionnaire vide si non trouvée
    """
    return KNOWN_THREATS.get(threat_id, {})

def get_all_threats() -> Dict[str, Dict[str, Any]]:
    """
    Récupère toutes les menaces connues.
    
    Returns:
        Dictionnaire de toutes les menaces
    """
    return KNOWN_THREATS

def get_threats_by_component(component_type: str) -> List[Dict[str, Any]]:
    """
    Récupère les menaces affectant un type de composant spécifique.
    
    Args:
        component_type: Type de composant
        
    Returns:
        Liste des menaces affectant le composant
    """
    return [
        {**threat, 'id': threat_id}
        for threat_id, threat in KNOWN_THREATS.items()
        if '*' in threat['affected_components'] or component_type in threat['affected_components']
    ]

def get_threats_by_risk_level(risk_level: str) -> List[Dict[str, Any]]:
    """
    Récupère les menaces d'un niveau de risque spécifique.
    
    Args:
        risk_level: Niveau de risque ('critical', 'high', 'medium', 'low')
        
    Returns:
        Liste des menaces du niveau de risque spécifié
    """
    return [
        {**threat, 'id': threat_id}
        for threat_id, threat in KNOWN_THREATS.items()
        if threat['base_risk'] >= RISK_LEVELS.get(risk_level, 0)
    ] 