# Guide d'Utilisation du Convertisseur XML/YAML

## Installation

```bash
pip install convertisseur-xml-yaml
```

## Utilisation de Base

### Conversion XML vers YAML

```bash
# Conversion d'un fichier
convertisseur fichier.xml

# Conversion avec sortie spécifique
convertisseur fichier.xml -o sortie.yaml

# Conversion d'un répertoire
convertisseur repertoire/
```

### Conversion YAML vers XML

```bash
# Conversion d'un fichier
convertisseur fichier.yaml -r

# Conversion avec sortie spécifique
convertisseur fichier.yaml -r -o sortie.xml

# Conversion d'un répertoire
convertisseur repertoire/ -r
```

### Utilisation avec l'Entrée Standard

```bash
# Conversion depuis stdin
cat fichier.xml | convertisseur -

# Conversion vers stdout
convertisseur fichier.xml -o -
```

## Options

- `-r, --reverse` : Convertir de YAML vers XML
- `-o, --output` : Spécifier le fichier de sortie
- `-p, --preserve` : Préserver la structure des répertoires
- `-m, --max-size` : Taille maximale des fichiers en Mo (défaut: 100)

## Exemples

### Conversion Simple

```bash
# XML vers YAML
convertisseur config.xml

# YAML vers XML
convertisseur config.yaml -r
```

### Conversion avec Structure Préservée

```bash
# Préserver la structure des répertoires
convertisseur src/ -p -o output/
```

### Conversion avec Limite de Taille

```bash
# Limiter la taille des fichiers à 50 Mo
convertisseur data/ -m 50
```

## Gestion des Erreurs

Le convertisseur gère plusieurs types d'erreurs :

- Fichiers inexistants
- Fichiers trop volumineux
- XML/YAML invalide
- Erreurs de conversion
- Erreurs d'entrée/sortie

Les erreurs sont affichées avec leur niveau de sévérité :
- WARNING : Problèmes non critiques
- ERROR : Problèmes critiques

## Journalisation

Le convertisseur génère des logs détaillés :
- Opérations de conversion
- Création de répertoires
- Erreurs et avertissements
- Résumé des opérations 