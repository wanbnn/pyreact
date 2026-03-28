# 🐍 PyReact - Framework Web Declarativo para Python

## 📋 Visão Geral

PyReact é um framework web declarativo inspirado no React, mas construído nativamente para Python. O objetivo é permitir que desenvolvedores Python criem interfaces de usuário reativas, componentizadas e modernas, sem precisar aprender JavaScript/TypeScript.

---

## 🎯 Princípios Fundamentais

### 1. Declaratividade
- A UI é uma função do estado: `UI = f(state)`
- O desenvolvedor descreve **o que** quer renderizar, não **como** renderizar
- O framework gerencia o DOM virtual e aplica mudanças eficientemente

### 2. Componentização
- Tudo é um componente
- Componentes podem ser funcionais (funções puras) ou com estado (classes)
- Props fluem de pai para filho, eventos fluem de filho para pai
- Composição através de children

### 3. Reatividade
- Mudanças de estado disparam re-renderizações automáticas
- Detecção de mudanças eficiente (não usa dirty checking em tudo)
- Hooks para gerenciar ciclo de vida e estado em componentes funcionais

### 4. Isomorfismo (Opcional)
- Suporte a Server-Side Rendering (SSR)
- Hydration no cliente para interatividade
- SEO-friendly por padrão

---

## 🏗️ Arquitetura do Framework

```
pyreact/
├── core/
│   ├── __init__.py
│   ├── component.py          # Classe base Component
│   ├── element.py            # Elementos virtuais (vdom)
│   ├── renderer.py           # Renderizador DOM
│   ├── reconciler.py         # Algoritmo de reconciliação
│   ├── hooks.py              # Hooks (useState, useEffect, etc.)
│   ├── context.py            # API de Contexto
│   └── scheduler.py          # Scheduler de atualizações
├── dom/
│   ├── __init__.py
│   ├── dom_operations.py     # Operações DOM nativas
│   ├── events.py             # Sistema de eventos sintéticos
│   └── attributes.py         # Mapeamento de atributos
├── server/
│   ├── __init__.py
│   ├── ssr.py                # Server-side rendering
│   └── hydration.py          # Hydration client-side
├── utils/
│   ├── __init__.py
│   ├── diff.py               # Algoritmo de diff
│   └── object_pool.py        # Pool de objetos para performance
├── devtools/
│   ├── __init__.py
│   ├── debugger.py           # Ferramentas de debug
│   └── profiler.py           # Profiler de performance
└── __init__.py
```

---

## 📦 Sistema de Componentes

### Componente Funcional (Stateless)

```python
from pyreact import h, Component

def Welcome(props):
    """Componente funcional simples"""
    return h('div', {'className': 'welcome'},
        h('h1', None, f"Olá, {props['name']}!"),
        h('p', None, props.get('message', 'Bem-vindo!'))
    )
```

### Componente com Estado (Stateful)

```python
from pyreact import Component

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

### Componente com Hooks (Recomendado)

```python
from pyreact import h, use_state, use_effect

def Timer(props):
    # Hooks para estado
    seconds, set_seconds = use_state(0)
    is_running, set_is_running = use_state(True)
    
    # Hook para efeitos (similar a useEffect)
    @use_effect([])
    def setup_timer():
        def tick():
            if is_running:
                set_seconds(lambda s: s + 1)
        
        interval_id = setInterval(tick, 1000)
        return lambda: clearInterval(interval_id)  # Cleanup
    
    return h('div', None,
        h('p', None, f"Segundos: {seconds}"),
        h('button', {'onClick': lambda _: set_is_running(not is_running)},
            "Pausar/Retomar" if is_running else "Retomar")
    )
```

---

## 🌳 Virtual DOM (VDOM)

### Estrutura do VNode

```python
class VNode:
    """
    Nó do Virtual DOM
    
    Atributos:
        type: str | callable - Tipo do elemento ('div', 'span', Component)
        props: dict - Propriedades/atributos do elemento
        children: list[VNode | str] - Filhos do elemento
        key: str | int | None - Chave para reconciliação de listas
        ref: Ref | None - Referência ao nó DOM real
    """
    def __init__(self, type, props=None, children=None, key=None, ref=None):
        self.type = type
        self.props = props or {}
        self.children = children or []
        self.key = key
        self.ref = ref
        self._dom_node = None
        self._parent = None
```

### Função `h()` (createElement)

```python
def h(type, props=None, *children):
    """
    Função para criar elementos virtuais (hyperscript)
    
    Args:
        type: Tag HTML ('div', 'span') ou Componente (Counter, App)
        props: Dicionário de propriedades/atributos
        *children: Filhos (strings, VNodes, ou listas)
    
    Returns:
        VNode: Nó virtual
    
    Exemplos:
        h('div', {'id': 'app'}, 'Hello')
        h('div', None, h('span', None, 'text'))
        h(List, {'items': [1,2,3]})
    """
    # Flatten children
    flat_children = []
    for child in children:
        if isinstance(child, list):
            flat_children.extend(child)
        elif child is not None:
            flat_children.append(child)
    
    # Extrair key e ref de props
    key = props.pop('key', None) if props else None
    ref = props.pop('ref', None) if props else None
    
    return VNode(type, props, flat_children, key, ref)
```

---

## 🔄 Algoritmo de Reconciliação

### Diff Algorithm (Virtual DOM Diff)

O algoritmo de diff segue os princípios do React:

1. **Elementos de tipos diferentes** → Substitui completamente a árvore
2. **Elementos do mesmo tipo** → Atualiza apenas atributos/props
3. **Filhos com keys** → Reordena/move ao invés de recriar
4. **Componentes** → Compara props e decide se re-renderiza

```python
class Reconciler:
    def diff(self, old_vnode, new_vnode, parent_dom, index=0):
        """
        Compara dois VNodes e aplica mudanças ao DOM real
        
        Returns:
            VNode: O novo VNode (pode ser reutilizado ou novo)
        """
        # Caso 1: Novo nó é None → remover
        if new_vnode is None:
            if old_vnode:
                self.remove_node(parent_dom, index)
            return None
        
        # Caso 2: Nó antigo é None → criar
        if old_vnode is None:
            new_dom = self.create_dom(new_vnode)
            self.insert_node(parent_dom, new_dom, index)
            return new_vnode
        
        # Caso 3: Tipos diferentes → substituir
        if old_vnode.type != new_vnode.type:
            new_dom = self.create_dom(new_vnode)
            self.replace_node(parent_dom, new_dom, index)
            return new_vnode
        
        # Caso 4: Mesmo tipo → atualizar
        if self.is_component(old_vnode):
            return self.update_component(old_vnode, new_vnode)
        else:
            return self.update_dom_element(old_vnode, new_vnode)
```

### Keyed Children (Reconciliação de Listas)

```python
def reconcile_children(self, old_children, new_children, parent_dom):
    """
    Reconcilia filhos usando keys para minimizar operações DOM
    """
    # Criar mapa de keys dos filhos antigos
    old_keyed = {child.key: (i, child) for i, child in enumerate(old_children) if child.key}
    
    # Processar novos filhos
    for new_index, new_child in enumerate(new_children):
        if new_child.key and new_child.key in old_keyed:
            # Mover filho existente
            old_index, old_child = old_keyed[new_child.key]
            self.move_if_needed(parent_dom, old_index, new_index)
            self.diff(old_child, new_child, parent_dom, new_index)
        else:
            # Criar novo filho
            self.create_and_insert(parent_dom, new_child, new_index)
    
    # Remover filhos que não existem mais
    self.remove_orphans(old_children, new_children, parent_dom)
```

---

## 🪝 Sistema de Hooks

### Regras dos Hooks

1. **Apenas no topo do componente** - Não dentro de loops, condicionais ou funções aninhadas
2. **Apenas em componentes funcionais** - Não em classes ou funções comuns
3. **Ordem preservada** - Hooks são identificados pela ordem de chamada

### Hook Index Stack

```python
# Contexto global para hooks
_current_component = None
_hook_index = 0

def use_state(initial_value):
    """
    Hook de estado
    
    Returns:
        tuple: (valor_atual, função_setter)
    """
    global _hook_index
    
    component = _current_component
    hook_index = _hook_index
    
    # Inicializar se não existe
    if hook_index >= len(component._hooks):
        component._hooks.append({
            'value': initial_value() if callable(initial_value) else initial_value,
            'dispatch': lambda action: component._dispatch_state(hook_index, action)
        })
    
    _hook_index += 1
    
    hook = component._hooks[hook_index]
    return hook['value'], hook['dispatch']
```

### Lista de Hooks Principais

```python
# Estado e Reducer
use_state(initial)           # Estado local simples
use_reducer(reducer, init)   # Estado com reducer (Redux-like)

# Efeitos
use_effect(setup, deps)      # Efeitos com cleanup
use_layout_effect(setup, deps)  # Efeitos síncronos antes do paint

# Contexto
use_context(context)         # Consumir contexto

# Refs
use_ref(initial)             # Referência mutável sem re-render

# Memoização
use_memo(factory, deps)      # Memoização de valores
use_callback(callback, deps) # Memoização de callbacks

# Outros
use_imperative_handle(ref, create, deps)  # Expor métodos ao pai
use_debug_value(value, formatter)  # Debug no DevTools
use_id()                     # ID único para acessibilidade
use_transition()             # Transições não-bloqueantes
use_deferred_value(value)    # Valor deferido para performance
```

### Implementação do use_effect

```python
def use_effect(setup, dependencies=None):
    """
    Hook para efeitos colaterais
    
    Args:
        setup: Função que retorna cleanup ou None
        dependencies: Lista de valores para comparar
    
    Exemplo:
        @use_effect([user_id])
        def setup_subscription():
            subscribe(user_id)
            return lambda: unsubscribe(user_id)
    """
    global _hook_index
    
    component = _current_component
    hook_index = _hook_index
    
    # Inicializar hook
    if hook_index >= len(component._hooks):
        component._hooks.append({
            'setup': None,
            'cleanup': None,
            'deps': None
        })
    
    hook = component._hooks[hook_index]
    _hook_index += 1
    
    # Verificar se deps mudaram
    deps_changed = (
        hook['deps'] is None or
        dependencies is None or
        any(a != b for a, b in zip(hook['deps'], dependencies))
    )
    
    if deps_changed:
        # Executar cleanup anterior
        if hook['cleanup']:
            hook['cleanup']()
        
        # Executar novo setup
        hook['cleanup'] = setup()
        hook['deps'] = dependencies
    
    # Agendar cleanup para quando componente desmontar
    component._add_cleanup(hook_index, hook['cleanup'])
```

---

## 🎨 Sistema de Estilos

### CSS-in-Python (Estilos Inline)

```python
from pyreact import h, styled

# Estilos inline com objetos Python
def Card(props):
    return h('div', {
        'style': {
            'backgroundColor': '#fff',
            'borderRadius': '8px',
            'padding': '16px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        }
    }, props['children'])
```

### Styled Components (CSS-in-Python)

```python
from pyreact import styled

# Criar componente estilizado
Button = styled('button', '''
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 14px;
    cursor: pointer;
    transition: background-color 0.2s;
    
    &:hover {
        background-color: #0056b3;
    }
    
    &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
''')

# Uso
h(Button, {'onClick': handle_click}, 'Clique aqui')
```

### CSS Modules (Arquivos .css)

```python
from pyreact import h
from pyreact.styles import css_module

# Importar CSS Module
styles = css_module('./Card.module.css')

def Card(props):
    return h('div', {'className': styles['card']},
        h('h2', {'className': styles['title']}, props['title']),
        props['children']
    )
```

---

## 📡 Sistema de Eventos

### Eventos Sintéticos

```python
class SyntheticEvent:
    """
    Evento sintético cross-browser
    
    Atributos:
        type: str - Tipo do evento ('click', 'change', etc.)
        target: Element - Elemento que disparou o evento
        currentTarget: Element - Elemento atual no bubbling
        nativeEvent: Event - Evento DOM nativo
    """
    
    def __init__(self, native_event):
        self.native_event = native_event
        self.type = native_event.type
        self.target = native_event.target
        self.currentTarget = native_event.currentTarget
        self._propagation_stopped = False
        self._default_prevented = False
    
    def stop_propagation(self):
        """Para a propagação do evento (bubbling)"""
        self._propagation_stopped = True
        self.native_event.stopPropagation()
    
    def prevent_default(self):
        """Previne a ação padrão do navegador"""
        self._default_prevented = True
        self.native_event.preventDefault()
    
    def persist(self):
        """Persiste o evento para uso assíncrono"""
        # Em PyReact, eventos são persistentes por padrão
        pass
```

### Mapeamento de Eventos

```python
# Eventos suportados
EVENT_TYPES = {
    # Clipboard
    'onCopy', 'onCut', 'onPaste',
    
    # Keyboard
    'onKeyDown', 'onKeyPress', 'onKeyUp',
    
    # Focus
    'onFocus', 'onBlur',
    
    # Form
    'onChange', 'onInput', 'onSubmit', 'onReset',
    
    # Mouse
    'onClick', 'onDoubleClick', 'onMouseDown', 'onMouseUp',
    'onMouseEnter', 'onMouseLeave', 'onMouseMove', 'onMouseOut', 'onMouseOver',
    
    # Touch
    'onTouchStart', 'onTouchMove', 'onTouchEnd', 'onTouchCancel',
    
    # UI
    'onScroll', 'onResize',
    
    # Drag
    'onDrag', 'onDragEnd', 'onDragEnter', 'onDragExit', 'onDragLeave',
    'onDragOver', 'onDragStart', 'onDrop',
    
    # Animation
    'onAnimationStart', 'onAnimationEnd', 'onAnimationIteration',
    
    # Transition
    'onTransitionEnd',
}

def add_event_listener(dom_node, event_name, handler):
    """
    Adiciona event listener com delegação
    
    Args:
        dom_node: Nó DOM real
        event_name: Nome do evento ('onClick')
        handler: Função handler
    """
    # Converter onClick -> click
    native_event = event_name[2:].lower()
    
    # Criar wrapper com evento sintético
    def wrapper(native_event):
        synthetic = SyntheticEvent(native_event)
        handler(synthetic)
    
    dom_node.addEventListener(native_event, wrapper)
    return wrapper
```

---

## 🔄 Gerenciamento de Estado

### Estado Local (Component State)

```python
class Component:
    def __init__(self, props):
        self.props = props
        self.state = {}
        self._pending_state = None
        self._is_mounted = False
    
    def set_state(self, new_state, callback=None):
        """
        Atualiza o estado do componente
        
        Args:
            new_state: dict ou callable que retorna dict
            callback: Função chamada após atualização
        """
        if callable(new_state):
            new_state = new_state(self.state)
        
        self._pending_state = {**self.state, **new_state}
        
        # Agendar atualização
        schedule_update(self)
        
        if callback:
            self._callbacks.append(callback)
    
    def _apply_state(self):
        """Aplica estado pendente"""
        if self._pending_state:
            self.state = self._pending_state
            self._pending_state = None
            return True
        return False
```

### Context API (Estado Global)

```python
def create_context(default_value=None):
    """
    Cria um contexto para compartilhar estado
    
    Returns:
        tuple: (Provider, Consumer, Context)
    """
    context_id = generate_id()
    
    class Provider(Component):
        def __init__(self, props):
            super().__init__(props)
            self.value = props['value']
        
        def render(self):
            # Registrar no contexto
            context_registry[context_id] = self.value
            return self.props['children']
    
    def use_context_value():
        return context_registry.get(context_id, default_value)
    
    return Provider, use_context_value, context_id

# Uso
ThemeContext = create_context('light')

def App():
    return h(ThemeContext.Provider, {'value': 'dark'},
        h(Toolbar, None)
    )

def Toolbar():
    theme = use_context(ThemeContext)
    return h('div', {'className': f'toolbar-{theme}'}, '...')
```

### useReducer (Redux-like)

```python
def use_reducer(reducer, initial_state, init=None):
    """
    Hook para estado complexo com reducer
    
    Args:
        reducer: função(state, action) -> new_state
        initial_state: estado inicial
        init: função para inicialização lazy
    
    Returns:
        tuple: (state, dispatch)
    """
    initial = init(initial_state) if init else initial_state
    
    def dispatch(action):
        def update_state(prev_state):
            return reducer(prev_state, action)
        
        set_state(update_state)
    
    state, set_state = use_state(initial)
    return state, dispatch

# Exemplo
def reducer(state, action):
    if action['type'] == 'INCREMENT':
        return {'count': state['count'] + 1}
    elif action['type'] == 'DECREMENT':
        return {'count': state['count'] - 1}
    return state

def Counter():
    state, dispatch = use_reducer(reducer, {'count': 0})
    
    return h('div', None,
        h('span', None, f"Count: {state['count']}"),
        h('button', {'onClick': lambda _: dispatch({'type': 'INCREMENT'})}, '+'),
        h('button', {'onClick': lambda _: dispatch({'type': 'DECREMENT'})}, '-'),
    )
```

---

## 🚀 Renderização

### Renderização no Cliente (CSR)

```python
def render(element, container):
    """
    Renderiza um elemento PyReact em um container DOM
    
    Args:
        element: VNode ou Component
        container: Elemento DOM raiz
    
    Exemplo:
        render(h(App, None), document.getElementById('root'))
    """
    # Limpar container se necessário
    while container.firstChild:
        container.removeChild(container.firstChild)
    
    # Criar fiber root
    root = create_root(container)
    
    # Agendar renderização inicial
    schedule_root_update(root, element)
    
    return root
```

### Renderização no Servidor (SSR)

```python
def render_to_string(element):
    """
    Renderiza elemento como string HTML
    
    Args:
        element: VNode ou Component
    
    Returns:
        str: HTML string
    """
    def render_node(node):
        if isinstance(node, str):
            return escape_html(node)
        
        if callable(node.type):
            # É um componente
            component = node.type(node.props)
            return render_node(component.render())
        
        # É um elemento HTML
        tag = node.type
        attrs = render_attrs(node.props)
        children = ''.join(render_node(child) for child in node.children)
        
        if tag in VOID_ELEMENTS:
            return f'<{tag}{attrs} />'
        else:
            return f'<{tag}{attrs}>{children}</{tag}>'
    
    return render_node(element)

def render_to_static_markup(element):
    """
    Renderiza sem data attributes (para emails, etc.)
    """
    # Similar a render_to_string mas sem data-reactid, etc.
    pass
```

### Hydration

```python
def hydrate(element, container):
    """
    Anexa event listeners ao HTML existente
    
    Args:
        element: VNode esperado
        container: Elemento DOM com HTML do servidor
    """
    # Percorrer DOM existente e anexar listeners
    # Verificar se HTML corresponde ao esperado
    # Avisar sobre mismatch em desenvolvimento
    
    root = create_root(container, {'hydrate': True})
    schedule_root_update(root, element)
    return root
```

---

## ⚡ Scheduler e Prioridades

### Scheduler de Atualizações

```python
class Scheduler:
    """
    Gerencia atualizações com prioridades
    
    Prioridades (maior = mais urgente):
        - IMMEDIATE: 99 - Executa imediatamente
        - USER_BLOCKING: 98 - Interações de usuário
        - NORMAL: 97 - Atualizações normais
        - LOW: 96 - Preloading, etc.
        - IDLE: 95 - Tarefas de fundo
    """
    
    IMMEDIATE_PRIORITY = 99
    USER_BLOCKING_PRIORITY = 98
    NORMAL_PRIORITY = 97
    LOW_PRIORITY = 96
    IDLE_PRIORITY = 95
    
    def __init__(self):
        self._queue = []
        self._scheduled = False
    
    def schedule_callback(self, callback, priority=NORMAL_PRIORITY):
        """Agenda callback com prioridade"""
        task = {
            'callback': callback,
            'priority': priority,
            'expirationTime': current_time() + timeout_for_priority(priority)
        }
        
        # Inserir ordenado por prioridade
        insert_sorted(self._queue, task)
        self._ensure_scheduled()
    
    def _ensure_scheduled(self):
        """Garante que o loop está agendado"""
        if not self._scheduled:
            self._scheduled = True
            request_idle_callback(self._work_loop)
    
    def _work_loop(self, deadline):
        """Processa tarefas até deadline"""
        while self._queue and not deadline.did_timeout:
            task = self._queue.pop(0)
            task['callback']()
        
        self._scheduled = False
        if self._queue:
            self._ensure_scheduled()
```

### Fiber Architecture

```python
class Fiber:
    """
    Unidade de trabalho no algoritmo de reconciliação
    
    Permite pausar, retomar e abortar renderização
    """
    
    def __init__(self, type, props=None):
        self.type = type
        self.props = props or {}
        self.state_node = None  # DOM node ou instância do componente
        
        # Árvore de fibers
        self.return_fiber = None  # Pai
        self.child = None         # Primeiro filho
        self.sibling = None       # Próximo irmão
        
        # Lista de efeitos
        self.effect_tag = None  # 'PLACEMENT', 'UPDATE', 'DELETION'
        self.alternate = None   # Fiber da renderização anterior
        
        # Hooks (para componentes funcionais)
        self.hook_list = []
        self.hook_index = 0
```

---

## 🔧 Ciclo de Vida

### Métodos de Ciclo de Vida (Componentes de Classe)

```python
class Component:
    # Montagem
    def component_will_mount(self):
        """Chamado antes de montar (deprecated)"""
        pass
    
    def component_did_mount(self):
        """Chamado após montar no DOM"""
        pass
    
    # Atualização
    def component_will_receive_props(self, next_props):
        """Chamado quando props mudam (deprecated)"""
        pass
    
    def should_component_update(self, next_props, next_state):
        """Retorna False para prevenir re-render"""
        return True
    
    def component_will_update(self, next_props, next_state):
        """Chamado antes de atualizar (deprecated)"""
        pass
    
    def component_did_update(self, prev_props, prev_state):
        """Chamado após atualizar"""
        pass
    
    # Desmontagem
    def component_will_unmount(self):
        """Chamado antes de desmontar"""
        pass
    
    # Error Handling
    def component_did_catch(self, error, info):
        """Captura erros de filhos"""
        pass
```

### Equivalente com Hooks

```python
# Montagem + Desmontagem
@use_effect([])
def mount():
    print("Montado!")
    return lambda: print("Desmontado!")

# Atualização
@use_effect([count])
def update():
    print(f"Count mudou para {count}")

# Cleanup antes de cada atualização
@use_effect([resource_id])
def subscribe():
    subscription = subscribe_to(resource_id)
    return lambda: subscription.unsubscribe()
```

---

## 🎭 Error Boundaries

```python
class ErrorBoundary(Component):
    """
    Captura erros em componentes filhos
    """
    
    def __init__(self, props):
        super().__init__(props)
        self.state = {'has_error': False, 'error': None}
    
    @staticmethod
    def get_derived_state_from_error(error):
        """Atualiza estado quando há erro"""
        return {'has_error': True, 'error': error}
    
    def component_did_catch(self, error, info):
        """Log do erro"""
        log_error(error, info)
    
    def render(self):
        if self.state['has_error']:
            return self.props.get('fallback', h('h1', None, 'Algo deu errado!'))
        
        return self.props['children']

# Uso
h(ErrorBoundary, {'fallback': h('div', None, 'Erro!')},
    h(RiskyComponent, None)
)
```

---

## 📦 Portals

```python
def create_portal(child, container):
    """
    Renderiza filho em um nó DOM diferente
    
    Args:
        child: VNode para renderizar
        container: Elemento DOM destino
    
    Returns:
        Portal: Objeto portal
    
    Exemplo:
        create_portal(
            h(Modal, None),
            document.getElementById('modal-root')
        )
    """
    return Portal(child, container)

# Uso - Modal
def Modal(props):
    return create_portal(
        h('div', {'className': 'modal-overlay'},
            h('div', {'className': 'modal-content'},
                props['children']
            )
        ),
        document.body
    )
```

---

## 🔗 Refs

### createRef

```python
class Ref:
    """Referência a um elemento DOM ou componente"""
    def __init__(self):
        self.current = None

def create_ref():
    return Ref()

# Uso em componente de classe
class TextInput(Component):
    def __init__(self, props):
        super().__init__(props)
        self.input_ref = create_ref()
    
    def focus(self):
        self.input_ref.current.focus()
    
    def render(self):
        return h('input', {'ref': self.input_ref, 'type': 'text'})
```

### useRef Hook

```python
def use_ref(initial_value=None):
    """
    Hook para referência mutável
    
    Diferente de useState, mudar ref.current NÃO causa re-render
    """
    global _hook_index
    
    component = _current_component
    hook_index = _hook_index
    
    if hook_index >= len(component._hooks):
        ref = Ref()
        ref.current = initial_value
        component._hooks.append(ref)
    
    _hook_index += 1
    return component._hooks[hook_index]
```

### forwardRef

```python
def forward_ref(render):
    """
    Permite que componente funcional receba ref
    
    Args:
        render: função(props, ref) -> VNode
    
    Exemplo:
        @forward_ref
        def FancyInput(props, ref):
            return h('input', {
                'ref': ref,
                'className': 'fancy-input',
                **props
            })
    """
    def wrapper(props):
        ref = props.pop('ref', None)
        return render(props, ref)
    
    wrapper._forward_ref = True
    return wrapper
```

### useImperativeHandle

```python
def use_imperative_handle(ref, create_handle, deps=None):
    """
    Customiza o valor exposto pelo ref
    
    Args:
        ref: Ref passado pelo pai
        create_handle: função que retorna objeto a expor
        deps: Dependências para recriar
    """
    def effect():
        if ref:
            ref.current = create_handle()
        return lambda: None
    
    use_effect(effect, deps)
```

---

## 🧪 Testes

### Test Renderer

```python
from pyreact.testing import render, screen, fireEvent

def test_counter():
    # Renderizar componente
    render(h(Counter, None))
    
    # Encontrar elementos
    button = screen.get_by_text('+1')
    count = screen.get_by_text('Contagem: 0')
    
    # Simular evento
    fireEvent.click(button)
    
    # Verificar resultado
    assert count.text == 'Contagem: 1'
```

### Snapshot Testing

```python
from pyreact.testing import render_to_json

def test_button_snapshot():
    tree = render_to_json(h(Button, {'variant': 'primary'}, 'Click me'))
    
    assert tree == {
        'type': 'button',
        'props': {'className': 'btn btn-primary'},
        'children': ['Click me']
    }
```

---

## 🛠️ DevTools

### Integração com DevTools

```python
# O framework deve expor hooks para DevTools

__REACT_DEVTOOLS_GLOBAL_HOOK__ = {
    'renderers': {},
    'supportsFiber': True,
    'inject': lambda renderer: ...,
    'onCommitFiberRoot': lambda: ...,
    'onCommitFiberUnmount': lambda: ...,
}
```

### DevTools Protocol

```python
class DevToolsHook:
    def __init__(self):
        self._renderer_id = None
        self._hook = None
    
    def inject(self, renderer):
        """Registra renderer no DevTools"""
        self._renderer_id = len(self._hook['renderers'])
        self._hook['renderers'][self._renderer_id] = renderer
    
    def on_commit_root(self, root):
        """Notifica DevTools sobre commit"""
        if self._hook:
            self._hook['onCommitFiberRoot'](self._renderer_id, root)
    
    def on_commit_unmount(self, fiber):
        """Notifica DevTools sobre unmount"""
        if self._hook:
            self._hook['onCommitFiberUnmount'](self._renderer_id, fiber)
```

---

## 📁 Estrutura de Arquivos Recomendada

```
meu_projeto_pyreact/
├── src/
│   ├── components/
│   │   ├── __init__.py
│   │   ├── Button.py
│   │   ├── Input.py
│   │   ├── Modal.py
│   │   └── Layout.py
│   ├── hooks/
│   │   ├── __init__.py
│   │   ├── use_auth.py
│   │   └── use_api.py
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── Home.py
│   │   └── About.py
│   ├── styles/
│   │   ├── global.css
│   │   └── variables.css
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py
│   ├── App.py
│   └── index.py
├── public/
│   └── index.html
├── tests/
│   ├── __init__.py
│   ├── test_components.py
│   └── test_hooks.py
├── pyproject.toml
└── README.md
```

---

## 🚀 CLI e Build

### Comandos CLI

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

# Gerar hook
pyreact generate hook useAuth
```

### Configuração (pyproject.toml)

```toml
[tool.pyreact]
# Entrada principal
entry = "src/index.py"
# Diretório de saída
output = "dist"
# Servidor de desenvolvimento
dev_port = 3000
# SSR
ssr = true
# CSS Modules
css_modules = true
# Source maps
source_maps = true
```

---

## 🔒 Segurança

### Sanitização de HTML

```python
def escape_html(text):
    """Escapa caracteres HTML perigosos"""
    return (text
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
        .replace("'", '&#x27;'))

def dangerously_set_inner_html(html):
    """
    Permite HTML raw (usar com cuidado!)
    
    Args:
        html: dict com chave '__html'
    
    Exemplo:
        h('div', {
            'dangerouslySetInnerHTML': {'__html': '<span>Raw HTML</span>'}
        })
    """
    if '__html' not in html:
        raise ValueError('dangerouslySetInnerHTML requer {__html: "..."}')
    return html['__html']
```

### Validação de Props

```python
def validate_props(component_name, props, propTypes):
    """
    Valida props em desenvolvimento
    
    Args:
        component_name: Nome do componente
        props: Props recebidas
        propTypes: Definição de tipos esperados
    """
    if not IS_PRODUCTION:
        for prop_name, validator in propTypes.items():
            error = validator(props, prop_name, component_name)
            if error:
                console.warn(error)

# Uso
def Button(props):
    validate_props('Button', props, {
        'onClick': PropTypes.function,
        'disabled': PropTypes.boolean,
        'children': PropTypes.node,
    })
    # ...
```

---

## 📊 Performance

### Memoização

```python
def memo(component, are_props_equal=None):
    """
    Memoiza componente (similar a React.memo)
    
    Args:
        component: Componente funcional
        are_props_equal: Função customizada de comparação
    
    Returns:
        Componente memoizado
    """
    def memoized(props):
        # Comparar com props anteriores
        if are_props_equal:
            if are_props_equal(memoized._prev_props, props):
                return memoized._prev_result
        
        result = component(props)
        memoized._prev_props = props
        memoized._prev_result = result
        return result
    
    memoized._prev_props = None
    memoized._prev_result = None
    return memoized
```

### useMemo e useCallback

```python
def use_memo(factory, deps):
    """
    Memoiza valor computado
    
    Args:
        factory: Função que cria o valor
        deps: Dependências
    """
    global _hook_index
    
    component = _current_component
    hook_index = _hook_index
    
    if hook_index >= len(component._hooks):
        component._hooks.append({
            'value': factory(),
            'deps': deps
        })
    
    hook = component._hooks[hook_index]
    _hook_index += 1
    
    # Verificar se deps mudaram
    if deps_changed(hook['deps'], deps):
        hook['value'] = factory()
        hook['deps'] = deps
    
    return hook['value']

def use_callback(callback, deps):
    """
    Memoiza callback
    
    Args:
        callback: Função
        deps: Dependências
    """
    return use_memo(lambda: callback, deps)
```

### Code Splitting

```python
def lazy(loader):
    """
    Carrega componente sob demanda
    
    Args:
        loader: Função async que retorna módulo
    
    Returns:
        Componente lazy
    """
    class LazyComponent(Component):
        def __init__(self, props):
            super().__init__(props)
            self.state = {'loaded': False, 'component': None, 'error': None}
        
        def component_did_mount(self):
            async def load():
                try:
                    module = await loader()
                    self.set_state({
                        'loaded': True,
                        'component': module.default
                    })
                except Exception as e:
                    self.set_state({'error': e})
            
            load()
        
        def render(self):
            if self.state['error']:
                return self.props.get('fallback', h('div', None, 'Erro ao carregar'))
            
            if not self.state['loaded']:
                return self.props.get('loading', h('div', None, 'Carregando...'))
            
            Component = self.state['component']
            return h(Component, self.props)
    
    return LazyComponent

# Uso
HeavyComponent = lazy(lambda: import_module('./HeavyComponent.py'))

h(Suspense, {'fallback': h('div', None, 'Carregando...')},
    h(HeavyComponent, None)
)
```

---

## 🌐 Integração com Backend

### Fetch de Dados

```python
def use_fetch(url, options=None):
    """
    Hook para fetch de dados
    
    Returns:
        dict: {data, loading, error, refetch}
    """
    data, set_data = use_state(None)
    loading, set_loading = use_state(True)
    error, set_error = use_state(None)
    
    @use_effect([url])
    def fetch_data():
        async def do_fetch():
            try:
                response = await fetch(url, options)
                json = await response.json()
                set_data(json)
                set_error(None)
            except Exception as e:
                set_error(e)
            finally:
                set_loading(False)
        
        do_fetch()
    
    def refetch():
        set_loading(True)
        # Re-trigger effect
    
    return {'data': data, 'loading': loading, 'error': error, 'refetch': refetch}

# Uso
def UserList():
    result = use_fetch('/api/users')
    
    if result['loading']:
        return h('div', None, 'Carregando...')
    
    if result['error']:
        return h('div', None, f"Erro: {result['error']}")
    
    return h('ul', None,
        [h('li', {'key': user['id']}, user['name']) for user in result['data']]
    )
```

---

## 📚 API Completa de Exportação

```python
# pyreact/__init__.py

# Core
from .core.component import Component
from .core.element import h, VNode, create_element
from .core.renderer import render, hydrate, create_root
from .core.reconciler import Reconciler

# Hooks
from .core.hooks import (
    use_state,
    use_reducer,
    use_effect,
    use_layout_effect,
    use_context,
    use_ref,
    use_memo,
    use_callback,
    use_imperative_handle,
    use_debug_value,
    use_id,
    use_transition,
    use_deferred_value,
)

# Context
from .core.context import create_context

# Refs
from .core.refs import create_ref, forward_ref

# Portals
from .core.portal import create_portal

# Memo
from .core.memo import memo, lazy

# Error Boundaries
from .core.error_boundary import ErrorBoundary

# Styles
from .styles import styled, css_module

# Server
from .server.ssr import render_to_string, render_to_static_markup

# Testing (apenas em ambiente de teste)
try:
    from .testing import render, screen, fireEvent
except ImportError:
    pass

__all__ = [
    # Core
    'Component', 'h', 'VNode', 'create_element', 'render', 'hydrate', 'create_root',
    
    # Hooks
    'use_state', 'use_reducer', 'use_effect', 'use_layout_effect',
    'use_context', 'use_ref', 'use_memo', 'use_callback',
    'use_imperative_handle', 'use_debug_value', 'use_id',
    'use_transition', 'use_deferred_value',
    
    # Context
    'create_context',
    
    # Refs
    'create_ref', 'forward_ref',
    
    # Portals
    'create_portal',
    
    # Memo
    'memo', 'lazy',
    
    # Error Boundaries
    'ErrorBoundary',
    
    # Styles
    'styled', 'css_module',
    
    # Server
    'render_to_string', 'render_to_static_markup',
]
```

---

## ✅ Checklist de Implementação

### Fase 1 - Core
- [ ] Sistema de VNode e função h()
- [ ] Classe base Component
- [ ] Renderizador DOM básico
- [ ] Algoritmo de reconciliação
- [ ] Sistema de eventos sintéticos

### Fase 2 - Hooks
- [ ] use_state
- [ ] use_effect
- [ ] use_context
- [ ] use_ref
- [ ] use_memo / use_callback
- [ ] use_reducer

### Fase 3 - Features
- [ ] Context API
- [ ] Refs e forwardRef
- [ ] Portals
- [ ] Error Boundaries
- [ ] Suspense (básico)

### Fase 4 - Performance
- [ ] Fiber architecture
- [ ] Scheduler com prioridades
- [ ] Keyed reconciliation
- [ ] Memoização

### Fase 5 - SSR
- [ ] render_to_string
- [ ] Hydration
- [ ] Streaming SSR

### Fase 6 - DevTools
- [ ] Debug mode
- [ ] Profiler
- [ ] StrictMode

### Fase 7 - CLI
- [ ] create app
- [ ] dev server
- [ ] build
- [ ] test runner

---

## 📖 Referências

1. **React Documentation** - https://react.dev/
2. **React Source Code** - https://github.com/facebook/react
3. **Fiber Architecture** - https://github.com/acdlite/react-fiber-architecture
4. **React Reconciliation** - https://react.dev/learn/preserving-and-resetting-state

---

## 📝 Notas Finais

Este documento serve como especificação completa para a implementação do PyReact. Cada seção deve ser implementada seguindo as especificações aqui descritas. A ordem de implementação deve seguir o checklist acima, começando pelo core e avançando para features mais complexas.

**Importante**: 
- Manter compatibilidade semântica com React
- Priorizar performance e DX (Developer Experience)
- Documentar todas as APIs públicas
- Escrever testes para cada feature
- Seguir PEP 8 para código Python

---

*Documento criado para especificação do framework PyReact*
*Versão: 1.0.0*
