"""
Attributes Module
=================

This module handles mapping between HTML attributes and DOM properties.
"""

from typing import Any, Dict, Optional


# HTML attributes that map to different DOM properties
PROPERTY_NAMES: Dict[str, str] = {
    'acceptCharset': 'accept-charset',
    'accessKey': 'accesskey',
    'allowFullScreen': 'allowfullscreen',
    'autoComplete': 'autocomplete',
    'autoFocus': 'autofocus',
    'autoPlay': 'autoplay',
    'cellPadding': 'cellpadding',
    'cellSpacing': 'cellspacing',
    'charSet': 'charset',
    'className': 'class',
    'colSpan': 'colspan',
    'contentEditable': 'contenteditable',
    'contextMenu': 'contextmenu',
    'crossOrigin': 'crossorigin',
    'dateTime': 'datetime',
    'encType': 'enctype',
    'formAction': 'formaction',
    'formEncType': 'formenctype',
    'formMethod': 'formmethod',
    'formNoValidate': 'formnovalidate',
    'formTarget': 'formtarget',
    'frameBorder': 'frameborder',
    'hrefLang': 'hreflang',
    'htmlFor': 'for',
    'httpEquiv': 'http-equiv',
    'isMap': 'ismap',
    'itemProp': 'itemprop',
    'itemScope': 'itemscope',
    'itemType': 'itemtype',
    'keyParams': 'keyparams',
    'keyType': 'keytype',
    'marginHeight': 'marginheight',
    'marginWidth': 'marginwidth',
    'maxLength': 'maxlength',
    'mediaGroup': 'mediagroup',
    'noValidate': 'novalidate',
    'playsInline': 'playsinline',
    'radioGroup': 'radiogroup',
    'readOnly': 'readonly',
    'rowSpan': 'rowspan',
    'spellCheck': 'spellcheck',
    'srcDoc': 'srcdoc',
    'srcLang': 'srclang',
    'srcSet': 'srcset',
    'tabIndex': 'tabindex',
    'useMap': 'usemap',
    'vocab': 'vocab',
}

# Reverse mapping
ATTRIBUTE_NAMES = {v: k for k, v in PROPERTY_NAMES.items()}

# Boolean attributes
BOOLEAN_ATTRIBUTES = {
    'allowfullscreen',
    'async',
    'autofocus',
    'autoplay',
    'checked',
    'controls',
    'default',
    'defer',
    'disabled',
    'formnovalidate',
    'hidden',
    'ismap',
    'itemscope',
    'loop',
    'multiple',
    'muted',
    'nomodule',
    'novalidate',
    'open',
    'playsinline',
    'readonly',
    'required',
    'reversed',
    'selected',
    'truespeed',
}

# Attributes that should be set as properties
PROPERTIES = {
    'value',
    'checked',
    'selected',
    'selectedIndex',
    'defaultValue',
    'defaultChecked',
}

# Attributes with units
UNITLESS_PROPERTIES = {
    'animationIterationCount',
    'borderImageOutset',
    'borderImageSlice',
    'borderImageWidth',
    'boxFlex',
    'boxFlexGroup',
    'boxOrdinalGroup',
    'columnCount',
    'columns',
    'flex',
    'flexGrow',
    'flexPositive',
    'flexShrink',
    'flexNegative',
    'flexOrder',
    'gridArea',
    'gridColumn',
    'gridColumnEnd',
    'gridColumnStart',
    'gridRow',
    'gridRowEnd',
    'gridRowStart',
    'lineClamp',
    'lineHeight',
    'opacity',
    'order',
    'orphans',
    'tabSize',
    'widows',
    'zIndex',
    'zoom',
    'fillOpacity',
    'floodOpacity',
    'stopOpacity',
    'strokeDasharray',
    'strokeDashoffset',
    'strokeMiterlimit',
    'strokeOpacity',
    'strokeWidth',
}


def is_custom_attribute(name: str) -> bool:
    """
    Check if an attribute is custom (data-*, aria-*)
    
    Args:
        name: Attribute name
    
    Returns:
        bool: True if custom attribute
    """
    return name.startswith('data-') or name.startswith('aria-')


def should_set_attribute(name: str, value: Any) -> bool:
    """
    Check if attribute should be set
    
    Args:
        name: Attribute name
        value: Attribute value
    
    Returns:
        bool: True if should set
    """
    # Skip null/undefined
    if value is None:
        return False
    
    # Skip event handlers (handled separately)
    if name.startswith('on'):
        return False
    
    # Skip style (handled separately)
    if name == 'style':
        return False
    
    # Skip ref and key
    if name in ('ref', 'key'):
        return False
    
    return True


def get_attribute_name(property_name: str) -> str:
    """
    Get HTML attribute name from DOM property name
    
    Args:
        property_name: DOM property name
    
    Returns:
        str: HTML attribute name
    """
    return PROPERTY_NAMES.get(property_name, property_name.lower())


def get_property_name(attribute_name: str) -> str:
    """
    Get DOM property name from HTML attribute name
    
    Args:
        attribute_name: HTML attribute name
    
    Returns:
        str: DOM property name
    """
    return ATTRIBUTE_NAMES.get(attribute_name, attribute_name)


def is_boolean_attribute(name: str) -> bool:
    """
    Check if attribute is boolean
    
    Args:
        name: Attribute name
    
    Returns:
        bool: True if boolean attribute
    """
    return name.lower() in BOOLEAN_ATTRIBUTES


def is_property(name: str) -> bool:
    """
    Check if attribute should be set as a property
    
    Args:
        name: Attribute name
    
    Returns:
        bool: True if should be property
    """
    return name in PROPERTIES


def get_style_value(name: str, value: Any) -> str:
    """
    Convert style value to string
    
    Args:
        name: CSS property name
        value: CSS value
    
    Returns:
        str: Style string
    """
    if value is None or value == '':
        return ''
    
    if isinstance(value, number):
        if name not in UNITLESS_PROPERTIES:
            return f"{value}px"
        return str(value)
    
    return str(value)


def escape_html_value(value: str) -> str:
    """
    Escape HTML special characters
    
    Args:
        value: Value to escape
    
    Returns:
        str: Escaped value
    """
    return (
        str(value)
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
        .replace("'", '&#x27;')
    )


def render_attributes(props: Dict[str, Any]) -> str:
    """
    Render attributes as HTML string
    
    Args:
        props: Props dictionary
    
    Returns:
        str: HTML attribute string
    """
    result = []
    
    for name, value in props.items():
        if not should_set_attribute(name, value):
            continue
        
        attr_name = get_attribute_name(name)
        
        if is_boolean_attribute(attr_name):
            if value:
                result.append(attr_name)
        else:
            escaped = escape_html_value(value)
            result.append(f'{attr_name}="{escaped}"')
    
    return ' '.join(result)


# Number type check (for Python 2/3 compatibility)
try:
    number = (int, float)
except NameError:
    number = (int, float)
