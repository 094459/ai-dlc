"""
Configuration Validation Helper utilities for system settings validation and migration.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from app.models import db, SystemConfiguration
from app.components.analytics.tracking import track_admin_action


class ConfigValidationHelper:
    """Helper class for configuration validation and migration."""
    
    # Configuration validation rules
    VALIDATION_RULES = {
        'site_name': {
            'type': 'string',
            'min_length': 1,
            'max_length': 100,
            'required': True,
            'description': 'Site name must be between 1 and 100 characters'
        },
        'max_facts_per_user_per_day': {
            'type': 'integer',
            'min_value': 1,
            'max_value': 1000,
            'required': True,
            'description': 'Must be between 1 and 1000'
        },
        'max_comments_per_user_per_day': {
            'type': 'integer',
            'min_value': 1,
            'max_value': 10000,
            'required': True,
            'description': 'Must be between 1 and 10000'
        },
        'enable_user_registration': {
            'type': 'boolean',
            'required': True,
            'description': 'Must be true or false'
        },
        'enable_fact_voting': {
            'type': 'boolean',
            'required': True,
            'description': 'Must be true or false'
        },
        'enable_comment_voting': {
            'type': 'boolean',
            'required': True,
            'description': 'Must be true or false'
        },
        'maintenance_mode': {
            'type': 'boolean',
            'required': True,
            'description': 'Must be true or false'
        },
        'max_file_upload_size_mb': {
            'type': 'integer',
            'min_value': 1,
            'max_value': 100,
            'required': True,
            'description': 'Must be between 1 and 100 MB'
        },
        'session_timeout_minutes': {
            'type': 'integer',
            'min_value': 5,
            'max_value': 10080,  # 1 week
            'required': True,
            'description': 'Must be between 5 minutes and 1 week (10080 minutes)'
        },
        'email_notifications_enabled': {
            'type': 'boolean',
            'required': True,
            'description': 'Must be true or false'
        },
        'analytics_enabled': {
            'type': 'boolean',
            'required': True,
            'description': 'Must be true or false'
        },
        'moderation_auto_hide_threshold': {
            'type': 'integer',
            'min_value': 1,
            'max_value': 100,
            'required': True,
            'description': 'Must be between 1 and 100 reports'
        },
        'fact_edit_time_limit_hours': {
            'type': 'integer',
            'min_value': 0,
            'max_value': 168,  # 1 week
            'required': True,
            'description': 'Must be between 0 and 168 hours (1 week)'
        },
        'comment_edit_time_limit_hours': {
            'type': 'integer',
            'min_value': 0,
            'max_value': 72,  # 3 days
            'required': True,
            'description': 'Must be between 0 and 72 hours (3 days)'
        }
    }
    
    @staticmethod
    def validate_configuration(key: str, value: Any, admin_user_id: str = None) -> Dict[str, Any]:
        """
        Validate a configuration value against defined rules.
        
        Args:
            key: Configuration key
            value: Value to validate
            admin_user_id: ID of admin performing validation (optional)
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Track validation if admin_user_id provided
            if admin_user_id:
                track_admin_action(admin_user_id, 'configuration', 'validate_config', {
                    'config_key': key,
                    'value_type': type(value).__name__
                })
            
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'normalized_value': value
            }
            
            # Check if configuration key is known
            if key not in ConfigValidationHelper.VALIDATION_RULES:
                validation_result['warnings'].append(
                    f'Configuration key "{key}" is not in the standard configuration set'
                )
                return validation_result
            
            rules = ConfigValidationHelper.VALIDATION_RULES[key]
            
            # Check if required
            if rules.get('required', False) and (value is None or value == ''):
                validation_result['valid'] = False
                validation_result['errors'].append(f'Configuration "{key}" is required')
                return validation_result
            
            # Type validation and conversion
            expected_type = rules['type']
            
            if expected_type == 'string':
                validation_result.update(
                    ConfigValidationHelper._validate_string(key, value, rules)
                )
            elif expected_type == 'integer':
                validation_result.update(
                    ConfigValidationHelper._validate_integer(key, value, rules)
                )
            elif expected_type == 'boolean':
                validation_result.update(
                    ConfigValidationHelper._validate_boolean(key, value, rules)
                )
            elif expected_type == 'json':
                validation_result.update(
                    ConfigValidationHelper._validate_json(key, value, rules)
                )
            elif expected_type == 'float':
                validation_result.update(
                    ConfigValidationHelper._validate_float(key, value, rules)
                )
            
            # Additional business logic validation
            validation_result.update(
                ConfigValidationHelper._validate_business_rules(key, validation_result['normalized_value'])
            )
            
            return validation_result
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f'Validation error: {str(e)}'],
                'warnings': [],
                'normalized_value': value
            }
    
    @staticmethod
    def _validate_string(key: str, value: Any, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate string configuration value."""
        result = {'valid': True, 'errors': [], 'warnings': [], 'normalized_value': str(value)}
        
        str_value = str(value).strip()
        result['normalized_value'] = str_value
        
        # Length validation
        if 'min_length' in rules and len(str_value) < rules['min_length']:
            result['valid'] = False
            result['errors'].append(
                f'"{key}" must be at least {rules["min_length"]} characters long'
            )
        
        if 'max_length' in rules and len(str_value) > rules['max_length']:
            result['valid'] = False
            result['errors'].append(
                f'"{key}" must be no more than {rules["max_length"]} characters long'
            )
        
        # Pattern validation
        if 'pattern' in rules:
            if not re.match(rules['pattern'], str_value):
                result['valid'] = False
                result['errors'].append(
                    f'"{key}" does not match required pattern: {rules.get("pattern_description", rules["pattern"])}'
                )
        
        return result
    
    @staticmethod
    def _validate_integer(key: str, value: Any, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate integer configuration value."""
        result = {'valid': True, 'errors': [], 'warnings': [], 'normalized_value': value}
        
        try:
            int_value = int(value)
            result['normalized_value'] = int_value
        except (ValueError, TypeError):
            result['valid'] = False
            result['errors'].append(f'"{key}" must be a valid integer')
            return result
        
        # Range validation
        if 'min_value' in rules and int_value < rules['min_value']:
            result['valid'] = False
            result['errors'].append(
                f'"{key}" must be at least {rules["min_value"]}'
            )
        
        if 'max_value' in rules and int_value > rules['max_value']:
            result['valid'] = False
            result['errors'].append(
                f'"{key}" must be no more than {rules["max_value"]}'
            )
        
        return result
    
    @staticmethod
    def _validate_boolean(key: str, value: Any, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate boolean configuration value."""
        result = {'valid': True, 'errors': [], 'warnings': [], 'normalized_value': value}
        
        if isinstance(value, bool):
            result['normalized_value'] = value
        elif isinstance(value, str):
            str_value = value.lower().strip()
            if str_value in ('true', '1', 'yes', 'on', 'enabled'):
                result['normalized_value'] = True
            elif str_value in ('false', '0', 'no', 'off', 'disabled'):
                result['normalized_value'] = False
            else:
                result['valid'] = False
                result['errors'].append(
                    f'"{key}" must be a valid boolean value (true/false, yes/no, 1/0, on/off, enabled/disabled)'
                )
        else:
            result['valid'] = False
            result['errors'].append(f'"{key}" must be a boolean value')
        
        return result
    
    @staticmethod
    def _validate_json(key: str, value: Any, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate JSON configuration value."""
        result = {'valid': True, 'errors': [], 'warnings': [], 'normalized_value': value}
        
        if isinstance(value, (dict, list)):
            result['normalized_value'] = value
        elif isinstance(value, str):
            try:
                parsed_json = json.loads(value)
                result['normalized_value'] = parsed_json
            except json.JSONDecodeError as e:
                result['valid'] = False
                result['errors'].append(f'"{key}" must be valid JSON: {str(e)}')
        else:
            result['valid'] = False
            result['errors'].append(f'"{key}" must be valid JSON')
        
        return result
    
    @staticmethod
    def _validate_float(key: str, value: Any, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate float configuration value."""
        result = {'valid': True, 'errors': [], 'warnings': [], 'normalized_value': value}
        
        try:
            float_value = float(value)
            result['normalized_value'] = float_value
        except (ValueError, TypeError):
            result['valid'] = False
            result['errors'].append(f'"{key}" must be a valid number')
            return result
        
        # Range validation
        if 'min_value' in rules and float_value < rules['min_value']:
            result['valid'] = False
            result['errors'].append(
                f'"{key}" must be at least {rules["min_value"]}'
            )
        
        if 'max_value' in rules and float_value > rules['max_value']:
            result['valid'] = False
            result['errors'].append(
                f'"{key}" must be no more than {rules["max_value"]}'
            )
        
        return result
    
    @staticmethod
    def _validate_business_rules(key: str, value: Any) -> Dict[str, Any]:
        """Validate business-specific rules for configuration values."""
        result = {'valid': True, 'errors': [], 'warnings': []}
        
        # Specific business rule validations
        if key == 'max_file_upload_size_mb':
            if isinstance(value, (int, float)) and value > 50:
                result['warnings'].append(
                    'File upload sizes over 50MB may cause performance issues'
                )
        
        elif key == 'session_timeout_minutes':
            if isinstance(value, int):
                if value < 30:
                    result['warnings'].append(
                        'Session timeout less than 30 minutes may impact user experience'
                    )
                elif value > 1440:  # 24 hours
                    result['warnings'].append(
                        'Session timeout over 24 hours may pose security risks'
                    )
        
        elif key == 'moderation_auto_hide_threshold':
            if isinstance(value, int) and value < 3:
                result['warnings'].append(
                    'Auto-hide threshold below 3 reports may result in false positives'
                )
        
        elif key == 'maintenance_mode':
            if value is True:
                result['warnings'].append(
                    'Enabling maintenance mode will restrict user access to the application'
                )
        
        return result
    
    @staticmethod
    def validate_all_configurations(admin_user_id: str) -> Dict[str, Any]:
        """
        Validate all current system configurations.
        
        Args:
            admin_user_id: ID of admin performing validation
            
        Returns:
            Dictionary with validation results for all configurations
        """
        try:
            # Track validation operation
            track_admin_action(admin_user_id, 'configuration', 'validate_all_configs')
            
            all_configs = SystemConfiguration.query.all()
            validation_results = {
                'total_configs': len(all_configs),
                'valid_configs': 0,
                'invalid_configs': 0,
                'configs_with_warnings': 0,
                'results': {},
                'summary': {
                    'errors': [],
                    'warnings': []
                }
            }
            
            for config in all_configs:
                # Get typed value for validation
                typed_value = config.get_typed_value()
                
                # Validate configuration
                validation = ConfigValidationHelper.validate_configuration(
                    config.key, typed_value, admin_user_id
                )
                
                validation_results['results'][config.key] = {
                    'current_value': typed_value,
                    'validation': validation,
                    'last_updated': config.updated_at.isoformat() if config.updated_at else None
                }
                
                # Update counters
                if validation['valid']:
                    validation_results['valid_configs'] += 1
                else:
                    validation_results['invalid_configs'] += 1
                    validation_results['summary']['errors'].extend([
                        f"{config.key}: {error}" for error in validation['errors']
                    ])
                
                if validation['warnings']:
                    validation_results['configs_with_warnings'] += 1
                    validation_results['summary']['warnings'].extend([
                        f"{config.key}: {warning}" for warning in validation['warnings']
                    ])
            
            # Check for missing required configurations
            missing_configs = []
            for key, rules in ConfigValidationHelper.VALIDATION_RULES.items():
                if rules.get('required', False):
                    if not any(config.key == key for config in all_configs):
                        missing_configs.append(key)
            
            if missing_configs:
                validation_results['summary']['errors'].extend([
                    f"Missing required configuration: {key}" for key in missing_configs
                ])
            
            validation_results['missing_required_configs'] = missing_configs
            validation_results['validated_at'] = datetime.utcnow().isoformat()
            
            return validation_results
            
        except Exception as e:
            return {
                'error': str(e),
                'validated_at': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def migrate_configuration_format(admin_user_id: str, from_version: str = '1.0', 
                                   to_version: str = '2.0') -> Dict[str, Any]:
        """
        Migrate configuration format between versions.
        
        Args:
            admin_user_id: ID of admin performing migration
            from_version: Source version
            to_version: Target version
            
        Returns:
            Dictionary with migration results
        """
        try:
            # Track migration operation
            track_admin_action(admin_user_id, 'configuration', 'migrate_config_format', {
                'from_version': from_version,
                'to_version': to_version
            })
            
            migration_results = {
                'migrated_configs': 0,
                'failed_migrations': 0,
                'errors': [],
                'changes_made': []
            }
            
            # Example migration logic (would be version-specific)
            if from_version == '1.0' and to_version == '2.0':
                # Example: Rename old configuration keys
                old_to_new_mapping = {
                    'max_daily_facts': 'max_facts_per_user_per_day',
                    'max_daily_comments': 'max_comments_per_user_per_day',
                    'allow_registration': 'enable_user_registration'
                }
                
                for old_key, new_key in old_to_new_mapping.items():
                    old_config = SystemConfiguration.query.filter_by(key=old_key).first()
                    if old_config:
                        # Check if new key already exists
                        existing_new = SystemConfiguration.query.filter_by(key=new_key).first()
                        if not existing_new:
                            # Migrate the configuration
                            old_config.key = new_key
                            migration_results['migrated_configs'] += 1
                            migration_results['changes_made'].append(
                                f'Renamed "{old_key}" to "{new_key}"'
                            )
                        else:
                            # Remove old configuration if new one exists
                            db.session.delete(old_config)
                            migration_results['changes_made'].append(
                                f'Removed duplicate "{old_key}" (kept "{new_key}")'
                            )
                
                db.session.commit()
            
            migration_results['migrated_at'] = datetime.utcnow().isoformat()
            return migration_results
            
        except Exception as e:
            db.session.rollback()
            return {
                'error': str(e),
                'migrated_at': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def get_configuration_schema() -> Dict[str, Any]:
        """
        Get the complete configuration schema with validation rules.
        
        Returns:
            Dictionary containing the configuration schema
        """
        return {
            'version': '2.0',
            'configurations': ConfigValidationHelper.VALIDATION_RULES,
            'categories': {
                'general': ['site_name'],
                'limits': [
                    'max_facts_per_user_per_day',
                    'max_comments_per_user_per_day',
                    'max_file_upload_size_mb'
                ],
                'features': [
                    'enable_user_registration',
                    'enable_fact_voting',
                    'enable_comment_voting',
                    'email_notifications_enabled',
                    'analytics_enabled'
                ],
                'security': [
                    'session_timeout_minutes'
                ],
                'moderation': [
                    'moderation_auto_hide_threshold',
                    'fact_edit_time_limit_hours',
                    'comment_edit_time_limit_hours'
                ],
                'system': [
                    'maintenance_mode'
                ]
            },
            'generated_at': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def suggest_configuration_improvements(admin_user_id: str) -> Dict[str, Any]:
        """
        Suggest improvements for current configuration.
        
        Args:
            admin_user_id: ID of admin requesting suggestions
            
        Returns:
            Dictionary with configuration improvement suggestions
        """
        try:
            # Track suggestion request
            track_admin_action(admin_user_id, 'configuration', 'get_improvement_suggestions')
            
            suggestions = {
                'performance_improvements': [],
                'security_improvements': [],
                'user_experience_improvements': [],
                'maintenance_suggestions': []
            }
            
            # Get current configurations
            configs = {
                config.key: config.get_typed_value() 
                for config in SystemConfiguration.query.all()
            }
            
            # Performance suggestions
            if configs.get('max_file_upload_size_mb', 5) > 10:
                suggestions['performance_improvements'].append(
                    'Consider reducing max_file_upload_size_mb to improve server performance'
                )
            
            if configs.get('session_timeout_minutes', 1440) > 2880:  # 48 hours
                suggestions['performance_improvements'].append(
                    'Consider reducing session_timeout_minutes to free up server resources'
                )
            
            # Security suggestions
            if configs.get('session_timeout_minutes', 1440) > 1440:  # 24 hours
                suggestions['security_improvements'].append(
                    'Consider reducing session timeout for better security'
                )
            
            if not configs.get('analytics_enabled', True):
                suggestions['security_improvements'].append(
                    'Enable analytics to monitor for suspicious activities'
                )
            
            # User experience suggestions
            if configs.get('max_facts_per_user_per_day', 10) < 5:
                suggestions['user_experience_improvements'].append(
                    'Consider increasing daily fact limit to improve user engagement'
                )
            
            if configs.get('fact_edit_time_limit_hours', 24) < 2:
                suggestions['user_experience_improvements'].append(
                    'Consider allowing longer edit time for facts to improve user satisfaction'
                )
            
            # Maintenance suggestions
            if configs.get('moderation_auto_hide_threshold', 5) > 10:
                suggestions['maintenance_suggestions'].append(
                    'Consider lowering auto-hide threshold to reduce moderator workload'
                )
            
            return {
                'suggestions': suggestions,
                'total_suggestions': sum(len(s) for s in suggestions.values()),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat()
            }
