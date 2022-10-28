# Pysaköinnin Sähköinen Asiointi API

Django API application
for [Pysäköinnin Sähköinen Asiointi](https://helsinkisolutionoffice.atlassian.net/wiki/spaces/PSA/overview)

## Running the application with docker-compose

Insert the following configuration files to your local directory

```
./config.env
DEBUG=True
SECRET_KEY="development"
ALLOWED_HOSTS="localhost"

# Database related secrets
DB_PASSWORD="root"
DB_NAME="parking-service"
DB_USER="parking-user"
DB_HOST="localhost"
DB_PORT=5432
```

```
./docker-compose.override.yml

version: '3'
services:
  server:
    container_name: parking-service-server
    env_file:
      - config.env
    environment:
      - DB_HOST=parking-service-db
    depends_on:
      - db

  db:
    container_name: parking-service-db
    image: postgres:alpine
    restart: always
    environment:
      - POSTGRES_USER=parking-user
      - POSTGRES_PASSWORD=root
      - POSTGRES_DB=parking-service
    volumes:
      - db:/var/lib/postgresql/data

volumes:
  db:
    driver: local
```

Then simply run `docker-compose up` and Docker will build PostgreSQL database and Django server instances

## Running the application with hot-reload (recommended for active development)

- Install a Python virtual environment of your choice (for example [venv](https://docs.python.org/3/tutorial/venv.html))
  with Python 3.x
- In a new terminal window start a local database instance with
  `docker run --name parking-service-db -p 5432:5432 -e POSTGRES_USER=parking-user -e POSTGRES_PASSWORD=root -e POSTGRES_DB=parking-service postgres:alpine`
- Insert `config.env` file from above to your root directory
- Activate virtual environment
- Install dependencies with `pip install -r requirements.in`
- Run migrations `python manage.py migrate`
- Run server `python manage.py runserver`

Note: psycopg2 may require a local installation of PostgreSQL. Install for macOS with Homebrew `brew install postgresql`

## Generating requirements.txt

- Install [pip-tools](https://github.com/jazzband/pip-tools)
- Run `pip-compile` to generate a new requirements.txt file 