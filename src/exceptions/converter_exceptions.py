"""
Module de gestion des exceptions pour le convertisseur XML/YAML.
"""

class ConverterError(Exception):
    """Exception de base pour le convertisseur."""
    pass

class FileError(ConverterError):
    """Exception liée aux fichiers."""
    pass

class ValidationError(ConverterError):
    """Exception liée à la validation."""
    pass

class ConversionError(ConverterError):
    """Exception liée à la conversion."""
    pass

class ConfigurationError(ConverterError):
    """Exception liée à la configuration."""
    pass 