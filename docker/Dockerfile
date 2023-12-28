FROM python:3.8.18-slim-bullseye
RUN apt-get update \
    && apt-get install -y \
    curl \
    gcc \
    git \
    ruby-sass \
    gnupg2 \
    libc6-dev \
    libdpkg-perl \
    make \
    gettext \
    libpq-dev
RUN touch /etc/apt/preferences.d/nodejs && \
    echo "Package: nodejs\nPin: origin deb.nodesource.com\nPin-Priority: 1001" > /etc/apt/preferences.d/nodejs
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash - && apt install nodejs -y
RUN pip install poetry
RUN poetry config virtualenvs.create false
COPY ./ /ej-application
WORKDIR ej-application
# Installs main and dev groups dependencies
RUN poetry install --with main,dev
