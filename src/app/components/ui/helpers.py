"""
UI Framework helper functions for component rendering and template utilities.
"""

import logging
from typing import Dict, List, Any, Optional
from flask import render_template_string, current_app
from jinja2 import Template, Environment, FileSystemLoader
from .services import ComponentService, ThemeService, ResponsiveService, AccessibilityService

logger = logging.getLogger(__name__)


def render_component(component_name: str, **props) -> str:
    """
    Render a UI component with the given properties.
    
    Args:
        component_name: Name of the component to render
        **props: Component properties
        
    Returns:
        Rendered HTML string
    """
    try:
        # Get component definition
        definition = ComponentService.get_component_definition(component_name)
        if not definition:
            logger.error(f"Unknown component: {component_name}")
            return f"<!-- Unknown component: {component_name} -->"
        
        # Validate props
        is_valid, errors = ComponentService.validate_component_props(component_name, props)
        if not is_valid:
            logger.warning(f"Component validation errors for {component_name}: {errors}")
            # Continue rendering with available props for graceful degradation
        
        # Prepare props with defaults
        prepared_props = ComponentService.prepare_component_props(component_name, props)
        
        # Generate CSS classes
        css_classes = ComponentService.get_component_css_classes(component_name, prepared_props)
        prepared_props['css_classes'] = ' '.join(css_classes)
        
        # Generate ARIA attributes
        aria_attrs = AccessibilityService.generate_aria_attributes(component_name, prepared_props)
        prepared_props['aria_attributes'] = aria_attrs
        
        # Get theme variables
        theme_vars = get_theme_variables()
        prepared_props['theme'] = theme_vars
        
        # Render template
        template_path = definition['template']
        try:
            return render_template_string(
                get_component_template(template_path),
                **prepared_props
            )
        except Exception as e:
            logger.error(f"Error rendering component template {template_path}: {str(e)}")
            return f"<!-- Error rendering component: {component_name} -->"
            
    except Exception as e:
        logger.error(f"Error rendering component {component_name}: {str(e)}")
        return f"<!-- Error rendering component: {component_name} -->"


def get_component_template(template_path: str) -> str:
    """
    Get component template content.
    
    Args:
        template_path: Path to the template file
        
    Returns:
        Template content as string
    """
    # Component templates are defined inline for now
    # In a real application, these would be loaded from files
    
    templates = {
        'ui/components/button.html': '''
<button 
    type="{{ type }}" 
    class="{{ css_classes }}{% if href %} btn-link{% endif %}"
    {% if disabled %}disabled{% endif %}
    {% if onclick %}onclick="{{ onclick }}"{% endif %}
    {% for attr, value in aria_attributes.items() %}{{ attr }}="{{ value }}" {% endfor %}
>
    {% if loading %}
        <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
    {% endif %}
    {% if icon %}
        <i class="{{ icon }}{% if text %} me-2{% endif %}" aria-hidden="true"></i>
    {% endif %}
    {% if href %}
        <a href="{{ href }}" class="stretched-link">{{ text }}</a>
    {% else %}
        {{ text }}
    {% endif %}
</button>
        ''',
        
        'ui/components/card.html': '''
<div class="{{ css_classes }}{% if shadow != 'none' %} shadow-{{ shadow }}{% endif %}{% if border %} border{% endif %}">
    {% if title %}
    <div class="card-header">
        <h5 class="card-title mb-0">{{ title }}</h5>
    </div>
    {% endif %}
    <div class="card-body">
        {{ content | safe }}
    </div>
    {% if footer %}
    <div class="card-footer">
        {{ footer | safe }}
    </div>
    {% endif %}
</div>
        ''',
        
        'ui/components/alert.html': '''
<div class="{{ css_classes }} alert-{{ type }}{% if dismissible %} alert-dismissible fade show{% endif %}" 
     {% for attr, value in aria_attributes.items() %}{{ attr }}="{{ value }}" {% endfor %}>
    {% if icon %}
        {% set icon_class = {
            'success': 'fas fa-check-circle',
            'danger': 'fas fa-exclamation-triangle', 
            'warning': 'fas fa-exclamation-circle',
            'info': 'fas fa-info-circle'
        }[type] %}
        <i class="{{ icon_class }} me-2" aria-hidden="true"></i>
    {% endif %}
    {{ message }}
    {% if dismissible %}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    {% endif %}
</div>
        ''',
        
        'ui/components/modal.html': '''
<div class="modal fade" id="{{ id }}" tabindex="-1" 
     {% for attr, value in aria_attributes.items() %}{{ attr }}="{{ value }}" {% endfor %}
     {% if not backdrop %}data-bs-backdrop="static"{% endif %}
     {% if not keyboard %}data-bs-keyboard="false"{% endif %}>
    <div class="modal-dialog{% if size != 'md' %} modal-{{ size }}{% endif %}">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="{{ id }}-title">{{ title }}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                {{ content | safe }}
            </div>
            {% if footer_buttons %}
            <div class="modal-footer">
                {% for button in footer_buttons %}
                    {{ render_component('button', **button) | safe }}
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
</div>
        ''',
        
        'ui/components/form_field.html': '''
<div class="mb-3">
    <label for="{{ name }}" class="form-label">
        {{ label }}
        {% if required %}<span class="text-danger">*</span>{% endif %}
    </label>
    
    {% if type == 'textarea' %}
        <textarea 
            id="{{ name }}" 
            name="{{ name }}" 
            class="form-control{% if error %} is-invalid{% endif %}"
            {% if placeholder %}placeholder="{{ placeholder }}"{% endif %}
            {% if required %}required{% endif %}
            {% if disabled %}disabled{% endif %}
            {% if readonly %}readonly{% endif %}
            {% for attr, value in aria_attributes.items() %}{{ attr }}="{{ value }}" {% endfor %}
        >{{ value or '' }}</textarea>
    {% elif type == 'select' %}
        <select 
            id="{{ name }}" 
            name="{{ name }}" 
            class="form-select{% if error %} is-invalid{% endif %}"
            {% if required %}required{% endif %}
            {% if disabled %}disabled{% endif %}
            {% for attr, value in aria_attributes.items() %}{{ attr }}="{{ value }}" {% endfor %}
        >
            {% if placeholder %}<option value="">{{ placeholder }}</option>{% endif %}
            {% for option in options %}
                <option value="{{ option.value }}" {% if option.value == value %}selected{% endif %}>
                    {{ option.text }}
                </option>
            {% endfor %}
        </select>
    {% elif type == 'checkbox' %}
        <div class="form-check">
            <input 
                type="checkbox" 
                id="{{ name }}" 
                name="{{ name }}" 
                class="form-check-input{% if error %} is-invalid{% endif %}"
                value="1"
                {% if value %}checked{% endif %}
                {% if required %}required{% endif %}
                {% if disabled %}disabled{% endif %}
                {% for attr, value in aria_attributes.items() %}{{ attr }}="{{ value }}" {% endfor %}
            >
            <label class="form-check-label" for="{{ name }}">
                {{ label }}
            </label>
        </div>
    {% else %}
        <input 
            type="{{ type }}" 
            id="{{ name }}" 
            name="{{ name }}" 
            class="form-control{% if error %} is-invalid{% endif %}"
            {% if value %}value="{{ value }}"{% endif %}
            {% if placeholder %}placeholder="{{ placeholder }}"{% endif %}
            {% if required %}required{% endif %}
            {% if disabled %}disabled{% endif %}
            {% if readonly %}readonly{% endif %}
            {% for attr, value in aria_attributes.items() %}{{ attr }}="{{ value }}" {% endfor %}
        >
    {% endif %}
    
    {% if help_text %}
        <div class="form-text">{{ help_text }}</div>
    {% endif %}
    
    {% if error %}
        <div class="invalid-feedback" id="{{ name }}-error">{{ error }}</div>
    {% endif %}
</div>
        ''',
        
        'ui/components/pagination.html': '''
<nav aria-label="Pagination">
    {% if show_info %}
        <div class="d-flex justify-content-between align-items-center mb-3">
            <span class="text-muted">
                Page {{ current_page }} of {{ total_pages }}
            </span>
        </div>
    {% endif %}
    
    <ul class="pagination{% if size != 'md' %} pagination-{{ size }}{% endif %} justify-content-center">
        <!-- Previous button -->
        <li class="page-item{% if current_page <= 1 %} disabled{% endif %}">
            <a class="page-link" href="{% if current_page > 1 %}{{ base_url }}?page={{ current_page - 1 }}{% else %}#{% endif %}" 
               {% if current_page <= 1 %}tabindex="-1" aria-disabled="true"{% endif %}>
                <span aria-hidden="true">&laquo;</span>
                <span class="sr-only">Previous</span>
            </a>
        </li>
        
        <!-- Page numbers -->
        {% set start_page = [1, current_page - 2] | max %}
        {% set end_page = [total_pages, current_page + 2] | min %}
        
        {% if start_page > 1 %}
            <li class="page-item">
                <a class="page-link" href="{{ base_url }}?page=1">1</a>
            </li>
            {% if start_page > 2 %}
                <li class="page-item disabled">
                    <span class="page-link">...</span>
                </li>
            {% endif %}
        {% endif %}
        
        {% for page in range(start_page, end_page + 1) %}
            <li class="page-item{% if page == current_page %} active{% endif %}">
                <a class="page-link" href="{{ base_url }}?page={{ page }}"
                   {% if page == current_page %}aria-current="page"{% endif %}>
                    {{ page }}
                </a>
            </li>
        {% endfor %}
        
        {% if end_page < total_pages %}
            {% if end_page < total_pages - 1 %}
                <li class="page-item disabled">
                    <span class="page-link">...</span>
                </li>
            {% endif %}
            <li class="page-item">
                <a class="page-link" href="{{ base_url }}?page={{ total_pages }}">{{ total_pages }}</a>
            </li>
        {% endif %}
        
        <!-- Next button -->
        <li class="page-item{% if current_page >= total_pages %} disabled{% endif %}">
            <a class="page-link" href="{% if current_page < total_pages %}{{ base_url }}?page={{ current_page + 1 }}{% else %}#{% endif %}"
               {% if current_page >= total_pages %}tabindex="-1" aria-disabled="true"{% endif %}>
                <span class="sr-only">Next</span>
                <span aria-hidden="true">&raquo;</span>
            </a>
        </li>
    </ul>
</nav>
        ''',
        
        'ui/components/breadcrumb.html': '''
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        {% for item in items %}
            <li class="breadcrumb-item{% if loop.last %} active{% endif %}"
                {% if loop.last %}aria-current="page"{% endif %}>
                {% if not loop.last and item.url %}
                    <a href="{{ item.url }}">{{ item.text }}</a>
                {% else %}
                    {{ item.text }}
                {% endif %}
            </li>
        {% endfor %}
    </ol>
</nav>
        ''',
        
        'ui/components/badge.html': '''
<span class="{{ css_classes }} badge bg-{{ variant }}{% if pill %} rounded-pill{% endif %}">
    {{ text }}
</span>
        '''
    }
    
    return templates.get(template_path, f'<!-- Template not found: {template_path} -->')


def get_theme_variables(theme: str = None) -> Dict[str, str]:
    """
    Get theme variables for the current or specified theme.
    
    Args:
        theme: Theme name (optional, uses current theme if not specified)
        
    Returns:
        Dictionary of theme variables
    """
    return ThemeService.get_theme_variables(theme)


def generate_css_classes(*class_lists) -> str:
    """
    Generate CSS class string from multiple class lists.
    
    Args:
        *class_lists: Variable number of class lists (strings, lists, or dicts)
        
    Returns:
        Space-separated CSS class string
    """
    classes = []
    
    for class_list in class_lists:
        if isinstance(class_list, str):
            classes.extend(class_list.split())
        elif isinstance(class_list, list):
            classes.extend(class_list)
        elif isinstance(class_list, dict):
            # Conditional classes: {'class-name': condition}
            classes.extend([cls for cls, condition in class_list.items() if condition])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_classes = []
    for cls in classes:
        if cls and cls not in seen:
            seen.add(cls)
            unique_classes.append(cls)
    
    return ' '.join(unique_classes)


def create_responsive_grid(items: List[Any], columns: Dict[str, int] = None) -> List[List[Any]]:
    """
    Create responsive grid layout for items.
    
    Args:
        items: List of items to arrange in grid
        columns: Dictionary of breakpoint -> column count (e.g., {'sm': 1, 'md': 2, 'lg': 3})
        
    Returns:
        List of rows, each containing a list of items
    """
    if columns is None:
        columns = {'sm': 1, 'md': 2, 'lg': 3}
    
    # Use the largest column count for grid creation
    max_columns = max(columns.values())
    
    rows = []
    for i in range(0, len(items), max_columns):
        row = items[i:i + max_columns]
        rows.append(row)
    
    return rows


def format_component_props(**props) -> Dict[str, Any]:
    """
    Format and sanitize component properties.
    
    Args:
        **props: Component properties
        
    Returns:
        Formatted properties dictionary
    """
    formatted_props = {}
    
    for key, value in props.items():
        # Convert snake_case to kebab-case for HTML attributes
        if key.startswith('data_') or key.startswith('aria_'):
            formatted_key = key.replace('_', '-')
        else:
            formatted_key = key
        
        # Handle boolean values
        if isinstance(value, bool):
            if value:
                formatted_props[formatted_key] = formatted_key  # HTML boolean attribute
        else:
            formatted_props[formatted_key] = value
    
    return formatted_props


def generate_utility_css() -> str:
    """
    Generate utility CSS classes for common styling needs.
    
    Returns:
        CSS string with utility classes
    """
    css_lines = []
    
    # Spacing utilities
    spacing_props = {
        'm': 'margin',
        'mt': 'margin-top',
        'mr': 'margin-right', 
        'mb': 'margin-bottom',
        'ml': 'margin-left',
        'mx': 'margin-left margin-right',
        'my': 'margin-top margin-bottom',
        'p': 'padding',
        'pt': 'padding-top',
        'pr': 'padding-right',
        'pb': 'padding-bottom',
        'pl': 'padding-left',
        'px': 'padding-left padding-right',
        'py': 'padding-top padding-bottom'
    }
    
    spacing_values = {
        '0': '0',
        '1': 'var(--spacing-xs)',
        '2': 'var(--spacing-sm)',
        '3': 'var(--spacing-md)',
        '4': 'var(--spacing-lg)',
        '5': 'var(--spacing-xl)'
    }
    
    for prop_name, css_props in spacing_props.items():
        for size, value in spacing_values.items():
            css_properties = css_props.split()
            css_lines.append(f'.{prop_name}-{size} {{')
            for css_prop in css_properties:
                css_lines.append(f'  {css_prop}: {value} !important;')
            css_lines.append('}')
    
    # Display utilities
    display_values = ['none', 'block', 'inline', 'inline-block', 'flex', 'inline-flex', 'grid']
    for display in display_values:
        css_lines.append(f'.d-{display} {{ display: {display} !important; }}')
    
    # Text utilities
    text_aligns = ['left', 'center', 'right', 'justify']
    for align in text_aligns:
        css_lines.append(f'.text-{align} {{ text-align: {align} !important; }}')
    
    # Color utilities
    colors = ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark']
    for color in colors:
        css_lines.append(f'.text-{color} {{ color: var(--color-{color}) !important; }}')
        css_lines.append(f'.bg-{color} {{ background-color: var(--color-{color}) !important; }}')
    
    # Flexbox utilities
    flex_directions = ['row', 'column', 'row-reverse', 'column-reverse']
    for direction in flex_directions:
        css_lines.append(f'.flex-{direction} {{ flex-direction: {direction} !important; }}')
    
    justify_content = {
        'start': 'flex-start',
        'end': 'flex-end', 
        'center': 'center',
        'between': 'space-between',
        'around': 'space-around',
        'evenly': 'space-evenly'
    }
    for name, value in justify_content.items():
        css_lines.append(f'.justify-content-{name} {{ justify-content: {value} !important; }}')
    
    align_items = {
        'start': 'flex-start',
        'end': 'flex-end',
        'center': 'center', 
        'baseline': 'baseline',
        'stretch': 'stretch'
    }
    for name, value in align_items.items():
        css_lines.append(f'.align-items-{name} {{ align-items: {value} !important; }}')
    
    return '\n'.join(css_lines)


def get_component_library_css() -> str:
    """
    Generate CSS for all UI components.
    
    Returns:
        Complete CSS for the component library
    """
    css_sections = [
        # Theme variables
        ThemeService.generate_css_variables(),
        '',
        # Responsive grid
        ResponsiveService.get_breakpoint_css(),
        '',
        ResponsiveService.get_grid_css(),
        '',
        # Accessibility
        AccessibilityService.get_accessibility_css(),
        '',
        # Utility classes
        generate_utility_css(),
        '',
        # Component-specific styles
        '''
/* UI Component Styles */
.ui-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.5rem 1rem;
    border: var(--border-width) var(--border-style) transparent;
    border-radius: var(--border-radius);
    font-family: var(--font-family);
    font-size: var(--font-size-base);
    line-height: var(--line-height);
    text-decoration: none;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
}

.ui-button--primary {
    background-color: var(--color-primary);
    color: var(--color-white);
    border-color: var(--color-primary);
}

.ui-button--primary:hover {
    background-color: var(--color-primary);
    opacity: 0.9;
}

.ui-button--secondary {
    background-color: var(--color-secondary);
    color: var(--color-white);
    border-color: var(--color-secondary);
}

.ui-button--sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.875rem;
}

.ui-button--lg {
    padding: 0.75rem 1.5rem;
    font-size: 1.125rem;
}

.ui-button--disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.ui-card {
    background-color: var(--color-white);
    border: var(--border-width) var(--border-style) rgba(0, 0, 0, 0.125);
    border-radius: var(--border-radius);
    overflow: hidden;
}

.ui-alert {
    padding: 1rem;
    border: var(--border-width) var(--border-style) transparent;
    border-radius: var(--border-radius);
    margin-bottom: 1rem;
}

.ui-alert--success {
    background-color: rgba(40, 167, 69, 0.1);
    border-color: var(--color-success);
    color: var(--color-success);
}

.ui-alert--danger {
    background-color: rgba(220, 53, 69, 0.1);
    border-color: var(--color-danger);
    color: var(--color-danger);
}

.ui-alert--warning {
    background-color: rgba(255, 193, 7, 0.1);
    border-color: var(--color-warning);
    color: var(--color-warning);
}

.ui-alert--info {
    background-color: rgba(23, 162, 184, 0.1);
    border-color: var(--color-info);
    color: var(--color-info);
}

.ui-badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    font-weight: 600;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    border-radius: var(--border-radius);
}
        '''
    ]
    
    return '\n'.join(css_sections)
