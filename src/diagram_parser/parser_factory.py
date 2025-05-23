"""
Module de factory pour les parsers de diagrammes.
"""

from typing import Dict, List, Optional, Tuple
import logging
import re
from dataclasses import dataclass
from collections import defaultdict
from .drawio import DrawIOParser
from .plantuml import PlantUMLParser
#from .mermaid import MermaidParser

logger = logging.getLogger(__name__)

@dataclass
class DetectionResult:
    """Résultat de la détection du type de diagramme."""
    format_type: str
    confidence: float
    details: Dict[str, any]

class ParserError(Exception):
    """Exception de base pour les erreurs de parsing."""
    pass

class FormatDetectionError(ParserError):
    """Erreur lors de la détection du format."""
    pass

class ParserNotFoundError(ParserError):
    """Erreur lorsque le parser n'est pas trouvé."""
    pass

class DiagramParserFactory:
    """Factory pour la création de parsers de diagrammes."""
    
    def __init__(self):
        self.parsers = {
            'drawio': DrawIOParser,
            'plantuml': PlantUMLParser
        }
        
        # Signatures pour la détection automatique
        self.format_signatures = {
            'drawio': [
                (r'<\?xml.*?<mxfile', 1.0),  # Signature XML DrawIO
                (r'<mxGraphModel', 0.8),      # Signature alternative
                (r'<mxCell', 0.6)            # Signature faible
            ],
            'plantuml': [
                (r'@startuml', 1.0),         # Signature PlantUML
                (r'@enduml', 0.8),           # Signature alternative
                (r'->', 0.6)                 # Signature faible
            ]
        }
    
    def detect_diagram_type(self, content: str) -> DetectionResult:
        """
        Détecte automatiquement le type de diagramme.
        
        Args:
            content: Le contenu du diagramme à analyser
            
        Returns:
            DetectionResult: Le résultat de la détection avec le format et le niveau de confiance
            
        Raises:
            FormatDetectionError: Si le format ne peut pas être détecté
        """
        try:
            scores = defaultdict(float)
            details = defaultdict(list)
            
            # Analyse du contenu pour chaque format
            for format_type, signatures in self.format_signatures.items():
                for pattern, weight in signatures:
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    for match in matches:
                        scores[format_type] += weight
                        details[format_type].append({
                            'pattern': pattern,
                            'weight': weight,
                            'position': match.start()
                        })
            
            if not scores:
                raise FormatDetectionError("Aucun format de diagramme détecté")
            
            # Sélection du format avec le meilleur score
            best_format = max(scores.items(), key=lambda x: x[1])
            
            return DetectionResult(
                format_type=best_format[0],
                confidence=best_format[1],
                details=details[best_format[0]]
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection du format: {str(e)}")
            raise FormatDetectionError(f"Erreur lors de la détection du format: {str(e)}")
    
    def get_parser(self, format_type: Optional[str] = None, content: Optional[str] = None) -> any:
        """
        Récupère le parser approprié pour le format spécifié.
        
        Args:
            format_type: Le type de format (optionnel si content est fourni)
            content: Le contenu du diagramme (optionnel si format_type est fourni)
            
        Returns:
            Le parser approprié
            
        Raises:
            ParserNotFoundError: Si le parser n'est pas trouvé
            FormatDetectionError: Si le format ne peut pas être détecté
            ValueError: Si ni format_type ni content n'est fourni
        """
        try:
            # Si le format n'est pas spécifié, essayer de le détecter
            if not format_type and content:
                detection_result = self.detect_diagram_type(content)
                format_type = detection_result.format_type
                logger.info(f"Format détecté: {format_type} (confiance: {detection_result.confidence})")
            elif not format_type:
                raise ValueError("format_type ou content doit être fourni")
            
            # Récupération du parser
            parser_class = self.parsers.get(format_type)
            if not parser_class:
                raise ParserNotFoundError(f"Parser non trouvé pour le format: {format_type}")
            
            return parser_class()
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du parser: {str(e)}")
            raise
    
    def parse_diagram(self, content: str, format_type: Optional[str] = None) -> Dict:
        """
        Parse un diagramme en détectant automatiquement son format si nécessaire.
        
        Args:
            content: Le contenu du diagramme
            format_type: Le type de format (optionnel)
            
        Returns:
            Dict: Le résultat du parsing
            
        Raises:
            ParserError: Si une erreur survient lors du parsing
        """
        try:
            parser = self.get_parser(format_type, content)
            return parser.parse(content)
            
        except Exception as e:
            logger.error(f"Erreur lors du parsing du diagramme: {str(e)}")
            raise ParserError(f"Erreur lors du parsing du diagramme: {str(e)}")

def get_parser(xml_content: str):
    """
    Retourne le parseur adapté au contenu XML fourni.
    """
    if '<mxfile' in xml_content or '<mxCell' in xml_content:
        return DrawIOParser(xml_content)
    #elif 'plantuml' in xml_content.lower():
    #    return PlantUMLParser(xml_content)
    #elif 'mermaid' in xml_content.lower():
    #    return MermaidParser(xml_content)
    else:
        raise ValueError("Type de diagramme non supporté") 