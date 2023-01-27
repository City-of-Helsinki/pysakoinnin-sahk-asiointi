FROM python:3.8

WORKDIR /usr/src/app
RUN chmod g+w /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY manage.py ./
COPY pysakoinnin_sahk_asiointi/*.py pysakoinnin_sahk_asiointi/
COPY rectification/*.py rectification/
COPY docker-entrypoint.sh ./

RUN ["chmod", "+x", "/usr/src/app/docker-entrypoint.sh"]

ENTRYPOINT [ "./docker-entrypoint.sh" ]