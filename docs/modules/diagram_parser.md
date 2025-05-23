# Module Diagram Parser

## Vue d'ensemble
Le module Diagram Parser est responsable de l'analyse et de l'extraction des informations des diagrammes DrawIO. Il transforme les fichiers XML DrawIO en une représentation structurée utilisable par le reste de l'application.

## Composants principaux

### Parser Factory
- **Rôle** : Crée et configure les parsers appropriés
- **Fonctionnalités** :
  - Détection automatique du type de diagramme
  - Configuration des parsers spécifiques
  - Gestion des erreurs de parsing

### DrawIO Parser
- **Rôle** : Parse les fichiers XML DrawIO
- **Fonctionnalités** :
  - Extraction des composants
  - Analyse des relations
  - Gestion des attributs
  - Support des styles et formats

## Utilisation

```python
from src.diagram_parser.parser_factory import ParserFactory

# Création d'un parser
parser = ParserFactory.create_parser("drawio")

# Parsing d'un fichier
result = parser.parse("diagram.drawio.xml")
```

## Détails techniques

### Structure des données
- Composants : éléments graphiques (formes, conteneurs)
- Relations : connexions entre composants
- Attributs : propriétés des éléments

### Gestion des erreurs
- Validation du format XML
- Vérification de la structure
- Gestion des cas particuliers

## Tests
```bash
pytest tests/unit/test_diagram_parser.py
```

## Dépendances
- xml.etree.ElementTree
- logging
- typing 