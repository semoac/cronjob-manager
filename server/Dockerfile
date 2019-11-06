FROM python:3-alpine
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app
#RUN curl --silent https://bootstrap.pypa.io/get-pip.py | python3.7
RUN pip3 install pipenv

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN set -ex && pipenv install --deploy --system

COPY . /app/server/

CMD gunicorn -b 0.0.0.0:8000 server.app:app