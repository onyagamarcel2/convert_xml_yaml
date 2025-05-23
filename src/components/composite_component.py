"""
Module de gestion des composants composites.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class CompositeComponent:
    """Représente un composant composite."""
    id: str
    name: str
    type: str
    subcomponents: List[Dict]
    parent: Optional[str] = None
    security_context: Dict = None
    
    def __post_init__(self):
        if self.security_context is None:
            self.security_context = {
                'authentication': 'none',
                'authorization': 'none',
                'data_sensitivity': 'public'
            }

class CompositeComponentManager:
    """Gère la détection et la gestion des composants composites."""
    
    def __init__(self):
        self.composite_patterns = {
            'microservice': {
                'required_components': {'api', 'database'},
                'optional_components': {'cache', 'message-queue'},
                'naming_patterns': [
                    r'(?i)(service|microservice|backend)',
                    r'(?i)(bounded\s*context|domain)'
                ]
            },
            'web-application': {
                'required_components': {'frontend', 'api'},
                'optional_components': {'cdn', 'cache'},
                'naming_patterns': [
                    r'(?i)(web|application|portal)',
                    r'(?i)(spa|mpa|frontend)'
                ]
            },
            'cloud-service': {
                'required_components': {'api', 'database'},
                'optional_components': {'serverless', 'monitoring'},
                'naming_patterns': [
                    r'(?i)(cloud|aws|azure|gcp)',
                    r'(?i)(managed\s*service|platform)'
                ]
            }
        }
        
        self.component_hierarchy = defaultdict(list)
        self.composite_components = {}
    
    def detect_composite_components(self, components: List[Dict]) -> List[CompositeComponent]:
        """Détecte les composants composites dans la liste des composants."""
        # Construction de la hiérarchie des composants
        self._build_component_hierarchy(components)
        
        # Détection des composants composites
        composite_components = []
        for comp_type, pattern_info in self.composite_patterns.items():
            detected_composites = self._detect_composite_type(components, comp_type, pattern_info)
            composite_components.extend(detected_composites)
        
        return composite_components
    
    def _build_component_hierarchy(self, components: List[Dict]):
        """Construit la hiérarchie des composants."""
        self.component_hierarchy.clear()
        
        for component in components:
            comp_id = component.get('id', '')
            parent_id = component.get('parent', None)
            
            if parent_id:
                self.component_hierarchy[parent_id].append(comp_id)
    
    def _detect_composite_type(self, components: List[Dict], comp_type: str, pattern_info: Dict) -> List[CompositeComponent]:
        """Détecte les composants composites d'un type spécifique."""
        detected_composites = []
        
        # Création d'un dictionnaire des composants par ID
        components_by_id = {comp.get('id'): comp for comp in components}
        
        # Recherche des composants potentiels
        for component in components:
            if self._is_potential_composite(component, comp_type, pattern_info):
                # Vérification des sous-composants requis
                subcomponents = self._find_subcomponents(component, components_by_id, pattern_info)
                
                if self._validate_composite_structure(subcomponents, pattern_info):
                    composite = self._create_composite_component(component, subcomponents, comp_type)
                    detected_composites.append(composite)
        
        return detected_composites
    
    def _is_potential_composite(self, component: Dict, comp_type: str, pattern_info: Dict) -> bool:
        """Vérifie si un composant est potentiellement un composite."""
        value = component.get('value', '').lower()
        
        # Vérification des patterns de nommage
        return any(
            bool(re.search(pattern, value))
            for pattern in pattern_info['naming_patterns']
        )
    
    def _find_subcomponents(self, parent: Dict, components_by_id: Dict[str, Dict], pattern_info: Dict) -> List[Dict]:
        """Trouve les sous-composants d'un composant composite."""
        subcomponents = []
        parent_id = parent.get('id', '')
        
        # Recherche des sous-composants dans la hiérarchie
        for child_id in self.component_hierarchy.get(parent_id, []):
            child = components_by_id.get(child_id)
            if child:
                subcomponents.append(child)
        
        return subcomponents
    
    def _validate_composite_structure(self, subcomponents: List[Dict], pattern_info: Dict) -> bool:
        """Valide la structure d'un composant composite."""
        # Vérification des composants requis
        required_types = pattern_info['required_components']
        found_required = {
            comp.get('type', '')
            for comp in subcomponents
            if comp.get('type', '') in required_types
        }
        
        if not required_types.issubset(found_required):
            return False
        
        # Vérification des composants optionnels
        optional_types = pattern_info['optional_components']
        found_optional = {
            comp.get('type', '')
            for comp in subcomponents
            if comp.get('type', '') in optional_types
        }
        
        # Un composite est valide s'il a tous les composants requis
        # et au moins un composant optionnel
        return len(found_optional) > 0
    
    def _create_composite_component(self, parent: Dict, subcomponents: List[Dict], comp_type: str) -> CompositeComponent:
        """Crée un composant composite à partir de ses sous-composants."""
        # Détermination du contexte de sécurité
        security_context = self._determine_security_context(subcomponents)
        
        return CompositeComponent(
            id=parent.get('id', ''),
            name=parent.get('value', ''),
            type=comp_type,
            subcomponents=subcomponents,
            parent=parent.get('parent'),
            security_context=security_context
        )
    
    def _determine_security_context(self, subcomponents: List[Dict]) -> Dict:
        """Détermine le contexte de sécurité d'un composant composite."""
        security_context = {
            'authentication': 'none',
            'authorization': 'none',
            'data_sensitivity': 'public'
        }
        
        # Analyse des sous-composants pour déterminer le contexte de sécurité
        for component in subcomponents:
            # Authentication
            if component.get('authentication') == 'required':
                security_context['authentication'] = 'required'
            
            # Authorization
            if component.get('authorization') == 'required':
                security_context['authorization'] = 'required'
            
            # Data sensitivity
            component_sensitivity = component.get('data_sensitivity', 'public')
            if component_sensitivity == 'restricted':
                security_context['data_sensitivity'] = 'restricted'
            elif component_sensitivity == 'confidential' and security_context['data_sensitivity'] == 'public':
                security_context['data_sensitivity'] = 'confidential'
        
        return security_context 