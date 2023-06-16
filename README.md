# Pysaköinnin Sähköinen Asiointi API

Django API application
for [Pysäköinnin Sähköinen Asiointi](https://helsinkisolutionoffice.atlassian.net/wiki/spaces/PSA/overview)

## Running the application with docker-compose

⚠️ ️Requires a `config.env` file to run, contact admin if needed

To override production Docker-Compose settings insert the following file to your root

```
./docker-compose.override.yml

version: '3'
services:
  server:
    container_name: api-server
    env_file:
      - config.env
    environment:
      - DATABASE_URL=postgres://parking-user:root@api-db:5432/parking-service
    expose:
      - 8080
    depends_on:
      - db

  db:
    container_name: api-db
    image: postgres:alpine
    restart: always
    environment:
      - POSTGRES_USER=parking-user
      - POSTGRES_PASSWORD=root
      - POSTGRES_DB=parking-service
    volumes:
      - db:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    expose:
      - 5432

volumes:
  db:
    driver: local
```

Then simply run `docker-compose up` and Docker will build PostgreSQL database and Django server instances

Note that running the app with Docker proxies the application to port `8080`

## Running the application with hot-reload (recommended for active development)

- Install a Python virtual environment of your choice (for example [venv](https://docs.python.org/3/tutorial/venv.html))
  with Python 3.x
- In a new terminal window start a local database instance with
  `docker run --name parking-service-db -p 5432:5432 -e POSTGRES_USER=parking-user -e POSTGRES_PASSWORD=root -e POSTGRES_DB=parking-service postgres:alpine`
- Make sure a `config.env` file is present in your root directory
- Activate virtual environment
- Install dependencies with `pip install -r requirements.in`
- Run migrations `python manage.py migrate`
- Run server `python manage.py runserver`


- Alternatively you can run server with `gunicorn pysakoinnin_sahk_asiointi.wsgi:application --bind 0.0.0.0:8000`

Note: psycopg2 may require a local installation of PostgreSQL. Install for macOS with Homebrew `brew install postgresql`

## Generating requirements.txt

- Install [pip-tools](https://github.com/jazzband/pip-tools)
- Run `pip-compile` to generate a new requirements.txt file 