"""
Module de détection des flux de communication.
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict
import logging
import re
from ..utils.validators import validate_and_correct_flow
from ..protocols.protocol_types import COMMUNICATION_PROTOCOLS

logger = logging.getLogger(__name__)

@dataclass
class FlowContext:
    """Contexte de détection pour les flux."""
    source_component: Optional[Dict] = None
    target_component: Optional[Dict] = None
    bidirectional: bool = False
    conditional: bool = False
    conditions: List[str] = None
    protocol: str = 'unknown'
    security_context: Dict = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = []
        if self.security_context is None:
            self.security_context = {
                'encryption': 'none',
                'authentication': 'none',
                'authorization': 'none'
            }

class FlowDetector:
    """Classe pour la détection des flux de communication."""
    
    def __init__(self):
        self.protocols = COMMUNICATION_PROTOCOLS
        self.flow_context = FlowContext()
        
        # Patterns pour la détection des flux conditionnels
        self.conditional_patterns = {
            'if': r'(?i)(if|when|condition|check)',
            'error': r'(?i)(error|exception|fail|invalid)',
            'timeout': r'(?i)(timeout|expire|deadline)',
            'retry': r'(?i)(retry|attempt|repeat)',
            'fallback': r'(?i)(fallback|alternative|backup)'
        }
        
        # Patterns pour la détection des flux bidirectionnels
        self.bidirectional_patterns = {
            'sync': r'(?i)(sync|synchronous|request-response)',
            'async': r'(?i)(async|asynchronous|event)',
            'stream': r'(?i)(stream|continuous|realtime)',
            'websocket': r'(?i)(websocket|ws|wss)',
            'grpc': r'(?i)(grpc|rpc|remote)'
        }
    
    def detect_flows(self, cells: List[Dict], components: List[Dict]) -> List[Dict]:
        """Détecte les flux de communication dans les cellules."""
        flows = []
        components_by_id = {comp.get('id'): comp for comp in components}
        
        # Première passe : détection basique
        for cell in cells:
            if self._is_flow_cell(cell):
                flow = self._create_flow(cell, components_by_id)
                if flow:
                    flows.append(flow)
        
        # Deuxième passe : amélioration avec le contexte
        improved_flows = []
        for flow in flows:
            improved_flow = self._improve_flow_detection(flow, components_by_id)
            if improved_flow:
                # Validation et correction
                validation_result = validate_and_correct_flow(improved_flow, components_by_id, self.protocols)
                
                # Log des avertissements
                for warning in validation_result.warnings:
                    logger.warning(f"Flux {improved_flow.get('id', 'unknown')}: {warning}")
                
                improved_flows.append(validation_result.corrected_data)
        
        return improved_flows
    
    def _is_flow_cell(self, cell: Dict) -> bool:
        """Vérifie si une cellule représente un flux."""
        return (
            cell.get('edge', '0') == '1' and
            'source' in cell and
            'target' in cell
        )
    
    def _create_flow(self, cell: Dict, components_by_id: Dict[str, Dict]) -> Optional[Dict]:
        """Crée un objet flux à partir d'une cellule."""
        source_id = cell.get('source', '')
        target_id = cell.get('target', '')
        
        source_component = components_by_id.get(source_id)
        target_component = components_by_id.get(target_id)
        
        if not source_component or not target_component:
            return None
        
        # Initialisation du contexte
        self.flow_context = FlowContext(
            source_component=source_component,
            target_component=target_component
        )
        
        # Détection du protocole
        protocol = self._detect_protocol(source_component, target_component, cell)
        self.flow_context.protocol = protocol
        
        # Détection des caractéristiques du flux
        self._detect_flow_characteristics(cell)
        
        # Création du flux
        return {
            'id': cell.get('id', ''),
            'source': source_id,
            'target': target_id,
            'protocol': protocol,
            'bidirectional': self.flow_context.bidirectional,
            'conditional': self.flow_context.conditional,
            'conditions': self.flow_context.conditions,
            'security': self.flow_context.security_context,
            'value': cell.get('value', '')
        }
    
    def _detect_protocol(self, source: Dict, target: Dict, cell: Dict) -> str:
        """Détecte le protocole de communication."""
        value = cell.get('value', '').lower()
        source_type = source.get('type', '').lower()
        target_type = target.get('type', '').lower()
        
        # Vérification des patterns de protocole dans la valeur
        for protocol, info in self.protocols.items():
            if any(pattern in value for pattern in info.get('patterns', [])):
                return protocol
        
        # Détection basée sur les types de composants
        if 'database' in source_type or 'database' in target_type:
            return 'tcp'
        elif 'api' in source_type or 'api' in target_type:
            return 'https'
        elif 'message-queue' in source_type or 'message-queue' in target_type:
            return 'amqp'
        elif 'cache' in source_type or 'cache' in target_type:
            return 'tcp'
        elif 'web-application' in source_type or 'web-application' in target_type:
            return 'https'
        
        # Détection basée sur le style
        style = cell.get('style', '').lower()
        if 'dashed' in style:
            return 'udp'
        elif 'dotted' in style:
            return 'ws'
        
        return 'tcp'  # Protocole par défaut
    
    def _detect_flow_characteristics(self, cell: Dict):
        """Détecte les caractéristiques du flux (bidirectionnel, conditionnel)."""
        value = cell.get('value', '').lower()
        style = cell.get('style', '').lower()
        
        # Détection des flux bidirectionnels
        self.flow_context.bidirectional = any(
            bool(re.search(pattern, value))
            for pattern in self.bidirectional_patterns.values()
        ) or 'double' in style
        
        # Détection des flux conditionnels
        self.flow_context.conditional = any(
            bool(re.search(pattern, value))
            for pattern in self.conditional_patterns.values()
        )
        
        # Extraction des conditions
        if self.flow_context.conditional:
            self.flow_context.conditions = self._extract_conditions(value)
        
        # Mise à jour du contexte de sécurité
        self._update_security_context()
    
    def _extract_conditions(self, value: str) -> List[str]:
        """Extrait les conditions d'un flux conditionnel."""
        conditions = []
        
        # Extraction des conditions basées sur les patterns
        for condition_type, pattern in self.conditional_patterns.items():
            if re.search(pattern, value):
                conditions.append(condition_type)
        
        # Extraction des conditions explicites
        if 'if' in value.lower():
            # Recherche des conditions entre "if" et la fin de la ligne ou un point
            if_matches = re.finditer(r'(?i)if\s+([^\.]+)', value)
            for match in if_matches:
                conditions.append(match.group(1).strip())
        
        return conditions
    
    def _update_security_context(self):
        """Met à jour le contexte de sécurité du flux."""
        protocol = self.flow_context.protocol
        protocol_info = self.protocols.get(protocol, {})
        
        # Mise à jour basée sur le protocole
        self.flow_context.security_context.update({
            'encryption': protocol_info.get('encryption', 'none'),
            'authentication': protocol_info.get('authentication', 'none'),
            'authorization': protocol_info.get('authorization', 'none')
        })
        
        # Mise à jour basée sur les composants
        source = self.flow_context.source_component
        target = self.flow_context.target_component
        
        if source and target:
            # Authentication
            if source.get('authentication') == 'required' or target.get('authentication') == 'required':
                self.flow_context.security_context['authentication'] = 'required'
            
            # Authorization
            if source.get('authorization') == 'required' or target.get('authorization') == 'required':
                self.flow_context.security_context['authorization'] = 'required'
    
    def _improve_flow_detection(self, flow: Dict, components_by_id: Dict[str, Dict]) -> Optional[Dict]:
        """Améliore la détection d'un flux en utilisant le contexte."""
        source = components_by_id.get(flow.get('source', ''))
        target = components_by_id.get(flow.get('target', ''))
        
        if not source or not target:
            return None
        
        # Mise à jour du contexte
        self.flow_context.source_component = source
        self.flow_context.target_component = target
        
        # Vérification de la cohérence du protocole
        protocol = flow.get('protocol', '')
        if protocol in self.protocols:
            protocol_info = self.protocols[protocol]
            
            # Vérification de la compatibilité avec les types de composants
            source_type = source.get('type', '').lower()
            target_type = target.get('type', '').lower()
            
            if not self._is_protocol_compatible(protocol, source_type, target_type):
                # Tentative de correction du protocole
                corrected_protocol = self._correct_protocol(source_type, target_type)
                if corrected_protocol:
                    flow['protocol'] = corrected_protocol
                    logger.warning(f"Protocole corrigé pour le flux {flow.get('id', '')}: {protocol} -> {corrected_protocol}")
        
        return flow
    
    def _is_protocol_compatible(self, protocol: str, source_type: str, target_type: str) -> bool:
        """Vérifie si un protocole est compatible avec les types de composants."""
        protocol_info = self.protocols.get(protocol, {})
        compatible_types = protocol_info.get('compatible_types', set())
        
        return (
            source_type in compatible_types or
            target_type in compatible_types or
            not compatible_types  # Si aucun type compatible n'est spécifié
        )
    
    def _correct_protocol(self, source_type: str, target_type: str) -> Optional[str]:
        """Corrige le protocole en fonction des types de composants."""
        # Règles de correction basées sur les types
        if 'database' in source_type or 'database' in target_type:
            return 'tcp'
        elif 'api' in source_type or 'api' in target_type:
            return 'https'
        elif 'message-queue' in source_type or 'message-queue' in target_type:
            return 'amqp'
        elif 'cache' in source_type or 'cache' in target_type:
            return 'tcp'
        elif 'web-application' in source_type or 'web-application' in target_type:
            return 'https'
        
        return None 