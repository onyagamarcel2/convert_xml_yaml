# Module Reporting

## Vue d'ensemble
Le module Reporting gère la génération de rapports détaillés sur le processus de conversion. Il fournit des statistiques, des logs et des informations sur les erreurs et avertissements.

## Composants principaux

### Conversion Reporter
- **Rôle** : Génération de rapports de conversion
- **Fonctionnalités** :
  - Statistiques de conversion
  - Logs détaillés
  - Rapports d'erreurs
  - Résumés de conversion

### Conversion Stats
- **Rôle** : Suivi des statistiques
- **Fonctionnalités** :
  - Compteurs d'éléments
  - Temps de conversion
  - Taux de succès
  - Métriques de qualité

## Utilisation

```python
from src.reporting.conversion_reporter import ConversionReporter

# Création d'un reporter
reporter = ConversionReporter(output_dir="reports")

# Génération d'un rapport
reporter.generate_report(
    format="yaml",
    include_stats=True,
    include_details=True
)
```

## Détails techniques

### Types de rapports
- JSON : format structuré
- YAML : format lisible
- Résumé : vue d'ensemble
- Détail : informations complètes

### Structure des rapports
```yaml
report:
  timestamp: "2024-03-14T12:00:00Z"
  statistics:
    total_files: 10
    successful: 8
    failed: 2
    components: 50
    relations: 100
  errors:
    - type: "validation_error"
      message: "Invalid component name"
  warnings:
    - type: "naming_convention"
      message: "Component name too short"
```

## Configuration

### Options de reporting
```yaml
reporting:
  output_dir: "reports"
  log_level: "INFO"
  include_stats: true
  include_details: true
  format: "yaml"
```

## Tests
```bash
pytest tests/unit/test_reporting.py
```

## Dépendances
- yaml
- json
- logging
- datetime
- pathlib 