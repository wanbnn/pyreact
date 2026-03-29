# Guia de Publicação no PyPI

Este guia explica como publicar o PyReact no PyPI para que qualquer usuário possa instalar com `pip install pyreact`.

---

## Pré-requisitos

1. **Conta no PyPI**
   - Criar conta em: https://pypi.org/account/register/
   - Criar API Token: https://pypi.org/manage/account/token/

2. **Ferramentas necessárias**
   ```bash
   pip install build twine
   ```

---

## Passo a Passo

### 1. Build do Projeto

```bash
# Limpar builds anteriores
python -c "import shutil; from pathlib import Path; [shutil.rmtree(p, ignore_errors=True) for p in ['build', 'dist', 'pyreact.egg-info']]"

# Criar build
python -m build
```

Isso gera:
- `dist/pyreact-1.0.0.tar.gz` (source distribution)
- `dist/pyreact-1.0.0-py3-none-any.whl` (wheel)

---

### 2. Verificar a Build

```bash
# Verificar arquivos
twine check dist/*
```

---

### 3. Testar no TestPyPI (Recomendado)

```bash
# Upload para TestPyPI
twine upload --repository testpypi dist/*

# Testar instalação
pip install --index-url https://test.pypi.org/simple/ pyreact
```

---

### 4. Publicar no PyPI Oficial

```bash
# Upload para PyPI
twine upload dist/*
```

---

## Autenticação

### Opção 1: API Token (Recomendado)

1. Criar token em: https://pypi.org/manage/account/token/
2. Usar o token como senha:
   ```
   Username: __token__
   Password: pypi-<seu-token>
   ```

### Opção 2: Arquivo .pypirc

Criar arquivo `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-<seu-token>

[testpypi]
username = __token__
password = pypi-<seu-token>
```

---

## Após Publicação

### Verificar se foi publicado

```bash
# Verificar no PyPI
pip search pyreact

# Ou acessar: https://pypi.org/project/pyreact/
```

### Instalar

```bash
# Usuários podem instalar com:
pip install pyreact
```

---

## Atualizações

### Para atualizar versão:

1. Atualizar versão em `pyproject.toml`:
   ```toml
   version = "1.1.0"
   ```

2. Criar nova build:
   ```bash
   python -m build
   ```

3. Publicar:
   ```bash
   twine upload dist/*
   ```

---

## Versionamento Semântico

Usar formato: `MAJOR.MINOR.PATCH`

- **MAJOR**: Mudanças incompatíveis
- **MINOR**: Novas funcionalidades compatíveis
- **PATCH**: Correções de bugs

Exemplos:
- `1.0.0` → `1.0.1` (bug fix)
- `1.0.1` → `1.1.0` (nova funcionalidade)
- `1.1.0` → `2.0.0` (breaking change)

---

## Checklist de Publicação

- [ ] Atualizar versão em `pyproject.toml`
- [ ] Atualizar `CHANGELOG.md`
- [ ] Testar build localmente
- [ ] Verificar com `twine check`
- [ ] Testar no TestPyPI
- [ ] Publicar no PyPI
- [ ] Verificar instalação
- [ ] Criar release no GitHub

---

## Troubleshooting

### Erro: "File already exists"

**Causa:** Versão já publicada.

**Solução:** Incrementar versão.

### Erro: "Invalid authentication"

**Causa:** Token incorreto.

**Solução:** Verificar token em https://pypi.org/manage/account/token/

### Erro: "Package name already taken"

**Causa:** Nome já existe no PyPI.

**Solução:** Escolher outro nome ou verificar se é seu.

---

## Links Úteis

- PyPI: https://pypi.org/
- TestPyPI: https://test.pypi.org/
- Documentação: https://packaging.python.org/
- Twine: https://twine.readthedocs.io/

---

**Última atualização:** 28/03/2026
