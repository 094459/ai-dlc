"""
UI Framework services for theme management, component rendering, and responsive design.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from flask import current_app, session, request
from datetime import datetime

logger = logging.getLogger(__name__)


class ThemeService:
    """Service for managing application themes and styling."""
    
    # Default theme configuration
    DEFAULT_THEMES = {
        'light': {
            'name': 'Light Theme',
            'colors': {
                'primary': '#007bff',
                'secondary': '#6c757d',
                'success': '#28a745',
                'danger': '#dc3545',
                'warning': '#ffc107',
                'info': '#17a2b8',
                'light': '#f8f9fa',
                'dark': '#343a40',
                'white': '#ffffff',
                'black': '#000000'
            },
            'typography': {
                'font_family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                'font_size_base': '16px',
                'line_height': '1.5',
                'headings': {
                    'h1': '2.5rem',
                    'h2': '2rem',
                    'h3': '1.75rem',
                    'h4': '1.5rem',
                    'h5': '1.25rem',
                    'h6': '1rem'
                }
            },
            'spacing': {
                'xs': '0.25rem',
                'sm': '0.5rem',
                'md': '1rem',
                'lg': '1.5rem',
                'xl': '3rem'
            },
            'borders': {
                'radius': '0.375rem',
                'width': '1px',
                'style': 'solid'
            },
            'shadows': {
                'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
                'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
            }
        },
        'dark': {
            'name': 'Dark Theme',
            'colors': {
                'primary': '#0d6efd',
                'secondary': '#6c757d',
                'success': '#198754',
                'danger': '#dc3545',
                'warning': '#fd7e14',
                'info': '#0dcaf0',
                'light': '#212529',
                'dark': '#f8f9fa',
                'white': '#000000',
                'black': '#ffffff'
            },
            'typography': {
                'font_family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                'font_size_base': '16px',
                'line_height': '1.5',
                'headings': {
                    'h1': '2.5rem',
                    'h2': '2rem',
                    'h3': '1.75rem',
                    'h4': '1.5rem',
                    'h5': '1.25rem',
                    'h6': '1rem'
                }
            },
            'spacing': {
                'xs': '0.25rem',
                'sm': '0.5rem',
                'md': '1rem',
                'lg': '1.5rem',
                'xl': '3rem'
            },
            'borders': {
                'radius': '0.375rem',
                'width': '1px',
                'style': 'solid'
            },
            'shadows': {
                'sm': '0 1px 2px 0 rgba(255, 255, 255, 0.05)',
                'md': '0 4px 6px -1px rgba(255, 255, 255, 0.1)',
                'lg': '0 10px 15px -3px rgba(255, 255, 255, 0.1)',
                'xl': '0 20px 25px -5px rgba(255, 255, 255, 0.1)'
            }
        }
    }
    
    @staticmethod
    def get_current_theme() -> str:
        """Get the current theme for the user."""
        # Check user session first
        theme = session.get('theme')
        if theme and theme in ThemeService.DEFAULT_THEMES:
            return theme
        
        # Check user agent for dark mode preference
        user_agent = request.headers.get('User-Agent', '') if request else ''
        if 'dark' in user_agent.lower():
            return 'dark'
        
        # Default to light theme
        return 'light'
    
    @staticmethod
    def set_user_theme(theme: str) -> bool:
        """Set theme preference for the current user."""
        if theme not in ThemeService.DEFAULT_THEMES:
            return False
        
        session['theme'] = theme
        return True
    
    @staticmethod
    def get_theme_config(theme: str = None) -> Dict[str, Any]:
        """Get complete theme configuration."""
        if theme is None:
            theme = ThemeService.get_current_theme()
        
        return ThemeService.DEFAULT_THEMES.get(theme, ThemeService.DEFAULT_THEMES['light'])
    
    @staticmethod
    def get_theme_variables(theme: str = None) -> Dict[str, str]:
        """Get CSS variables for the specified theme."""
        config = ThemeService.get_theme_config(theme)
        variables = {}
        
        # Color variables
        for name, value in config['colors'].items():
            variables[f'--color-{name}'] = value
        
        # Typography variables
        typography = config['typography']
        variables['--font-family'] = typography['font_family']
        variables['--font-size-base'] = typography['font_size_base']
        variables['--line-height'] = typography['line_height']
        
        for heading, size in typography['headings'].items():
            variables[f'--font-size-{heading}'] = size
        
        # Spacing variables
        for name, value in config['spacing'].items():
            variables[f'--spacing-{name}'] = value
        
        # Border variables
        borders = config['borders']
        variables['--border-radius'] = borders['radius']
        variables['--border-width'] = borders['width']
        variables['--border-style'] = borders['style']
        
        # Shadow variables
        for name, value in config['shadows'].items():
            variables[f'--shadow-{name}'] = value
        
        return variables
    
    @staticmethod
    def generate_css_variables(theme: str = None) -> str:
        """Generate CSS custom properties for the theme."""
        variables = ThemeService.get_theme_variables(theme)
        css_lines = [':root {']
        
        for name, value in variables.items():
            css_lines.append(f'  {name}: {value};')
        
        css_lines.append('}')
        return '\n'.join(css_lines)


class ComponentService:
    """Service for managing UI components and their rendering."""
    
    # Component library definitions
    COMPONENT_LIBRARY = {
        'button': {
            'template': 'ui/components/button.html',
            'props': {
                'text': {'type': 'string', 'required': True},
                'type': {'type': 'string', 'default': 'button', 'options': ['button', 'submit', 'reset']},
                'variant': {'type': 'string', 'default': 'primary', 'options': ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark']},
                'size': {'type': 'string', 'default': 'md', 'options': ['sm', 'md', 'lg']},
                'disabled': {'type': 'boolean', 'default': False},
                'loading': {'type': 'boolean', 'default': False},
                'icon': {'type': 'string', 'required': False},
                'href': {'type': 'string', 'required': False},
                'onclick': {'type': 'string', 'required': False}
            }
        },
        'card': {
            'template': 'ui/components/card.html',
            'props': {
                'title': {'type': 'string', 'required': False},
                'content': {'type': 'string', 'required': True},
                'footer': {'type': 'string', 'required': False},
                'variant': {'type': 'string', 'default': 'default', 'options': ['default', 'primary', 'secondary', 'success', 'danger', 'warning', 'info']},
                'shadow': {'type': 'string', 'default': 'md', 'options': ['none', 'sm', 'md', 'lg', 'xl']},
                'border': {'type': 'boolean', 'default': True}
            }
        },
        'alert': {
            'template': 'ui/components/alert.html',
            'props': {
                'message': {'type': 'string', 'required': True},
                'type': {'type': 'string', 'default': 'info', 'options': ['success', 'danger', 'warning', 'info']},
                'dismissible': {'type': 'boolean', 'default': False},
                'icon': {'type': 'boolean', 'default': True}
            }
        },
        'modal': {
            'template': 'ui/components/modal.html',
            'props': {
                'id': {'type': 'string', 'required': True},
                'title': {'type': 'string', 'required': True},
                'content': {'type': 'string', 'required': True},
                'size': {'type': 'string', 'default': 'md', 'options': ['sm', 'md', 'lg', 'xl']},
                'backdrop': {'type': 'boolean', 'default': True},
                'keyboard': {'type': 'boolean', 'default': True},
                'footer_buttons': {'type': 'array', 'default': []}
            }
        },
        'form_field': {
            'template': 'ui/components/form_field.html',
            'props': {
                'name': {'type': 'string', 'required': True},
                'label': {'type': 'string', 'required': True},
                'type': {'type': 'string', 'default': 'text', 'options': ['text', 'email', 'password', 'number', 'tel', 'url', 'search', 'textarea', 'select', 'checkbox', 'radio']},
                'value': {'type': 'string', 'required': False},
                'placeholder': {'type': 'string', 'required': False},
                'required': {'type': 'boolean', 'default': False},
                'disabled': {'type': 'boolean', 'default': False},
                'readonly': {'type': 'boolean', 'default': False},
                'help_text': {'type': 'string', 'required': False},
                'error': {'type': 'string', 'required': False},
                'options': {'type': 'array', 'required': False}  # For select, radio, checkbox
            }
        },
        'pagination': {
            'template': 'ui/components/pagination.html',
            'props': {
                'current_page': {'type': 'integer', 'required': True},
                'total_pages': {'type': 'integer', 'required': True},
                'base_url': {'type': 'string', 'required': True},
                'show_info': {'type': 'boolean', 'default': True},
                'size': {'type': 'string', 'default': 'md', 'options': ['sm', 'md', 'lg']}
            }
        },
        'breadcrumb': {
            'template': 'ui/components/breadcrumb.html',
            'props': {
                'items': {'type': 'array', 'required': True},  # [{'text': 'Home', 'url': '/'}, ...]
                'separator': {'type': 'string', 'default': '/'}
            }
        },
        'badge': {
            'template': 'ui/components/badge.html',
            'props': {
                'text': {'type': 'string', 'required': True},
                'variant': {'type': 'string', 'default': 'primary', 'options': ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark']},
                'pill': {'type': 'boolean', 'default': False}
            }
        }
    }
    
    @staticmethod
    def get_component_definition(component_name: str) -> Optional[Dict[str, Any]]:
        """Get component definition from the library."""
        return ComponentService.COMPONENT_LIBRARY.get(component_name)
    
    @staticmethod
    def validate_component_props(component_name: str, props: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate component properties against the definition."""
        definition = ComponentService.get_component_definition(component_name)
        if not definition:
            return False, [f"Unknown component: {component_name}"]
        
        errors = []
        component_props = definition.get('props', {})
        
        # Check required props
        for prop_name, prop_def in component_props.items():
            if prop_def.get('required', False) and prop_name not in props:
                errors.append(f"Required property '{prop_name}' is missing")
        
        # Validate prop types and values
        for prop_name, value in props.items():
            if prop_name not in component_props:
                continue  # Allow extra props for flexibility
            
            prop_def = component_props[prop_name]
            prop_type = prop_def.get('type')
            
            # Type validation
            if prop_type == 'string' and not isinstance(value, str):
                errors.append(f"Property '{prop_name}' must be a string")
            elif prop_type == 'integer' and not isinstance(value, int):
                errors.append(f"Property '{prop_name}' must be an integer")
            elif prop_type == 'boolean' and not isinstance(value, bool):
                errors.append(f"Property '{prop_name}' must be a boolean")
            elif prop_type == 'array' and not isinstance(value, list):
                errors.append(f"Property '{prop_name}' must be an array")
            
            # Options validation
            options = prop_def.get('options')
            if options and value not in options:
                errors.append(f"Property '{prop_name}' must be one of: {', '.join(options)}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def prepare_component_props(component_name: str, props: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare component props with defaults and validation."""
        definition = ComponentService.get_component_definition(component_name)
        if not definition:
            return props
        
        prepared_props = props.copy()
        component_props = definition.get('props', {})
        
        # Apply defaults
        for prop_name, prop_def in component_props.items():
            if prop_name not in prepared_props and 'default' in prop_def:
                prepared_props[prop_name] = prop_def['default']
        
        return prepared_props
    
    @staticmethod
    def get_component_css_classes(component_name: str, props: Dict[str, Any]) -> List[str]:
        """Generate CSS classes for a component based on its props."""
        classes = [f'ui-{component_name}']
        
        # Add variant classes
        if 'variant' in props:
            classes.append(f'ui-{component_name}--{props["variant"]}')
        
        # Add size classes
        if 'size' in props:
            classes.append(f'ui-{component_name}--{props["size"]}')
        
        # Add state classes
        if props.get('disabled'):
            classes.append(f'ui-{component_name}--disabled')
        if props.get('loading'):
            classes.append(f'ui-{component_name}--loading')
        if props.get('active'):
            classes.append(f'ui-{component_name}--active')
        
        return classes


class ResponsiveService:
    """Service for responsive design utilities and breakpoint management."""
    
    # Responsive breakpoints
    BREAKPOINTS = {
        'xs': '0px',
        'sm': '576px',
        'md': '768px',
        'lg': '992px',
        'xl': '1200px',
        'xxl': '1400px'
    }
    
    # Grid system configuration
    GRID_CONFIG = {
        'columns': 12,
        'gutter': '1.5rem',
        'container_max_widths': {
            'sm': '540px',
            'md': '720px',
            'lg': '960px',
            'xl': '1140px',
            'xxl': '1320px'
        }
    }
    
    @staticmethod
    def get_breakpoint_css() -> str:
        """Generate CSS for responsive breakpoints."""
        css_lines = []
        
        # Container styles
        css_lines.append('.container {')
        css_lines.append('  width: 100%;')
        css_lines.append('  padding-right: calc(var(--spacing-md) * 0.5);')
        css_lines.append('  padding-left: calc(var(--spacing-md) * 0.5);')
        css_lines.append('  margin-right: auto;')
        css_lines.append('  margin-left: auto;')
        css_lines.append('}')
        
        # Responsive container max-widths
        for breakpoint, max_width in ResponsiveService.GRID_CONFIG['container_max_widths'].items():
            bp_size = ResponsiveService.BREAKPOINTS[breakpoint]
            css_lines.append(f'@media (min-width: {bp_size}) {{')
            css_lines.append(f'  .container {{ max-width: {max_width}; }}')
            css_lines.append('}')
        
        return '\n'.join(css_lines)
    
    @staticmethod
    def get_grid_css() -> str:
        """Generate CSS for the grid system."""
        css_lines = []
        columns = ResponsiveService.GRID_CONFIG['columns']
        gutter = ResponsiveService.GRID_CONFIG['gutter']
        
        # Row styles
        css_lines.append('.row {')
        css_lines.append('  display: flex;')
        css_lines.append('  flex-wrap: wrap;')
        css_lines.append(f'  margin-right: calc({gutter} * -0.5);')
        css_lines.append(f'  margin-left: calc({gutter} * -0.5);')
        css_lines.append('}')
        
        # Column base styles
        css_lines.append('[class*="col-"] {')
        css_lines.append('  position: relative;')
        css_lines.append('  width: 100%;')
        css_lines.append(f'  padding-right: calc({gutter} * 0.5);')
        css_lines.append(f'  padding-left: calc({gutter} * 0.5);')
        css_lines.append('}')
        
        # Generate column classes for each breakpoint
        for breakpoint, bp_size in ResponsiveService.BREAKPOINTS.items():
            if breakpoint == 'xs':
                # Base column classes (no media query for xs)
                for i in range(1, columns + 1):
                    width = (i / columns) * 100
                    css_lines.append(f'.col-{i} {{ flex: 0 0 {width:.6f}%; max-width: {width:.6f}%; }}')
            else:
                # Responsive column classes
                css_lines.append(f'@media (min-width: {bp_size}) {{')
                for i in range(1, columns + 1):
                    width = (i / columns) * 100
                    css_lines.append(f'  .col-{breakpoint}-{i} {{ flex: 0 0 {width:.6f}%; max-width: {width:.6f}%; }}')
                css_lines.append('}')
        
        return '\n'.join(css_lines)
    
    @staticmethod
    def generate_responsive_classes(base_class: str, properties: Dict[str, str]) -> str:
        """Generate responsive utility classes."""
        css_lines = []
        
        for breakpoint, bp_size in ResponsiveService.BREAKPOINTS.items():
            if breakpoint == 'xs':
                # Base classes (no media query for xs)
                for prop_name, prop_value in properties.items():
                    css_lines.append(f'.{base_class}-{prop_name} {{ {prop_value} }}')
            else:
                # Responsive classes
                css_lines.append(f'@media (min-width: {bp_size}) {{')
                for prop_name, prop_value in properties.items():
                    css_lines.append(f'  .{base_class}-{breakpoint}-{prop_name} {{ {prop_value} }}')
                css_lines.append('}')
        
        return '\n'.join(css_lines)


class AccessibilityService:
    """Service for accessibility features and ARIA support."""
    
    @staticmethod
    def generate_aria_attributes(component_type: str, props: Dict[str, Any]) -> Dict[str, str]:
        """Generate appropriate ARIA attributes for a component."""
        aria_attrs = {}
        
        # Common ARIA attributes based on component type
        if component_type == 'button':
            if props.get('disabled'):
                aria_attrs['aria-disabled'] = 'true'
            if props.get('loading'):
                aria_attrs['aria-busy'] = 'true'
            if props.get('expanded') is not None:
                aria_attrs['aria-expanded'] = str(props['expanded']).lower()
        
        elif component_type == 'modal':
            aria_attrs['role'] = 'dialog'
            aria_attrs['aria-modal'] = 'true'
            if props.get('title'):
                aria_attrs['aria-labelledby'] = f"{props['id']}-title"
        
        elif component_type == 'alert':
            aria_attrs['role'] = 'alert'
            aria_attrs['aria-live'] = 'polite'
        
        elif component_type == 'form_field':
            if props.get('required'):
                aria_attrs['aria-required'] = 'true'
            if props.get('error'):
                aria_attrs['aria-invalid'] = 'true'
                aria_attrs['aria-describedby'] = f"{props['name']}-error"
        
        return aria_attrs
    
    @staticmethod
    def get_accessibility_css() -> str:
        """Generate CSS for accessibility features."""
        css_lines = [
            # Focus styles
            '*:focus {',
            '  outline: 2px solid var(--color-primary);',
            '  outline-offset: 2px;',
            '}',
            '',
            # Skip links
            '.skip-link {',
            '  position: absolute;',
            '  top: -40px;',
            '  left: 6px;',
            '  background: var(--color-primary);',
            '  color: var(--color-white);',
            '  padding: 8px;',
            '  text-decoration: none;',
            '  z-index: 1000;',
            '}',
            '',
            '.skip-link:focus {',
            '  top: 6px;',
            '}',
            '',
            # Screen reader only content
            '.sr-only {',
            '  position: absolute !important;',
            '  width: 1px !important;',
            '  height: 1px !important;',
            '  padding: 0 !important;',
            '  margin: -1px !important;',
            '  overflow: hidden !important;',
            '  clip: rect(0, 0, 0, 0) !important;',
            '  white-space: nowrap !important;',
            '  border: 0 !important;',
            '}',
            '',
            # High contrast mode support
            '@media (prefers-contrast: high) {',
            '  * {',
            '    border-color: ButtonText !important;',
            '  }',
            '}',
            '',
            # Reduced motion support
            '@media (prefers-reduced-motion: reduce) {',
            '  * {',
            '    animation-duration: 0.01ms !important;',
            '    animation-iteration-count: 1 !important;',
            '    transition-duration: 0.01ms !important;',
            '  }',
            '}'
        ]
        
        return '\n'.join(css_lines)
    
    @staticmethod
    def validate_accessibility(component_type: str, props: Dict[str, Any]) -> List[str]:
        """Validate component for accessibility compliance."""
        warnings = []
        
        # Check for missing alt text on images
        if component_type == 'image' and not props.get('alt'):
            warnings.append("Image components should have alt text for accessibility")
        
        # Check for missing labels on form fields
        if component_type == 'form_field' and not props.get('label'):
            warnings.append("Form fields should have labels for accessibility")
        
        # Check for button text
        if component_type == 'button' and not props.get('text') and not props.get('aria-label'):
            warnings.append("Buttons should have text or aria-label for accessibility")
        
        # Check for modal titles
        if component_type == 'modal' and not props.get('title'):
            warnings.append("Modals should have titles for accessibility")
        
        return warnings
