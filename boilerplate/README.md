# Orbit Board — Boilerplate PyReact

Aplicação de gestão de tarefas criada pela CLI do PyReact e expandida para
demonstrar o framework em um projeto com estrutura, estado e testes reais.

## O que o exemplo demonstra

- scaffold criado com `pyreact create boilerplate`;
- componentes funcionais reutilizáveis;
- `use_state` para tarefas e filtro ativo;
- `use_memo` e hook customizado para métricas derivadas;
- eventos de criação, conclusão, exclusão e filtragem;
- reconciliação do DOM após múltiplas atualizações;
- SSR estático de componentes de apresentação;
- testes de integração no DOM Python;
- teste E2E no Chromium;
- servidor de desenvolvimento e build estático.

## Estrutura

```text
boilerplate/
├── public/index.html          # interface web servida pelo CLI
├── src/
│   ├── components/
│   │   ├── stat_card.py
│   │   └── task_card.py
│   ├── hooks/use_task_stats.py
│   └── index.py               # aplicação construída com a API PyReact
├── tests/
│   ├── test_app.py            # integração do runtime Python
│   └── test_browser_e2e.py    # fluxo real no Chromium
└── pyproject.toml
```

## Instalação

Como este boilerplate está dentro do repositório do framework, instale a versão
local em modo editável:

```bash
cd ..
python -m pip install -e ".[e2e]"
cd boilerplate
python -m playwright install chromium
```

## Executar

```bash
pyreact dev
```

Acesse `http://127.0.0.1:3000`.

Para executar sem abrir o navegador automaticamente:

```bash
pyreact dev --no-open --port 3000
```

## Testar

```bash
python -m pytest -q
```

Resultado esperado:

```text
5 passed
```

## Build

```bash
pyreact build
```

O resultado é criado em `dist/index.html`.

## Nota sobre o runtime atual

O código em `src/index.py` exercita o runtime Python do PyReact nos testes de
integração. A versão atual da CLI ainda não transpila Python para JavaScript;
por isso, o servidor web entrega a implementação equivalente e autocontida de
`public/index.html`. Os dois caminhos representam a mesma aplicação e são
validados separadamente.

