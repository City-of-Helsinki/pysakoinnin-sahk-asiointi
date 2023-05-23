# Build a base image for development and production stages.
# Note that this stage won't get thrown out so we need to think about
# layer sizes from this point on.
FROM helsinkitest/python:3.9-slim as appbase

WORKDIR /usr/src/app
RUN chmod g+w /usr/src/app

# Copy requirement files.
COPY requirements.txt ./

# Install main project dependencies and clean up.
# Note that production dependencies are installed here as well since
# that is the default state of the image and development stages are
# just extras.
RUN apt-get update && apt-get install -y telnet traceroute postgresql
RUN pip install --no-cache-dir -r ./requirements.txt

# Copy and set the entrypoint.
COPY docker-entrypoint.sh ./
RUN ["chmod", "+x", "/usr/src/app/docker-entrypoint.sh"]
ENTRYPOINT ["./docker-entrypoint.sh"]

ENV STATIC_ROOT /var/parking-service/static
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /var/parking-service/static

# Build production image using the appbase stage as base. This should always
# be the last stage of Dockerfile.
FROM appbase as production

# Copy application code.
COPY . ./

# /app/data needs write access for Django management commands to work
RUN mkdir -p ./data
RUN chgrp -R 0 ./data && chmod g+w -R ./data

# Set user and document the port.
USER nobody:0
EXPOSE 8000/tcp