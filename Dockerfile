FROM python:3.9

WORKDIR /usr/src/app
RUN chmod g+w /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y telnet traceroute

COPY manage.py ./
COPY pysakoinnin_sahk_asiointi/ pysakoinnin_sahk_asiointi/
COPY api/ api/
COPY docker-entrypoint.sh ./

RUN ["chmod", "+x", "/usr/src/app/docker-entrypoint.sh"]

ENTRYPOINT [ "./docker-entrypoint.sh" ]