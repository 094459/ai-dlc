"""
System Configuration Service for managing application settings and feature flags.
"""

import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from app.models import db, SystemConfiguration, User
from app.models.admin import AdminActivity


class SystemConfigurationService:
    """Service for managing system-wide configuration settings."""
    
    # Default configuration values
    DEFAULT_CONFIGS = {
        'site_name': {
            'value': 'Fact Checker',
            'data_type': 'string',
            'description': 'Name of the application displayed to users',
            'is_public': True
        },
        'max_facts_per_user_per_day': {
            'value': '10',
            'data_type': 'integer',
            'description': 'Maximum number of facts a user can create per day',
            'is_public': False
        },
        'max_comments_per_user_per_day': {
            'value': '50',
            'data_type': 'integer',
            'description': 'Maximum number of comments a user can create per day',
            'is_public': False
        },
        'enable_user_registration': {
            'value': 'true',
            'data_type': 'boolean',
            'description': 'Allow new users to register accounts',
            'is_public': True
        },
        'enable_fact_voting': {
            'value': 'true',
            'data_type': 'boolean',
            'description': 'Enable voting on facts',
            'is_public': True
        },
        'enable_comment_voting': {
            'value': 'true',
            'data_type': 'boolean',
            'description': 'Enable voting on comments',
            'is_public': True
        },
        'maintenance_mode': {
            'value': 'false',
            'data_type': 'boolean',
            'description': 'Enable maintenance mode (restricts access)',
            'is_public': True
        },
        'max_file_upload_size_mb': {
            'value': '5',
            'data_type': 'integer',
            'description': 'Maximum file upload size in megabytes',
            'is_public': False
        },
        'session_timeout_minutes': {
            'value': '1440',
            'data_type': 'integer',
            'description': 'User session timeout in minutes (24 hours default)',
            'is_public': False
        },
        'email_notifications_enabled': {
            'value': 'true',
            'data_type': 'boolean',
            'description': 'Enable email notifications system-wide',
            'is_public': False
        },
        'analytics_enabled': {
            'value': 'true',
            'data_type': 'boolean',
            'description': 'Enable analytics tracking',
            'is_public': False
        },
        'moderation_auto_hide_threshold': {
            'value': '5',
            'data_type': 'integer',
            'description': 'Number of reports that trigger automatic content hiding',
            'is_public': False
        },
        'fact_edit_time_limit_hours': {
            'value': '24',
            'data_type': 'integer',
            'description': 'Time limit for editing facts after creation (hours)',
            'is_public': False
        },
        'comment_edit_time_limit_hours': {
            'value': '2',
            'data_type': 'integer',
            'description': 'Time limit for editing comments after creation (hours)',
            'is_public': False
        }
    }
    
    def get_configuration(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: Configuration key
            default: Default value if configuration not found
            
        Returns:
            Configuration value converted to proper type
        """
        try:
            config = SystemConfiguration.query.filter_by(key=key).first()
            if config:
                return config.get_typed_value()
            return default
            
        except Exception:
            return default
    
    def set_configuration(self, key: str, value: Any, admin_user_id: str, 
                         description: str = None) -> bool:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
            admin_user_id: ID of admin user making the change
            description: Optional description of the change
            
        Returns:
            True if successful, False otherwise
        """
        try:
            config = SystemConfiguration.query.filter_by(key=key).first()
            old_value = None
            
            if config:
                old_value = config.value
                config.value = str(value)
                config.updated_at = datetime.utcnow()
            else:
                # Create new configuration
                data_type = self._infer_data_type(value)
                config = SystemConfiguration(
                    key=key,
                    value=str(value),
                    data_type=data_type,
                    description=description or f'Configuration for {key}',
                    is_public=False  # Default to private for new configs
                )
                db.session.add(config)
            
            db.session.commit()
            
            # Log the configuration change
            self._log_configuration_change(
                admin_user_id, key, old_value, str(value), description
            )
            
            return True
            
        except Exception as e:
            db.session.rollback()
            # Log error
            self._log_admin_activity(
                admin_user_id,
                'configuration_error',
                'set_config_error',
                f'Error setting configuration {key}: {str(e)}',
                severity='medium'
            )
            return False
    
    def get_all_configurations(self, include_private: bool = False) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Args:
            include_private: Whether to include private configurations
            
        Returns:
            Dictionary of all configurations
        """
        try:
            query = SystemConfiguration.query
            if not include_private:
                query = query.filter_by(is_public=True)
            
            configs = query.all()
            
            return {
                config.key: {
                    'value': config.get_typed_value(),
                    'data_type': config.data_type,
                    'description': config.description,
                    'is_public': config.is_public,
                    'updated_at': config.updated_at.isoformat() if config.updated_at else None
                }
                for config in configs
            }
            
        except Exception:
            return {}
    
    def get_configurations_by_category(self, category: str = None) -> List[Dict[str, Any]]:
        """
        Get configurations grouped by category or all if no category specified.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of configuration dictionaries
        """
        try:
            query = SystemConfiguration.query
            if category:
                # For now, we'll use key prefixes as categories
                query = query.filter(SystemConfiguration.key.like(f'{category}_%'))
            
            configs = query.order_by(SystemConfiguration.key).all()
            
            return [
                {
                    'key': config.key,
                    'value': config.get_typed_value(),
                    'data_type': config.data_type,
                    'description': config.description,
                    'is_public': config.is_public,
                    'created_at': config.created_at.isoformat(),
                    'updated_at': config.updated_at.isoformat() if config.updated_at else None
                }
                for config in configs
            ]
            
        except Exception:
            return []
    
    def initialize_default_configurations(self, admin_user_id: str) -> bool:
        """
        Initialize default system configurations if they don't exist.
        
        Args:
            admin_user_id: ID of admin user performing initialization
            
        Returns:
            True if successful, False otherwise
        """
        try:
            initialized_count = 0
            
            for key, config_data in self.DEFAULT_CONFIGS.items():
                existing = SystemConfiguration.query.filter_by(key=key).first()
                if not existing:
                    config = SystemConfiguration(
                        key=key,
                        value=config_data['value'],
                        data_type=config_data['data_type'],
                        description=config_data['description'],
                        is_public=config_data.get('is_public', False)
                    )
                    db.session.add(config)
                    initialized_count += 1
            
            if initialized_count > 0:
                db.session.commit()
                
                # Log initialization
                self._log_admin_activity(
                    admin_user_id,
                    'system_initialization',
                    'init_default_configs',
                    f'Initialized {initialized_count} default configurations',
                    severity='low'
                )
            
            return True
            
        except Exception as e:
            db.session.rollback()
            self._log_admin_activity(
                admin_user_id,
                'system_error',
                'init_config_error',
                f'Error initializing default configurations: {str(e)}',
                severity='high'
            )
            return False
    
    def validate_configuration(self, key: str, value: Any) -> Dict[str, Any]:
        """
        Validate a configuration value before setting it.
        
        Args:
            key: Configuration key
            value: Value to validate
            
        Returns:
            Dictionary with validation result and any errors
        """
        try:
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Check if configuration exists or is in defaults
            config = SystemConfiguration.query.filter_by(key=key).first()
            if not config and key not in self.DEFAULT_CONFIGS:
                validation_result['warnings'].append(
                    f'Configuration {key} is not a standard configuration'
                )
            
            # Type validation
            if config:
                expected_type = config.data_type
            elif key in self.DEFAULT_CONFIGS:
                expected_type = self.DEFAULT_CONFIGS[key]['data_type']
            else:
                expected_type = self._infer_data_type(value)
            
            # Validate based on expected type
            if expected_type == 'integer':
                try:
                    int_value = int(value)
                    if int_value < 0 and key.endswith(('_limit', '_max', '_threshold')):
                        validation_result['errors'].append(
                            f'Value must be non-negative for {key}'
                        )
                except (ValueError, TypeError):
                    validation_result['errors'].append(
                        f'Value must be an integer for {key}'
                    )
                    validation_result['valid'] = False
            
            elif expected_type == 'boolean':
                if str(value).lower() not in ('true', 'false', '1', '0', 'yes', 'no', 'on', 'off'):
                    validation_result['errors'].append(
                        f'Value must be a boolean (true/false) for {key}'
                    )
                    validation_result['valid'] = False
            
            elif expected_type == 'json':
                try:
                    if isinstance(value, str):
                        json.loads(value)
                except json.JSONDecodeError:
                    validation_result['errors'].append(
                        f'Value must be valid JSON for {key}'
                    )
                    validation_result['valid'] = False
            
            # Specific validations for known configurations
            if key == 'max_file_upload_size_mb' and validation_result['valid']:
                size_mb = int(value)
                if size_mb > 100:  # 100MB limit
                    validation_result['warnings'].append(
                        'File upload size over 100MB may cause performance issues'
                    )
                elif size_mb < 1:
                    validation_result['errors'].append(
                        'File upload size must be at least 1MB'
                    )
                    validation_result['valid'] = False
            
            elif key == 'session_timeout_minutes' and validation_result['valid']:
                timeout = int(value)
                if timeout < 5:
                    validation_result['errors'].append(
                        'Session timeout must be at least 5 minutes'
                    )
                    validation_result['valid'] = False
                elif timeout > 10080:  # 1 week
                    validation_result['warnings'].append(
                        'Session timeout over 1 week may pose security risks'
                    )
            
            return validation_result
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f'Validation error: {str(e)}'],
                'warnings': []
            }
    
    def backup_configurations(self, admin_user_id: str) -> Optional[str]:
        """
        Create a backup of all configurations.
        
        Args:
            admin_user_id: ID of admin user creating backup
            
        Returns:
            JSON string of all configurations or None if error
        """
        try:
            configs = SystemConfiguration.query.all()
            backup_data = {
                'backup_timestamp': datetime.utcnow().isoformat(),
                'backup_by': admin_user_id,
                'configurations': [
                    {
                        'key': config.key,
                        'value': config.value,
                        'data_type': config.data_type,
                        'description': config.description,
                        'is_public': config.is_public,
                        'created_at': config.created_at.isoformat(),
                        'updated_at': config.updated_at.isoformat() if config.updated_at else None
                    }
                    for config in configs
                ]
            }
            
            backup_json = json.dumps(backup_data, indent=2)
            
            # Log backup creation
            self._log_admin_activity(
                admin_user_id,
                'system_backup',
                'create_config_backup',
                f'Created configuration backup with {len(configs)} configurations',
                severity='low'
            )
            
            return backup_json
            
        except Exception as e:
            self._log_admin_activity(
                admin_user_id,
                'system_error',
                'backup_error',
                f'Error creating configuration backup: {str(e)}',
                severity='medium'
            )
            return None
    
    def restore_configurations(self, backup_data: str, admin_user_id: str) -> bool:
        """
        Restore configurations from backup data.
        
        Args:
            backup_data: JSON string containing backup data
            admin_user_id: ID of admin user performing restore
            
        Returns:
            True if successful, False otherwise
        """
        try:
            backup = json.loads(backup_data)
            configurations = backup.get('configurations', [])
            
            restored_count = 0
            updated_count = 0
            
            for config_data in configurations:
                existing = SystemConfiguration.query.filter_by(
                    key=config_data['key']
                ).first()
                
                if existing:
                    # Update existing configuration
                    existing.value = config_data['value']
                    existing.data_type = config_data['data_type']
                    existing.description = config_data['description']
                    existing.is_public = config_data['is_public']
                    existing.updated_at = datetime.utcnow()
                    updated_count += 1
                else:
                    # Create new configuration
                    config = SystemConfiguration(
                        key=config_data['key'],
                        value=config_data['value'],
                        data_type=config_data['data_type'],
                        description=config_data['description'],
                        is_public=config_data['is_public']
                    )
                    db.session.add(config)
                    restored_count += 1
            
            db.session.commit()
            
            # Log restore operation
            self._log_admin_activity(
                admin_user_id,
                'system_restore',
                'restore_config_backup',
                f'Restored {restored_count} new and updated {updated_count} existing configurations',
                severity='medium'
            )
            
            return True
            
        except Exception as e:
            db.session.rollback()
            self._log_admin_activity(
                admin_user_id,
                'system_error',
                'restore_error',
                f'Error restoring configuration backup: {str(e)}',
                severity='high'
            )
            return False
    
    def _infer_data_type(self, value: Any) -> str:
        """Infer data type from value."""
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, (dict, list)):
            return 'json'
        else:
            return 'string'
    
    def _log_configuration_change(self, admin_id: str, key: str, old_value: str, 
                                 new_value: str, description: str = None):
        """Log configuration changes for audit purposes."""
        try:
            details = {
                'configuration_key': key,
                'old_value': old_value,
                'new_value': new_value,
                'change_description': description
            }
            
            self._log_admin_activity(
                admin_id,
                'configuration_change',
                'update_config',
                f'Updated configuration {key} from "{old_value}" to "{new_value}"',
                target_type='configuration',
                target_id=key,
                severity='low',
                details=details
            )
            
        except Exception:
            # Don't let logging errors break the main functionality
            pass
    
    def _log_admin_activity(self, admin_id: str, activity_type: str, action: str, 
                           description: str, target_type: str = None, target_id: str = None,
                           severity: str = 'low', details: Dict = None):
        """Log admin activity for audit purposes."""
        try:
            activity = AdminActivity(
                admin_id=admin_id,
                activity_type=activity_type,
                action=action,
                description=description,
                target_type=target_type,
                target_id=target_id,
                severity=severity,
                details=details
            )
            
            db.session.add(activity)
            db.session.commit()
            
        except Exception:
            # Don't let logging errors break the main functionality
            db.session.rollback()
