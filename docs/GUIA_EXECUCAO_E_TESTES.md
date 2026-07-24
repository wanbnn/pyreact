# Guia de Execução e Testes — PyReact

## Preparação

Na raiz do repositório:

```bash
python -m pip install -e ".[dev]"
```

Para executar os testes E2E, instale também o Playwright e o Chromium:

```bash
python -m pip install playwright
python -m playwright install chromium
```

## Testar o framework

Suíte completa:

```bash
python -m pytest -q
```

Somente E2E:

```bash
python -m pytest tests/e2e -q
```

Com cobertura:

```bash
python -m pytest --cov=pyreact --cov-report=term-missing
```

## Criar e executar um projeto

```bash
pyreact create meu-app
cd meu-app
pyreact dev
```

Em ambientes de CI ou quando não se deseja abrir uma janela automaticamente:

```bash
pyreact dev --no-open --port 3000
```

Acesse `http://127.0.0.1:3000`.

## Gerar arquivos

```bash
pyreact generate component Button
pyreact generate component Counter --class
pyreact generate hook useCounter
```

## Build

```bash
pyreact build
```

Os arquivos públicos são copiados para `dist`. O conteúdo dessa pasta pode ser
servido por qualquer servidor HTTP estático.

## Gerar novamente os PDFs

```bash
python scripts/generate_pdfs.py
```

O comando atualiza:

- `docs/Manual_PyReact.pdf`;
- `docs/Relatorio_Correcoes_e_Testes.pdf`;
- `docs/Guia_Execucao_e_Testes.pdf`.

