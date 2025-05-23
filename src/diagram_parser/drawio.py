"""
Module de parsing des diagrammes DrawIO.
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict
import logging
import re
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
from ..utils.validators import validate_xml_structure, validate_relationships
from ..components.component_types import COMPONENT_TYPES
from ..flows.flow_detector import FlowDetector
from ..threats.threat_detector import ThreatDetector

logger = logging.getLogger(__name__)

@dataclass
class DrawIOContext:
    """Contexte de parsing pour les diagrammes DrawIO."""
    custom_styles: Dict[str, Dict] = None
    style_mappings: Dict[str, str] = None
    relationship_rules: Dict[str, List[str]] = None
    validation_errors: List[str] = None
    
    def __post_init__(self):
        if self.custom_styles is None:
            self.custom_styles = {}
        if self.style_mappings is None:
            self.style_mappings = {}
        if self.relationship_rules is None:
            self.relationship_rules = {}
        if self.validation_errors is None:
            self.validation_errors = []

class DrawIOParser:
    """Classe pour le parsing des diagrammes DrawIO."""
    
    def __init__(self):
        self.context = DrawIOContext()
        self.flow_detector = FlowDetector()
        self.threat_detector = ThreatDetector()
        
        # Règles de validation des relations
        self.relationship_rules = {
            'database': {
                'allowed_targets': ['api', 'web-application', 'microservice'],
                'required_protocols': ['tcp', 'https']
            },
            'api': {
                'allowed_targets': ['web-application', 'microservice', 'gateway'],
                'required_protocols': ['https', 'http']
            },
            'web-application': {
                'allowed_targets': ['api', 'database', 'cache'],
                'required_protocols': ['https', 'http']
            }
        }
        
        # Styles personnalisés par défaut
        self.default_custom_styles = {
            'secure': {
                'strokeColor': '#00FF00',
                'fillColor': '#E6FFE6',
                'dashed': '0',
                'thickness': '2'
            },
            'insecure': {
                'strokeColor': '#FF0000',
                'fillColor': '#FFE6E6',
                'dashed': '1',
                'thickness': '2'
            },
            'critical': {
                'strokeColor': '#FF0000',
                'fillColor': '#FFE6E6',
                'dashed': '0',
                'thickness': '3'
            },
            'warning': {
                'strokeColor': '#FFA500',
                'fillColor': '#FFF3E6',
                'dashed': '1',
                'thickness': '2'
            }
        }
    
    def parse(self, xml_content: str) -> Dict:
        """Parse le contenu XML d'un diagramme DrawIO."""
        try:
            # Validation de la structure XML
            validation_result = validate_xml_structure(xml_content)
            if not validation_result.is_valid:
                for error in validation_result.errors:
                    logger.error(f"Erreur de validation XML: {error}")
                    self.context.validation_errors.append(error)
                raise ValueError("Structure XML invalide")
            
            # Parsing du XML
            root = ET.fromstring(xml_content)
            
            # Extraction des styles personnalisés
            self._extract_custom_styles(root)
            
            # Extraction des cellules
            cells = self._extract_cells(root)
            
            # Validation des relations
            relationship_validation = validate_relationships(cells, self.relationship_rules)
            if not relationship_validation.is_valid:
                for error in relationship_validation.errors:
                    logger.warning(f"Relation invalide: {error}")
                    self.context.validation_errors.append(error)
            
            # Détection des composants
            components = self._detect_components(cells)
            
            # Détection des flux
            flows = self.flow_detector.detect_flows(cells, components)
            
            # Détection des menaces
            threats = self.threat_detector.detect_threats(cells, components, flows)
            
            return {
                'components': components,
                'flows': flows,
                'threats': threats,
                'validation_errors': self.context.validation_errors,
                'custom_styles': self.context.custom_styles
            }
            
        except ET.ParseError as e:
            logger.error(f"Erreur de parsing XML: {str(e)}")
            raise ValueError(f"XML invalide: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur inattendue: {str(e)}")
            raise
    
    def _extract_custom_styles(self, root: ET.Element):
        """Extrait les styles personnalisés du diagramme."""
        # Réinitialisation des styles
        self.context.custom_styles = self.default_custom_styles.copy()
        
        # Recherche des styles personnalisés dans le XML
        style_elements = root.findall(".//mxStyles/mxStyle")
        for style in style_elements:
            style_id = style.get('id', '')
            if style_id:
                style_dict = {}
                for key, value in style.attrib.items():
                    if key != 'id':
                        style_dict[key] = value
                self.context.custom_styles[style_id] = style_dict
        
        # Création des mappings de style
        self._create_style_mappings()
    
    def _create_style_mappings(self):
        """Crée des mappings entre les styles et les types de composants."""
        self.context.style_mappings = {
            'database': 'secure',
            'api': 'secure',
            'web-application': 'secure',
            'threat': 'warning',
            'critical-threat': 'critical',
            'insecure-flow': 'insecure'
        }
    
    def _extract_cells(self, root: ET.Element) -> List[Dict]:
        """Extrait les cellules du diagramme."""
        cells = []
        
        # Recherche des cellules dans le XML
        cell_elements = root.findall(".//mxCell")
        for cell in cell_elements:
            try:
                cell_dict = {
                    'id': cell.get('id', ''),
                    'value': cell.get('value', ''),
                    'style': cell.get('style', ''),
                    'edge': cell.get('edge', '0'),
                    'source': cell.get('source', ''),
                    'target': cell.get('target', ''),
                    'parent': cell.get('parent', '')
                }
                
                # Validation des attributs requis
                if not self._validate_cell_attributes(cell_dict):
                    continue
                
                # Application des styles personnalisés
                cell_dict = self._apply_custom_styles(cell_dict)
                
                cells.append(cell_dict)
                
            except Exception as e:
                logger.warning(f"Erreur lors de l'extraction de la cellule {cell.get('id', 'unknown')}: {str(e)}")
                continue
        
        return cells
    
    def _validate_cell_attributes(self, cell: Dict) -> bool:
        """Valide les attributs d'une cellule."""
        # Vérification des attributs requis
        if not cell['id']:
            logger.warning("Cellule sans ID ignorée")
            return False
        
        # Vérification des attributs pour les flux
        if cell['edge'] == '1':
            if not cell['source'] or not cell['target']:
                logger.warning(f"Flux {cell['id']} sans source ou cible ignoré")
                return False
        
        return True
    
    def _apply_custom_styles(self, cell: Dict) -> Dict:
        """Applique les styles personnalisés à une cellule."""
        style = cell.get('style', '')
        if not style:
            return cell
        
        # Recherche du style personnalisé correspondant
        for style_id, style_dict in self.context.custom_styles.items():
            if style_id in style:
                # Application des propriétés de style
                for key, value in style_dict.items():
                    if key not in style:
                        style += f";{key}={value}"
        
        cell['style'] = style
        return cell
    
    def _detect_components(self, cells: List[Dict]) -> List[Dict]:
        """Détecte les composants dans les cellules."""
        components = []
        
        for cell in cells:
            if self._is_component_cell(cell):
                component = self._create_component(cell)
                if component:
                    components.append(component)
        
        return components
    
    def _is_component_cell(self, cell: Dict) -> bool:
        """Vérifie si une cellule représente un composant."""
        return (
            cell.get('edge', '0') == '0' and
            'value' in cell and
            cell.get('id') not in ['0', '1']
        )
    
    def _create_component(self, cell: Dict) -> Optional[Dict]:
        """Crée un objet composant à partir d'une cellule."""
        # Détection du type de composant
        component_type = self._detect_component_type(cell)
        if not component_type:
            return None
        
        # Création du composant
        return {
            'id': cell.get('id', ''),
            'type': component_type,
            'name': cell.get('value', ''),
            'style': cell.get('style', ''),
            'parent': cell.get('parent', '')
        }
    
    def _detect_component_type(self, cell: Dict) -> Optional[str]:
        """Détecte le type de composant."""
        value = cell.get('value', '').lower()
        style = cell.get('style', '').lower()
        
        # Vérification des types connus
        for comp_type, info in COMPONENT_TYPES.items():
            # Vérification des styles
            if any(style_pattern in style for style_pattern in info['styles']):
                return comp_type
            
            # Vérification des mots-clés
            if any(keyword in value for keyword in info['styles']):
                return comp_type
        
        return None
    
    def validate_relationships(self, components: List[Dict], flows: List[Dict]) -> bool:
        """Valide les relations entre les composants."""
        is_valid = True
        
        for flow in flows:
            source_id = flow.get('source', '')
            target_id = flow.get('target', '')
            
            # Recherche des composants source et cible
            source = next((c for c in components if c['id'] == source_id), None)
            target = next((c for c in components if c['id'] == target_id), None)
            
            if not source or not target:
                logger.warning(f"Flux {flow['id']} avec composants manquants")
                continue
            
            # Vérification des règles de relation
            source_type = source.get('type', '')
            target_type = target.get('type', '')
            protocol = flow.get('protocol', '')
            
            if source_type in self.relationship_rules:
                rules = self.relationship_rules[source_type]
                
                # Vérification des cibles autorisées
                if target_type not in rules['allowed_targets']:
                    logger.warning(
                        f"Relation invalide: {source_type} -> {target_type} "
                        f"(cible non autorisée pour {source_type})"
                    )
                    is_valid = False
                
                # Vérification des protocoles requis
                if protocol not in rules['required_protocols']:
                    logger.warning(
                        f"Protocole invalide: {protocol} pour {source_type} -> {target_type} "
                        f"(protocoles autorisés: {rules['required_protocols']})"
                    )
                    is_valid = False
        
        return is_valid 