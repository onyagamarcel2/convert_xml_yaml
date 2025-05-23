"""
Module de reporting pour la conversion DrawIO vers Threagile.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
import json
import yaml
from pathlib import Path
from datetime import datetime
import time
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ConversionStats:
    """Statistiques de conversion."""
    total_files: int
    successful_conversions: int
    failed_conversions: int
    total_components: int
    total_technical_assets: int
    total_data_assets: int
    total_trust_boundaries: int
    total_relations: int
    conversion_time: float
    validation_errors: List[str]
    validation_warnings: List[str]

@dataclass
class ConversionResult:
    """Résultat d'une conversion."""
    success: bool
    input_file: str
    output_file: str
    stats: ConversionStats
    errors: List[str]
    warnings: List[str]
    details: Dict[str, Any]

class ConversionReporter:
    """Classe pour la génération de rapports de conversion."""
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialise le reporter.
        
        Args:
            output_dir: Répertoire de sortie pour les rapports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration du logging
        self._setup_logging()
        
        # Statistiques globales
        self.global_stats = ConversionStats(
            total_files=0,
            successful_conversions=0,
            failed_conversions=0,
            total_components=0,
            total_technical_assets=0,
            total_data_assets=0,
            total_trust_boundaries=0,
            total_relations=0,
            conversion_time=0.0,
            validation_errors=[],
            validation_warnings=[]
        )
        
        # Historique des conversions
        self.conversion_history: List[ConversionResult] = []
    
    def _setup_logging(self) -> None:
        """Configure le logging structuré."""
        # Création du handler pour les fichiers
        log_file = self.output_dir / f"conversion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Format du logging
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Ajout du handler au logger
        logger.addHandler(file_handler)
    
    def log_conversion_start(self, input_file: str) -> None:
        """
        Log le début d'une conversion.
        
        Args:
            input_file: Fichier d'entrée
        """
        logger.info(f"Début de la conversion: {input_file}")
    
    def log_conversion_end(self, result: ConversionResult) -> None:
        """
        Log la fin d'une conversion.
        
        Args:
            result: Résultat de la conversion
        """
        if result.success:
            logger.info(
                f"Conversion réussie: {result.input_file} -> {result.output_file} "
                f"(temps: {result.stats.conversion_time:.2f}s)"
            )
        else:
            logger.error(
                f"Échec de la conversion: {result.input_file} - "
                f"Erreurs: {', '.join(result.errors)}"
            )
    
    def log_validation_result(self, result: Any) -> None:
        """
        Log le résultat d'une validation.
        
        Args:
            result: Résultat de la validation
        """
        if hasattr(result, 'is_valid'):
            if result.is_valid:
                logger.info("Validation réussie")
            else:
                logger.error(f"Validation échouée: {', '.join(result.errors)}")
                if result.warnings:
                    logger.warning(f"Avertissements: {', '.join(result.warnings)}")
    
    def update_stats(self, result: ConversionResult) -> None:
        """
        Met à jour les statistiques globales.
        
        Args:
            result: Résultat de la conversion
        """
        self.global_stats.total_files += 1
        if result.success:
            self.global_stats.successful_conversions += 1
        else:
            self.global_stats.failed_conversions += 1
        
        # Mise à jour des compteurs
        self.global_stats.total_components += result.stats.total_components
        self.global_stats.total_technical_assets += result.stats.total_technical_assets
        self.global_stats.total_data_assets += result.stats.total_data_assets
        self.global_stats.total_trust_boundaries += result.stats.total_trust_boundaries
        self.global_stats.total_relations += result.stats.total_relations
        self.global_stats.conversion_time += result.stats.conversion_time
        
        # Ajout des erreurs et avertissements
        self.global_stats.validation_errors.extend(result.stats.validation_errors)
        self.global_stats.validation_warnings.extend(result.stats.validation_warnings)
        
        # Ajout à l'historique
        self.conversion_history.append(result)
    
    def generate_report(self, format: str = "json") -> str:
        """
        Génère un rapport de conversion.
        
        Args:
            format: Format du rapport ('json' ou 'yaml')
            
        Returns:
            str: Chemin du fichier de rapport généré
        """
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "global_stats": {
                "total_files": self.global_stats.total_files,
                "successful_conversions": self.global_stats.successful_conversions,
                "failed_conversions": self.global_stats.failed_conversions,
                "total_components": self.global_stats.total_components,
                "total_technical_assets": self.global_stats.total_technical_assets,
                "total_data_assets": self.global_stats.total_data_assets,
                "total_trust_boundaries": self.global_stats.total_trust_boundaries,
                "total_relations": self.global_stats.total_relations,
                "total_conversion_time": self.global_stats.conversion_time,
                "average_conversion_time": (
                    self.global_stats.conversion_time / self.global_stats.total_files
                    if self.global_stats.total_files > 0 else 0
                ),
                "validation_errors": self.global_stats.validation_errors,
                "validation_warnings": self.global_stats.validation_warnings
            },
            "conversion_history": [
                {
                    "input_file": result.input_file,
                    "output_file": result.output_file,
                    "success": result.success,
                    "conversion_time": result.stats.conversion_time,
                    "errors": result.errors,
                    "warnings": result.warnings,
                    "stats": {
                        "components": result.stats.total_components,
                        "technical_assets": result.stats.total_technical_assets,
                        "data_assets": result.stats.total_data_assets,
                        "trust_boundaries": result.stats.total_trust_boundaries,
                        "relations": result.stats.total_relations
                    }
                }
                for result in self.conversion_history
            ]
        }
        
        # Génération du rapport
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if format.lower() == "yaml":
            report_file = self.output_dir / f"conversion_report_{timestamp}.yaml"
            with open(report_file, 'w', encoding='utf-8') as f:
                yaml.dump(report_data, f, allow_unicode=True, sort_keys=False)
        else:
            report_file = self.output_dir / f"conversion_report_{timestamp}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Rapport généré: {report_file}")
        return str(report_file)
    
    def generate_summary(self) -> str:
        """
        Génère un résumé des conversions.
        
        Returns:
            str: Résumé formaté
        """
        summary = [
            "=== Résumé des Conversions ===",
            f"Total des fichiers: {self.global_stats.total_files}",
            f"Conversions réussies: {self.global_stats.successful_conversions}",
            f"Conversions échouées: {self.global_stats.failed_conversions}",
            f"Taux de réussite: {(self.global_stats.successful_conversions / self.global_stats.total_files * 100):.1f}%",
            "",
            "=== Statistiques Globales ===",
            f"Composants: {self.global_stats.total_components}",
            f"Assets techniques: {self.global_stats.total_technical_assets}",
            f"Assets de données: {self.global_stats.total_data_assets}",
            f"Limites de confiance: {self.global_stats.total_trust_boundaries}",
            f"Relations: {self.global_stats.total_relations}",
            "",
            "=== Temps de Conversion ===",
            f"Temps total: {self.global_stats.conversion_time:.2f}s",
            f"Temps moyen: {(self.global_stats.conversion_time / self.global_stats.total_files):.2f}s",
            "",
            "=== Validation ===",
            f"Erreurs: {len(self.global_stats.validation_errors)}",
            f"Avertissements: {len(self.global_stats.validation_warnings)}"
        ]
        
        return "\n".join(summary)
    
    def reset(self) -> None:
        """Réinitialise les statistiques et l'historique."""
        self.global_stats = ConversionStats(
            total_files=0,
            successful_conversions=0,
            failed_conversions=0,
            total_components=0,
            total_technical_assets=0,
            total_data_assets=0,
            total_trust_boundaries=0,
            total_relations=0,
            conversion_time=0.0,
            validation_errors=[],
            validation_warnings=[]
        )
        self.conversion_history = []
        logger.info("Statistiques réinitialisées") 