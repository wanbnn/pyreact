# Publicação automática no PyPI

O workflow `.github/workflows/publish.yml` executa em todo push para `master`.

## Fluxo

1. Instala o PyReact e as dependências de desenvolvimento.
2. Instala o Chromium usado pelos testes E2E.
3. Executa os testes do framework e do boilerplate.
4. Gera uma versão PEP 440 única a partir da versão-base:
   `1.0.5.post<ID da execução>`.
5. Constrói wheel e source distribution.
6. Valida os artefatos com `twine check`.
7. Publica no PyPI usando uma credencial OIDC temporária.

Se qualquer teste ou validação falhar, a publicação não acontece.

## Configuração única no PyPI

Não adicione tokens permanentes aos secrets do GitHub. No projeto
`pyreact-framework` do PyPI:

1. Acesse **Manage → Publishing**.
2. Adicione um **GitHub Trusted Publisher**.
3. Preencha:

| Campo | Valor |
|---|---|
| Owner | `wanbnn` |
| Repository | `pyreact` |
| Workflow | `publish.yml` |
| Environment | `pypi` |

Depois de salvar, execute novamente o workflow que eventualmente tenha falhado
antes dessa configuração.

## Versionamento

A versão declarada em `pyproject.toml` é a versão-base da próxima série de
publicações. Cada execução automática publica uma post-release única, por
exemplo:

```text
1.0.5.post1234501
1.0.5.post1234601
```

Para iniciar uma nova versão estável, altere `pyproject.toml` e
`pyreact/__init__.py` para a mesma versão, por exemplo `1.0.6`. Os próximos
pushes publicarão `1.0.6.post...`.

## Execução manual

Também é possível iniciar o workflow em **Actions → Test and publish PyReact →
Run workflow**. A publicação somente ocorre quando a execução usa a branch
`master`.

