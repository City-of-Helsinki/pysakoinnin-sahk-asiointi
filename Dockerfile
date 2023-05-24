# Build a base image for development and production stages.
# Note that this stage won't get thrown out so we need to think about
# layer sizes from this point on.
FROM nginx:stable-alpine3.17-slim as appbase

WORKDIR /usr/src/app
RUN chmod g+w /usr/src/app

# Copy requirement files.
COPY requirements.txt ./

# Install main project dependencies and clean up.
# Note that production dependencies are installed here as well since
# that is the default state of the image and development stages are
# just extras.
RUN apk update && apk add --no-cache traceroute postgresql python3
RUN python3 -m ensurepip
RUN pip3 install --no-cache-dir -r ./requirements.txt

ENV STATIC_ROOT /var/parking-service/static
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /var/parking-service/static

# Build production image using the appbase stage as base. This should always
# be the last stage of Dockerfile.
FROM appbase as prod

# Copy application code.
COPY . ./

# /app/data needs write access for Django management commands to work
RUN mkdir -p ./data
RUN chgrp -R 0 ./data && chmod g+w -R ./data

# Collect static files
RUN SECRET_KEY="only-used-for-collectstatic" python manage.py collectstatic --noinput

# Copy NGINX conf
COPY nginx.conf /etc/nginx/nginx.conf
# link nginx logs to container stdout
RUN ln -sf /dev/stdout /var/log/nginx/access.log && ln -sf /dev/stderr /var/log/nginx/error.log

# Copy and set the entrypoint.
COPY docker-entrypoint.sh ./
RUN ["chmod", "+x", "/usr/src/app/docker-entrypoint.sh"]
ENTRYPOINT ["./docker-entrypoint.sh"]

# Document the port and set random user to simulate OpenShift behaviour
USER nobody:0
EXPOSE 8080/tcp