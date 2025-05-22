#!/usr/bin/env python3

"""
Tool to convert XML <-> YAML
Supports:
- Input files, directories, or stdin
- Output YAML or reverse to XML with --reverse
- Summary output with count, errors, duration
- Automatic output file creation with corresponding extension
- Directory structure preservation
- File size validation
- Format validation
- Conversion result validation
"""

import argparse
import json
import os
import re
import sys
import time
import xml.parsers.expat
import xmltodict
import yaml
import logging
from io import StringIO
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from src.utils.file_handlers import (
    ensure_directory_exists,
    validate_file_size,
    preserve_directory_structure,
    get_files_to_process
)
from src.utils.validators import (
    validate_xml,
    validate_yaml,
    validate_conversion_result
)
from src.exceptions.converter_exceptions import (
    ConverterError,
    FileError,
    ValidationError,
    ConversionError
)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('converter.log')
    ]
)

logger = logging.getLogger(__name__)

ERRORS = {
    'WARNING': 1,
    'CRITICAL': 2
}

summary = {
    'converted': 0,
    'errors': 0,
    'start_time': time.time()
}

def die(msg: str, code: int = ERRORS['CRITICAL']) -> None:
    """
    Gère les erreurs fatales.
    
    Args:
        msg: Message d'erreur
        code: Code d'erreur
    """
    logger.error(msg)
    summary['errors'] += 1
    if code == ERRORS['CRITICAL']:
        sys.exit(code)

def xml_to_yaml(content: str, filepath: Optional[str] = None) -> Optional[str]:
    """
    Convertit du XML en YAML.
    
    Args:
        content: Contenu XML
        filepath: Chemin du fichier (optionnel)
        
    Returns:
        Contenu YAML ou None en cas d'erreur
    """
    try:
        if not validate_xml(content, filepath):
            raise ValidationError(f"Invalid XML in {filepath}")
        
        parsed = xmltodict.parse(content)
        return yaml.safe_dump(json.loads(json.dumps(parsed)), sort_keys=True)
    except (xml.parsers.expat.ExpatError, ValidationError) as e:
        file_detail = f" in file '{filepath}'" if filepath else ''
        die(f"Failed to parse XML{file_detail}: {e}", ERRORS['WARNING'])
        return None

def yaml_to_xml(content: str, filepath: Optional[str] = None) -> Optional[str]:
    """
    Convertit du YAML en XML.
    
    Args:
        content: Contenu YAML
        filepath: Chemin du fichier (optionnel)
        
    Returns:
        Contenu XML ou None en cas d'erreur
    """
    try:
        if not validate_yaml(content, filepath):
            raise ValidationError(f"Invalid YAML in {filepath}")
        
        parsed = yaml.safe_load(content)

        def convert_attributes(obj: Any) -> Any:
            if isinstance(obj, dict):
                new_dict = {}
                for key, value in obj.items():
                    if isinstance(key, str) and key.startswith('-'):
                        attr_key = key[1:]
                        if isinstance(value, dict):
                            new_dict.update(convert_attributes(value))
                        else:
                            new_dict[f'@{attr_key}'] = value
                    else:
                        new_dict[key] = convert_attributes(value)
                return new_dict
            elif isinstance(obj, list):
                return [convert_attributes(item) for item in obj]
            else:
                return obj

        converted = convert_attributes(parsed)
        
        # Validation du résultat
        if not validate_conversion_result(parsed, converted):
            raise ConversionError("Conversion result validation failed")
            
        return xmltodict.unparse(converted, pretty=True)
    except (yaml.YAMLError, ValidationError, ConversionError) as e:
        file_detail = f" in file '{filepath}'" if filepath else ''
        die(f"Failed to parse YAML{file_detail}: {e}", ERRORS['WARNING'])
        return None

def safe_read_stdin() -> Optional[str]:
    """
    Lit de manière sécurisée depuis stdin.
    
    Returns:
        Contenu lu ou None en cas d'erreur
    """
    try:
        if sys.stdin.isatty():
            die("No input provided on stdin", ERRORS['WARNING'])
        return sys.stdin.read()
    except OSError as e:
        die(f"Error reading from stdin: {e}", ERRORS['WARNING'])
        return None

def get_output_filename(input_file: str, reverse: bool = False) -> Optional[str]:
    """
    Génère le nom du fichier de sortie.
    
    Args:
        input_file: Chemin du fichier d'entrée
        reverse: Mode de conversion inverse
        
    Returns:
        Nom du fichier de sortie ou None
    """
    if input_file == '-':
        return None
    base_name = os.path.splitext(input_file)[0]
    return f"{base_name}.{'xml' if reverse else 'yaml'}"

def process_file(
    filepath: str,
    reverse: bool = False,
    output_file: Optional[str] = None,
    preserve_structure: bool = False,
    base_dir: Optional[str] = None,
    max_size_mb: int = 100
) -> None:
    """
    Traite un fichier.
    
    Args:
        filepath: Chemin du fichier
        reverse: Mode de conversion inverse
        output_file: Fichier de sortie
        preserve_structure: Préserver la structure
        base_dir: Répertoire de base
        max_size_mb: Taille maximale en Mo
    """
    if filepath == '-':
        content = safe_read_stdin()
        if content is None:
            return
        output = yaml_to_xml(content) if reverse else xml_to_yaml(content)
    else:
        # Vérification de la taille
        if not validate_file_size(filepath, max_size_mb):
            die(f"File {filepath} is too large", ERRORS['WARNING'])
            return
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            output = yaml_to_xml(content, filepath) if reverse else xml_to_yaml(content, filepath)

    if output is not None:
        if output_file:
            try:
                # Création du répertoire si nécessaire
                ensure_directory_exists(output_file)
                
                # Préservation de la structure si demandée
                if preserve_structure and base_dir:
                    output_file = preserve_directory_structure(filepath, output_file, base_dir)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(output)
                logger.info(f"Output written to: {output_file}")
            except IOError as e:
                die(f"Failed to write output file {output_file}: {e}", ERRORS['WARNING'])
        else:
            output_file = get_output_filename(filepath, reverse)
            if output_file:
                try:
                    ensure_directory_exists(output_file)
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(output)
                    logger.info(f"Output written to: {output_file}")
                except IOError as e:
                    die(f"Failed to write output file {output_file}: {e}", ERRORS['WARNING'])
            else:
                print(output)
        summary['converted'] += 1

def process_path(
    path: str,
    re_suffix: re.Pattern,
    reverse: bool = False,
    output_file: Optional[str] = None,
    preserve_structure: bool = False,
    max_size_mb: int = 100
) -> None:
    """
    Traite un chemin (fichier ou répertoire).
    
    Args:
        path: Chemin à traiter
        re_suffix: Motif de recherche
        reverse: Mode de conversion inverse
        output_file: Fichier de sortie
        preserve_structure: Préserver la structure
        max_size_mb: Taille maximale en Mo
    """
    if path == '-' or os.path.isfile(path):
        process_file(path, reverse, output_file, preserve_structure, None, max_size_mb)
    elif os.path.isdir(path):
        files = get_files_to_process(path, re_suffix)
        for filepath in files:
            process_file(
                filepath,
                reverse,
                output_file,
                preserve_structure,
                path,
                max_size_mb
            )
    else:
        die(f"Invalid path: {path}")

def print_summary() -> None:
    """Affiche le résumé des opérations."""
    duration = time.time() - summary['start_time']
    logger.info("\n--- Summary ---")
    logger.info(f"Files converted: {summary['converted']}")
    logger.info(f"Errors: {summary['errors']}")
    logger.info(f"Duration: {duration:.2f}s")

def main() -> None:
    """Fonction principale."""
    parser = argparse.ArgumentParser(description="Convert XML <-> YAML")
    parser.add_argument('paths', nargs='*', help="Files or directories to process. Use '-' for stdin.")
    parser.add_argument('-r', '--reverse', action='store_true', help="Convert from YAML to XML")
    parser.add_argument('-o', '--output', help="Specify output file name")
    parser.add_argument('-p', '--preserve', action='store_true', help="Preserve directory structure")
    parser.add_argument('-m', '--max-size', type=int, default=100, help="Maximum file size in MB")
    args = parser.parse_args()

    if not args.paths:
        args.paths = ['-']

    re_suffix = re.compile(r'.*\.ya?ml$', re.I) if args.reverse else re.compile(r'.*\.xml$', re.I)

    for path in args.paths:
        if path != '-' and not os.path.exists(path):
            die(f"'{path}' not found", code=ERRORS['WARNING'])

    for path in args.paths:
        process_path(
            path,
            re_suffix,
            reverse=args.reverse,
            output_file=args.output,
            preserve_structure=args.preserve,
            max_size_mb=args.max_size
        )

    print_summary()

if __name__ == '__main__':
    main()
