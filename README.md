# 🐍 PyReact - Framework Web Declarativo para Python

[![PyPI version](https://badge.fury.io/py/pyreact-framework.svg)](https://pypi.org/project/pyreact-framework/)
[![Python](https://img.shields.io/pypi/pyversions/pyreact-framework.svg)](https://pypi.org/project/pyreact-framework/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**PyReact** é um framework web declarativo inspirado no React, mas construído nativamente para Python. Permite criar interfaces de usuário reativas, com componentes, hooks e renderização eficiente.

---

## 📦 Instalação

### Via pip (Recomendado)

```bash
pip install pyreact-framework
```

### Via pip (GitHub)

```bash
pip install git+https://github.com/wanbnn/pyreact.git
```

### Desenvolvimento Local

```bash
git clone https://github.com/wanbnn/pyreact.git
cd pyreact
pip install -e .
```

---

## 🚀 Início Rápido

### Criar um Novo Projeto

```bash
# Criar projeto
pyreact-framework create meu-app

# Entrar no diretório
cd meu-app

# Iniciar servidor de desenvolvimento
pyreact-framework dev
```

### Exemplo de Contador

```python
from pyreact import h, render, use_state, Component

def Counter(props):
    """Componente de contador funcional"""
    count, set_count = use_state(0)
    
    return h('div', {'className': 'counter'},
        h('h1', None, f'Contador: {count}'),
        h('button', {'onClick': lambda: set_count(count + 1)}, '+'),
        h('button', {'onClick': lambda: set_count(count - 1)}, '-')
    )

# Renderizar
root = document.getElementById('root')
render(h(Counter, None), root)
```

---

## ✨ Funcionalidades

### Componentes Funcionais

```python
def Button(props):
    """Componente de botão reutilizável"""
    return h('button', {
        'className': 'btn',
        'onClick': props.get('onClick')
    }, props.get('children'))
```

### Componentes de Classe

```python
class Counter(Component):
    """Componente de contador com estado"""
    
    def __init__(self, props):
        super().__init__(props)
        self.state = {'count': 0}
    
    def render(self):
        return h('div', None,
            h('h1', None, f'Count: {self.state["count"]}'),
            h('button', {
                'onClick': lambda: self.set_state({'count': self.state['count'] + 1})
            }, 'Increment')
        )
```

### Hooks

```python
from pyreact import use_state, use_effect, use_ref

def MyComponent(props):
    # Estado local
    count, set_count = use_state(0)
    
    # Efeito colateral
    use_effect(lambda: print(f'Count: {count}'), [count])
    
    # Referência
    input_ref = use_ref(None)
    
    return h('div', None, f'Count: {count}')
```

---

## 📖 Documentação

### 📚 Documentação Completa

A documentação completa está disponível no **Read the Docs**:

🔗 **https://pyreact-framework.readthedocs.io/**

#### Conteúdo da Documentação:

- **Getting Started**
  - Installation
  - Quick Start
  - Tutorial (Todo App)
  
- **Core Concepts**
  - Components
  - Props
  - State
  - Events
  - Lifecycle
  
- **Advanced**
  - Server-Side Rendering (SSR)
  - Routing
  - Styling
  - Testing
  
- **API Reference**
  - Element API
  - Component API
  - Hooks API
  - CLI API

### CLI Commands

```bash
# Criar novo projeto
pyreact create <nome>

# Iniciar servidor de desenvolvimento
pyreact-framework dev [--port PORT]

# Gerar componente
pyreact generate component <nome>

# Gerar hook
pyreact generate hook <nome>

# Build para produção
pyreact build
```

### API Principal

#### `h(type, props, *children)`

Cria um elemento virtual (VNode).

```python
h('div', {'className': 'container'},
    h('h1', None, 'Título'),
    h('p', None, 'Parágrafo')
)
```

#### `render(element, container)`

Renderiza um elemento no container.

```python
render(h(App, None), document.getElementById('root'))
```

#### `create_root(container)`

Cria uma raiz de renderização (API moderna).

```python
root = create_root(document.getElementById('root'))
root.render(h(App, None))
```

---

## 🧪 Testes

### Executar Testes

```bash
# Testes unitários
pytest tests/

# Testes E2E
python tests/e2e/test_simple_e2e.py

# Testes A/B
python tests/e2e/test_ab_counter.py

# Com cobertura
pytest tests/ --cov=pyreact
```

### Documentação de Testes

Ver `Teste_Documentos/README.md` para mais detalhes.

---

## 📁 Estrutura do Projeto

```
pyreact/
├── pyreact/              # Código fonte
│   ├── cli/              # Interface de linha de comando
│   ├── core/             # Núcleo do framework
│   ├── dom/              # Operações DOM
│   ├── server/           # Renderização servidor
│   └── utils/            # Utilitários
├── tests/                # Testes
│   ├── e2e/              # Testes end-to-end
│   └── unit/             # Testes unitários
├── examples/             # Exemplos
├── Teste_Documentos/     # Documentação de testes
├── pyproject.toml        # Configuração do projeto
├── README.md             # Este arquivo
├── INSTALL.md            # Guia de instalação
├── PUBLISH.md            # Guia de publicação
└── LICENSE               # Licença MIT
```

---

## 🛠️ Desenvolvimento

### Configurar Ambiente

```bash
# Clonar repositório
git clone https://github.com/wanbnn/pyreact.git
cd pyreact

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -e .

# Instalar dependências de desenvolvimento
pip install pytest pytest-cov playwright
playwright install chromium
```

### Executar em Desenvolvimento

```bash
# Instalar em modo editável
pip install -e .

# Executar testes
pytest tests/ -v

# Criar build
python -m build
```

---

## 📦 Publicação

### Build

```bash
# Limpar builds anteriores
python -c "import shutil; from pathlib import Path; [shutil.rmtree(p, ignore_errors=True) for p in ['build', 'dist', 'pyreact.egg-info']]"

# Criar build
python -m build
```

### Publicar no PyPI

```bash
# Instalar twine
pip install twine

# Verificar build
twine check dist/*

# Publicar no TestPyPI (teste)
twine upload --repository testpypi dist/*

# Publicar no PyPI (oficial)
twine upload dist/*
```

Ver `PUBLISH.md` para mais detalhes.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 📞 Contato

- **GitHub Issues:** https://github.com/wanbnn/pyreact/issues
- **Documentação:** https://pyreact.readthedocs.io/
- **Email:** contato@pyreact.dev

---

## 🙏 Agradecimentos

- Inspirado no [React](https://reactjs.org/)
- Construído com ❤️ pela comunidade Python

---

**Feito com ❤️ pela comunidade Python**
