"""
Module de gestion des fichiers pour le convertisseur XML/YAML.
"""
import os
import logging
from pathlib import Path
from typing import Optional, Union, List, Tuple
from ..exceptions.converter_exceptions import FileError

logger = logging.getLogger(__name__)

def ensure_directory_exists(filepath: str) -> None:
    """
    Crée le répertoire parent du fichier s'il n'existe pas.
    
    Args:
        filepath: Chemin du fichier
    """
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def get_file_size(filepath: str) -> int:
    """
    Obtient la taille d'un fichier en octets.
    
    Args:
        filepath: Chemin du fichier
        
    Returns:
        Taille du fichier en octets
    """
    return os.path.getsize(filepath)

def validate_file_size(filepath: str, max_size_mb: int) -> bool:
    """
    Vérifie si la taille du fichier est inférieure à la limite.
    
    Args:
        filepath: Chemin du fichier
        max_size_mb: Taille maximale en Mo
        
    Returns:
        True si la taille est valide, False sinon
    """
    try:
        size_mb = get_file_size(filepath) / (1024 * 1024)
        if size_mb > max_size_mb:
            logger.warning(f"File {filepath} is too large ({size_mb:.2f}MB > {max_size_mb}MB)")
            return False
        return True
    except OSError as e:
        raise FileError(f"Erreur lors de la vérification de la taille du fichier: {e}")

def preserve_directory_structure(
    input_file: str,
    output_file: str,
    base_dir: str
) -> str:
    """
    Préserve la structure des répertoires lors de la conversion.
    
    Args:
        input_file: Fichier d'entrée
        output_file: Fichier de sortie
        base_dir: Répertoire de base
        
    Returns:
        Nouveau chemin du fichier de sortie
    """
    rel_path = os.path.relpath(input_file, base_dir)
    output_dir = os.path.dirname(output_file)
    new_output = os.path.join(output_dir, rel_path)
    ensure_directory_exists(new_output)
    return new_output

def get_files_to_process(
    directory: str,
    pattern: str
) -> List[str]:
    """
    Récupère la liste des fichiers à traiter.
    
    Args:
        directory: Répertoire à scanner
        pattern: Motif de recherche
        
    Returns:
        Liste des fichiers correspondants
    """
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if pattern in filename:
                files.append(os.path.join(root, filename))
    return files 