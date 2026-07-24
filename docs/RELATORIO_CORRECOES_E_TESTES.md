# Relatório de Correções e Testes — PyReact 1.0.5

Data da validação: 24/07/2026

## Resumo

O projeto foi analisado a partir de uma execução limpa da suíte. A primeira
execução apresentou 12 falhas e 6 erros. Após as correções e a inclusão do
pipeline de release, a suíte completa terminou com 106 testes aprovados.

## Problemas encontrados e correções

### Estado de componentes

`Component.set_state()` mantinha o novo estado apenas em uma fila quando o
componente não possuía um renderizador conectado. O estado agora é aplicado
sincronamente nesse cenário, incluindo a execução dos callbacks pendentes.

### Hooks

O cursor de hooks era global e podia ser compartilhado incorretamente entre
componentes. O cursor passou a pertencer ao componente atual, sendo reiniciado
a cada renderização. `use_effect`, `use_ref`, `use_memo` e `use_id` agora
preservam corretamente seus valores entre renderizações.

### Reconciliação e renderização

Componentes funcionais não recebiam um atualizador, portanto mudanças feitas
por `use_state` não chegavam ao DOM. O reconciliador agora:

- conecta componentes montados ao atualizador;
- reaplica hooks durante a renderização;
- atualiza, adiciona, substitui e remove filhos;
- substitui textos sem duplicar o conteúdo anterior;
- mantém a referência do nó DOM após uma atualização.

### Server-Side Rendering

`render_to_string()` não incluía `data-reactroot` quando o elemento raiz não
possuía props. O marcador agora é emitido somente no elemento raiz, sem poluir
os descendentes. `render_to_static_markup()` continua sem marcadores de
hidratação.

### Utilitários de teste

Os imports de `pyreact.testing` apontavam para módulos inexistentes. O renderer
de teste agora monta a árvore real, conecta o `screen`, suporta `rerender()` e
`cleanup()`, e os eventos são encaminhados aos listeners do DOM.

### CLI e projetos gerados

- adicionada a entrada de console `pyreact`, mantendo `pyreact-framework`;
- o scaffold passa a incluir `public/index.html` e `public/.gitkeep`;
- o comando `dev` ganhou `--no-open`, adequado para CI;
- o comando `build` agora cria um `dist` utilizável;
- o hook gerado deixou de usar `use_effect` como decorator inválido;
- a versão pública foi alinhada para 1.0.5.

### Testes E2E

Os testes antigos dependiam de executável instalado, diretórios fixos, sleeps
e portas fixas. Eles foram substituídos por E2E isolados que:

- criam um projeto temporário;
- escolhem uma porta livre;
- aguardam o servidor responder;
- validam scaffold, geração de componente/hook e build;
- abrem o Chromium e exercitam incremento e decremento do contador;
- finalizam o servidor mesmo quando um teste falha.

## Resultado final

Comando:

```bash
python -m pytest -q
```

Resultado:

```text
106 passed
```

Também foram verificados o carregamento do pacote, a renderização reativa, a
CLI, o servidor HTTP, o build de produção e a interação real no navegador.
