"""
Exceptions personnalisées pour le convertisseur XML/YAML.
"""

class ConverterError(Exception):
    """Exception de base pour le convertisseur."""
    pass

class FileError(ConverterError):
    """Erreur liée aux fichiers."""
    pass

class ValidationError(ConverterError):
    """Erreur de validation."""
    pass

class ConversionError(ConverterError):
    """Erreur de conversion."""
    pass

class ConfigurationError(ConverterError):
    """Exception liée à la configuration."""
    pass 