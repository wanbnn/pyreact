# Guia de Instalação do PyReact

## Instalação Local (Desenvolvimento)

### Opção 1: Modo Editável (Recomendado para desenvolvimento)
```bash
pip install -e .
```
Isso permite que você edite o código e as mudanças sejam refletidas imediatamente.

### Opção 2: Instalação normal
```bash
pip install .
```

---

## Build e Distribuição

### 1. Instalar ferramentas de build
```bash
pip install build twine
```

### 2. Criar pacotes de distribuição
```bash
python -m build
```
Isso gera na pasta `dist/`:
- `pyreact-1.0.0.tar.gz` (source distribution)
- `pyreact-1.0.0-py3-none-any.whl` (wheel)

### 3. Instalar a partir do wheel gerado
```bash
pip install dist/pyreact-1.0.0-py3-none-any.whl
```

---

## Publicação no PyPI

### Testar no TestPyPI primeiro
```bash
# Criar conta em https://test.pypi.org/
twine upload --repository testpypi dist/*
```

### Publicar no PyPI oficial
```bash
# Criar conta em https://pypi.org/
twine upload dist/*
```

---

## Após publicação, usuários podem instalar com:
```bash
pip install pyreact
```

---

## Verificar instalação
```python
import pyreact
print(pyreact.__version__)  # 1.0.0
```

---

## Estrutura do pyproject.toml

O arquivo já está configurado com:
- ✅ Metadados (nome, versão, descrição, autores)
- ✅ Dependências
- ✅ Scripts CLI (`pyreact` command)
- ✅ Classificadores PyPI
- ✅ Configuração de pacotes
- ✅ URLs do projeto

---

## Comandos úteis

```bash
# Verificar metadados do pacote
pip show pyreact

# Listar arquivos instalados
pip show -f pyreact

# Verificar dependências
pip check

# Desinstalar
pip uninstall pyreact
```

---

## Correções Realizadas

### 1. Imports Corrigidos
- Adicionado `Union` aos imports em `pyreact/core/component.py`
- Corrigido import em `pyreact/server/ssr.py` para usar `..core.element`

### 2. API DOM Padronizada
- Substituído métodos JavaScript (`appendChild`, `removeChild`, `firstChild`) por métodos Python (`append_child`, `remove_child`, `first_child`)
- Adicionados métodos à classe `Element` em `pyreact/dom/dom_operations.py`:
  - `set_attribute()`, `get_attribute()`, `remove_attribute()`
  - `set_style()`
  - `add_event_listener()`, `remove_event_listener()`
  - `set_inner_html()`
  - `insert_child()`, `remove_child_at()`, `replace_child_at()`, `move_child()`

### 3. Sistema de Hooks
- Adicionado contexto de componente no reconciler para suportar hooks
- Importadas funções `_set_current_component` e `_reset_hook_index` em `pyreact/core/reconciler.py`

### 4. Reconciler Reescrito
- Arquivo `pyreact/core/reconciler.py` reescrito para usar operações DOM do framework
- Arquivo `pyreact/core/renderer.py` reescrito para usar API Python consistente

---

## Status Atual

✅ Projeto instalável via `pip install -e .`
✅ Build criado com sucesso (`python -m build`)
✅ Exemplo `counter.py` funcionando
✅ CLI funcionando (`pyreact create meu-app`)
✅ Servidor de desenvolvimento implementado
✅ Contador funcionando corretamente
✅ Testes E2E implementados
✅ Pronto para publicação no PyPI

---

## Testes Realizados

### Testes E2E
- ✅ Criação de projeto
- ✅ Servidor de desenvolvimento
- ✅ Geração de componentes
- ✅ Geração de hooks
- ✅ Contador funcional

### Documentação de Testes
- 📄 `Teste_Documentos/test_report_final.md` - Relatório completo
- 📄 `Teste_Documentos/README.md` - Guia de testes
- 📄 `tests/e2e/test_simple_e2e.py` - Testes E2E
- 📄 `tests/e2e/test_ab_counter.py` - Testes A/B
- 📄 `tests/e2e/test_manual.py` - Testes manuais

---

## Correções Adicionais (CLI)

### 5. Encoding UTF-8 no Windows
- Adicionado `encoding='utf-8'` em todos os `write_text()` no arquivo `pyreact/cli/main.py`
- Substituído caracteres especiais (✓) por caracteres ASCII ([OK]) para compatibilidade com Windows

### 6. Comandos CLI Testados
```bash
# Criar novo projeto
pyreact create meu-app

# Iniciar servidor de desenvolvimento
pyreact dev

# Iniciar servidor em porta específica
pyreact dev --port 3001

# Criar componente
pyreact generate component Button

# Criar hook
pyreact generate hook useCounter
```

### 7. Servidor de Desenvolvimento
O servidor de desenvolvimento foi implementado com as seguintes funcionalidades:
- Servidor HTTP embutido (porta padrão: 3000)
- Abre automaticamente o navegador
- Gera HTML com runtime PyReact simulado
- Suporta hot reload (simulado)
- Pode ser interrompido com Ctrl+C
