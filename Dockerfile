FROM python:3.13-slim@sha256:36873bb51bd4d8a05e0023a74ad109b002e247bd903b4ca43a6566a499da58ae

# This prevents Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# This disables virtual env creation
ENV POETRY_VIRTUALENVS_CREATE 0

RUN apt-get -y update \
    && apt-get install -y locales locales-all gnupg sudo curl wget vim \
    unzip rsyslog gettext patch gcc g++ build-essential \
    pkg-config libxml2-dev libxmlsec1-dev libxmlsec1-openssl \
    && apt-get dist-upgrade -y \
    && rm -rf /var/lib/apt/lists

RUN pip install --upgrade pip poetry Cython~=3.0 gitignore_parser~=0.1

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --no-cache && rm -rf /root/.cache/

COPY . .

CMD ["python", "main.py"]