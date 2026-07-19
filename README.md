# calstat

A python project for ...

It is managed with Pixi, using Hatchling as its Python build backend, pytest for tests, and Ruff for linting and formatting.

## Development

Make sure to install Pixi before working on the project. In terms of the code editor, I use VSCode, and I have some useful settings for it in the repository. I also used the following extensions:

| Extension | ID | Purpose |
|---|---|---|
| Python | `ms-python.python` | Python editing, debugging, testing, and environment integration |
| Pylance | `ms-python.vscode-pylance` | Type analysis, hover information, navigation, and auto-imports |
| Python Environments | `ms-python.vscode-python-envs` | Environment discovery and selection |
| Pixi Code | `renan-r-santos.pixi-code` | Connects Pixi environments to VS Code's Python environment system |
| Ruff | `charliermarsh.ruff` | Ruff diagnostics, fixes, and formatting |
| Google Workspace Developer Tools | `google-workspace` | OAuth2 Scope Linting |

To start writing code, clone the repository using git, and install the environment using:

```bash
pixi install
```

Run the application through the named Pixi task:

```bash
pixi run run
```

Other commands you may need for development are defined in `pyproject.toml` under `tool.pixi.tasks`.