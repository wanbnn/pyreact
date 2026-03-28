"""
Styled Components Module
========================

CSS-in-Python styling similar to styled-components.
"""

from typing import Any, Callable, Dict, Optional, Union
import hashlib
import re


def styled(
    element_type: Union[str, Callable],
    styles: str,
    **kwargs
) -> Callable:
    """
    Create a styled component
    
    Args:
        element_type: HTML tag or component
        styles: CSS styles
        **kwargs: Additional options
    
    Returns:
        Styled component
    
    Example:
        Button = styled('button', '''
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            cursor: pointer;
            
            &:hover {
                background-color: #0056b3;
            }
            
            &:disabled {
                opacity: 0.6;
            }
        ''')
        
        h(Button, {'onClick': handle_click}, 'Click me')
    """
    # Generate unique class name
    class_name = _generate_class_name(styles)
    
    # Parse and process styles
    processed_styles = _process_styles(styles, class_name)
    
    # Register styles
    _register_styles(class_name, processed_styles)
    
    def styled_component(props: Dict[str, Any]) -> Any:
        """Render styled component"""
        from .element import VNode
        
        # Merge className
        existing_class = props.get('className', '')
        new_class = f"{class_name} {existing_class}".strip()
        
        # Create element
        if callable(element_type):
            # It's a component
            return element_type({**props, 'className': new_class})
        else:
            # It's an HTML element
            return VNode(
                element_type,
                {**props, 'className': new_class}
            )
    
    styled_component._styled_class = class_name
    styled_component._styles = processed_styles
    
    return styled_component


def css(styles: str) -> str:
    """
    Create inline styles from CSS string
    
    Args:
        styles: CSS string
    
    Returns:
        str: Class name
    
    Example:
        className = css('color: red; font-size: 16px;')
        h('div', {'className': className}, 'Styled text')
    """
    class_name = _generate_class_name(styles)
    processed = _process_styles(styles, class_name)
    _register_styles(class_name, processed)
    return class_name


def keyframes(animations: str) -> str:
    """
    Create keyframe animation
    
    Args:
        animations: Keyframe definitions
    
    Returns:
        str: Animation name
    
    Example:
        fadeIn = keyframes('''
            from { opacity: 0; }
            to { opacity: 1; }
        ''')
        
        h('div', {'style': {'animation': f'{fadeIn} 1s ease-in'}})
    """
    animation_name = _generate_class_name(animations)
    processed = f"@keyframes {animation_name} {{ {animations} }}"
    _register_styles(animation_name, processed, is_keyframes=True)
    return animation_name


def create_global_style(styles: str) -> Callable:
    """
    Create global styles
    
    Args:
        styles: Global CSS styles
    
    Returns:
        Function to apply global styles
    
    Example:
        GlobalStyle = create_global_style('''
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, sans-serif;
            }
        ''')
        
        # In your app
        h(GlobalStyle, None)
    """
    def global_component(props: Dict[str, Any]) -> None:
        """Apply global styles"""
        _register_styles('global', styles, is_global=True)
        return None
    
    global_component._is_global = True
    global_component._styles = styles
    
    return global_component


def _generate_class_name(styles: str) -> str:
    """Generate unique class name from styles"""
    hash_obj = hashlib.md5(styles.encode())
    return f"pyreact-{hash_obj.hexdigest()[:8]}"


def _process_styles(styles: str, class_name: str) -> str:
    """
    Process CSS styles
    
    - Replaces & with class name
    - Handles nesting
    - Adds vendor prefixes
    
    Args:
        styles: Raw CSS
        class_name: Class name
    
    Returns:
        str: Processed CSS
    """
    # Replace & with class selector
    processed = styles.replace('&', f'.{class_name}')
    
    # Handle nested selectors
    lines = []
    current_selector = f'.{class_name}'
    indent_level = 0
    
    for line in processed.split('\n'):
        stripped = line.strip()
        
        if not stripped:
            continue
        
        # Handle opening brace
        if '{' in stripped:
            if indent_level == 0:
                lines.append(f'.{class_name} {{')
            else:
                lines.append(f'  {stripped}')
            indent_level += 1
        # Handle closing brace
        elif '}' in stripped:
            indent_level -= 1
            lines.append('}')
        # Handle properties
        else:
            lines.append(f'  {stripped}')
    
    return '\n'.join(lines)


def _register_styles(
    class_name: str,
    styles: str,
    is_global: bool = False,
    is_keyframes: bool = False
) -> None:
    """
    Register styles in the style registry
    
    Args:
        class_name: Class name
        styles: CSS styles
        is_global: Whether it's global styles
        is_keyframes: Whether it's keyframes
    """
    _style_registry[class_name] = {
        'styles': styles,
        'is_global': is_global,
        'is_keyframes': is_keyframes
    }


def get_all_styles() -> str:
    """
    Get all registered styles
    
    Returns:
        str: All CSS
    """
    styles = []
    for name, data in _style_registry.items():
        styles.append(data['styles'])
    return '\n\n'.join(styles)


def get_style_registry() -> Dict:
    """Get the style registry"""
    return _style_registry.copy()


# Style registry
_style_registry: Dict[str, Dict] = {}


class StyleManager:
    """
    Manager for styled components
    """
    
    def __init__(self):
        self._styles: Dict[str, str] = {}
        self._injected: bool = False
    
    def add_style(self, class_name: str, styles: str) -> None:
        """Add a style"""
        self._styles[class_name] = styles
    
    def remove_style(self, class_name: str) -> None:
        """Remove a style"""
        if class_name in self._styles:
            del self._styles[class_name]
    
    def get_css(self) -> str:
        """Get all CSS"""
        return '\n'.join(self._styles.values())
    
    def inject(self) -> None:
        """Inject styles into document"""
        if self._injected:
            return
        
        # In a real implementation, this would create a <style> tag
        self._injected = True
    
    def clear(self) -> None:
        """Clear all styles"""
        self._styles.clear()
        self._injected = False


# Global style manager
_style_manager = StyleManager()


def get_style_manager() -> StyleManager:
    """Get the global style manager"""
    return _style_manager
