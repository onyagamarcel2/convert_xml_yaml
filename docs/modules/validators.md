# Module Validators

## Vue d'ensemble
Le module Validators assure la conformité des modèles générés avec les spécifications Threagile. Il implémente un système complet de validation pour garantir la qualité et la cohérence des données.

## Composants principaux

### Threagile Validator
- **Rôle** : Validation des modèles Threagile
- **Fonctionnalités** :
  - Validation de la structure
  - Vérification des règles de sécurité
  - Détection des incohérences
  - Validation des références

### Validation Rules
- **Rôle** : Définition des règles de validation
- **Fonctionnalités** :
  - Règles de structure
  - Règles de sécurité
  - Règles de conformité

## Utilisation

```python
from src.validators.threagile_validator import ThreagileValidator

# Création d'un validateur
validator = ThreagileValidator(config_path="config/threagile_schema.yaml")

# Validation d'un modèle
result = validator.validate_yaml(yaml_content)
```

## Détails techniques

### Types de validation
- Structure : vérification de la hiérarchie
- Types : validation des types de données
- Références : contrôle des liens entre éléments
- Sécurité : vérification des niveaux CIA

### Règles de validation
```yaml
validation_rules:
  id:
    pattern: "^[a-z0-9-]+$"
    unique: true
  name:
    min_length: 3
    max_length: 100
  description:
    min_length: 10
    max_length: 500
```

## Gestion des erreurs

### Types d'erreurs
- Erreurs de structure
- Erreurs de type
- Erreurs de référence
- Erreurs de sécurité

### Format des erreurs
```python
{
    "type": "validation_error",
    "message": "Invalid component name",
    "location": "components[0].name",
    "details": "Name must match pattern ^[a-z0-9-]+$"
}
```

## Tests
```bash
pytest tests/unit/test_validators.py
```

## Dépendances
- yaml
- jsonschema
- logging
- typing 