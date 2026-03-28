# 🐍 PyReact - Framework Web Declarativo para Python

[![PyPI version](https://badge.fury.io/py/pyreact.svg)](https://badge.fury.io/py/pyreact)
[![Python](https://img.shields.io/pypi/pyversions/pyreact.svg)](https://pypi.org/project/pyreact/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

PyReact é um framework web declarativo inspirado no React, mas construído nativamente para Python. O objetivo é permitir que desenvolvedores Python criem interfaces de usuário reativas, componentizadas e modernas, sem precisar aprender JavaScript/TypeScript.

## 📋 Visão Geral

### Princípios Fundamentais

1. **Declaratividade** - A UI é uma função do estado: `UI = f(state)`
2. **Componentização** - Tudo é um componente
3. **Reatividade** - Mudanças de estado disparam re-renderizações automáticas
4. **Isomorfismo** - Suporte a Server-Side Rendering (SSR)

## 🚀 Quick Start

### Instalação

```bash
pip install pyreact
```

### Exemplo Básico

```python
from pyreact import h, render, use_state

def Counter(props):
    """Componente contador com hooks"""
    count, set_count = use_state(0)
    
    return h('div', {'className': 'counter'},
        h('h1', None, f"Contagem: {count}"),
        h('button', {'onClick': lambda _: set_count(count + 1)}, '+'),
        h('button', {'onClick': lambda _: set_count(count - 1)}, '-')
    )

# Renderizar
render(h(Counter, None), document.getElementById('root'))
```

## 📦 Sistema de Componentes

### Componente Funcional

```python
from pyreact import h

def Welcome(props):
    """Componente funcional simples"""
    return h('div', {'className': 'welcome'},
        h('h1', None, f"Olá, {props['name']}!"),
        h('p', None, props.get('message', 'Bem-vindo!'))
    )
```

### Componente com Estado

```python
from pyreact import Component, h

class Counter(Component):
    def __init__(self, props):
        super().__init__(props)
        self.state = {'count': 0}
    
    def increment(self, event):
        self.set_state({'count': self.state['count'] + 1})
    
    def render(self):
        return h('div', {'className': 'counter'},
            h('span', None, f"Contagem: {self.state['count']}"),
            h('button', {'onClick': self.increment}, '+1')
        )
```

## 🪝 Hooks

### useState

```python
def Timer(props):
    seconds, set_seconds = use_state(0)
    
    @use_effect([])
    def setup_timer():
        def tick():
            set_seconds(lambda s: s + 1)
        interval_id = setInterval(tick, 1000)
        return lambda: clearInterval(interval_id)
    
    return h('div', None, f"Segundos: {seconds}")
```

### useEffect

```python
def UserProfile(props):
    user, set_user = use_state(None)
    loading, set_loading = use_state(True)
    
    @use_effect([props['user_id']])
    def fetch_user():
        async def load():
            data = await fetch(f"/api/users/{props['user_id']}")
            set_user(await data.json())
            set_loading(False)
        load()
    
    if loading:
        return h('div', None, 'Carregando...')
    
    return h('div', None, user['name'])
```

### useContext

```python
# Criar contexto
ThemeContext = create_context('light')

def App():
    return h(ThemeContext.Provider, {'value': 'dark'},
        h(Toolbar, None)
    )

def Toolbar():
    theme = use_context(ThemeContext)
    return h('div', {'className': f"toolbar-{theme}"}, '...')
```

### useReducer

```python
def reducer(state, action):
    if action['type'] == 'INCREMENT':
        return {'count': state['count'] + 1}
    elif action['type'] == 'DECREMENT':
        return {'count': state['count'] - 1}
    return state

def Counter(props):
    state, dispatch = use_reducer(reducer, {'count': 0})
    
    return h('div', None,
        h('span', None, f"Count: {state['count']}"),
        h('button', {'onClick': lambda _: dispatch({'type': 'INCREMENT'})}, '+'),
        h('button', {'onClick': lambda _: dispatch({'type': 'DECREMENT'})}, '-')
    )
```

## 🎨 Sistema de Estilos

### CSS-in-Python

```python
from pyreact import styled

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

# Uso
h(Button, {'onClick': handle_click}, 'Clique aqui')
```

### CSS Modules

```python
from pyreact import h, css_module

styles = css_module('./Card.module.css')

def Card(props):
    return h('div', {'className': styles['card']},
        h('h2', {'className': styles['title']}, props['title']),
        props['children']
    )
```

## 🌐 Server-Side Rendering

```python
from pyreact import render_to_string, hydrate

# No servidor
html = render_to_string(h(App, None))

# No cliente (hydration)
hydrate(h(App, None), document.getElementById('root'))
```

## 🧪 Testes

```python
from pyreact.testing import render, screen, fireEvent

def test_counter():
    # Renderizar
    result = render(h(Counter, None))
    
    # Encontrar elementos
    button = result.get_by_text('+1')
    count = result.get_by_text('Count: 0')
    
    # Simular evento
    fireEvent.click(button)
    
    # Verificar
    assert result.get_by_text('Count: 1')
```

## 📁 Estrutura de Arquivos

```
meu_projeto_pyreact/
├── src/
│   ├── components/
│   │   ├── Button.py
│   │   └── Input.py
│   ├── hooks/
│   │   └── use_auth.py
│   ├── pages/
│   │   ├── Home.py
│   │   └── About.py
│   ├── styles/
│   │   └── global.css
│   ├── App.py
│   └── index.py
├── public/
│   └── index.html
├── tests/
│   └── test_components.py
├── pyproject.toml
└── README.md
```

## 🔧 CLI

```bash
# Criar novo projeto
pyreact create meu-app

# Iniciar servidor de desenvolvimento
pyreact dev

# Build para produção
pyreact build

# Rodar testes
pyreact test

# Gerar componente
pyreact generate component Button
```

## 📚 API Completa

### Core

- `h(type, props, *children)` - Criar elementos virtuais
- `Component` - Classe base para componentes com estado
- `PureComponent` - Componente com shallow comparison
- `render(element, container)` - Renderizar na DOM
- `hydrate(element, container)` - Hidratar HTML existente

### Hooks

- `use_state(initial)` - Estado local
- `use_reducer(reducer, init)` - Estado com reducer
- `use_effect(setup, deps)` - Efeitos colaterais
- `use_context(context)` - Consumir contexto
- `use_ref(initial)` - Referência mutável
- `use_memo(factory, deps)` - Memoização de valores
- `use_callback(callback, deps)` - Memoização de callbacks

### Context

- `create_context(default)` - Criar contexto

### Refs

- `create_ref()` - Criar referência
- `forward_ref(render)` - Encaminhar ref

### Portal

- `create_portal(children, container)` - Renderizar em container diferente

### Memo

- `memo(component)` - Memoizar componente
- `lazy(loader)` - Carregar componente sob demanda

### Server

- `render_to_string(element)` - Renderizar para HTML
- `render_to_static_markup(element)` - HTML sem data attributes

## 📖 Documentação

Para documentação completa, visite: https://pyreact.readthedocs.io

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, leia o guia de contribuição.

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

*Feito com ❤️ pela comunidade Python*
