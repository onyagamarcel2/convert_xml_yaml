"""
Module pour parser différents types de diagrammes XML et les convertir en format Threagile.
"""

import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Tuple
import re
import logging
from .threats_database import (
    KNOWN_THREATS,
    RISK_FACTORS,
    RISK_LEVELS,
    get_threat_info,
    get_threats_by_component,
    get_threats_by_risk_level
)

logger = logging.getLogger(__name__)

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

# Types de composants et leurs attributs
COMPONENT_TYPES = {
    'web-application': {
        'styles': ['web', 'browser', 'client', 'frontend', 'ui', 'interface'],
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'api': {
        'styles': ['api', 'rest', 'graphql', 'endpoint', 'service'],
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'database': {
        'styles': ['database', 'db', 'sql', 'nosql', 'postgres', 'mysql', 'mongodb', 'oracle'],
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'confidential'
    },
    'cloud-service': {
        'styles': ['cloud', 'aws', 'azure', 'gcp', 's3', 'lambda', 'function'],
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'serverless': {
        'styles': ['lambda', 'function', 'serverless', 'faas'],
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'microservice': {
        'styles': ['service', 'microservice', 'ms', 'backend'],
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'load-balancer': {
        'styles': ['load-balancer', 'lb', 'haproxy', 'nginx'],
        'authentication': 'none',
        'authorization': 'none',
        'data_sensitivity': 'public'
    },
    'cache': {
        'styles': ['cache', 'redis', 'memcached', 'memory'],
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'message-queue': {
        'styles': ['queue', 'kafka', 'rabbitmq', 'mq', 'message'],
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'process': {
        'styles': ['process', 'application', 'app', 'program'],
        'authentication': 'none',
        'authorization': 'none',
        'data_sensitivity': 'public'
    },
    'gateway': {
        'styles': ['gateway', 'api-gateway', 'proxy'],
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'cdn': {
        'styles': ['cdn', 'content-delivery', 'edge'],
        'authentication': 'none',
        'authorization': 'none',
        'data_sensitivity': 'public'
    },
    'monitoring': {
        'styles': ['monitoring', 'metrics', 'logging', 'prometheus', 'grafana'],
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    }
}

# Types de données et leurs sensibilités
DATA_TYPES = {
    'user': {
        'sensitivity': 'confidential',
        'description': 'Données utilisateur',
        'examples': ['credentials', 'profile', 'personal']
    },
    'business': {
        'sensitivity': 'restricted',
        'description': 'Données métier',
        'examples': ['transactions', 'orders', 'invoices']
    },
    'system': {
        'sensitivity': 'internal',
        'description': 'Données système',
        'examples': ['logs', 'metrics', 'config']
    },
    'public': {
        'sensitivity': 'public',
        'description': 'Données publiques',
        'examples': ['content', 'static', 'media']
    }
}

# Protocoles de communication et leurs caractéristiques
COMMUNICATION_PROTOCOLS = {
    'http': {
        'security': 'low',
        'encryption': False,
        'authentication': 'none',
        'authorization': 'none',
        'data_sensitivity': 'public'
    },
    'https': {
        'security': 'high',
        'encryption': True,
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'ws': {
        'security': 'low',
        'encryption': False,
        'authentication': 'none',
        'authorization': 'none',
        'data_sensitivity': 'public'
    },
    'wss': {
        'security': 'high',
        'encryption': True,
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'grpc': {
        'security': 'medium',
        'encryption': True,
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'tcp': {
        'security': 'low',
        'encryption': False,
        'authentication': 'none',
        'authorization': 'none',
        'data_sensitivity': 'public'
    },
    'udp': {
        'security': 'low',
        'encryption': False,
        'authentication': 'none',
        'authorization': 'none',
        'data_sensitivity': 'public'
    },
    'mqtt': {
        'security': 'medium',
        'encryption': True,
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'amqp': {
        'security': 'high',
        'encryption': True,
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'kafka': {
        'security': 'high',
        'encryption': True,
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    }
}

class DiagramParser:
    """Parser générique pour les diagrammes XML."""

    def __init__(self, xml_content: str):
        """
        Initialise le parser avec le contenu XML.
        
        Args:
            xml_content: Contenu XML du diagramme
        """
        self.root = ET.fromstring(xml_content)
        self.diagram_type = self._detect_diagram_type()
        self.components = {}  # Cache des composants par ID
        
    def _detect_diagram_type(self) -> str:
        """
        Détecte le type de diagramme basé sur la structure XML.
        
        Returns:
            Type de diagramme détecté ('drawio', 'plantuml', 'mermaid', etc.)
        """
        # Vérification DrawIO
        if self.root.tag == 'mxfile' or 'drawio' in self.root.tag.lower():
            return 'drawio'
            
        # Vérification PlantUML
        if 'plantuml' in self.root.tag.lower():
            return 'plantuml'
            
        # Vérification Mermaid
        if 'mermaid' in self.root.tag.lower():
            return 'mermaid'
            
        # Par défaut, on considère que c'est un XML standard
        return 'standard'

    def _extract_cells(self) -> List[Dict[str, Any]]:
        """
        Extrait les cellules du diagramme selon son type.
        
        Returns:
            Liste des cellules extraites
        """
        if self.diagram_type == 'drawio':
            return self._extract_drawio_cells()
        elif self.diagram_type == 'plantuml':
            return self._extract_plantuml_cells()
        elif self.diagram_type == 'mermaid':
            return self._extract_mermaid_cells()
        else:
            return self._extract_standard_cells()

    def _extract_drawio_cells(self) -> List[Dict[str, Any]]:
        """Extrait les cellules d'un diagramme DrawIO."""
        cells = []
        for cell in self.root.findall('.//mxCell'):
            # Ignorer les cellules vides ou les cellules de structure
            if not cell.get('id') or cell.get('id') in ['0', '1']:
                continue
                
            cell_data = {
                'id': cell.get('id', ''),
                'value': cell.get('value', ''),
                'style': cell.get('style', ''),
                'source': cell.get('source', ''),
                'target': cell.get('target', ''),
                'vertex': cell.get('vertex', ''),
                'edge': cell.get('edge', ''),
                'parent': cell.get('parent', ''),
                'geometry': cell.find('mxGeometry')
            }
            cells.append(cell_data)
        return cells

    def _extract_plantuml_cells(self) -> List[Dict[str, Any]]:
        """Extrait les cellules d'un diagramme PlantUML."""
        cells = []
        # Implémentation spécifique pour PlantUML
        return cells

    def _extract_mermaid_cells(self) -> List[Dict[str, Any]]:
        """Extrait les cellules d'un diagramme Mermaid."""
        cells = []
        # Implémentation spécifique pour Mermaid
        return cells

    def _extract_standard_cells(self) -> List[Dict[str, Any]]:
        """Extrait les cellules d'un XML standard."""
        cells = []
        # Implémentation pour XML standard
        return cells

    def _identify_components(self, cells: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identifie les composants dans les cellules selon le type de diagramme.
        
        Args:
            cells: Liste des cellules extraites
            
        Returns:
            Liste des composants identifiés
        """
        components = []
        
        for cell in cells:
            if self.diagram_type == 'drawio':
                if cell.get('vertex') == '1':
                    component = self._create_component_from_drawio(cell)
                    if component:
                        components.append(component)
                        self.components[cell['id']] = component
            # Ajouter d'autres types de diagrammes ici
            
        return components

    def _determine_component_type(self, style: str, value: str = '') -> str:
        """
        Détermine le type de composant basé sur son style et sa valeur.
        
        Args:
            style: Style du composant
            value: Valeur du composant
            
        Returns:
            Type de composant
        """
        style_lower = style.lower()
        value_lower = value.lower()
        
        # Recherche dans les styles
        for comp_type, attrs in COMPONENT_TYPES.items():
            if any(s in style_lower for s in attrs['styles']):
                return comp_type
                
        # Recherche dans la valeur
        for comp_type, attrs in COMPONENT_TYPES.items():
            if any(s in value_lower for s in attrs['styles']):
                return comp_type
                
        return 'process'

    def _extract_data_assets(self, component: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrait les assets de données d'un composant.
        
        Args:
            component: Composant à analyser
            
        Returns:
            Liste des assets de données
        """
        data_assets = []
        value = component.get('value', '').lower()
        
        # Vérification des données métier en premier
        if any(word in value for word in ['order', 'transaction', 'invoice', 'payment', 'business']):
            data_assets.append({
                'id': f"data_{len(data_assets)}",
                'name': 'Business Data',
                'description': 'Données métier',
                'sensitivity': 'restricted'
            })
            
        # Puis vérification des autres types de données
        for data_type, info in DATA_TYPES.items():
            if any(example in value for example in info['examples']):
                data_assets.append({
                    'id': f"data_{len(data_assets)}",
                    'name': f"{data_type.capitalize()} Data",
                    'description': info['description'],
                    'sensitivity': info['sensitivity']
                })
                
        return data_assets

    def _create_component_from_drawio(self, cell: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crée un composant à partir d'une cellule DrawIO.
        
        Args:
            cell: Cellule DrawIO
            
        Returns:
            Composant créé ou None
        """
        style = cell.get('style', '').lower()
        value = cell.get('value', '')
        
        if not value:
            return None
            
        component_type = self._determine_component_type(style, value)
        component_attrs = COMPONENT_TYPES.get(component_type, COMPONENT_TYPES['process'])
        
        # Extraction des assets de données
        data_assets = self._extract_data_assets({'value': value})
        
        return {
            'id': cell['id'],
            'name': value,
            'type': component_type,
            'usage': 'business',
            'data_assets': data_assets,
            'authentication': component_attrs['authentication'],
            'authorization': component_attrs['authorization'],
            'data_sensitivity': component_attrs['data_sensitivity'],
            'tags': self._extract_component_tags(style, value)
        }

    def _extract_component_tags(self, style: str, value: str) -> List[str]:
        """
        Extrait les tags pertinents du composant.
        
        Args:
            style: Style du composant
            value: Valeur du composant
            
        Returns:
            Liste des tags
        """
        tags = set()
        style_lower = style.lower()
        value_lower = value.lower()
        
        # Tags basés sur le style
        for comp_type, attrs in COMPONENT_TYPES.items():
            if any(s in style_lower for s in attrs['styles']):
                tags.add(comp_type)
                
        # Tags basés sur la valeur
        if 'cloud' in value_lower:
            tags.add('cloud')
        if 'api' in value_lower:
            tags.add('api')
        if 'db' in value_lower or 'database' in value_lower:
            tags.add('database')
            
        return list(tags)

    def _identify_flows(self, cells: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identifie les flux entre les composants.
        
        Args:
            cells: Liste des cellules extraites
            
        Returns:
            Liste des flux identifiés
        """
        flows = []
        
        for cell in cells:
            if self.diagram_type == 'drawio':
                if cell.get('edge') == '1' and cell.get('source') and cell.get('target'):
                    flow = self._create_flow_from_drawio(cell)
                    if flow:
                        flows.append(flow)
            # Ajouter d'autres types de diagrammes ici
            
        return flows

    def _determine_protocol(self, style: str, value: str, source: Dict[str, Any], target: Dict[str, Any]) -> str:
        """
        Détermine le protocole de communication.
        
        Args:
            style: Style du flux
            value: Valeur du flux
            source: Composant source
            target: Composant cible
            
        Returns:
            Protocole identifié
        """
        style_lower = style.lower()
        value_lower = value.lower()
        
        # Recherche dans le style et la valeur
        for protocol in COMMUNICATION_PROTOCOLS:
            if protocol in style_lower or protocol in value_lower:
                return protocol
                
        # Détermination basée sur les composants
        source_type = source.get('type', 'process')
        target_type = target.get('type', 'process')
        
        # Priorité aux connexions base de données
        if 'database' in source_type or 'database' in target_type:
            return 'tcp'
        # Puis aux connexions API
        elif 'api' in source_type or 'api' in target_type:
            return 'https'
        # Puis aux connexions message queue
        elif 'message-queue' in source_type or 'message-queue' in target_type:
            return 'amqp'
        # Puis aux connexions cache
        elif 'cache' in source_type or 'cache' in target_type:
            return 'tcp'
            
        return 'http'

    def _create_flow_from_drawio(self, cell: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crée un flux à partir d'une cellule DrawIO.
        
        Args:
            cell: Cellule DrawIO
            
        Returns:
            Flux créé ou None
        """
        source_id = cell.get('source')
        target_id = cell.get('target')
        
        if not source_id or not target_id:
            return None
            
        source = self.components.get(source_id)
        target = self.components.get(target_id)
        
        if not source or not target:
            return None
            
        style = cell.get('style', '').lower()
        value = cell.get('value', '')
        
        protocol = self._determine_protocol(style, value, source, target)
        protocol_info = COMMUNICATION_PROTOCOLS.get(protocol, COMMUNICATION_PROTOCOLS['http'])
        
        # Détermination des données échangées
        data_assets = []
        if source.get('data_assets'):
            data_assets.extend(source['data_assets'])
        if target.get('data_assets'):
            data_assets.extend(target['data_assets'])
            
        # Déduplication des assets
        unique_assets = {asset['id']: asset for asset in data_assets}.values()
        
        return {
            'id': f"flow_{cell['id']}",
            'name': value or f"Flow from {source['name']} to {target['name']}",
            'source': source_id,
            'target': target_id,
            'protocol': protocol,
            'authentication': protocol_info['authentication'],
            'authorization': protocol_info['authorization'],
            'encryption': protocol_info['encryption'],
            'security_level': protocol_info['security'],
            'data_sensitivity': protocol_info['data_sensitivity'],
            'data_assets': list(unique_assets)
        }

    def _calculate_risk_score(self, threat: Dict[str, Any], affected_components: List[Dict[str, Any]]) -> int:
        """
        Calcule le score de risque pour une menace.
        
        Args:
            threat: Information sur la menace
            affected_components: Liste des composants affectés
            
        Returns:
            Score de risque calculé
        """
        threat_info = get_threat_info(threat.get('id', ''))
        score = threat_info.get('base_risk', 2)
        
        for component in affected_components:
            # Facteur de type de composant
            component_type = component.get('type', 'process')
            score += RISK_FACTORS['component_type'].get(component_type, 1)
            
            # Facteur d'authentification
            auth = component.get('authentication', 'none')
            score += RISK_FACTORS['authentication'].get(auth, 2)
            
            # Facteur d'autorisation
            authz = component.get('authorization', 'none')
            score += RISK_FACTORS['authorization'].get(authz, 2)
            
            # Facteur de sensibilité des données
            data_assets = component.get('data_assets', [])
            if data_assets:
                max_sensitivity = max(
                    RISK_FACTORS['data_sensitivity'].get(asset.get('sensitivity', 'internal'), 2)
                    for asset in data_assets
                )
                score += max_sensitivity
        
        return score

    def _determine_risk_level(self, score: int) -> str:
        """
        Détermine le niveau de risque basé sur le score.
        
        Args:
            score: Score de risque calculé
            
        Returns:
            Niveau de risque ('critical', 'high', 'medium', 'low')
        """
        for level, threshold in sorted(RISK_LEVELS.items(), key=lambda x: x[1], reverse=True):
            if score >= threshold:
                return level
        return 'low'

    def _extract_threats(self, cells: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extrait les menaces identifiées dans le diagramme.
        
        Args:
            cells: Liste des cellules extraites
            
        Returns:
            Liste des menaces identifiées
        """
        threats = []
        
        for cell in cells:
            if self.diagram_type == 'drawio':
                style = cell.get('style', '').lower()
                value = cell.get('value', '').lower()
                
                # Détection des menaces connues
                for threat_id, threat_info in KNOWN_THREATS.items():
                    if threat_id in value or threat_info['name'].lower() in value:
                        affected_assets = self._identify_affected_assets(cell)
                        affected_components = [self.components[asset_id] for asset_id in affected_assets if asset_id in self.components]
                        
                        # Calcul du score de risque
                        risk_score = self._calculate_risk_score(
                            {'id': threat_id, **threat_info},
                            affected_components
                        )
                        
                        # Détermination du niveau de risque
                        risk_level = self._determine_risk_level(risk_score)
                        
                        threat = {
                            'id': f"threat_{cell['id']}",
                            'name': threat_info['name'],
                            'description': threat_info.get('description', f"Identified threat: {cell.get('value', '')}"),
                            'risk_level': risk_level,
                            'risk_score': risk_score,
                            'affected_assets': affected_assets,
                            'mitigation': threat_info.get('mitigation', []),
                            'owasp_category': threat_info.get('owasp_category', ''),
                            'cwe': threat_info.get('cwe', '')
                        }
                        threats.append(threat)
                        break
                
                # Détection des menaces basée sur le style
                if 'cloud' in style or 'threat' in value or 'attack' in value:
                    affected_assets = self._identify_affected_assets(cell)
                    affected_components = [self.components[asset_id] for asset_id in affected_assets if asset_id in self.components]
                    
                    # Calcul du score de risque pour les menaces non connues
                    risk_score = self._calculate_risk_score(
                        {'id': 'unknown', 'base_risk': 2},
                        affected_components
                    )
                    
                    # Détermination du niveau de risque
                    risk_level = self._determine_risk_level(risk_score)
                    
                    threat = {
                        'id': f"threat_{cell['id']}",
                        'name': cell.get('value', 'Unnamed Threat'),
                        'description': f"Threat identified in diagram: {cell.get('value', '')}",
                        'risk_level': risk_level,
                        'risk_score': risk_score,
                        'affected_assets': affected_assets,
                        'mitigation': [],
                        'owasp_category': '',
                        'cwe': ''
                    }
                    threats.append(threat)
                    
        return threats

    def _identify_affected_assets(self, threat_cell: Dict[str, Any]) -> List[str]:
        """
        Identifie les assets affectés par une menace.
        
        Args:
            threat_cell: Cellule représentant la menace
            
        Returns:
            Liste des IDs des assets affectés
        """
        affected_assets = []
        
        # Recherche des composants connectés à la menace
        for cell in self.root.findall('.//mxCell'):
            if cell.get('edge') == '1':
                source = cell.get('source')
                target = cell.get('target')
                
                if source == threat_cell['id'] and target in self.components:
                    affected_assets.append(target)
                elif target == threat_cell['id'] and source in self.components:
                    affected_assets.append(source)
                    
        return affected_assets

    def to_threagile_format(self) -> Dict[str, Any]:
        """
        Convertit le diagramme en format Threagile.
        
        Returns:
            Dictionnaire au format Threagile
        """
        cells = self._extract_cells()
        components = self._identify_components(cells)
        flows = self._identify_flows(cells)
        threats = self._extract_threats(cells)
        
        return {
            "project": {
                "name": "Architecture from Diagram",
                "description": f"Architecture converted from {self.diagram_type} diagram",
                "version": "1.0.0"
            },
            "technical_assets": components,
            "data_flows": flows,
            "threats": threats,
            "security_controls": []
        }

def convert_diagram_to_threagile(xml_content: str) -> Dict[str, Any]:
    """
    Convertit un diagramme XML en format Threagile.
    
    Args:
        xml_content: Contenu XML du diagramme
        
    Returns:
        Dictionnaire au format Threagile
    """
    parser = DiagramParser(xml_content)
    return parser.to_threagile_format() 