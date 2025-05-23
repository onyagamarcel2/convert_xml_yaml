"""
Module de détection des menaces de sécurité.
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict
import logging
import re
from ..utils.validators import validate_and_correct_threat
from ..components.component_types import COMPONENT_TYPES
from ..flows.flow_detector import FlowDetector

logger = logging.getLogger(__name__)

@dataclass
class ThreatContext:
    """Contexte de détection pour les menaces."""
    affected_components: Set[str] = None
    affected_flows: Set[str] = None
    composite_threats: List[Dict] = None
    risk_scores: Dict[str, float] = None
    priority_levels: Dict[str, int] = None
    
    def __post_init__(self):
        if self.affected_components is None:
            self.affected_components = set()
        if self.affected_flows is None:
            self.affected_flows = set()
        if self.composite_threats is None:
            self.composite_threats = []
        if self.risk_scores is None:
            self.risk_scores = {}
        if self.priority_levels is None:
            self.priority_levels = {}

class ThreatDetector:
    """Classe pour la détection des menaces de sécurité."""
    
    def __init__(self):
        self.threat_context = ThreatContext()
        self.flow_detector = FlowDetector()
        
        # Patterns pour la détection des menaces
        self.threat_patterns = {
            'authentication': {
                'patterns': [
                    r'(?i)(auth|login|password|credential)',
                    r'(?i)(token|session|cookie)',
                    r'(?i)(identity|user|account)'
                ],
                'risk_factors': {
                    'authentication': 0.8,
                    'authorization': 0.6,
                    'data_sensitivity': 0.4
                }
            },
            'authorization': {
                'patterns': [
                    r'(?i)(authz|permission|role|access)',
                    r'(?i)(privilege|right|policy)',
                    r'(?i)(control|restrict|limit)'
                ],
                'risk_factors': {
                    'authorization': 0.8,
                    'data_sensitivity': 0.6,
                    'authentication': 0.4
                }
            },
            'data_exposure': {
                'patterns': [
                    r'(?i)(data|information|sensitive)',
                    r'(?i)(exposure|leak|breach)',
                    r'(?i)(pii|personal|confidential)'
                ],
                'risk_factors': {
                    'data_sensitivity': 0.8,
                    'encryption': 0.6,
                    'authentication': 0.4
                }
            },
            'injection': {
                'patterns': [
                    r'(?i)(injection|sql|nosql)',
                    r'(?i)(xss|script|code)',
                    r'(?i)(command|shell|exec)'
                ],
                'risk_factors': {
                    'input_validation': 0.8,
                    'authentication': 0.6,
                    'authorization': 0.4
                }
            },
            'dos': {
                'patterns': [
                    r'(?i)(dos|ddos|flood)',
                    r'(?i)(overload|exhaust|resource)',
                    r'(?i)(bottleneck|throttle|limit)'
                ],
                'risk_factors': {
                    'availability': 0.8,
                    'resource_limits': 0.6,
                    'monitoring': 0.4
                }
            }
        }
        
        # Patterns pour les menaces composites
        self.composite_threat_patterns = {
            'authentication_bypass': {
                'required_threats': {'authentication', 'authorization'},
                'optional_threats': {'injection', 'data_exposure'},
                'risk_multiplier': 1.5
            },
            'data_breach': {
                'required_threats': {'data_exposure', 'authorization'},
                'optional_threats': {'authentication', 'injection'},
                'risk_multiplier': 1.8
            },
            'service_compromise': {
                'required_threats': {'injection', 'dos'},
                'optional_threats': {'authentication', 'authorization'},
                'risk_multiplier': 1.6
            }
        }
        
        # Niveaux de priorité
        self.priority_levels = {
            'critical': 1,
            'high': 2,
            'medium': 3,
            'low': 4
        }
    
    def detect_threats(self, cells: List[Dict], components: List[Dict], flows: List[Dict]) -> List[Dict]:
        """Détecte les menaces de sécurité dans les cellules."""
        threats = []
        components_by_id = {comp.get('id'): comp for comp in components}
        flows_by_id = {flow.get('id'): flow for flow in flows}
        
        # Première passe : détection basique
        for cell in cells:
            if self._is_threat_cell(cell):
                threat = self._create_threat(cell, components_by_id, flows_by_id)
                if threat:
                    threats.append(threat)
        
        # Deuxième passe : amélioration avec le contexte
        improved_threats = []
        for threat in threats:
            improved_threat = self._improve_threat_detection(threat, components_by_id, flows_by_id)
            if improved_threat:
                # Validation et correction
                validation_result = validate_and_correct_threat(improved_threat, components_by_id, flows_by_id)
                
                # Log des avertissements
                for warning in validation_result.warnings:
                    logger.warning(f"Menace {improved_threat.get('id', 'unknown')}: {warning}")
                
                improved_threats.append(validation_result.corrected_data)
        
        # Détection des menaces composites
        composite_threats = self._detect_composite_threats(improved_threats)
        
        # Calcul des scores de risque et priorisation
        final_threats = self._calculate_risk_scores(improved_threats + composite_threats)
        
        return final_threats
    
    def _is_threat_cell(self, cell: Dict) -> bool:
        """Vérifie si une cellule représente une menace."""
        return (
            cell.get('edge', '0') == '0' and
            'value' in cell and
            cell.get('id') not in ['0', '1'] and
            any(
                bool(re.search(pattern, cell.get('value', '').lower()))
                for patterns in self.threat_patterns.values()
                for pattern in patterns['patterns']
            )
        )
    
    def _create_threat(self, cell: Dict, components_by_id: Dict[str, Dict], flows_by_id: Dict[str, Dict]) -> Optional[Dict]:
        """Crée un objet menace à partir d'une cellule."""
        # Détection du type de menace
        threat_type = self._detect_threat_type(cell)
        if not threat_type:
            return None
        
        # Détection des composants et flux affectés
        affected_components = self._detect_affected_components(cell, components_by_id)
        affected_flows = self._detect_affected_flows(cell, flows_by_id)
        
        # Calcul du score de risque initial
        risk_score = self._calculate_initial_risk_score(
            threat_type,
            affected_components,
            affected_flows
        )
        
        # Création de la menace
        return {
            'id': cell.get('id', ''),
            'type': threat_type,
            'name': cell.get('value', ''),
            'affected_components': list(affected_components),
            'affected_flows': list(affected_flows),
            'risk_score': risk_score,
            'priority': self._determine_priority(risk_score),
            'value': cell.get('value', '')
        }
    
    def _detect_threat_type(self, cell: Dict) -> Optional[str]:
        """Détecte le type de menace."""
        value = cell.get('value', '').lower()
        
        for threat_type, info in self.threat_patterns.items():
            if any(bool(re.search(pattern, value)) for pattern in info['patterns']):
                return threat_type
        
        return None
    
    def _detect_affected_components(self, cell: Dict, components_by_id: Dict[str, Dict]) -> Set[str]:
        """Détecte les composants affectés par la menace."""
        affected = set()
        value = cell.get('value', '').lower()
        
        for comp_id, component in components_by_id.items():
            comp_value = component.get('value', '').lower()
            comp_type = component.get('type', '').lower()
            
            # Vérification de la présence du composant dans la description
            if comp_value in value or comp_id in value:
                affected.add(comp_id)
                continue
            
            # Vérification des types de composants sensibles
            if comp_type in ['database', 'api', 'web-application']:
                affected.add(comp_id)
        
        return affected
    
    def _detect_affected_flows(self, cell: Dict, flows_by_id: Dict[str, Dict]) -> Set[str]:
        """Détecte les flux affectés par la menace."""
        affected = set()
        value = cell.get('value', '').lower()
        
        for flow_id, flow in flows_by_id.items():
            flow_value = flow.get('value', '').lower()
            flow_protocol = flow.get('protocol', '').lower()
            
            # Vérification de la présence du flux dans la description
            if flow_value in value or flow_id in value:
                affected.add(flow_id)
                continue
            
            # Vérification des protocoles sensibles
            if flow_protocol in ['http', 'ws', 'tcp']:
                affected.add(flow_id)
        
        return affected
    
    def _calculate_initial_risk_score(self, threat_type: str, affected_components: Set[str], affected_flows: Set[str]) -> float:
        """Calcule le score de risque initial pour une menace."""
        base_score = 0.0
        threat_info = self.threat_patterns.get(threat_type, {})
        
        # Score de base basé sur le type de menace
        risk_factors = threat_info.get('risk_factors', {})
        for factor, weight in risk_factors.items():
            base_score += weight
        
        # Ajustement basé sur le nombre de composants affectés
        component_factor = min(len(affected_components) / 5, 1.0)
        base_score *= (1 + component_factor)
        
        # Ajustement basé sur le nombre de flux affectés
        flow_factor = min(len(affected_flows) / 3, 1.0)
        base_score *= (1 + flow_factor)
        
        return min(base_score, 1.0)
    
    def _determine_priority(self, risk_score: float) -> str:
        """Détermine le niveau de priorité basé sur le score de risque."""
        if risk_score >= 0.8:
            return 'critical'
        elif risk_score >= 0.6:
            return 'high'
        elif risk_score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _improve_threat_detection(self, threat: Dict, components_by_id: Dict[str, Dict], flows_by_id: Dict[str, Dict]) -> Optional[Dict]:
        """Améliore la détection d'une menace en utilisant le contexte."""
        threat_type = threat.get('type', '')
        if not threat_type:
            return None
        
        # Mise à jour du contexte
        self.threat_context.affected_components.update(threat.get('affected_components', []))
        self.threat_context.affected_flows.update(threat.get('affected_flows', []))
        
        # Vérification de la cohérence des composants affectés
        valid_components = []
        for comp_id in threat.get('affected_components', []):
            if comp_id in components_by_id:
                valid_components.append(comp_id)
            else:
                logger.warning(f"Composant invalide {comp_id} pour la menace {threat.get('id', '')}")
        
        threat['affected_components'] = valid_components
        
        # Vérification de la cohérence des flux affectés
        valid_flows = []
        for flow_id in threat.get('affected_flows', []):
            if flow_id in flows_by_id:
                valid_flows.append(flow_id)
            else:
                logger.warning(f"Flux invalide {flow_id} pour la menace {threat.get('id', '')}")
        
        threat['affected_flows'] = valid_flows
        
        return threat
    
    def _detect_composite_threats(self, threats: List[Dict]) -> List[Dict]:
        """Détecte les menaces composites."""
        composite_threats = []
        threats_by_type = defaultdict(list)
        
        # Regroupement des menaces par type
        for threat in threats:
            threats_by_type[threat.get('type', '')].append(threat)
        
        # Détection des menaces composites
        for comp_type, pattern_info in self.composite_threat_patterns.items():
            required_threats = pattern_info['required_threats']
            optional_threats = pattern_info['optional_threats']
            
            # Vérification des menaces requises
            if not all(threat_type in threats_by_type for threat_type in required_threats):
                continue
            
            # Création de la menace composite
            composite_threat = self._create_composite_threat(
                comp_type,
                required_threats,
                optional_threats,
                threats_by_type,
                pattern_info['risk_multiplier']
            )
            
            if composite_threat:
                composite_threats.append(composite_threat)
        
        return composite_threats
    
    def _create_composite_threat(self, comp_type: str, required_threats: Set[str], optional_threats: Set[str],
                               threats_by_type: Dict[str, List[Dict]], risk_multiplier: float) -> Optional[Dict]:
        """Crée une menace composite à partir de menaces existantes."""
        # Collecte des composants et flux affectés
        affected_components = set()
        affected_flows = set()
        base_risk_score = 0.0
        
        # Traitement des menaces requises
        for threat_type in required_threats:
            for threat in threats_by_type[threat_type]:
                affected_components.update(threat.get('affected_components', []))
                affected_flows.update(threat.get('affected_flows', []))
                base_risk_score = max(base_risk_score, threat.get('risk_score', 0.0))
        
        # Traitement des menaces optionnelles
        for threat_type in optional_threats:
            if threat_type in threats_by_type:
                for threat in threats_by_type[threat_type]:
                    affected_components.update(threat.get('affected_components', []))
                    affected_flows.update(threat.get('affected_flows', []))
                    base_risk_score = max(base_risk_score, threat.get('risk_score', 0.0))
        
        # Calcul du score de risque final
        risk_score = min(base_risk_score * risk_multiplier, 1.0)
        
        return {
            'id': f"composite_{comp_type}",
            'type': comp_type,
            'name': f"Composite Threat: {comp_type}",
            'affected_components': list(affected_components),
            'affected_flows': list(affected_flows),
            'risk_score': risk_score,
            'priority': self._determine_priority(risk_score),
            'is_composite': True,
            'base_threats': list(required_threats.union(optional_threats))
        }
    
    def _calculate_risk_scores(self, threats: List[Dict]) -> List[Dict]:
        """Calcule les scores de risque finaux et priorise les menaces."""
        # Calcul des scores de risque finaux
        for threat in threats:
            # Ajustement basé sur le contexte global
            context_factor = self._calculate_context_factor(threat)
            threat['risk_score'] = min(threat.get('risk_score', 0.0) * context_factor, 1.0)
            
            # Mise à jour de la priorité
            threat['priority'] = self._determine_priority(threat['risk_score'])
        
        # Tri des menaces par priorité et score de risque
        return sorted(
            threats,
            key=lambda t: (
                self.priority_levels.get(t.get('priority', 'low'), 4),
                -t.get('risk_score', 0.0)
            )
        )
    
    def _calculate_context_factor(self, threat: Dict) -> float:
        """Calcule un facteur d'ajustement basé sur le contexte global."""
        factor = 1.0
        
        # Ajustement basé sur le nombre total de composants affectés
        total_components = len(self.threat_context.affected_components)
        if total_components > 0:
            affected_ratio = len(threat.get('affected_components', [])) / total_components
            factor *= (1 + affected_ratio)
        
        # Ajustement basé sur le nombre total de flux affectés
        total_flows = len(self.threat_context.affected_flows)
        if total_flows > 0:
            affected_ratio = len(threat.get('affected_flows', [])) / total_flows
            factor *= (1 + affected_ratio)
        
        return factor 