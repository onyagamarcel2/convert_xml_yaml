"""
Module de mapping pour la conversion vers le format Threagile.
"""

from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass
import logging
import yaml
from pathlib import Path
import re
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class MappingResult:
    """Résultat du mapping."""
    success: bool
    mapped_data: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    details: Dict[str, Any]

class ThreagileMapper:
    """Classe pour le mapping des données vers le format Threagile."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le mapper Threagile.
        
        Args:
            config_path: Chemin vers le fichier de configuration (optionnel)
        """
        # Chargement de la configuration
        self.config = self._load_config(config_path) if config_path else {}
        
        # Mapping des types de composants DrawIO vers Threagile
        self.component_type_mapping = self.config.get('component_types', {
            'web-application': 'web-application',
            'mobile-app': 'mobile-app',
            'desktop-app': 'desktop-app',
            'service': 'service',
            'database': 'database',
            'file-storage': 'file-storage',
            'message-queue': 'message-queue',
            'load-balancer': 'load-balancer',
            'reverse-proxy': 'reverse-proxy',
            'waf': 'waf',
            'ids': 'ids',
            'ips': 'ips',
            'vpn': 'vpn',
            'firewall': 'firewall',
            'gateway': 'gateway',
            'api-gateway': 'api-gateway',
            'service-mesh': 'service-mesh',
            'monitoring': 'monitoring',
            'logging': 'logging',
            'authentication': 'authentication',
            'authorization': 'authorization',
            'key-management': 'key-management',
            'certificate-management': 'certificate-management',
            'secret-management': 'secret-management',
            'identity-management': 'identity-management',
            'access-management': 'access-management',
            'audit-logging': 'audit-logging',
            'backup': 'backup',
            'disaster-recovery': 'disaster-recovery',
            'business-continuity': 'business-continuity',
            'incident-response': 'incident-response',
            'vulnerability-management': 'vulnerability-management',
            'patch-management': 'patch-management',
            'configuration-management': 'configuration-management',
            'change-management': 'change-management',
            'release-management': 'release-management',
            'deployment': 'deployment',
            'container-orchestration': 'container-orchestration',
            'service-discovery': 'service-discovery',
            'api-management': 'api-management',
            'content-delivery': 'content-delivery',
            'dns': 'dns',
            'dhcp': 'dhcp',
            'ntp': 'ntp',
            'syslog': 'syslog',
            'monitoring-agent': 'monitoring-agent',
            'logging-agent': 'logging-agent',
            'security-agent': 'security-agent',
            'endpoint-protection': 'endpoint-protection',
            'mobile-device-management': 'mobile-device-management',
            'unified-endpoint-management': 'unified-endpoint-management',
            'email': 'email',
            'chat': 'chat',
            'collaboration': 'collaboration',
            'document-management': 'document-management',
            'knowledge-management': 'knowledge-management',
            'project-management': 'project-management',
            'issue-tracking': 'issue-tracking',
            'version-control': 'version-control',
            'build-automation': 'build-automation',
            'test-automation': 'test-automation',
            'deployment-automation': 'deployment-automation',
            'infrastructure-as-code': 'infrastructure-as-code',
            'configuration-as-code': 'configuration-as-code',
            'policy-as-code': 'policy-as-code',
            'security-as-code': 'security-as-code',
            'compliance-as-code': 'compliance-as-code',
            'governance-as-code': 'governance-as-code',
            'risk-management': 'risk-management',
            'compliance-management': 'compliance-management',
            'audit-management': 'audit-management',
            'incident-management': 'incident-management',
            'problem-management': 'problem-management',
            'change-management': 'change-management',
            'release-management': 'release-management',
            'deployment-management': 'deployment-management',
            'configuration-management': 'configuration-management',
            'asset-management': 'asset-management',
            'license-management': 'license-management',
            'vendor-management': 'vendor-management',
            'contract-management': 'contract-management',
            'service-level-management': 'service-level-management',
            'availability-management': 'availability-management',
            'capacity-management': 'capacity-management',
            'continuity-management': 'continuity-management'
        })
        
        # Mapping des protocoles
        self.protocol_mapping = self.config.get('protocols', {
            'http': 'http',
            'https': 'https',
            'tcp': 'tcp',
            'udp': 'udp',
            'ssh': 'ssh',
            'ftp': 'ftp',
            'smtp': 'smtp',
            'pop3': 'pop3',
            'imap': 'imap',
            'dns': 'dns',
            'dhcp': 'dhcp',
            'ntp': 'ntp',
            'snmp': 'snmp',
            'ldap': 'ldap',
            'kerberos': 'kerberos',
            'radius': 'radius',
            'tacacs+': 'tacacs+',
            'syslog': 'syslog',
            'syslog-tls': 'syslog-tls',
            'syslog-udp': 'syslog-udp',
            'syslog-tcp': 'syslog-tcp',
            'syslog-tls-tcp': 'syslog-tls-tcp',
            'syslog-tls-udp': 'syslog-tls-udp',
            'syslog-tls-tcp-udp': 'syslog-tls-tcp-udp',
            'syslog-tls-tcp-tls': 'syslog-tls-tcp-tls',
            'syslog-tls-udp-tls': 'syslog-tls-udp-tls',
            'syslog-tls-tcp-udp-tls': 'syslog-tls-tcp-udp-tls',
            'syslog-tls-tcp-tls-udp': 'syslog-tls-tcp-tls-udp',
            'syslog-tls-udp-tls-tcp': 'syslog-tls-udp-tls-tcp',
            'syslog-tls-tcp-udp-tls-tcp': 'syslog-tls-tcp-udp-tls-tcp',
            'syslog-tls-tcp-tls-udp-tcp': 'syslog-tls-tcp-tls-udp-tcp',
            'syslog-tls-udp-tls-tcp-udp': 'syslog-tls-udp-tls-tcp-udp',
            'syslog-tls-tcp-udp-tls-tcp-udp': 'syslog-tls-tcp-udp-tls-tcp-udp'
        })
        
        # Mapping des niveaux de sécurité
        self.security_level_mapping = self.config.get('security_levels', {
            'public': 'public',
            'internal': 'internal',
            'restricted': 'restricted',
            'confidential': 'confidential',
            'strictly-confidential': 'strictly-confidential',
            'operational': 'operational',
            'important': 'important',
            'critical': 'critical',
            'mission-critical': 'mission-critical'
        })
        
        # Mapping des types de relations
        self.relation_type_mapping = self.config.get('relation_types', {
            'data-flow': 'data-flow',
            'trust-boundary': 'trust-boundary',
            'communication': 'communication',
            'dependency': 'dependency',
            'inheritance': 'inheritance',
            'composition': 'composition',
            'aggregation': 'aggregation',
            'association': 'association'
        })
        
        # Validation des références
        self._reference_cache = {
            'components': set(),
            'technical_assets': set(),
            'data_assets': set(),
            'trust_boundaries': set()
        }
    
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
    
    def _validate_references(self, data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """
        Valide les références entre les différents éléments.
        
        Args:
            data: Données à valider
            
        Returns:
            Tuple[List[str], List[str]]: Erreurs et avertissements
        """
        errors = []
        warnings = []
        
        # Validation des références dans les composants
        for component in data.get('components', []):
            for asset_id in component.get('technical_assets', []):
                if asset_id not in self._reference_cache['technical_assets']:
                    errors.append(f"Composant {component['id']}: référence invalide vers l'asset technique {asset_id}")
            
            for asset_id in component.get('data_assets', []):
                if asset_id not in self._reference_cache['data_assets']:
                    errors.append(f"Composant {component['id']}: référence invalide vers l'asset de données {asset_id}")
            
            for boundary_id in component.get('trust_boundaries', []):
                if boundary_id not in self._reference_cache['trust_boundaries']:
                    errors.append(f"Composant {component['id']}: référence invalide vers la limite de confiance {boundary_id}")
        
        # Validation des références dans les limites de confiance
        for boundary in data.get('trust_boundaries', []):
            for component_id in boundary.get('components', []):
                if component_id not in self._reference_cache['components']:
                    errors.append(f"Limite de confiance {boundary['id']}: référence invalide vers le composant {component_id}")
            
            for asset_id in boundary.get('technical_assets', []):
                if asset_id not in self._reference_cache['technical_assets']:
                    errors.append(f"Limite de confiance {boundary['id']}: référence invalide vers l'asset technique {asset_id}")
            
            for asset_id in boundary.get('data_assets', []):
                if asset_id not in self._reference_cache['data_assets']:
                    errors.append(f"Limite de confiance {boundary['id']}: référence invalide vers l'asset de données {asset_id}")
        
        return errors, warnings
    
    def _map_relations(self, relations: List[Dict]) -> Tuple[List[Dict], List[str], List[str]]:
        """
        Convertit les relations DrawIO en format Threagile.
        
        Args:
            relations: Liste des relations à convertir
            
        Returns:
            Tuple[List[Dict], List[str], List[str]]: Relations converties, erreurs et avertissements
        """
        mapped_relations = []
        errors = []
        warnings = []
        
        for i, relation in enumerate(relations):
            try:
                mapped_relation = {
                    'id': relation.get('id', f'relation-{i}'),
                    'name': relation.get('name', f'Relation {i}'),
                    'description': relation.get('description', ''),
                    'type': self.relation_type_mapping.get(
                        relation.get('type', '').lower(),
                        'data-flow'  # Type par défaut
                    ),
                    'source': relation.get('source', ''),
                    'target': relation.get('target', ''),
                    'protocol': self.protocol_mapping.get(
                        relation.get('protocol', '').lower(),
                        'tcp'  # Protocole par défaut
                    ),
                    'authentication': relation.get('authentication', 'none'),
                    'authorization': relation.get('authorization', 'none'),
                    'encryption': relation.get('encryption', 'none'),
                    'data_assets': relation.get('data_assets', []),
                    'tags': relation.get('tags', [])
                }
                
                # Validation des champs requis
                if not mapped_relation['source']:
                    errors.append(f"Relation {i}: source manquante")
                if not mapped_relation['target']:
                    errors.append(f"Relation {i}: cible manquante")
                
                # Validation des références
                if mapped_relation['source'] not in self._reference_cache['components'] and \
                   mapped_relation['source'] not in self._reference_cache['technical_assets']:
                    errors.append(f"Relation {i}: source invalide {mapped_relation['source']}")
                
                if mapped_relation['target'] not in self._reference_cache['components'] and \
                   mapped_relation['target'] not in self._reference_cache['technical_assets']:
                    errors.append(f"Relation {i}: cible invalide {mapped_relation['target']}")
                
                mapped_relations.append(mapped_relation)
                
            except Exception as e:
                errors.append(f"Erreur lors du mapping de la relation {i}: {str(e)}")
        
        return mapped_relations, errors, warnings
    
    def map_to_threagile(self, drawio_data: Dict[str, Any]) -> MappingResult:
        """
        Convertit les données DrawIO en format Threagile.
        
        Args:
            drawio_data: Les données DrawIO à convertir
            
        Returns:
            MappingResult: Le résultat de la conversion
        """
        try:
            errors = []
            warnings = []
            details = {}
            
            # Réinitialisation du cache de références
            self._reference_cache = {
                'components': set(),
                'technical_assets': set(),
                'data_assets': set(),
                'trust_boundaries': set()
            }
            
            # Création de la structure de base Threagile
            threagile_data = {
                'title': drawio_data.get('title', 'Untitled'),
                'description': drawio_data.get('description', ''),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'author': drawio_data.get('author', 'Unknown'),
                'components': [],
                'data_assets': [],
                'trust_boundaries': [],
                'technical_assets': [],
                'relations': []
            }
            
            # Mapping des composants
            if 'components' in drawio_data:
                components, comp_errors, comp_warnings = self._map_components(drawio_data['components'])
                threagile_data['components'] = components
                errors.extend(comp_errors)
                warnings.extend(comp_warnings)
                # Mise à jour du cache de références
                self._reference_cache['components'].update(c['id'] for c in components)
            
            # Mapping des assets techniques
            if 'technical_assets' in drawio_data:
                assets, asset_errors, asset_warnings = self._map_technical_assets(drawio_data['technical_assets'])
                threagile_data['technical_assets'] = assets
                errors.extend(asset_errors)
                warnings.extend(asset_warnings)
                # Mise à jour du cache de références
                self._reference_cache['technical_assets'].update(a['id'] for a in assets)
            
            # Mapping des limites de confiance
            if 'trust_boundaries' in drawio_data:
                boundaries, boundary_errors, boundary_warnings = self._map_trust_boundaries(drawio_data['trust_boundaries'])
                threagile_data['trust_boundaries'] = boundaries
                errors.extend(boundary_errors)
                warnings.extend(boundary_warnings)
                # Mise à jour du cache de références
                self._reference_cache['trust_boundaries'].update(b['id'] for b in boundaries)
            
            # Mapping des assets de données
            if 'data_assets' in drawio_data:
                data_assets, data_errors, data_warnings = self._map_data_assets(drawio_data['data_assets'])
                threagile_data['data_assets'] = data_assets
                errors.extend(data_errors)
                warnings.extend(data_warnings)
                # Mise à jour du cache de références
                self._reference_cache['data_assets'].update(d['id'] for d in data_assets)
            
            # Mapping des relations
            if 'relations' in drawio_data:
                relations, relation_errors, relation_warnings = self._map_relations(drawio_data['relations'])
                threagile_data['relations'] = relations
                errors.extend(relation_errors)
                warnings.extend(relation_warnings)
            
            # Validation des références
            ref_errors, ref_warnings = self._validate_references(threagile_data)
            errors.extend(ref_errors)
            warnings.extend(ref_warnings)
            
            return MappingResult(
                success=len(errors) == 0,
                mapped_data=threagile_data,
                errors=errors,
                warnings=warnings,
                details=details
            )
            
        except Exception as e:
            logger.error(f"Erreur lors du mapping vers Threagile: {str(e)}")
            return MappingResult(
                success=False,
                mapped_data={},
                errors=[f"Erreur lors du mapping: {str(e)}"],
                warnings=[],
                details={}
            )
    
    def _map_components(self, components: List[Dict]) -> Tuple[List[Dict], List[str], List[str]]:
        """Convertit les composants DrawIO en format Threagile."""
        mapped_components = []
        errors = []
        warnings = []
        
        for i, component in enumerate(components):
            try:
                mapped_component = {
                    'id': component.get('id', f'component-{i}'),
                    'name': component.get('name', f'Component {i}'),
                    'type': self.component_type_mapping.get(
                        component.get('type', '').lower(),
                        'service'  # Type par défaut
                    ),
                    'description': component.get('description', ''),
                    'tags': component.get('tags', []),
                    'technical_assets': component.get('technical_assets', []),
                    'data_assets': component.get('data_assets', []),
                    'trust_boundaries': component.get('trust_boundaries', [])
                }
                
                # Validation des champs requis
                if not mapped_component['name']:
                    errors.append(f"Composant {i}: nom manquant")
                if not mapped_component['type']:
                    errors.append(f"Composant {i}: type manquant")
                
                mapped_components.append(mapped_component)
                
            except Exception as e:
                errors.append(f"Erreur lors du mapping du composant {i}: {str(e)}")
        
        return mapped_components, errors, warnings
    
    def _map_technical_assets(self, assets: List[Dict]) -> Tuple[List[Dict], List[str], List[str]]:
        """Convertit les assets techniques DrawIO en format Threagile."""
        mapped_assets = []
        errors = []
        warnings = []
        
        for i, asset in enumerate(assets):
            try:
                mapped_asset = {
                    'id': asset.get('id', f'asset-{i}'),
                    'name': asset.get('name', f'Asset {i}'),
                    'type': self.component_type_mapping.get(
                        asset.get('type', '').lower(),
                        'service'  # Type par défaut
                    ),
                    'description': asset.get('description', ''),
                    'usage': asset.get('usage', 'business'),
                    'owner': asset.get('owner', 'Unknown'),
                    'confidentiality': self.security_level_mapping.get(
                        asset.get('confidentiality', '').lower(),
                        'internal'  # Niveau par défaut
                    ),
                    'integrity': self.security_level_mapping.get(
                        asset.get('integrity', '').lower(),
                        'operational'  # Niveau par défaut
                    ),
                    'availability': self.security_level_mapping.get(
                        asset.get('availability', '').lower(),
                        'operational'  # Niveau par défaut
                    ),
                    'justification_cia_rating': asset.get('justification_cia_rating', ''),
                    'multi_tenant': asset.get('multi_tenant', False),
                    'redundant': asset.get('redundant', False),
                    'custom_developed_parts': asset.get('custom_developed_parts', False),
                    'encryption': asset.get('encryption', 'none'),
                    'authentication': asset.get('authentication', 'none'),
                    'authorization': asset.get('authorization', 'none'),
                    'justification_authentication': asset.get('justification_authentication', ''),
                    'justification_authorization': asset.get('justification_authorization', '')
                }
                
                # Validation des champs requis
                if not mapped_asset['name']:
                    errors.append(f"Asset {i}: nom manquant")
                if not mapped_asset['type']:
                    errors.append(f"Asset {i}: type manquant")
                
                mapped_assets.append(mapped_asset)
                
            except Exception as e:
                errors.append(f"Erreur lors du mapping de l'asset {i}: {str(e)}")
        
        return mapped_assets, errors, warnings
    
    def _map_trust_boundaries(self, boundaries: List[Dict]) -> Tuple[List[Dict], List[str], List[str]]:
        """Convertit les limites de confiance DrawIO en format Threagile."""
        mapped_boundaries = []
        errors = []
        warnings = []
        
        for i, boundary in enumerate(boundaries):
            try:
                mapped_boundary = {
                    'id': boundary.get('id', f'boundary-{i}'),
                    'name': boundary.get('name', f'Trust Boundary {i}'),
                    'description': boundary.get('description', ''),
                    'type': boundary.get('type', 'network'),
                    'components': boundary.get('components', []),
                    'technical_assets': boundary.get('technical_assets', []),
                    'data_assets': boundary.get('data_assets', [])
                }
                
                # Validation des champs requis
                if not mapped_boundary['name']:
                    errors.append(f"Limite de confiance {i}: nom manquant")
                if not mapped_boundary['type']:
                    errors.append(f"Limite de confiance {i}: type manquant")
                
                mapped_boundaries.append(mapped_boundary)
                
            except Exception as e:
                errors.append(f"Erreur lors du mapping de la limite de confiance {i}: {str(e)}")
        
        return mapped_boundaries, errors, warnings
    
    def _map_data_assets(self, data_assets: List[Dict]) -> Tuple[List[Dict], List[str], List[str]]:
        """Convertit les assets de données DrawIO en format Threagile."""
        mapped_data_assets = []
        errors = []
        warnings = []
        
        for i, data_asset in enumerate(data_assets):
            try:
                mapped_data_asset = {
                    'id': data_asset.get('id', f'data-{i}'),
                    'name': data_asset.get('name', f'Data Asset {i}'),
                    'description': data_asset.get('description', ''),
                    'usage': data_asset.get('usage', 'business'),
                    'owner': data_asset.get('owner', 'Unknown'),
                    'confidentiality': self.security_level_mapping.get(
                        data_asset.get('confidentiality', '').lower(),
                        'internal'  # Niveau par défaut
                    ),
                    'integrity': self.security_level_mapping.get(
                        data_asset.get('integrity', '').lower(),
                        'operational'  # Niveau par défaut
                    ),
                    'availability': self.security_level_mapping.get(
                        data_asset.get('availability', '').lower(),
                        'operational'  # Niveau par défaut
                    ),
                    'justification_cia_rating': data_asset.get('justification_cia_rating', ''),
                    'storage': data_asset.get('storage', ''),
                    'format': data_asset.get('format', ''),
                    'origin': data_asset.get('origin', ''),
                    'quantity': data_asset.get('quantity', ''),
                    'tags': data_asset.get('tags', [])
                }
                
                # Validation des champs requis
                if not mapped_data_asset['name']:
                    errors.append(f"Asset de données {i}: nom manquant")
                
                mapped_data_assets.append(mapped_data_asset)
                
            except Exception as e:
                errors.append(f"Erreur lors du mapping de l'asset de données {i}: {str(e)}")
        
        return mapped_data_assets, errors, warnings 