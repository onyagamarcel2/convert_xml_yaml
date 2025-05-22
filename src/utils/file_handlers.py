"""
Module de gestion des fichiers pour le convertisseur XML/YAML.
"""
import os
import logging
from pathlib import Path
from typing import Optional, Union, List, Tuple

logger = logging.getLogger(__name__)

def ensure_directory_exists(filepath: str) -> None:
    """
    Crée le répertoire parent si nécessaire.
    
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

def validate_file_size(filepath: str, max_size_mb: int = 100) -> bool:
    """
    Vérifie si la taille du fichier est acceptable.
    
    Args:
        filepath: Chemin du fichier
        max_size_mb: Taille maximale en Mo
        
    Returns:
        True si la taille est acceptable, False sinon
    """
    size_bytes = get_file_size(filepath)
    size_mb = size_bytes / (1024 * 1024)
    if size_mb > max_size_mb:
        logger.warning(f"File {filepath} is too large ({size_mb:.2f}MB > {max_size_mb}MB)")
        return False
    return True

def preserve_directory_structure(input_path: str, output_path: str, base_dir: str) -> str:
    """
    Préserve la structure des répertoires lors de la conversion.
    
    Args:
        input_path: Chemin du fichier d'entrée
        output_path: Chemin du fichier de sortie
        base_dir: Répertoire de base
        
    Returns:
        Chemin du fichier de sortie avec la structure préservée
    """
    if not os.path.isabs(input_path):
        input_path = os.path.abspath(input_path)
    
    rel_path = os.path.relpath(input_path, base_dir)
    output_dir = os.path.join(output_path, os.path.dirname(rel_path))
    ensure_directory_exists(output_dir)
    
    return os.path.join(output_dir, os.path.basename(rel_path))

def get_files_to_process(path: str, pattern: str) -> List[str]:
    """
    Récupère la liste des fichiers à traiter.
    
    Args:
        path: Chemin du fichier ou répertoire
        pattern: Motif de recherche des fichiers
        
    Returns:
        Liste des fichiers à traiter
    """
    if os.path.isfile(path):
        return [path]
    
    files = []
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            if pattern.match(filename):
                files.append(os.path.join(root, filename))
    return files 