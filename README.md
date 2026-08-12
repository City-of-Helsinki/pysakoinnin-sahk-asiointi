# Pysaköinnin Sähköinen Asiointi API

Django API application
for [Pysäköinnin Sähköinen Asiointi](https://helsinkisolutionoffice.atlassian.net/wiki/spaces/PSA/overview)

## Running locally

⚠️ ️Requires a `config.env` file to run, contact admin if needed and remember to add the file to the root of the directory.

### With Docker

1. Copy `config.env.example` to `config.env` and change the variable values to your liking.
2. Run `docker compose up` and Docker will build PostgreSQL database and Django server instances
3. You can open http://localhost:8080/api/v1/docs to view the API endpoints in browser

Note that running the app with Docker proxies the application to port `8080`

### Running the application with hot-reload (recommended for active development)

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. In a new terminal window start a local database instance with
  `docker run --name parking-service-db -p 5432:5432 -e POSTGRES_USER=parking-user -e POSTGRES_PASSWORD=root -e POSTGRES_DB=parking-service postgres:alpine`
3. Install dependencies with `uv sync`
4. Run migrations `uv run manage.py migrate`
5. Run server `uv run manage.py runserver`
6. you can open `http://localhost:8000/api/v1/docs` to view the API endpoints in browser


- Alternatively you can run server with `uv run --group prod gunicorn pysakoinnin_sahk_asiointi.wsgi:application --bind 0.0.0.0:8000`

## Managing dependencies

Dependencies are managed with [uv](https://docs.astral.sh/uv/) and defined in `pyproject.toml`.
Production dependencies live in `[project.dependencies]`, development-only dependencies in the
`dev` group and production-only dependencies (e.g. `gunicorn`) in the `prod` group under
`[dependency-groups]`.

- Add or update a dependency: `uv add <package>` (use `--group dev` or `--group prod` for the
  respective groups)
- Regenerate `uv.lock` after manually editing `pyproject.toml`: `uv lock`
- Install everything needed for local development: `uv sync --all-groups`

## Code format

This project uses [Ruff](https://docs.astral.sh/ruff/) for code formatting and quality checking.
Ruff needs to be explicitly installed in your Python environment, as it is not included in the `uv` setup.

Basic `ruff` commands:

* lint: `ruff check`
* apply safe lint fixes: `ruff check --fix`
* check formatting: `ruff format --check`
* format: `ruff format`

[`pre-commit`](https://pre-commit.com/) can be used to install and
run all the formatting tools as git hooks automatically before a
commit.

Set up the git hooks with `uvx pre-commit install`. To run all hooks
manually, use `uvx pre-commit run --all-files`.

If `pre-commit` is installed in the uv environment, the same commands
can be run with `uv run pre-commit` instead.
