"""
CSS Module Module
=================

Support for CSS modules in PyReact.
"""

from typing import Any, Dict, Optional
import re
import os


def css_module(file_path: str) -> Dict[str, str]:
    """
    Load a CSS module
    
    Args:
        file_path: Path to CSS module file
    
    Returns:
        dict: Mapping of local class names to unique class names
    
    Example:
        # Card.module.css
        # .card { padding: 16px; }
        # .title { font-size: 24px; }
        
        styles = css_module('./Card.module.css')
        
        h('div', {'className': styles['card']},
            h('h2', {'className': styles['title']}, 'Title')
        )
    """
    # Generate unique prefix for this module
    module_id = _generate_module_id(file_path)
    
    # Parse CSS file
    css_content = _read_css_file(file_path)
    
    # Extract class names and transform
    class_map = {}
    processed_css = []
    
    for line in css_content.split('\n'):
        # Find class definitions
        match = re.match(r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)\s*\{', line)
        if match:
            local_name = match.group(1)
            unique_name = f"{module_id}__{local_name}"
            class_map[local_name] = unique_name
            processed_css.append(line.replace(f'.{local_name}', f'.{unique_name}'))
        else:
            processed_css.append(line)
    
    # Register processed CSS
    _register_module_css(module_id, '\n'.join(processed_css))
    
    return class_map


def load_css(file_path: str) -> str:
    """
    Load a regular CSS file
    
    Args:
        file_path: Path to CSS file
    
    Returns:
        str: CSS content
    
    Example:
        load_css('./styles/global.css')
    """
    css_content = _read_css_file(file_path)
    _register_global_css(css_content)
    return css_content


def get_class_name(module: Dict[str, str], class_name: str) -> str:
    """
    Get unique class name from module
    
    Args:
        module: CSS module dict
        class_name: Local class name
    
    Returns:
        str: Unique class name
    """
    return module.get(class_name, class_name)


def _generate_module_id(file_path: str) -> str:
    """Generate unique module ID"""
    import hashlib
    hash_obj = hashlib.md5(file_path.encode())
    return f"m{hash_obj.hexdigest()[:6]}"


def _read_css_file(file_path: str) -> str:
    """
    Read CSS file content
    
    Args:
        file_path: Path to CSS file
    
    Returns:
        str: CSS content
    """
    # In a real implementation, this would read from filesystem
    # For now, return empty string
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception:
        pass
    
    return ''


def _register_module_css(module_id: str, css: str) -> None:
    """
    Register module CSS
    
    Args:
        module_id: Module ID
        css: CSS content
    """
    _module_registry[module_id] = css


def _register_global_css(css: str) -> None:
    """
    Register global CSS
    
    Args:
        css: CSS content
    """
    _global_styles.append(css)


def get_all_module_css() -> str:
    """
    Get all module CSS
    
    Returns:
        str: All module CSS
    """
    return '\n\n'.join(_module_registry.values())


def get_all_global_css() -> str:
    """
    Get all global CSS
    
    Returns:
        str: All global CSS
    """
    return '\n\n'.join(_global_styles)


# Registries
_module_registry: Dict[str, str] = {}
_global_styles: list = []


class CSSModuleManager:
    """
    Manager for CSS modules
    """
    
    def __init__(self):
        self._modules: Dict[str, Dict[str, str]] = {}
        self._css_cache: Dict[str, str] = {}
    
    def load_module(self, file_path: str) -> Dict[str, str]:
        """
        Load a CSS module
        
        Args:
            file_path: Path to CSS module
        
        Returns:
            dict: Class name mapping
        """
        if file_path in self._modules:
            return self._modules[file_path]
        
        module = css_module(file_path)
        self._modules[file_path] = module
        return module
    
    def get_module(self, file_path: str) -> Optional[Dict[str, str]]:
        """
        Get a loaded module
        
        Args:
            file_path: Path to CSS module
        
        Returns:
            dict or None: Module class mapping
        """
        return self._modules.get(file_path)
    
    def get_all_css(self) -> str:
        """
        Get all CSS
        
        Returns:
            str: All CSS
        """
        module_css = get_all_module_css()
        global_css = get_all_global_css()
        return f"{global_css}\n\n{module_css}"
    
    def clear(self) -> None:
        """Clear all modules"""
        self._modules.clear()
        self._css_cache.clear()
        _module_registry.clear()
        _global_styles.clear()


# Global CSS module manager
_css_module_manager = CSSModuleManager()


def get_css_module_manager() -> CSSModuleManager:
    """Get the global CSS module manager"""
    return _css_module_manager
