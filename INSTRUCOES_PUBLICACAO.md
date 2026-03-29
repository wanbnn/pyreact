# 🚀 Instruções de Publicação - PyReact v1.0.0

## Status Atual

✅ **Build criada com sucesso!**

Arquivos gerados em `dist/`:
- `pyreact-1.0.0-py3-none-any.whl` (65 KB) - Wheel
- `pyreact-1.0.0.tar.gz` (61 KB) - Source distribution

---

## 📋 Pré-requisitos para Publicação

### 1. Conta no PyPI

1. Acesse: https://pypi.org/account/register/
2. Crie uma conta
3. Verifique seu email

### 2. API Token

1. Acesse: https://pypi.org/manage/account/token/
2. Crie um novo token
3. Copie o token (começa com `pypi-`)

### 3. Instalar Twine

```bash
pip install twine
```

---

## 🚀 Publicar no PyPI

### Opção 1: Usar Script Python

```bash
python scripts/publish.py
```

### Opção 2: Usar Script Bash (Linux/Mac)

```bash
bash scripts/publish.sh
```

### Opção 3: Comando Manual

```bash
# Verificar build
twine check dist/*

# Publicar
twine upload dist/*
```

**Quando solicitado:**
- Username: `__token__`
- Password: `pypi-<seu-token-aqui>`

---

## ✅ Verificar Publicação

### 1. Aguardar alguns minutos

O PyPI pode levar alguns minutos para processar.

### 2. Verificar no site

Acesse: https://pypi.org/project/pyreact/

### 3. Testar instalação

```bash
# Em um ambiente limpo
pip install pyreact

# Verificar
python -c "import pyreact; print(pyreact.__version__)"
```

---

## 🎯 Após Publicação

### 1. Criar Release no GitHub

```bash
# Criar tag
git tag v1.0.0
git push origin v1.0.0

# No GitHub:
# - Criar novo release
# - Anexar arquivos de dist/
# - Escrever release notes
```

### 2. Anunciar

- Twitter/LinkedIn
- Reddit: r/Python
- Hacker News
- Python Weekly

---

## 📊 Checklist Final

- [ ] Conta criada no PyPI
- [ ] API Token gerado
- [ ] Twine instalado
- [ ] Build verificada (`twine check dist/*`)
- [ ] Publicado no PyPI
- [ ] Verificado no site
- [ ] Testado instalação
- [ ] Release criado no GitHub
- [ ] Anunciado

---

## ⚠️ Problemas Comuns

### "File already exists"

**Causa:** Versão já publicada.

**Solução:** Incrementar versão em `pyproject.toml`.

### "Invalid authentication"

**Causa:** Token incorreto.

**Solução:** Verificar token em https://pypi.org/manage/account/token/

### "Package name already taken"

**Causa:** Nome já existe.

**Solução:** Escolher outro nome ou verificar se é seu.

---

## 📞 Suporte

Se encontrar problemas:

1. Verificar documentação: https://packaging.python.org/
2. Verificar status do PyPI: https://status.python.org/
3. Pedir ajuda: https://github.com/wanbnn/pyreact/issues

---

**Última atualização:** 28/03/2026
**Versão:** 1.0.0
**Status:** ✅ Pronto para publicação
