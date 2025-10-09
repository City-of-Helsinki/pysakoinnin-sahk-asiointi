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

1. Install a Python virtual environment of your choice (for example [venv](https://docs.python.org/3/tutorial/venv.html))
  with Python 3.x
2. In a new terminal window start a local database instance with
  `docker run --name parking-service-db -p 5432:5432 -e POSTGRES_USER=parking-user -e POSTGRES_PASSWORD=root -e POSTGRES_DB=parking-service postgres:alpine`
3. Activate virtual environment
    - if you are using venv, the command is `source [insert your venv directory name here]/bin/activate` on Mac and Unix and `[insert your venv directory name here]\Scripts\activate.bat` on Windows
    - the virtual environment can be deactivated with `deactivate`
4. Install dependencies with `pip install -r requirements.in`
5. Run migrations `python manage.py migrate`
6. Run server `python manage.py runserver`
7. you can open `http://localhost:8000/api/v1/docs` to view the API endpoints in browser


- Alternatively you can run server with `gunicorn pysakoinnin_sahk_asiointi.wsgi:application --bind 0.0.0.0:8000`

## Generating a new requirements.txt

- Install [pip-tools](https://github.com/jazzband/pip-tools)
- Run `pip-compile` to generate a new requirements.txt file
