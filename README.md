# Arclith POC Todo

POC Arclith montrant qu'un même coeur applicatif peut être exposé par FastAPI, FastMCP et LangGraph.

## Liens du projet

- Framework : [karned-agency/arclith](https://github.com/karned-agency/arclith)
- Documentation : [arclith.karned.bzh](https://arclith.karned.bzh/)
- Tutoriel associé : [Todo list](https://arclith.karned.bzh/tutorials/todo-list/)
- Issues du framework : [karned-agency/arclith/issues](https://github.com/karned-agency/arclith/issues)

## Ce que le POC démontre

- `Todo`, `CreateTodoPort` et `ListTodosPort` restent dans le coeur métier.
- FastAPI adapte HTTP vers les ports inbound.
- FastMCP expose les mêmes use cases sous forme de tools MCP.
- LangGraph orchestre une conversation, mais appelle les mêmes ports que l'API et le MCP.
- Les intent-interpreters séparent la classification d'action (`TodoActionInterpreter`) de
  l'extraction de champs (`TodoConversationInterpreter`).
- Le runtime utilise MongoDB pour partager les données entre processus.
- Les tests utilisent une config `memory` temporaire pour rester rapides et déterministes.

## Installer

```bash
uv sync
uv run python -m pytest
```

## Lancer les tests

```bash
uv run python -m pytest
```

La suite de tests copie `config/` dans un dossier temporaire et remplace `repository: mongodb` par
`repository: memory`. Cela permet de tester le coeur, le MCP et l'agent sans démarrer MongoDB.

## Configurer MongoDB pour le runtime

`config/secrets.yaml` déclare le mapping attendu. Créez un fichier local `secrets.yaml` à la racine:

```yaml
adapters:
  mongodb:
    uri: "mongodb://arclith:arclith@127.0.0.1:27017/todo_list_service?authSource=admin"
```

Ce fichier est ignoré par Git.

## Lancer l'API

```bash
MODE=api uv run python main.py
```

Swagger:

```text
http://127.0.0.1:8120/docs
```

## Lancer le MCP

```bash
MODE=mcp_http uv run python main.py
```

Endpoint MCP:

```text
http://127.0.0.1:8121/mcp
```

## Lancer LangGraph

LM Studio doit exposer un serveur OpenAI-compatible sur `http://127.0.0.1:1234/v1`.

```bash
uv run langgraph dev --no-browser --allow-blocking --port 2024
```

Le graphe est déclaré dans `langgraph.json`:

```text
todo_agent -> src/todo_list_service/adapters/inbound/langgraph/agent.py:agent
```

## Découpage principal

```text
domain/models/todo.py
domain/ports/inbound/create_todo.py
domain/ports/inbound/list_todos.py
application/use_cases/create_todo.py
application/use_cases/list_todos.py
application/intent_interpreters/
adapters/inbound/fastapi/
adapters/inbound/fastmcp/
adapters/inbound/langgraph/
adapters/outbound/mongodb/
infrastructure/containers/todo_container.py
```

Le container est le seul endroit qui choisit le repository concret. Les adapters inbound ne parlent
qu'aux ports applicatifs.
