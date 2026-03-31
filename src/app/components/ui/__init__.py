"""
UI Framework Component

Provides comprehensive UI components, styling framework, and responsive design utilities
for the fact checker application. Includes theme management, component library,
and accessibility features.
"""

from .services import (
    ThemeService,
    ComponentService,
    ResponsiveService,
    AccessibilityService
)

from .helpers import (
    render_component,
    get_theme_variables,
    generate_css_classes,
    create_responsive_grid,
    format_component_props
)

__all__ = [
    'ThemeService',
    'ComponentService', 
    'ResponsiveService',
    'AccessibilityService',
    'render_component',
    'get_theme_variables',
    'generate_css_classes',
    'create_responsive_grid',
    'format_component_props'
]
