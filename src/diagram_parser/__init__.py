"""
Module principal pour le parsing des diagrammes.
"""

from .parser_factory import DiagramParserFactory
 
def parse_diagram(xml_content: str):
    """Parse un diagramme en utilisant le parser approprié."""
    return DiagramParserFactory.parse_diagram(xml_content) 