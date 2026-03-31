"""
UI Framework routes for theme management and component showcase.
"""

import logging
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from .services import ThemeService, ComponentService, ResponsiveService, AccessibilityService
from .helpers import (
    render_component, get_theme_variables, generate_css_classes,
    get_component_library_css, generate_utility_css
)

logger = logging.getLogger(__name__)

ui_bp = Blueprint('ui', __name__, url_prefix='/ui')


@ui_bp.route('/theme')
def theme_selector():
    """Theme selection page."""
    current_theme = ThemeService.get_current_theme()
    available_themes = list(ThemeService.DEFAULT_THEMES.keys())
    
    return render_template('ui/theme_selector.html', 
                         current_theme=current_theme,
                         available_themes=available_themes,
                         themes=ThemeService.DEFAULT_THEMES)


@ui_bp.route('/theme/set/<theme_name>')
def set_theme(theme_name):
    """Set user theme preference."""
    success = ThemeService.set_user_theme(theme_name)
    
    if success:
        return redirect(request.referrer or url_for('main.index'))
    else:
        return jsonify({'error': 'Invalid theme'}), 400


@ui_bp.route('/api/theme/current')
def get_current_theme():
    """API endpoint to get current theme configuration."""
    theme_name = ThemeService.get_current_theme()
    theme_config = ThemeService.get_theme_config(theme_name)
    theme_variables = ThemeService.get_theme_variables(theme_name)
    
    return jsonify({
        'name': theme_name,
        'config': theme_config,
        'variables': theme_variables
    })


@ui_bp.route('/api/theme/css')
def get_theme_css():
    """API endpoint to get theme CSS variables."""
    theme_name = request.args.get('theme')
    css_variables = ThemeService.generate_css_variables(theme_name)
    
    return css_variables, 200, {'Content-Type': 'text/css'}


@ui_bp.route('/components')
def component_showcase():
    """Component showcase and documentation page."""
    components = ComponentService.COMPONENT_LIBRARY
    current_theme = ThemeService.get_current_theme()
    
    return render_template('ui/component_showcase.html',
                         components=components,
                         current_theme=current_theme)


@ui_bp.route('/components/<component_name>')
def component_detail(component_name):
    """Detailed component documentation and examples."""
    definition = ComponentService.get_component_definition(component_name)
    
    if not definition:
        return render_template('errors/404.html'), 404
    
    # Generate example props
    example_props = {}
    for prop_name, prop_def in definition.get('props', {}).items():
        if prop_def.get('required', False):
            if prop_def['type'] == 'string':
                example_props[prop_name] = f'Example {prop_name}'
            elif prop_def['type'] == 'boolean':
                example_props[prop_name] = True
            elif prop_def['type'] == 'integer':
                example_props[prop_name] = 1
            elif prop_def['type'] == 'array':
                example_props[prop_name] = []
        elif 'default' in prop_def:
            example_props[prop_name] = prop_def['default']
    
    # Render example component
    example_html = render_component(component_name, **example_props)
    
    return render_template('ui/component_detail.html',
                         component_name=component_name,
                         definition=definition,
                         example_props=example_props,
                         example_html=example_html)


@ui_bp.route('/api/component/render', methods=['POST'])
def render_component_api():
    """API endpoint to render a component with given props."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        component_name = data.get('component')
        props = data.get('props', {})
        
        if not component_name:
            return jsonify({'error': 'Component name is required'}), 400
        
        # Validate component exists
        definition = ComponentService.get_component_definition(component_name)
        if not definition:
            return jsonify({'error': f'Unknown component: {component_name}'}), 400
        
        # Validate props
        is_valid, errors = ComponentService.validate_component_props(component_name, props)
        
        # Render component
        html = render_component(component_name, **props)
        
        return jsonify({
            'html': html,
            'valid': is_valid,
            'errors': errors if not is_valid else []
        })
        
    except Exception as e:
        logger.error(f"Error rendering component via API: {str(e)}")
        return jsonify({'error': 'Failed to render component'}), 500


@ui_bp.route('/css/framework.css')
def framework_css():
    """Serve the complete UI framework CSS."""
    theme_name = request.args.get('theme')
    css_content = get_component_library_css()
    
    # Add theme-specific variables if theme is specified
    if theme_name:
        theme_css = ThemeService.generate_css_variables(theme_name)
        css_content = theme_css + '\n\n' + css_content
    
    return css_content, 200, {'Content-Type': 'text/css'}


@ui_bp.route('/css/utilities.css')
def utilities_css():
    """Serve utility CSS classes."""
    css_content = generate_utility_css()
    return css_content, 200, {'Content-Type': 'text/css'}


@ui_bp.route('/css/responsive.css')
def responsive_css():
    """Serve responsive grid CSS."""
    css_content = ResponsiveService.get_breakpoint_css() + '\n\n' + ResponsiveService.get_grid_css()
    return css_content, 200, {'Content-Type': 'text/css'}


@ui_bp.route('/css/accessibility.css')
def accessibility_css():
    """Serve accessibility CSS."""
    css_content = AccessibilityService.get_accessibility_css()
    return css_content, 200, {'Content-Type': 'text/css'}


@ui_bp.route('/api/validate-component', methods=['POST'])
def validate_component_api():
    """API endpoint to validate component props."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        component_name = data.get('component')
        props = data.get('props', {})
        
        if not component_name:
            return jsonify({'error': 'Component name is required'}), 400
        
        # Validate component exists
        definition = ComponentService.get_component_definition(component_name)
        if not definition:
            return jsonify({'error': f'Unknown component: {component_name}'}), 400
        
        # Validate props
        is_valid, errors = ComponentService.validate_component_props(component_name, props)
        
        # Check accessibility
        accessibility_warnings = AccessibilityService.validate_accessibility(component_name, props)
        
        return jsonify({
            'valid': is_valid,
            'errors': errors,
            'accessibility_warnings': accessibility_warnings,
            'component_definition': definition
        })
        
    except Exception as e:
        logger.error(f"Error validating component: {str(e)}")
        return jsonify({'error': 'Failed to validate component'}), 500


@ui_bp.route('/playground')
def component_playground():
    """Interactive component playground for testing and development."""
    components = list(ComponentService.COMPONENT_LIBRARY.keys())
    current_theme = ThemeService.get_current_theme()
    
    return render_template('ui/component_playground.html',
                         components=components,
                         current_theme=current_theme)


@ui_bp.route('/style-guide')
def style_guide():
    """Complete style guide showing all design tokens and components."""
    current_theme = ThemeService.get_current_theme()
    theme_config = ThemeService.get_theme_config(current_theme)
    components = ComponentService.COMPONENT_LIBRARY
    
    return render_template('ui/style_guide.html',
                         theme_config=theme_config,
                         components=components,
                         current_theme=current_theme)


@ui_bp.route('/api/breakpoints')
def get_breakpoints():
    """API endpoint to get responsive breakpoints."""
    return jsonify({
        'breakpoints': ResponsiveService.BREAKPOINTS,
        'grid_config': ResponsiveService.GRID_CONFIG
    })


# Template context processors
@ui_bp.app_context_processor
def inject_ui_helpers():
    """Inject UI helper functions into template context."""
    return {
        'render_component': render_component,
        'get_theme_variables': get_theme_variables,
        'generate_css_classes': generate_css_classes,
        'current_theme': ThemeService.get_current_theme,
        'ui_component_exists': lambda name: ComponentService.get_component_definition(name) is not None
    }
