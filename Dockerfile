FROM python:3.11-slim as base

ENV TZ=Asia/Tokyo \
    \
    POETRY_VERSION=1.4.0 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false
ENV PATH="$POETRY_HOME/bin:$PATH"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        curl \
        build-essential \
        git  \
        cron && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -


FROM base as development
WORKDIR /app
CMD bash -c "poetry install && /bin/bash"


FROM base as production
WORKDIR /app
COPY crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab && \
    /usr/bin/crontab /etc/cron.d/crontab

CMD bash -c "poetry install --no-dev && cron -f"
