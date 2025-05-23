# Module Mappers

## Vue d'ensemble
Le module Mappers est responsable de la transformation des éléments DrawIO en format Threagile. Il gère le mapping des composants, relations et attributs selon des règles configurables.

## Composants principaux

### Threagile Mapper
- **Rôle** : Conversion des données DrawIO vers Threagile
- **Fonctionnalités** :
  - Mapping des composants
  - Transformation des relations
  - Gestion des attributs de sécurité
  - Support des composants composites

### Mapping Rules
- **Rôle** : Configuration des règles de mapping
- **Fonctionnalités** :
  - Définition des correspondances
  - Validation des règles
  - Gestion des cas particuliers

## Utilisation

```python
from src.mappers.threagile_mapper import ThreagileMapper

# Création d'un mapper
mapper = ThreagileMapper(config_path="config/mapping_rules.yaml")

# Conversion des données
result = mapper.map_to_threagile(drawio_data)
```

## Détails techniques

### Structure de mapping
- Composants : mapping des types et attributs
- Relations : transformation des connexions
- Attributs : conversion des propriétés

### Règles de validation
- Vérification des champs requis
- Validation des types
- Contrôle des références

## Configuration

### Format YAML
```yaml
component_types:
  web-application:
    - "web-app"
    - "webapp"
  database:
    - "database"
    - "db"
```

### Règles de validation
```yaml
validation_rules:
  component_naming: "^[a-z0-9-]+$"
  min_description_length: 10
  max_description_length: 500
```

## Tests
```bash
pytest tests/unit/test_mappers.py
```

## Dépendances
- yaml
- logging
- typing
- re 