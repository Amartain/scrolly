# Scrolly

A local, offline, neurodivergent-friendly task manager. Runs on your machine, in your browser.

## Install and run

```
pip install scrolly
scrolly
```

Your data lives in `~/.scrolly/`. Nothing leaves your machine.

## Develop

```
py -m pip install uv
uv sync
cd frontend && npm install && npx playwright install chromium && cd ..
uv run poe dev      # API + frontend with hot reload
uv run poe check    # linters, types, tests, end-to-end
```

Licensed under the AGPL-3.0 (see `LICENSE`).
