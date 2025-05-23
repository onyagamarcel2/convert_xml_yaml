"""
Module de détection des composants.
"""

from typing import Dict, List, Optional, Tuple, Set
from .component_types import COMPONENT_TYPES
from .composite_component import CompositeComponentManager, CompositeComponent
from ..utils.validators import validate_and_correct_component
import logging
import re
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class DetectionContext:
    """Contexte de détection pour les composants."""
    connected_components: Set[str] = None
    parent_component: Optional[str] = None
    component_hierarchy: Dict[str, List[str]] = None
    security_context: Dict[str, str] = None
    
    def __post_init__(self):
        if self.connected_components is None:
            self.connected_components = set()
        if self.component_hierarchy is None:
            self.component_hierarchy = defaultdict(list)
        if self.security_context is None:
            self.security_context = {}

class ComponentDetector:
    """Classe pour la détection des composants."""
    
    def __init__(self):
        self.component_types = COMPONENT_TYPES
        self.min_confidence_score = 0.3
        self.context = DetectionContext()
        self.composite_manager = CompositeComponentManager()
        
        # Patterns avancés pour la détection
        self.advanced_patterns = {
            'database': {
                'patterns': [
                    r'(?i)(db|database|sql|nosql|postgres|mysql|mongodb|oracle)',
                    r'(?i)(data\s*store|data\s*warehouse|data\s*lake)',
                    r'(?i)(rdbms|document\s*store|key\s*value)'
                ],
                'context_rules': [
                    lambda ctx: 'api' in ctx.connected_components,
                    lambda ctx: 'web-application' in ctx.connected_components
                ]
            },
            'api': {
                'patterns': [
                    r'(?i)(api|rest|graphql|endpoint|service)',
                    r'(?i)(resource|controller|handler)',
                    r'(?i)(gateway|proxy|router)'
                ],
                'context_rules': [
                    lambda ctx: 'web-application' in ctx.connected_components,
                    lambda ctx: 'database' in ctx.connected_components
                ]
            },
            'web-application': {
                'patterns': [
                    r'(?i)(web|browser|client|frontend|ui|interface)',
                    r'(?i)(spa|mpa|application)',
                    r'(?i)(portal|dashboard|console)'
                ],
                'context_rules': [
                    lambda ctx: 'api' in ctx.connected_components,
                    lambda ctx: 'cdn' in ctx.connected_components
                ]
            },
            'cloud-service': {
                'patterns': [
                    r'(?i)(cloud|aws|azure|gcp|s3|lambda|function)',
                    r'(?i)(managed\s*service|platform\s*service)',
                    r'(?i)(infrastructure\s*as\s*code|iac)'
                ],
                'context_rules': [
                    lambda ctx: any(service in ctx.connected_components for service in ['api', 'database', 'serverless']),
                    lambda ctx: 'monitoring' in ctx.connected_components
                ]
            },
            'serverless': {
                'patterns': [
                    r'(?i)(lambda|function|serverless|faas)',
                    r'(?i)(event\s*driven|trigger)',
                    r'(?i)(stateless|ephemeral)'
                ],
                'context_rules': [
                    lambda ctx: 'cloud-service' in ctx.connected_components,
                    lambda ctx: 'api' in ctx.connected_components
                ]
            },
            'microservice': {
                'patterns': [
                    r'(?i)(service|microservice|ms|backend)',
                    r'(?i)(bounded\s*context|domain)',
                    r'(?i)(service\s*mesh|sidecar)'
                ],
                'context_rules': [
                    lambda ctx: 'api' in ctx.connected_components,
                    lambda ctx: 'message-queue' in ctx.connected_components
                ]
            },
            'load-balancer': {
                'patterns': [
                    r'(?i)(load-balancer|lb|haproxy|nginx)',
                    r'(?i)(traffic\s*manager|ingress)',
                    r'(?i)(reverse\s*proxy|forward\s*proxy)'
                ],
                'context_rules': [
                    lambda ctx: len(ctx.connected_components) > 2,
                    lambda ctx: 'web-application' in ctx.connected_components
                ]
            },
            'cache': {
                'patterns': [
                    r'(?i)(cache|redis|memcached|memory)',
                    r'(?i)(distributed\s*cache|session\s*store)',
                    r'(?i)(in-memory|temporary\s*storage)'
                ],
                'context_rules': [
                    lambda ctx: 'database' in ctx.connected_components,
                    lambda ctx: 'api' in ctx.connected_components
                ]
            },
            'message-queue': {
                'patterns': [
                    r'(?i)(queue|kafka|rabbitmq|mq|message)',
                    r'(?i)(event\s*bus|pub\s*sub)',
                    r'(?i)(stream|pipeline)'
                ],
                'context_rules': [
                    lambda ctx: 'microservice' in ctx.connected_components,
                    lambda ctx: 'serverless' in ctx.connected_components
                ]
            },
            'process': {
                'patterns': [
                    r'(?i)(process|application|app|program)',
                    r'(?i)(worker|job|task)',
                    r'(?i)(batch|scheduled)'
                ],
                'context_rules': [
                    lambda ctx: 'database' in ctx.connected_components,
                    lambda ctx: 'message-queue' in ctx.connected_components
                ]
            },
            'gateway': {
                'patterns': [
                    r'(?i)(gateway|api-gateway|proxy)',
                    r'(?i)(bff|backend\s*for\s*frontend)',
                    r'(?i)(edge\s*service|entry\s*point)'
                ],
                'context_rules': [
                    lambda ctx: 'api' in ctx.connected_components,
                    lambda ctx: 'web-application' in ctx.connected_components
                ]
            },
            'cdn': {
                'patterns': [
                    r'(?i)(cdn|content-delivery|edge)',
                    r'(?i)(static\s*content|media\s*delivery)',
                    r'(?i)(cache\s*network|distributed\s*network)'
                ],
                'context_rules': [
                    lambda ctx: 'web-application' in ctx.connected_components,
                    lambda ctx: 'cloud-service' in ctx.connected_components
                ]
            },
            'monitoring': {
                'patterns': [
                    r'(?i)(monitoring|metrics|logging|prometheus|grafana)',
                    r'(?i)(observability|telemetry)',
                    r'(?i)(alert|dashboard|visualization)'
                ],
                'context_rules': [
                    lambda ctx: len(ctx.connected_components) > 1,
                    lambda ctx: 'cloud-service' in ctx.connected_components
                ]
            }
        }
    
    def detect_components(self, cells: List[Dict]) -> List[Dict]:
        """Détecte les composants dans les cellules."""
        components = []
        
        # Première passe : détection basique
        for cell in cells:
            if self._is_component_cell(cell):
                component = self._create_component(cell)
                if component:
                    components.append(component)
        
        # Mise à jour du contexte
        self._update_detection_context(components)
        
        # Deuxième passe : amélioration avec le contexte
        improved_components = []
        for component in components:
            improved_component = self._improve_component_detection(component)
            if improved_component:
                # Validation et correction
                validation_result = validate_and_correct_component(improved_component, self.component_types)
                
                # Log des avertissements
                for warning in validation_result.warnings:
                    logger.warning(f"Composant {improved_component.get('id', 'unknown')}: {warning}")
                
                improved_components.append(validation_result.corrected_data)
        
        # Détection des composants composites
        composite_components = self.composite_manager.detect_composite_components(improved_components)
        
        # Fusion des composants simples et composites
        final_components = self._merge_components(improved_components, composite_components)
        
        return final_components
    
    def _merge_components(self, simple_components: List[Dict], composite_components: List[CompositeComponent]) -> List[Dict]:
        """Fusionne les composants simples et composites."""
        final_components = []
        
        # Ajout des composants simples qui ne font pas partie d'un composite
        used_component_ids = set()
        for composite in composite_components:
            used_component_ids.update(comp.get('id', '') for comp in composite.subcomponents)
        
        for component in simple_components:
            if component.get('id', '') not in used_component_ids:
                final_components.append(component)
        
        # Ajout des composants composites
        for composite in composite_components:
            final_components.append({
                'id': composite.id,
                'name': composite.name,
                'type': composite.type,
                'is_composite': True,
                'subcomponents': composite.subcomponents,
                'parent': composite.parent,
                'authentication': composite.security_context['authentication'],
                'authorization': composite.security_context['authorization'],
                'data_sensitivity': composite.security_context['data_sensitivity']
            })
        
        return final_components
    
    def _update_detection_context(self, components: List[Dict]):
        """Met à jour le contexte de détection avec les composants détectés."""
        self.context = DetectionContext()
        
        # Mise à jour des composants connectés
        for component in components:
            comp_id = component.get('id', '')
            comp_type = component.get('type', '')
            
            # Ajout au contexte de sécurité
            self.context.security_context[comp_id] = {
                'authentication': component.get('authentication', 'none'),
                'authorization': component.get('authorization', 'none'),
                'data_sensitivity': component.get('data_sensitivity', 'public')
            }
            
            # Mise à jour de la hiérarchie
            if 'parent' in component:
                self.context.component_hierarchy[component['parent']].append(comp_id)
                self.context.parent_component = component['parent']
    
    def _improve_component_detection(self, component: Dict) -> Optional[Dict]:
        """Améliore la détection d'un composant en utilisant le contexte."""
        comp_type = component.get('type', '')
        comp_id = component.get('id', '')
        
        # Mise à jour des composants connectés pour ce composant
        self.context.connected_components = set(
            comp.get('type', '') for comp in self.component_types.values()
            if comp.get('id', '') in self.context.component_hierarchy.get(comp_id, [])
        )
        
        # Vérification des règles contextuelles
        if comp_type in self.advanced_patterns:
            pattern_info = self.advanced_patterns[comp_type]
            
            # Vérification des patterns avancés
            value = component.get('value', '').lower()
            pattern_matches = any(
                bool(re.search(pattern, value))
                for pattern in pattern_info['patterns']
            )
            
            # Vérification des règles contextuelles
            context_matches = any(
                rule(self.context)
                for rule in pattern_info['context_rules']
            )
            
            # Ajustement du score de confiance
            if pattern_matches and context_matches:
                component['confidence_score'] = min(1.0, component.get('confidence_score', 0.0) + 0.2)
            elif not pattern_matches or not context_matches:
                component['confidence_score'] = max(0.0, component.get('confidence_score', 0.0) - 0.1)
        
        return component
    
    def _is_component_cell(self, cell: Dict) -> bool:
        """Vérifie si une cellule représente un composant."""
        return (
            cell.get('edge', '0') == '0' and
            'value' in cell and
            cell.get('id') not in ['0', '1']  # Ignorer les cellules structurelles
        )
    
    def _create_component(self, cell: Dict) -> Optional[Dict]:
        """Crée un objet composant à partir d'une cellule."""
        # Calcul des scores pour chaque type possible
        scores = self._calculate_component_scores(cell)
        
        # Sélection du type avec le meilleur score
        best_type, best_score = self._select_best_type(scores)
        
        if best_score < self.min_confidence_score:
            logger.warning(f"Score de confiance faible ({best_score:.2f}) pour le composant: {cell.get('value', '')}")
        
        type_info = self.component_types[best_type]
        
        return {
            'id': cell.get('id', ''),
            'name': cell.get('value', ''),
            'type': best_type,
            'confidence_score': best_score,
            'authentication': type_info['authentication'],
            'authorization': type_info['authorization'],
            'data_sensitivity': type_info['data_sensitivity'],
            'style': cell.get('style', ''),
            'value': cell.get('value', '')
        }
    
    def _calculate_component_scores(self, cell: Dict) -> Dict[str, float]:
        """
        Calcule un score pour chaque type de composant possible.
        Le score est basé sur plusieurs critères :
        - Correspondance des styles (40%)
        - Correspondance des mots-clés (30%)
        - Cohérence des attributs (20%)
        - Patterns spécifiques (10%)
        """
        scores = {}
        value = cell.get('value', '').lower()
        style = cell.get('style', '').lower()
        
        for comp_type, info in self.component_types.items():
            score = 0.0
            
            # 1. Score pour les styles (40%)
            style_matches = sum(1 for style_pattern in info['styles'] if style_pattern in style)
            if style_matches > 0:
                score += 0.4 * (style_matches / len(info['styles']))
            
            # 2. Score pour les mots-clés (30%)
            keyword_matches = sum(1 for keyword in info['styles'] if keyword in value)
            if keyword_matches > 0:
                score += 0.3 * (keyword_matches / len(info['styles']))
            
            # 3. Score pour la cohérence des attributs (20%)
            if self._check_attributes_consistency(cell, info):
                score += 0.2
            
            # 4. Score pour les patterns spécifiques (10%)
            if comp_type in self.advanced_patterns:
                pattern_info = self.advanced_patterns[comp_type]
                if any(bool(re.search(pattern, value)) for pattern in pattern_info['patterns']):
                    score += 0.1
            
            scores[comp_type] = score
        
        return scores
    
    def _select_best_type(self, scores: Dict[str, float]) -> Tuple[str, float]:
        """Sélectionne le type avec le meilleur score."""
        if not scores:
            return 'process', 0.0
        
        best_type = max(scores.items(), key=lambda x: x[1])
        return best_type
    
    def _check_attributes_consistency(self, cell: Dict, type_info: Dict) -> bool:
        """Vérifie la cohérence des attributs avec le type de composant."""
        style = cell.get('style', '').lower()
        
        # Vérification de la présence d'attributs de sécurité
        has_auth = 'auth' in style or 'login' in style
        has_authz = 'role' in style or 'permission' in style
        
        # Vérification de la cohérence avec les exigences du type
        if type_info['authentication'] == 'required' and not has_auth:
            return False
        if type_info['authorization'] == 'required' and not has_authz:
            return False
        
        return True 