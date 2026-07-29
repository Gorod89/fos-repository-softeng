# Быстрый старт

## Вариант 1. Codespaces

Откройте репозиторий в GitHub Codespaces. Конфигурация в `.devcontainer/`
подготавливает Python 3.12, uv, Docker CLI, клиент PostgreSQL и Jupyter.

## Вариант 2. Локальная среда

Установите Git, Python 3.12, uv и Docker Desktop или Docker Engine:

```bash
git clone https://github.com/Gorod89/fos-repository-softeng.git
cd fos-repository-softeng
uv sync --frozen
make validate
```

Затем перейдите в каталог нужного задания и выполните его `make install` и
`make test`.

## Диагностика

- `python --version` должен показать Python 3.12;
- `uv --version` — uv 0.8.4 или совместимую версию;
- `docker compose version` необходим для M2 и M8;
- секреты хранятся только в локальном `.env`, который запрещено коммитить.

Если команда не работает, приложите к issue точную команду, полный текст ошибки,
операционную систему и результат `make doctor` из starter-проекта.
