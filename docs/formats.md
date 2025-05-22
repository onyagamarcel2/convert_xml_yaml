# Formats Supportés

## XML

Le convertisseur supporte les formats XML suivants :

### Structure de Base

```xml
<?xml version="1.0" encoding="UTF-8"?>
<root>
    <element attribute="value">
        <child>content</child>
    </element>
</root>
```

### Attributs

Les attributs XML sont convertis en YAML de deux façons :

1. Préfixe `-` :
```yaml
root:
  element:
    -attribute: value
    child: content
```

2. Préfixe `@` :
```yaml
root:
  element:
    @attribute: value
    child: content
```

### Éléments Imbriqués

```xml
<root>
    <parent>
        <child>
            <grandchild>value</grandchild>
        </child>
    </parent>
</root>
```

```yaml
root:
  parent:
    child:
      grandchild: value
```

### Listes

```xml
<root>
    <items>
        <item>1</item>
        <item>2</item>
        <item>3</item>
    </items>
</root>
```

```yaml
root:
  items:
    item:
      - 1
      - 2
      - 3
```

## YAML

Le convertisseur supporte les formats YAML suivants :

### Types de Données

- Chaînes de caractères
- Nombres
- Booléens
- Null
- Tableaux
- Objets

### Exemples

```yaml
# Chaînes
string: "Hello, World!"
multiline: |
  Line 1
  Line 2

# Nombres
integer: 42
float: 3.14

# Booléens
true_value: true
false_value: false

# Null
null_value: null

# Tableaux
array:
  - item1
  - item2
  - item3

# Objets
object:
  key1: value1
  key2: value2
```

## Limitations

### XML

- Les commentaires XML ne sont pas préservés
- Les espaces de noms XML ne sont pas gérés
- Les CDATA ne sont pas gérés
- Les entités XML ne sont pas gérées

### YAML

- Les ancres et références YAML ne sont pas gérées
- Les tags YAML ne sont pas gérés
- Les styles de chaînes YAML ne sont pas préservés
- Les commentaires YAML ne sont pas préservés

## Bonnes Pratiques

### XML

- Utiliser une déclaration XML valide
- Structurer les données de manière hiérarchique
- Utiliser des noms d'éléments et d'attributs significatifs
- Éviter les caractères spéciaux dans les noms

### YAML

- Utiliser l'indentation cohérente
- Préférer les styles de chaînes simples
- Éviter les caractères spéciaux dans les clés
- Utiliser des noms de clés significatifs 