"""
Module de validation pour les données Threagile.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
import logging
import yaml
from pathlib import Path
import re
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Résultat de la validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    details: Dict[str, Any]

class ThreagileValidator:
    """Classe pour la validation des données Threagile."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le validateur Threagile.
        
        Args:
            config_path: Chemin vers le fichier de configuration (optionnel)
        """
        # Chargement de la configuration
        self.config = self._load_config(config_path) if config_path else {}
        
        # Champs requis
        self.required_fields = self.config.get('required_fields', {
            'title': str,
            'description': str,
            'date': str,
            'author': str,
            'components': list,
            'data_assets': list,
            'trust_boundaries': list,
            'technical_assets': list,
            'relations': list
        })
        
        # Champs des composants
        self.component_fields = self.config.get('component_fields', {
            'id': str,
            'name': str,
            'type': str,
            'description': str,
            'tags': list,
            'technical_assets': list,
            'data_assets': list,
            'trust_boundaries': list,
            'security_controls': list,
            'compliance_requirements': list
        })
        
        # Champs des assets techniques
        self.technical_asset_fields = self.config.get('technical_asset_fields', {
            'id': str,
            'name': str,
            'type': str,
            'description': str,
            'usage': str,
            'owner': str,
            'confidentiality': str,
            'integrity': str,
            'availability': str,
            'justification_cia_rating': str,
            'multi_tenant': bool,
            'redundant': bool,
            'custom_developed_parts': bool,
            'encryption': str,
            'authentication': str,
            'authorization': str,
            'justification_authentication': str,
            'justification_authorization': str,
            'security_controls': list,
            'compliance_requirements': list,
            'vulnerabilities': list,
            'threats': list
        })
        
        # Champs des assets de données
        self.data_asset_fields = self.config.get('data_asset_fields', {
            'id': str,
            'name': str,
            'description': str,
            'usage': str,
            'owner': str,
            'confidentiality': str,
            'integrity': str,
            'availability': str,
            'justification_cia_rating': str,
            'storage': str,
            'format': str,
            'origin': str,
            'quantity': str,
            'tags': list,
            'security_controls': list,
            'compliance_requirements': list,
            'data_classification': str,
            'retention_period': str,
            'backup_frequency': str
        })
        
        # Champs des limites de confiance
        self.trust_boundary_fields = self.config.get('trust_boundary_fields', {
            'id': str,
            'name': str,
            'description': str,
            'type': str,
            'components': list,
            'technical_assets': list,
            'data_assets': list,
            'security_controls': list,
            'compliance_requirements': list
        })
        
        # Champs des relations
        self.relation_fields = self.config.get('relation_fields', {
            'id': str,
            'name': str,
            'description': str,
            'type': str,
            'source': str,
            'target': str,
            'protocol': str,
            'authentication': str,
            'authorization': str,
            'encryption': str,
            'data_assets': list,
            'tags': list,
            'security_controls': list,
            'compliance_requirements': list
        })
        
        # Règles de validation spécifiques
        self.validation_rules = self.config.get('validation_rules', {
            'component_naming': r'^[a-z0-9-]+$',
            'asset_naming': r'^[a-z0-9-]+$',
            'date_format': r'^\d{4}-\d{2}-\d{2}$',
            'min_description_length': 10,
            'max_description_length': 500,
            'min_name_length': 3,
            'max_name_length': 100,
            'allowed_special_chars': '-_',
            'max_tags': 10,
            'max_technical_assets': 50,
            'max_data_assets': 50,
            'max_trust_boundaries': 20,
            'max_relations': 100
        })
        
        # Niveaux de sécurité valides
        self.valid_security_levels = self.config.get('security_levels', {
            'confidentiality': {'public', 'internal', 'restricted', 'confidential', 'strictly-confidential'},
            'integrity': {'operational', 'important', 'critical', 'mission-critical'},
            'availability': {'operational', 'important', 'critical', 'mission-critical'}
        })
        
        # Règles de conformité Threagile
        self.threagile_compliance_rules = self.config.get('compliance_rules', {
            'required_trust_boundaries': True,
            'required_data_assets': True,
            'required_technical_assets': True,
            'unique_ids': True,
            'valid_relationships': True,
            'required_security_controls': True,
            'required_compliance_requirements': True,
            'required_cia_ratings': True,
            'required_justifications': True
        })
        
        # Types de composants valides
        self.valid_component_types = self._get_valid_component_types()
        
        # Types d'assets valides
        self.valid_asset_types = self._get_valid_asset_types()
        
        # Types de relations valides
        self.valid_relation_types = self._get_valid_relation_types()
        
        # Types de limites de confiance valides
        self.valid_boundary_types = self._get_valid_boundary_types()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Charge la configuration depuis un fichier YAML.
        
        Args:
            config_path: Chemin vers le fichier de configuration
            
        Returns:
            Dict[str, Any]: Configuration chargée
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Impossible de charger la configuration: {str(e)}")
            return {}
    
    def _get_valid_relation_types(self) -> Set[str]:
        """Retourne l'ensemble des types de relations valides."""
        return {
            'data-flow',
            'trust-boundary',
            'communication',
            'dependency',
            'inheritance',
            'composition',
            'aggregation',
            'association'
        }
    
    def _get_valid_boundary_types(self) -> Set[str]:
        """Retourne l'ensemble des types de limites de confiance valides."""
        return {
            'network',
            'physical',
            'logical',
            'organizational',
            'legal',
            'regulatory'
        }
    
    def _validate_data_assets(self, data_assets: List[Dict]) -> Tuple[List[str], List[str]]:
        """Valide la liste des assets de données."""
        errors = []
        warnings = []
        
        for i, asset in enumerate(data_assets):
            # Vérification des champs requis
            for field, field_type in self.data_asset_fields.items():
                if field not in asset:
                    errors.append(f"Asset de données {i}: champ requis manquant: {field}")
                elif not isinstance(asset[field], field_type):
                    errors.append(f"Asset de données {i}: type invalide pour {field}: attendu {field_type.__name__}")
            
            # Vérifications supplémentaires
            if 'data_classification' in asset and asset['data_classification'] not in self.valid_security_levels['confidentiality']:
                warnings.append(f"Asset de données {i}: classification de données invalide: {asset['data_classification']}")
            
            # Validation des longueurs
            if 'name' in asset:
                if len(asset['name']) < self.validation_rules['min_name_length']:
                    warnings.append(f"Asset de données {i}: nom trop court")
                elif len(asset['name']) > self.validation_rules['max_name_length']:
                    warnings.append(f"Asset de données {i}: nom trop long")
            
            if 'description' in asset:
                if len(asset['description']) < self.validation_rules['min_description_length']:
                    warnings.append(f"Asset de données {i}: description trop courte")
                elif len(asset['description']) > self.validation_rules['max_description_length']:
                    warnings.append(f"Asset de données {i}: description trop longue")
        
        return errors, warnings
    
    def _validate_trust_boundaries(self, boundaries: List[Dict]) -> Tuple[List[str], List[str]]:
        """Valide la liste des limites de confiance."""
        errors = []
        warnings = []
        
        for i, boundary in enumerate(boundaries):
            # Vérification des champs requis
            for field, field_type in self.trust_boundary_fields.items():
                if field not in boundary:
                    errors.append(f"Limite de confiance {i}: champ requis manquant: {field}")
                elif not isinstance(boundary[field], field_type):
                    errors.append(f"Limite de confiance {i}: type invalide pour {field}: attendu {field_type.__name__}")
            
            # Vérifications supplémentaires
            if 'type' in boundary and boundary['type'] not in self.valid_boundary_types:
                warnings.append(f"Limite de confiance {i}: type invalide: {boundary['type']}")
            
            # Validation des longueurs
            if 'name' in boundary:
                if len(boundary['name']) < self.validation_rules['min_name_length']:
                    warnings.append(f"Limite de confiance {i}: nom trop court")
                elif len(boundary['name']) > self.validation_rules['max_name_length']:
                    warnings.append(f"Limite de confiance {i}: nom trop long")
            
            if 'description' in boundary:
                if len(boundary['description']) < self.validation_rules['min_description_length']:
                    warnings.append(f"Limite de confiance {i}: description trop courte")
                elif len(boundary['description']) > self.validation_rules['max_description_length']:
                    warnings.append(f"Limite de confiance {i}: description trop longue")
        
        return errors, warnings
    
    def _validate_relations(self, relations: List[Dict], components: List[Dict], assets: List[Dict]) -> Tuple[List[str], List[str]]:
        """Valide la liste des relations."""
        errors = []
        warnings = []
        
        # Création des sets d'IDs pour la validation
        component_ids = {comp['id'] for comp in components if 'id' in comp}
        asset_ids = {asset['id'] for asset in assets if 'id' in asset}
        valid_ids = component_ids | asset_ids
        
        for i, relation in enumerate(relations):
            # Vérification des champs requis
            for field, field_type in self.relation_fields.items():
                if field not in relation:
                    errors.append(f"Relation {i}: champ requis manquant: {field}")
                elif not isinstance(relation[field], field_type):
                    errors.append(f"Relation {i}: type invalide pour {field}: attendu {field_type.__name__}")
            
            # Vérifications supplémentaires
            if 'type' in relation and relation['type'] not in self.valid_relation_types:
                warnings.append(f"Relation {i}: type invalide: {relation['type']}")
            
            # Validation des références
            if 'source' in relation and relation['source'] not in valid_ids:
                errors.append(f"Relation {i}: source invalide: {relation['source']}")
            
            if 'target' in relation and relation['target'] not in valid_ids:
                errors.append(f"Relation {i}: cible invalide: {relation['target']}")
            
            # Validation des longueurs
            if 'name' in relation:
                if len(relation['name']) < self.validation_rules['min_name_length']:
                    warnings.append(f"Relation {i}: nom trop court")
                elif len(relation['name']) > self.validation_rules['max_name_length']:
                    warnings.append(f"Relation {i}: nom trop long")
            
            if 'description' in relation:
                if len(relation['description']) < self.validation_rules['min_description_length']:
                    warnings.append(f"Relation {i}: description trop courte")
                elif len(relation['description']) > self.validation_rules['max_description_length']:
                    warnings.append(f"Relation {i}: description trop longue")
        
        return errors, warnings
    
    def validate_yaml(self, yaml_content: str) -> ValidationResult:
        """
        Valide le contenu YAML pour Threagile.
        
        Args:
            yaml_content: Le contenu YAML à valider
            
        Returns:
            ValidationResult: Le résultat de la validation
        """
        try:
            # Parsing du YAML
            data = yaml.safe_load(yaml_content)
            if not data:
                return ValidationResult(
                    is_valid=False,
                    errors=["Contenu YAML vide"],
                    warnings=[],
                    details={}
                )
            
            errors = []
            warnings = []
            details = {}
            
            # Validation des champs requis
            for field, field_type in self.required_fields.items():
                if field not in data:
                    errors.append(f"Champ requis manquant: {field}")
                elif not isinstance(data[field], field_type):
                    errors.append(f"Type invalide pour {field}: attendu {field_type.__name__}")
            
            # Validation des composants
            if 'components' in data:
                component_errors, component_warnings = self._validate_components(data['components'])
                errors.extend(component_errors)
                warnings.extend(component_warnings)
            
            # Validation des assets techniques
            if 'technical_assets' in data:
                asset_errors, asset_warnings = self._validate_technical_assets(data['technical_assets'])
                errors.extend(asset_errors)
                warnings.extend(asset_warnings)
            
            # Validation des assets de données
            if 'data_assets' in data:
                data_asset_errors, data_asset_warnings = self._validate_data_assets(data['data_assets'])
                errors.extend(data_asset_errors)
                warnings.extend(data_asset_warnings)
            
            # Validation des limites de confiance
            if 'trust_boundaries' in data:
                boundary_errors, boundary_warnings = self._validate_trust_boundaries(data['trust_boundaries'])
                errors.extend(boundary_errors)
                warnings.extend(boundary_warnings)
            
            # Validation des relations
            if 'relations' in data:
                relation_errors, relation_warnings = self._validate_relations(
                    data['relations'],
                    data.get('components', []),
                    data.get('technical_assets', [])
                )
                errors.extend(relation_errors)
                warnings.extend(relation_warnings)
            
            # Validation des règles de conformité
            self._validate_threagile_compliance(data, errors, warnings)
            
            # Validation des IDs uniques
            self._validate_unique_ids(data, errors)
            
            # Validation des relations
            self._validate_relationships(data, errors, warnings)
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                details=details
            )
            
        except yaml.YAMLError as e:
            logger.error(f"Erreur de parsing YAML: {str(e)}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Erreur de parsing YAML: {str(e)}"],
                warnings=[],
                details={}
            )
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la validation: {str(e)}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Erreur inattendue: {str(e)}"],
                warnings=[],
                details={}
            )
    
    def _validate_components(self, components: List[Dict]) -> Tuple[List[str], List[str]]:
        """Valide la liste des composants."""
        errors = []
        warnings = []
        
        for i, component in enumerate(components):
            # Vérification des champs requis
            for field, field_type in self.component_fields.items():
                if field not in component:
                    errors.append(f"Composant {i}: champ requis manquant: {field}")
                elif not isinstance(component[field], field_type):
                    errors.append(f"Composant {i}: type invalide pour {field}: attendu {field_type.__name__}")
            
            # Vérifications supplémentaires
            if 'type' in component and component['type'] not in self.valid_component_types:
                warnings.append(f"Composant {i}: type inconnu: {component['type']}")
        
        return errors, warnings
    
    def _validate_technical_assets(self, assets: List[Dict]) -> Tuple[List[str], List[str]]:
        """Valide la liste des assets techniques."""
        errors = []
        warnings = []
        
        for i, asset in enumerate(assets):
            # Vérification des champs requis
            for field, field_type in self.technical_asset_fields.items():
                if field not in asset:
                    errors.append(f"Asset {i}: champ requis manquant: {field}")
                elif not isinstance(asset[field], field_type):
                    errors.append(f"Asset {i}: type invalide pour {field}: attendu {field_type.__name__}")
            
            # Vérifications supplémentaires
            if 'type' in asset and asset['type'] not in self.valid_asset_types:
                warnings.append(f"Asset {i}: type inconnu: {asset['type']}")
        
        return errors, warnings
    
    def _validate_threagile_compliance(self, data: Dict, errors: List[str], warnings: List[str]) -> None:
        """Valide la conformité avec les règles Threagile."""
        rules = self.threagile_compliance_rules
        
        # Vérification des limites de confiance
        if rules['required_trust_boundaries'] and 'trust_boundaries' in data:
            if not data['trust_boundaries']:
                errors.append("Au moins une limite de confiance est requise")
        
        # Vérification des assets de données
        if rules['required_data_assets'] and 'data_assets' in data:
            if not data['data_assets']:
                errors.append("Au moins un asset de données est requis")
        
        # Vérification des assets techniques
        if rules['required_technical_assets'] and 'technical_assets' in data:
            if not data['technical_assets']:
                errors.append("Au moins un asset technique est requis")
        
        # Vérification des IDs uniques
        if rules['unique_ids']:
            self._validate_unique_ids(data, errors)
    
    def _validate_unique_ids(self, data: Dict, errors: List[str]) -> None:
        """Valide l'unicité des IDs."""
        all_ids = set()
        
        # Collecte des IDs de composants
        if 'components' in data:
            for i, component in enumerate(data['components']):
                if 'id' in component:
                    if component['id'] in all_ids:
                        errors.append(f"ID dupliqué trouvé: {component['id']}")
                    all_ids.add(component['id'])
        
        # Collecte des IDs d'assets
        if 'technical_assets' in data:
            for i, asset in enumerate(data['technical_assets']):
                if 'id' in asset:
                    if asset['id'] in all_ids:
                        errors.append(f"ID dupliqué trouvé: {asset['id']}")
                    all_ids.add(asset['id'])
    
    def _validate_relationships(self, data: Dict, errors: List[str], warnings: List[str]) -> None:
        """Valide les relations entre les éléments."""
        if 'components' in data and 'technical_assets' in data:
            # Création des sets d'IDs pour la validation
            component_ids = {comp['id'] for comp in data['components'] if 'id' in comp}
            asset_ids = {asset['id'] for asset in data['technical_assets'] if 'id' in asset}
            
            # Validation des références dans les composants
            for i, component in enumerate(data['components']):
                if 'technical_assets' in component:
                    for asset_id in component['technical_assets']:
                        if asset_id not in asset_ids:
                            errors.append(f"Composant {i}: référence à un asset inexistant: {asset_id}")
                
                if 'data_assets' in component:
                    for data_id in component['data_assets']:
                        if data_id not in asset_ids:
                            errors.append(f"Composant {i}: référence à un asset de données inexistant: {data_id}")
        
    def _get_valid_component_types(self) -> Set[str]:
        """Retourne l'ensemble des types de composants valides."""
        return {
            'web-application',
            'mobile-app',
            'desktop-app',
            'service',
            'database',
            'file-storage',
            'message-queue',
            'load-balancer',
            'reverse-proxy',
            'waf',
            'ids',
            'ips',
            'vpn',
            'firewall',
            'gateway',
            'api-gateway',
            'service-mesh',
            'monitoring',
            'logging',
            'authentication',
            'authorization',
            'key-management',
            'certificate-management',
            'secret-management',
            'identity-management',
            'access-management',
            'audit-logging',
            'backup',
            'disaster-recovery',
            'business-continuity',
            'incident-response',
            'vulnerability-management',
            'patch-management',
            'configuration-management',
            'change-management',
            'release-management',
            'deployment',
            'container-orchestration',
            'service-discovery',
            'api-management',
            'content-delivery',
            'dns',
            'dhcp',
            'ntp',
            'syslog',
            'monitoring-agent',
            'logging-agent',
            'security-agent',
            'endpoint-protection',
            'mobile-device-management',
            'unified-endpoint-management',
            'email',
            'chat',
            'collaboration',
            'document-management',
            'knowledge-management',
            'project-management',
            'issue-tracking',
            'version-control',
            'build-automation',
            'test-automation',
            'deployment-automation',
            'infrastructure-as-code',
            'configuration-as-code',
            'policy-as-code',
            'security-as-code',
            'compliance-as-code',
            'governance-as-code',
            'risk-management',
            'compliance-management',
            'audit-management',
            'incident-management',
            'problem-management',
            'change-management',
            'release-management',
            'deployment-management',
            'configuration-management',
            'asset-management',
            'license-management',
            'vendor-management',
            'contract-management',
            'service-level-management',
            'availability-management',
            'capacity-management',
            'continuity-management',
            'security-management',
            'risk-management',
            'compliance-management',
            'audit-management',
            'incident-management',
            'problem-management',
            'change-management',
            'release-management',
            'deployment-management',
            'configuration-management',
            'asset-management',
            'license-management',
            'vendor-management',
            'contract-management',
            'service-level-management',
            'availability-management',
            'capacity-management',
            'continuity-management'
        }
    
    def _get_valid_asset_types(self) -> Set[str]:
        """Retourne l'ensemble des types d'assets valides."""
        return {
            'application',
            'service',
            'database',
            'file-storage',
            'message-queue',
            'load-balancer',
            'reverse-proxy',
            'waf',
            'ids',
            'ips',
            'vpn',
            'firewall',
            'gateway',
            'api-gateway',
            'service-mesh',
            'monitoring',
            'logging',
            'authentication',
            'authorization',
            'key-management',
            'certificate-management',
            'secret-management',
            'identity-management',
            'access-management',
            'audit-logging',
            'backup',
            'disaster-recovery',
            'business-continuity',
            'incident-response',
            'vulnerability-management',
            'patch-management',
            'configuration-management',
            'change-management',
            'release-management',
            'deployment',
            'container-orchestration',
            'service-discovery',
            'api-management',
            'content-delivery',
            'dns',
            'dhcp',
            'ntp',
            'syslog',
            'monitoring-agent',
            'logging-agent',
            'security-agent',
            'endpoint-protection',
            'mobile-device-management',
            'unified-endpoint-management',
            'email',
            'chat',
            'collaboration',
            'document-management',
            'knowledge-management',
            'project-management',
            'issue-tracking',
            'version-control',
            'build-automation',
            'test-automation',
            'deployment-automation',
            'infrastructure-as-code',
            'configuration-as-code',
            'policy-as-code',
            'security-as-code',
            'compliance-as-code',
            'governance-as-code',
            'risk-management',
            'compliance-management',
            'audit-management',
            'incident-management',
            'problem-management',
            'change-management',
            'release-management',
            'deployment-management',
            'configuration-management',
            'asset-management',
            'license-management',
            'vendor-management',
            'contract-management',
            'service-level-management',
            'availability-management',
            'capacity-management',
            'continuity-management',
            'security-management',
            'risk-management',
            'compliance-management',
            'audit-management',
            'incident-management',
            'problem-management',
            'change-management',
            'release-management',
            'deployment-management',
            'configuration-management',
            'asset-management',
            'license-management',
            'vendor-management',
            'contract-management',
            'service-level-management',
            'availability-management',
            'capacity-management',
            'continuity-management'
        }
    
    def validate_post_conversion(self, yaml_content: str) -> ValidationResult:
        """
        Valide le contenu YAML après conversion.
        
        Args:
            yaml_content: Le contenu YAML à valider
            
        Returns:
            ValidationResult: Le résultat de la validation
        """
        result = self.validate_yaml(yaml_content)
        if not result.is_valid:
            return result
            
        try:
            data = yaml.safe_load(yaml_content)
            errors = []
            warnings = []
            details = {}
            
            # Validation des noms et formats
            self._validate_naming_conventions(data, errors, warnings)
            
            # Validation des descriptions
            self._validate_descriptions(data, errors, warnings)
            
            # Validation des niveaux de sécurité
            self._validate_security_levels(data, errors, warnings)
            
            # Validation de la conformité Threagile
            self._validate_threagile_compliance(data, errors, warnings)
            
            # Validation des relations et dépendances
            self._validate_relationships(data, errors, warnings)
            
            # Mise à jour du résultat
            result.errors.extend(errors)
            result.warnings.extend(warnings)
            result.is_valid = len(errors) == 0
            result.details.update(details)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la validation post-conversion: {str(e)}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Erreur lors de la validation post-conversion: {str(e)}"],
                warnings=[],
                details={}
            )
    
    def _validate_naming_conventions(self, data: Dict, errors: List[str], warnings: List[str]) -> None:
        """Valide les conventions de nommage."""
        # Validation des noms de composants
        if 'components' in data:
            for i, component in enumerate(data['components']):
                if 'name' in component:
                    if not re.match(self.validation_rules['component_naming'], component['name']):
                        errors.append(f"Composant {i}: nom invalide '{component['name']}'")
        
        # Validation des noms d'assets
        if 'technical_assets' in data:
            for i, asset in enumerate(data['technical_assets']):
                if 'name' in asset:
                    if not re.match(self.validation_rules['asset_naming'], asset['name']):
                        errors.append(f"Asset {i}: nom invalide '{asset['name']}'")
    
    def _validate_descriptions(self, data: Dict, errors: List[str], warnings: List[str]) -> None:
        """Valide les descriptions."""
        min_length = self.validation_rules['min_description_length']
        max_length = self.validation_rules['max_description_length']
        
        # Validation de la description principale
        if 'description' in data:
            desc = data['description']
            if len(desc) < min_length:
                warnings.append(f"Description principale trop courte ({len(desc)} caractères)")
            elif len(desc) > max_length:
                warnings.append(f"Description principale trop longue ({len(desc)} caractères)")
        
        # Validation des descriptions des composants
        if 'components' in data:
            for i, component in enumerate(data['components']):
                if 'description' in component:
                    desc = component['description']
                    if len(desc) < min_length:
                        warnings.append(f"Description du composant {i} trop courte ({len(desc)} caractères)")
                    elif len(desc) > max_length:
                        warnings.append(f"Description du composant {i} trop longue ({len(desc)} caractères)")
    
    def _validate_security_levels(self, data: Dict, errors: List[str], warnings: List[str]) -> None:
        """Valide les niveaux de sécurité."""
        if 'technical_assets' in data:
            for i, asset in enumerate(data['technical_assets']):
                for level_type, valid_levels in self.valid_security_levels.items():
                    if level_type in asset:
                        if asset[level_type] not in valid_levels:
                            errors.append(
                                f"Asset {i}: niveau de {level_type} invalide '{asset[level_type]}'"
                            )
    
    def _validate_relationships(self, data: Dict, errors: List[str], warnings: List[str]) -> None:
        """Valide les relations entre les éléments."""
        if 'components' in data and 'technical_assets' in data:
            # Création des sets d'IDs pour la validation
            component_ids = {comp['id'] for comp in data['components'] if 'id' in comp}
            asset_ids = {asset['id'] for asset in data['technical_assets'] if 'id' in asset}
            
            # Validation des références dans les composants
            for i, component in enumerate(data['components']):
                if 'technical_assets' in component:
                    for asset_id in component['technical_assets']:
                        if asset_id not in asset_ids:
                            errors.append(f"Composant {i}: référence à un asset inexistant: {asset_id}")
                
                if 'data_assets' in component:
                    for data_id in component['data_assets']:
                        if data_id not in asset_ids:
                            errors.append(f"Composant {i}: référence à un asset de données inexistant: {data_id}") 